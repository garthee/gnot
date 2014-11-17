import re

from jinja2 import Markup

from db import export_sql


def render(vis, request, info):
    info["message"] = []
    table = request.args.get("table", '')
    field = request.args.get("field", '')
    where = request.args.get("where", '1=1')
    reload = int(request.args.get("reload", 0))
    view = request.args.get("view", '')
    start = request.args.get("start", '0')  # start at 0
    limit = request.args.get("limit", '1000')

    groupBy = request.args.get("groupBy", '')
    if groupBy and len(groupBy) > 0: groupBy = ' group by %s ' % groupBy

    orderBy = request.args.get("orderBy", '')
    if orderBy and len(orderBy) > 0: orderBy = ' order by %s ' % orderBy

    sfield = request.args.get("sfield", [])
    pfield = request.args.get("pfield", [])

    if len(table) == 0 or not field or len(sfield) < 2:
        info["message"].append("Table  or field missing.")
        info["message_class"] = "failure"
    else:

        if len(sfield) > 5:
            info["message"].append("Too many fields. Only first 5 are used.")
            sfield = sfield[:5]
            pfield = pfield[:5]

        info["fieldValue"] = pfield[0]
        info["title"] = "FIELD_1: <em>%s</em> against <br />OTHER FIELDS: <em>%s</em> from <br />TABLE: <em>%s</em>" % (
        pfield[0], ', '.join(pfield[1:]), table)

        sql = "select %s from %s where %s %s %s limit %s offset %s" % (
        ','.join(sfield), table, where, groupBy, orderBy, limit, start)

        header = "labels,%s" % (','.join(pfield[1:]))

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

            info["datfile"] = datfile

    info["title"] = Markup(info["title"])
    info["message"] = Markup(''.join('<p>%s</p>' % m for m in info["message"] if len(m) > 0))

	