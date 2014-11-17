from jinja2 import Markup

from db import export_sql


def render(vis, request, info):
    info["message"] = []

    reload = request.args.get("reload", 0)
    table = request.args.get("table", '')
    where = request.args.get("where", '1=1')
    field = request.args.get("field", '')
    view = request.args.get("view", '')
    start = request.args.get("start", '0')  # start at 0
    limit = request.args.get("limit", '1000')
    groupby = field

    pfield = request.args.get("pfield", [])

    if len(table) == 0 or not field:
        info["message"].append("table or field missing.")
        info["message_class"] = "failure"
    else:
        sql = "select %s, count(*) as n from %s where %s group by %s order by n desc limit %s offset %s" % (
        field, table, where, groupby, limit, start)

        (datfile, reload, result) = export_sql(sql, vis.config, reload, None, view)
        if len(result) > 0:
            info["message"].append(result)
            info["message_class"] = "failure"
        else:
            info["message_class"] = "success"
            if reload > 0:
                info["message"].append("Loaded fresh.")
            else:
                info["message"].append("Loading from cache. Use reload=1 to reload.")

            info["datfile"] = datfile

    info["title"] = "FIELDS: <em>%s</em> from <br />TABLE: <em>%s</em>" % (', '.join(pfield[:2]), table)
    info["title"] = Markup(info["title"])

    info["message"] = Markup(''.join('<p>%s</p>' % m for m in info["message"] if len(m) > 0))
	