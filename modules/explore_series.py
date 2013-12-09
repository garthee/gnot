import os
from db import export_sql
from jinja2 import Markup

def render(vis, request, info):
	info["message"] = []
	table = request.args.get("table", '')
	field = request.args.get("field", '')
	where = request.args.get("where", '1=1')
	reload = int(request.args.get("reload", 0))
	view = request.args.get("view", '')
	start = request.args.get("start", '0') # start at 0	
	limit = request.args.get("limit", '5000')
	
	pfield = request.args.get("pfield", [])
	
	xField = request.args.get("xField", '')
	annotate = request.args.get("annotate", '')
	
	groupby =  request.args.get("groupBy", '')
	if groupby and len(groupby) > 0: groupby = ' group by %s'%groupby

	if len(table) == 0 or len(xField) == 0 or len(field) == 0:
		info["message"].append("Table or field missing.")
		info["message_class"] = "failure"
	else:
		annotate = ',%s'%annotate if len(annotate) > 0 else ''
		sql = "select %s, %s %s from %s where %s %s order by 1 limit %s offset %s"%(xField, field, annotate, table, where, groupby, limit, start)
		annotate = ',annotate' if len(annotate) > 0 else ''
		header = "Date,%s%s"%(','.join(pfield), annotate)
		
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
	info["title"] = "%s from %s"%(','.join(pfield), table)

	