from collections import defaultdict
from jinja2 import Markup
from db import export_sql
import re
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
	years = sorted(table.keys(), key=lambda y: int(y))
	fo.write('Words,%s\n'%(','.join(years)))
	for word in words:
		row = [table[year].get(word, '0') for year in years]
		fo.write('%s,%s\n'%(word, ','.join(row)))
	fo.close()
	
	return years[0], years[-1]

def render(vis, request, info):
	info["message"] = []
	table = request.args.get("table", '')
	field = request.args.get("field", '')
	where = request.args.get("where", '1=1')
	reload = int(request.args.get("reload", 0))
	view = request.args.get("view", '')
	start = request.args.get("start", '0') # start at 0	
	limit = request.args.get("limit", '10000000')
	xField = request.args.get("xField", '')
	sub_field = request.args.get("sub_field", '')
	
	splitfield = re.findall(r'[^,]*\([^\)]*\)[^,]*|[^,]+', field)
	if len(table) == 0 or len(xField) == 0:
		info["message"].append("Table or xfield missing.")
		info["message_class"] = "failure"
	elif len(splitfield) != 2:
		info["message"].append("Need two fields : a field to group by, and another aggregate field.")
		info["message_class"] = "failure"
	else:
	
		sql = "select %s, %s from %s where %s group by 1,2 order by 1 limit %s offset %s"%(xField, field, table, where, limit, start)
		
		
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
			

		datfilen = datfile +'_2mat.csv'
		info["datfile"] = datfilen
		
		(startYear, endYear) = _array2mat(datfile, datfilen)
		info["title"] = "%s from %s to %s"%(field, startYear, endYear)
	info["message"] = Markup(''.join('<p>%s</p>'%m for m in info["message"] if len(m) > 0))

	return vis.render_template('explore_mashed_series.html', **info)