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
	fo.write('Years,%s\n'%(','.join(words)))
	years = sorted(table.keys())
	for year in years:
		row = [table[year].get(word, '0') for word in words]
		fo.write('%s,%s\n'%(year, ','.join(row)))
	fo.close()
	return years[0], years[-1]

def render(vis, request, info):
	info["message"] = []
	table = request.args.get("table", '')
	field = request.args.get("field", '')
	where = request.args.get("where", '1=1')
	reload = int(request.args.get("reload", 0))
	view = request.args.get("view", '')
	limit = request.args.get("limit", '1000')	
	start = request.args.get("start", '0') # start at 0
	xField = request.args.get("xField", '')
	splitfield = re.findall(r'[^,]*\([^\)]*\)[^,]*|[^,]+', field)
	if len(table) == 0 or len(xField) == 0:
		info["message"].append("Table or xfield missing.")
		info["message_class"] = "failure"
	elif len(splitfield) != 2:
		info["message"].append("Need two fields : a field to group by, and another aggregate field.")
		info["message_class"] = "failure"
	else:
	
		#sql = "select %s, %s from %s where %s group by 1,2 order by 1 limit %s offset %s"%(xField, field, table, where, limit, start)
		
		field = [re.compile(r'as').split(f)[0].strip() for f in field.split(',')]
		
		sql = "select t, %s, n from ( \
		select *,row_number() over (partition by 1,2 order by 3 desc) as rank from  \
			(select %s as t, %s, %s as n from %s where %s group by 1,2) \
		as a) \
		as a where rank >= %s and rank <=%s + %s"%(field[0], xField, field[0], field[1], table, where, start, start, limit)
		
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
		info["title"] = "%s from %s to %s"%(','.join(field), startYear, endYear)

	
	info["message"] = Markup(''.join('<p>%s</p>'%m for m in info["message"] if len(m) > 0))
	

	return vis.render_template('explore_series.html', **info)