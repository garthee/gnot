import os,re
import json, csv
from jinja2 import Markup
from db import export_sql

# from functools import lru_cache
# @lru_cache(maxsize=4095)
def ld(s, t):
	if not s: return len(t)
	if not t: return len(s)
	if s[0] == t[0]: return ld(s[1:], t[1:])
	l1 = ld(s, t[1:])
	l2 = ld(s[1:], t)
	l3 = ld(s[1:], t[1:])
	return 1 + min(l1, l2, l3)

def nest_array(nlist, keys):
	k = keys.pop()
	print(k)
	jout = {}
	for row in nlist:
		rk = row[k]
		if not rk in jout:
			jout[rk] = []
		del row[k]
		jout[rk].append(row)
	joutN = []
	for rk in jout:
		if type(jout[rk]) == list:
			if len(keys)>0:
				joutN.append({"name": rk, "children":nest_array(jout[rk], keys[:])})
			else:
				joutN.append({"name": rk, "children":jout[rk]})

	return joutN


def render(vis, request, info):
	info["message"] = []
	
	reload = int(request.args.get("reload", 0))
	table = request.args.get("table", '')
	where = request.args.get("where", '1=1')
	field = request.args.get("field", '')
	view = request.args.get("view", '')
	start = request.args.get("start", '0') # start at 0
	limit = request.args.get("limit", '1000')
	
	sql = "select table_catalog, table_schema, table_name, column_name, data_type " \
	 	  + ", 1 as size from information_schema.columns " \
	 	  + "where not (table_schema like '\%pg_\%' or table_schema like '\%gp\%' or table_schema like '\%schema\%') ";


	(datfile, reload, result) = export_sql(sql, vis.config, reload, None, view,  addHeader = True)
	json_file = datfile.replace('csv', 'json')
	

	if len(result) > 0:
		info["message"].append(result)
		info["message_class"] = "failure"
	else:
		info["message_class"] = "success"

		if reload > 0:
			info["message"].append("Loaded fresh.")
		
			keys = ['table_schema', 'table_name', 'column_name']
			keys.reverse()
			jout = nest_array(csv.DictReader(open(datfile)), keys)

			with open(json_file, 'w') as jf:
				json.dump({"name":'DB',"children":jout}, jf)

		else:
			info["message"].append("Loading from cache. Use reload=1 to reload.")
		

			# data_by_columns = {}
			# for row in csv.DictReader(f):
			# 	distances = []
			# 	cf = row['column_name']
			# 	for (k,v) in data_by_columns.items():						
			# 		if row['data_type'] == v['data_type']:
			# 			distances.append((k, ld(cf,k)))

			# 	closest = sorted(distances, key = lambda v: v[1])
			# 	if len(closest) > 0 
			# 		and (closest[0][1] < 1.1*(len(cf)>len(closest[0][0]) ? len(cf)-len(closest[0][0]) : len(closest[0][0]) - len(cf)):
			# 		data_by_columns[k].append(row)
			# 		if len(cf) < len(c):
			# 			data_by_columns[cf] = data_by_columns.pop(k)
			# 	else:
			# 		data_by_columns[cf] = row


	info["datfile"] = json_file
		
		
	
	
	info["title"] = "DB CONTENT"
	info["title"] = Markup(info["title"])		
	
	info["message"] = Markup(''.join('<p>%s</p>'%m for m in info["message"] if len(m) > 0))
			
