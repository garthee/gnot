#!/usr/bin/python

# libraries from werkzeug
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.wsgi import SharedDataMiddleware
from jinja2 import Environment, FileSystemLoader, Markup

import json, sys, os, inspect, re, subprocess
from collections import defaultdict

# python3
try:
    from urllib.parse import urlparse
except:
    from urlparse import urlparse

# our webserver implementation
class Visulizer(object):

    def __init__(self):

        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_path),  autoescape=True)
        self.jinja_env.filters['hostname'] = lambda x: urlparse(x).netloc

        self.url_map = Map([
            Rule('/', endpoint='home'),
            Rule('/headless', endpoint='render'),
            Rule('/render', endpoint='render')
        ])

        self.loadConfig()

        # add modules directory to search path
        cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0], "modules")))
        if cmd_subfolder not in sys.path:
            sys.path.insert(0, cmd_subfolder)

        cache_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0], "cache")))
        if not os.path.exists(cache_subfolder):
            os.makedirs(cache_subfolder)

    def loadConfig(self):
        config = json.loads(open(os.path.realpath(os.path.expanduser('~/.gnot_config')), 'r').read())

        user = config.get('db_user', '')
        if len(user) > 0: config["user"] = '--username %s'%user

        passwd = config.get('db_pass', '')
        if len(passwd) > 0: config["passwd"] = '-p %s'%passwd

        host = config.get('db_host', '')
        if len(host) > 0: config["host"] = '-h %s'%host

        port = config.get('db_port', '')
        if len(port): config["port"] = '-p %s'%port

        schema = config.get('db_schema', '')
        if len(schema) > 0 : schema += '.'
        config["schema"] = schema

        config["database"] = config.get("db_database", '')

        p = subprocess.check_output(['/bin/ps', '-o', 'comm,pid,user'])
        config["uid"] = hex(hash(p) & 0xffffffff) #32 bit

        self.config = config

    def _parse_query(self, request):
        query = request.args.get('query', '')

        #matches = re.findall(r'([^:]+):\s(?=[^\s]+)', query)
        reg = r'\s*([^:]+):\s+((?=\")\"[^\"]+\"|[^\s]+)'
        matches = re.findall(reg, query)

        entries = defaultdict(list)
        for (key, value) in matches:
            if value or len(value) > 0:
                entries[key].append(value.encode('ascii', 'ignore').decode('ascii').strip('"'))

        if type(entries['view'] == 'str') and len(entries['view']) > 0:
            schema = self.config.get('db_schema', '')
            if len(schema) > 0 : schema += '.'
            entries['table'] = [schema+'custom_view']

        r = {}
        for (key, value) in entries.items():
            r[key] = ','.join(value)

        tables = re.split(r',(?![^(]*\))', r.get('table', ''))
        if len(tables) > 1:
            tables = [tables[i] + ' as table_%d'%(i+1)  for i in range(len(tables))]
            
        #delimiter = " %s "%(r.get('join', ','));
        r['table'] = ','.join(tables)

        #split fields
        sfield = re.sub(r',(?=[^"]*"(?:[^"]*"[^"]*")*[^"]*$)', '___', r.get('field', '')) # remove commas between quotation marks and replace them with _
        sfield = re.sub(r",(?=[^']*'(?:[^']*'[^']*')*[^']*$)", '___', sfield) # remove commas between quotation marks and replace them with _
        sfield = re.split(r',(?![^(]*\))', sfield)
        sfield = [re.sub(r'___', ',',s) for s in sfield] #put comma's back
        pfield = [re.compile(r' as ').split(f)[-1].strip() for f in sfield]
        r['sfield'] = sfield
        r['pfield'] = pfield

        r['query'] = query
        request.args = r
        return entries['module'][0]

    def on_render(self, request, headLess = False):

        module_name = self._parse_query(request)
        try:
            info = {}
            renderer = __import__(module_name)
            result = renderer.render(self, request, info)

            if result: # some modules might generate their own outputs
                return result
            else:
                return self.render_template('%s.html'%(module_name), **info)

        except ImportError as strerror:
            print("module not found %s"%strerror)
            raise NotFound()

    # home window
    def on_home(self, request):
        return self.render_template('index.html')

    # following are standard werkzeug methods
    def error_404(self, error = None):
        response = self.render_template('404.html')
        response.status_code = 404
        return response

    def render_template(self, template_name, **context):
        t = self.jinja_env.get_template(template_name)
        return Response(t.render(context), mimetype='text/html')

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, 'on_' + endpoint)(request, **values)
        except NotFound as e:
            return self.error_404(e)
        except HTTPException as e:
            return e

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


def create_app():
    app = Visulizer()

    # set up static paths with direct access
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
        '/static':  os.path.join(os.path.dirname(__file__), 'static'),
        '/cache':  os.path.join(os.path.dirname(__file__), 'cache'),
        '/favicon.ico': os.path.join(os.path.dirname(__file__), 'favicon.ico'),
    })
    return app


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    # disable debugger if put in operation
    app = create_app()
    run_simple(app.config['web_host'], app.config['web_port'], app, use_debugger=(not app.config['isProduction']), use_reloader=True, threaded=True)