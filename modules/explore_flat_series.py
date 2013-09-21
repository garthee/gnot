from collections import defaultdict
from jinja2 import Markup
from db import export_sql

def _array2mat(fl, flo):

	f = open(fl, 'r')
	table = defaultdict(dict)
	words = set()
	for r in f:
		
		(word, year, item) = r.rstrip().split(',')

		year = int(year)
		table[year][word] = item
		words.add(word)
		
	f.close()
	fo = open(flo, 'w')
	fo.write('Years,%s\n'%(','.join(words)))
	for year in sorted(table.keys()):
		row = [table[year].get(word, '0') for word in words]
		fo.write('%s,%s\n'%(year, ','.join(row)))
	fo.close()
	years = table.keys()
	return min(years), max(years)

def render(vis, request, info):
	info["message"] = []
	table = request.args.get("table", '')
	field = request.args.get("field", '')
	where = request.args.get("where", '1=1')
	reload = int(request.args.get("reload", 0))
	view = request.args.get("view", '')
	

	xField = request.args.get("xField", '')
	sub_field = request.args.get("sub_field", '')
	

	if len(table) == 0 or len(xField) == 0 or len(field) == 0 or len(sub_field) == 0:
		info["message"].append("Table  or field missing.")
		info["message_class"] = "failure"
	else:
	
		sql = "select %s, %s, %s  from %s where %s group by 1,2 order by 1"%(field, xField, sub_field, table, where)
		
		
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
			

	
	info["message"] = Markup(''.join('<p>%s</p>'%m for m in info["message"] if len(m) > 0))
	datfilen = datfile +'_2mat.csv'
	info["datfile"] = datfilen
	
	(startYear, endYear) = _array2mat(datfile, datfilen)
	info["title"] = "%s from %d to %d"%(field, startYear, endYear)

	