#!/usr/bin/python

from db import export_sql
from jinja2 import Markup
import re
def render(vis, request, info):
	info["message"] = []
	
	reload = request.args.get("reload", 0)
	table = request.args.get("table", '')
	where = request.args.get("where", '1=1')
	field = request.args.get("field", '')
	view = request.args.get("view", '')
	start = request.args.get("start", '0') # start at 0
	limit = request.args.get("limit", '1000')#1000 links max
	
	source = request.args.get("source", '')
	target = request.args.get("target", '')
	orderBy = request.args.get("orderBy", '')
	if orderBy and len(orderBy)>0: orderBy = ' order by %s '%orderBy
			
	if len(table) == 0 or not source or not target or not field:
		info["message"].append("table, source, target, or field missing.")
		info["message_class"] = "failure"
	else:
		field = re.findall(r'[^,]*\([^\)]*\)[^,]*|[^,]+', field)
		if not field or len(field) == 0: 
			field = 'count(*)'
		else:
			field = field[0]
		sql = "select %s, %s, %s, '1' from (select * from %s where %s %s limit %s offset %s)"%(source, target, field, table, where, orderBy, limit, start) + \
		 " as a where %s is not null and %s is not null group by 1,2 "%(source, target)
		
		info["title"] = "Interactions between %s and %s as %s in %s"%(field[0], field[1], field[2], table)
		
		header = "source,target,value,group"
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
		
	info["message"] = Markup(''.join('<p>%s</p>'%m for m in info["message"] if len(m) > 0))