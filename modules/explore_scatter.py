import re

from jinja2 import Markup

from db import export_sql


def render(vis, request, info):
    info["message"] = []

    # user parameters
    table = request.args.get("table", '')
    field = request.args.get("field", '')
    where = request.args.get("where", '1=1')
    reload = int(request.args.get("reload", 0))
    view = request.args.get("view", '')
    limit = request.args.get("limit", '1000')
    start = request.args.get("start", '0')

    groupby = request.args.get("groupBy", '')
    if groupby and len(groupby) > 0: groupby = ' group by %s' % groupby

    orderBy = request.args.get("orderBy", '1')
    if orderBy and len(orderBy) > 0: orderBy = ' order by %s ' % orderBy

    pfield = request.args.get("pfield", [])  # fields split into an array
    sfield = request.args.get("sfield", [])  # field captions split into an array

    if len(table) == 0 or not field:
        info["message"].append("Table  or field missing.")
        info["message_class"] = "failure"
    elif len(sfield) < 2:
        info["message"].append("Not enough fields.")
        info["message_class"] = "failure"
    else:
        if len(sfield) > 4:
            info["message"].append("Too many fields. Only first 4 are used.")
            sfield = sfield[:4]

        info["xlabel"] = pfield[0]
        info["ylabel"] = pfield[1]

        # if z,c are not provided
        sfield.extend(['1'] * (4 - len(sfield)))
        pfield.extend(['1'] * (4 - len(pfield)))
        info["field3"] = pfield[3 - 1]
        info["field4"] = pfield[4 - 1]

        sql = "select %s from %s where %s %s %s limit %s offset %s" % (
        ','.join(sfield), table, where, groupby, orderBy, limit, start)
        header = "x,y,z,c"

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

    pfield = request.args.get("pfield", [])
    info[
        "title"] = "FIELD_X: <em>%s</em>, <br />FIELD_Y: <em>%s</em>, <br />FIELD_Z(size): <em>%s</em>, <br />FIELD_C(color): <em>%s</em> from <br />TABLE: <em>%s</em>" % (
    pfield[0], pfield[1], pfield[2], pfield[3], table)
    info["title"] = Markup(info["title"])

    info["message"] = Markup(''.join(['<p>%s</p>' % m for m in info["message"] if len(m) > 0]))


	