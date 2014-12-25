import json, csv, os

from collections import defaultdict
from werkzeug.wrappers import Response
from db import export_sql

def render(vis, request, info):
    dbscope = vis.config.get('db_scope', '')
    if len(dbscope) > 0 and (not 'where' in dbscope.lower()):
        dbscope = " WHERE " + dbscope

    if vis.config['db_system'] == 'mysql':
        sql = "SELECT table_name,column_name FROM information_schema.columns " + dbscope
    else:
        sql = "SELECT table_schema || '.' || table_name,column_name FROM information_schema.columns " + dbscope

    #load always
    reload = 1  # int(request.args.get("reload", 0))
    
    (datfile, reload, result) = export_sql(sql, vis.config, reload, None, None)

    table_list = defaultdict(list)

    reader = csv.DictReader(open(datfile, 'r'), fieldnames=( "table", "field" ))
    for row in reader:
        table_list[row['table']].append(row['field'])

    module_list = json.loads(open(os.path.realpath('modules/modules.json'), 'r').read())
    data = {'modules': module_list, 'tables': table_list}
    return Response(json.dumps(data))
