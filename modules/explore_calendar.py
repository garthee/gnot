from jinja2 import Markup
from db import export_sql

def render(vis, request, info):
    info["message"] = []

    # module independent user inputs
    table = request.args.get("table", '')
    where = request.args.get("where", '1=1')
    limit = request.args.get("limit", '3650')  # 10 years max
    start = request.args.get("start", '0')  # start at 0
    reload = int(request.args.get("reload", 0))
    view = request.args.get("view", '')

    # module dependent user inputs
    xField = request.args.get("xField", '')
    field = request.args.get("field", " count(*) ")

    # verify essential parameter details - smell test
    if len(table) == 0 or not xField:
        info["message"].append("Table or xField missing")
        info["message_class"] = "failure"
    else:
        # prepare sql query
        sql = "select %s, %s from %s where %s group by 1 order by 1 limit %s offset %s" % (
        xField, field, table, where, limit, start)

        header = "Date,Field"
        (datfile, reload, result) = export_sql(sql, vis.config, reload, header, view)

        if len(result) > 0:
            info["message"].append(result)
            info["message_class"] = "failure"
        else:
            info["message_class"] = "success"
            if reload > 0:
                info["message"].append("Loaded fresh.")
            else:
                info["message"].append("Loading from cache. Use reload=1 to reload.")

            # if success return data file
            info["datfile"] = datfile

    # prepare some messages
    info["message"] = Markup(''.join('<p>%s</p>' % m for m in info["message"] if len(m) > 0))

    pfield = request.args.get("pfield", [])
    info["title"] = "FIELDS: <em>%s</em> along <br />xFIELD: <em>%s</em> from <br />TABLE: <em>%s</em>" \
                    % (', '.join(pfield), xField, table)
    info["title"] = Markup(info["title"])

    # format the message to encode HTML characters
    info['query'] = Markup(request.args.get('query', ''))
	

	