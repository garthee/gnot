from collections import defaultdict

from jinja2 import Markup

from db import export_sql


def _array2mat(fl, flo):
    f = open(fl, 'r')
    table = defaultdict(dict)
    words = set()
    for r in f:
        (year, word, item) = r.rstrip().split(',')
        table[year][word] = item
        words.add(word)

    f.close()
    fo = open(flo, 'w')
    fo.write('Years,%s\n' % (','.join(words)))
    years = sorted(table.keys())
    for year in years:
        row = [table[year].get(word, '0') for word in words]
        fo.write('%s,%s\n' % (year, ','.join(row)))
    fo.close()
    return years[0], years[-1]


def render(vis, request, info):
    info["message"] = []

    reload = request.args.get("reload", 0)
    table = request.args.get("table", '')
    where = request.args.get("where", '1=1')
    field = request.args.get("field", '')
    view = request.args.get("view", '')
    start = request.args.get("start", '0')  # start at 0
    xField = request.args.get("xField", '')
    limit = request.args.get("limit", '20')

    if len(table) == 0 or len(field) == 0:
        info["message"].append("table or field missing.")
        info["message_class"] = "failure"
    else:
        sql = "select t, word, n from ( select *,row_number() over (partition by t order by n desc) as rank from ( select word, t,n from ( select word, t, count(*) as n from (select regexp_split_to_table(regexp_replace(lower(coalesce(%s,'')),'[^a-z0-9@]+',' ','g'),' ') as word, %s as t from %s where %s) as a where char_length(word) > 0 group by 1,2 ) as a where n > 5 ) as a ) as a where rank >= %s and rank <= %s + %s" % (
        field, xField, table, where, start, start, limit)

        header = None
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

            datfilen = datfile + '_2mat.csv'
            info["datfile"] = datfilen

        datfilen = datfile + '_2mat.csv'

        info["datfile"] = datfilen

        (startYear, endYear) = _array2mat(datfile, datfilen)
        print(startYear, endYear)

    pfield = request.args.get("pfield", [])
    info["title"] = "FIELDS: <em>%s</em> from <br />TABLE: <em>%s</em>" % (','.join(pfield), table)
    info["title"] = Markup(info["title"])

    info["message"] = Markup(''.join('<p>%s</p>' % m for m in info["message"] if len(m) > 0))

    return vis.render_template('explore_series.html', **info)