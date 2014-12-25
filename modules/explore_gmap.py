import re

from jinja2 import Markup

from db import export_sql


def render(vis, request, info):
    info["message"] = []

    # module independent user inputs
    table = request.args.get("table", '')
    where = request.args.get("where", '1=1')
    limit = request.args.get("limit", '5000')  # 10 years max
    start = request.args.get("start", '0')  # start at 0
    reload = int(request.args.get("reload", 0))
    view = request.args.get("view", '')

    limit = ' limit %s' % limit

    # module dependent user inputs
    latitude = request.args.get("latitude", '')
    longitude = request.args.get("longitude", '')
    field = request.args.get("field", ' count(*) ')
    xField = request.args.get("xField", "'1'")

    # verify essential parameter details - smell test
    if len(table) == 0 or len(latitude) == 0 or len(longitude) == 0:
        info["message"].append("Table or latitude or longitude missing")
        info["message_class"] = "failure"
    else:
        # prepare sql query
        sql = "select %s, %s, %s, %s from %s where %s group by 1,2,3 order by 1 %s offset %s" % (
        xField, latitude, longitude, field, table, where, limit, start)

        header = "t,latitude,longitude,count"
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
    field = ','.join([re.compile(r' as ').split(f)[-1].strip() for f in field.split(',')])
    info["message"] = Markup(''.join('<p>%s</p>' % m for m in info["message"] if len(m) > 0))

    info[
        "title"] = "FIELD: <em>%s</em> against <br />LATITUDE: <em>%s</em> and <br />LONGITUDE:<em>%s</em> along <br />xFIELD: <em>%s</em> from <br />TABLE: <em>%s</em>" % (
    field, latitude, longitude, xField, table)
    info["title"] = Markup(info["title"])

    if xField != "'1'":
        info["div_slider_counter"] = Markup('<p>Slider is at <span id="slider-time"></span></p>')
        info["div_slider"] = Markup(
            '<div id="slider-container" style="padding: 10px;"> <input type="hidden" value="40" id="slider" /></div>')

    # format the message to encode HTML characters
    info['query'] = Markup(request.args.get('query', ''))
	

	