#!/usr/bin/python

from werkzeug.wrappers import Response

from db import export_sql


def render(vis, request, info):
    info["message"] = []
    table = request.args.get("table", '')

    Date = request.args.get("Date", '')
    TargetField = request.args.get("TargetField", '')
    ShortText = request.args.get("ShortText", '')
    Text = request.args.get("Text", '')

    where = request.args.get("where", '1=1')
    reload = int(request.args.get("reload", 0))
    view = request.args.get("view", '')
    start = request.args.get("start", '0')  # start at 0
    limit = request.args.get("limit", '100000')

    sql = "select '%s',%s,%s,%s from %s where %s order by 2 limit %s offset %s" % (
    TargetField, Date, ShortText, Text, table, where, limit, start)

    header = "TargetField,Date,ShortText,Text"

    (datfile, reload, result) = export_sql(sql, vis.config, reload, header, view)
    if len(result) == 0:
        return Response(open(datfile, 'r'))


	