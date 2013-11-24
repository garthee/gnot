import os,re
import json, csv
from jinja2 import Markup
from db import export_sql
def render(vis, request, info):
	info["message"] = []
	
	reload = request.args.get("reload", 0)
	table = request.args.get("table", '')
	where = request.args.get("where", '1=1')
	view = request.args.get("view", '')
	start = request.args.get("start", '0') # start at 0
	limit = request.args.get("limit", '10000')
	
	#module dependent user inputs
	field = request.args.get("field", '')
	pfield = request.args.get("pfield", [])
	
	groupBy =  request.args.get("groupBy", '')
	if groupBy and len(groupBy) > 0:
		groupBy = ' group by %s '%groupBy

	orderBy = request.args.get("orderBy", '')	
	if orderBy and len(orderBy)>0:
		orderBy = ' order by %s '%orderBy
	
	if len(table) == 0 or not field:
		info["message"].append("table or field missing.")
		info["message_class"] = "failure"
	else:
		sql = "select row_number() over (order by 1) as rnum, * from (select %s from %s where %s %s %s limit %s offset %s) as a"%(field, table, where, groupBy, orderBy, limit, start)

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
			
			info["datfile"] = datfile
	
	divs = ['<div class="chart"><div class="title">%s<a href="javascript:reset(%d)" class="reset" style="display: none;">reset</a></div></div>'%(pfield[d], d) for d in range(len(pfield))]
	info['divs'] = Markup(''.join(divs))
	
	info["fieldY"] = pfield[0] if len(pfield) > 0 else "Y"
	info["message"] = Markup(''.join('<p>%s</p>'%m for m in info["message"] if len(m) > 0))

	info["title"] = "FIELDS: <em>%s</em> from <br />TABLE: <em>%s</em>"%(', '.join(pfield), table)
	info["title"] = Markup(info["title"])		
	