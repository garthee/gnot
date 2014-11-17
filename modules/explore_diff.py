import os
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
    limit = request.args.get("limit", '5000')  # max 5000 data points

    groupBy = request.args.get("groupBy", '')
    if groupBy and len(groupBy) > 0: groupBy = ' group by %s ' % groupBy

    xField = request.args.get("xField", '')
    pfield = request.args.get("pfield", [])
    sfield = request.args.get("sfield", [])

    if len(table) == 0 or len(xField) == 0 or len(field) == 0:
        info["message"].append("Table  or field missing.")
        info["message_class"] = "failure"
    elif len(sfield) < 2:
        info["message"].append("Need at least two fields.")
        info["message_class"] = "failure"
    else:

        sql = "select %s, %s from %s where %s %s order by 1 limit %s offset %s" % (
        xField, ','.join(sfield[:2]), table, where, groupBy, limit, start)

        header = "Date,A,B"

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

    info["title"] = "Diff of <br />FIELD: <em>%s</em> on <br />FIELD: <em>%s</em> from <br />TABLE: <em>%s</em>" % (
    pfield[1], pfield[0], table)
    info["title"] = Markup(info["title"])

    info["message"] = Markup(''.join('<p>%s</p>' % m for m in info["message"] if len(m) > 0))

