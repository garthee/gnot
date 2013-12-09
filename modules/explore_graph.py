#!/usr/bin/python

from db import export_sql
from jinja2 import Markup
import re
def render(vis, request, info):
	info["message"] = []
	
	reload = request.args.get("reload", 0)
	table = request.args.get("table", '')
	where = request.args.get("where", '1=1')
	field = request.args.get("field", ' count(*) ')
	view = request.args.get("view", '')
	start = request.args.get("start", '0') # start at 0
	limit = request.args.get("limit", '1000')#1000 links max
	
	pfield = request.args.get("pfield", [])
	sfield = request.args.get("sfield", [])
	
	source = request.args.get("source", '')
	target = request.args.get("target", '')
	orderBy = request.args.get("orderBy", '')
	if orderBy and len(orderBy)>0: orderBy = ' order by %s '%orderBy
			
	if len(table) == 0 or not source or not target or not field:
		info["message"].append("table, source, target, or field missing.")
		info["message_class"] = "failure"
	else:
		
		if not sfield or len(sfield) == 0: 
			sfield = ' count(*) '
		else:
			sfield = sfield[0]
		
		sql = "select %s, %s, %s from (select * from %s where %s)"%(source, target, sfield, table, where,) + \
		 " as a where %s is not null and %s is not null group by 1,2  %s limit %s offset %s"%(source, target, orderBy, limit, start)
		
		info["title"] = "Interactions between %s and %s as %s in %s"%(source, target, field, table)
		
		header = "source,target,value"
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
		
	pfield = request.args.get("pfield", [])
	info["title"] = "SOURCE: <em>%s</em>, <br />TARGET: <em>%s</em>, on <br />LINK: <em>%s</em> from <br />TABLE: <em>%s</em>"%(source,target,pfield[0], table)
	info["title"] = Markup(info["title"])		
	
	info["message"] = Markup(''.join('<p>%s</p>'%m for m in info["message"] if len(m) > 0))
