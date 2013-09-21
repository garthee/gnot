import os
from collections import defaultdict
import math

from db import export_sql

def _array2mat(fl, flo, islog = False):

	min_val = float('inf')
	max_val = 0
	
	f = open(fl, 'r')
	table = defaultdict(dict)
	years = set()
	wordcount = defaultdict(int)
	for r in f:
		
		(word, year, item) = r.rstrip().split(',')
		
		year = int(year)
		item = float(item)
		if islog:
			item = math.log(item)
			#print item
		table[word][year] = item
		max_val = max(item, max_val)
		min_val = min(item, min_val)
		
		years.add(year)
		wordcount[word] += item
	f.close()
	
	
	years = range(min(years),max(years)+1)
	
	
	fo = open(flo, 'w')
	fo.write('Words,%s\n'%(','.join([str(y) for y in years])))
	for word in sorted(wordcount, key=wordcount.get, reverse=True):
		ylist = table[word]
		fo.write('%s,%s\n'%(word, ','.join([str(ylist.get(y, '')) for y in years])))
	fo.close()
	print (min_val, max_val)
	return (min_val, max_val, min(years), max(years))

def render(vis, request):
	info = {}
	table = request.args.get("table", '')
	date_field = request.args.get("date_field", '')
	field = request.args.get("field", '')
	
	where = request.args.get("where", '1=1')
	reload = int(request.args.get("reload", 0))
	
	if len(table) == 0 or len(date_field) == 0 or len(field) == 0:
		info["message"] = "table or date_field or field missing"
		info["message_class"] = "failure"
	else:
	
		sql = "select %s, %s, count(*) as n from %s where %s group by 1,2 order by 1"%(field, date_field, table, where)
		datfile = 'cache/%s.csv'%hash(sql)
		datfilen = datfile +'temp.csv'	
		if reload > 0 or (not os.path.exists(os.path.realpath(datfile))):
			export_sql(sql, datfile, vis.config)
			info["message"] = "Loaded fresh."
		else:
			info["message"] = "Loading from cache. Use reload=1 to reload."
		
		
		info["message_class"] = "success"
		info["datfile"] = datfilen
	
	(min_c, max_c, startYear, endYear) = _array2mat(datfile, datfilen, 0)
	info["title"] = "%s from %d to %d"%(field, startYear, endYear)
	return vis.render_template('explore_fieldyear.html', **info)

	