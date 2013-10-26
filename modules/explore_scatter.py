from db import export_sql
from jinja2 import Markup
import re
def render(vis, request, info):
	info["message"] = []
	table = request.args.get("table", '')
	field = request.args.get("field", '')
	where = request.args.get("where", '1=1')
	reload = int(request.args.get("reload", 0))
	view = request.args.get("view", '')
	limit = request.args.get("limit", '1000')#max 5000 data points
	start = request.args.get("start", '0') # start at 0
	info["title"] = "%s from %s"%(field, table)

	
	field = re.findall(r'[^,]*\([^\)]*\)[^,]*|[^,]+', field)
	rfield = [re.compile(r' as ').split(f)[-1].strip() for f in field]
	if len(table) == 0 or len(field) == 0:
		info["message"].append("Table  or field missing.")
		info["message_class"] = "failure"
	elif len(field) < 2 :
		info["message"].append("Not enough fields.")
		info["message_class"] = "failure"
	else:
		if  len(field) > 4: 
			info["message"].append("Too many fields. Only last 4 are used.")
			field = field[-4:]

		info["xlabel"] = rfield[0]
		info["ylabel"] = rfield[1]
		
		# if z,c are not provided
		field.extend(['1']*(4-len(field)))
		info["field3"] = field[3-1]
		info["field4"] = field[4-1]
		field = ','.join(field)
	
		sql = "select %s from %s where %s order by 1 limit %s offset %s"%(field, table, where, limit, start)
		header = "x,y,z,c"
		
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

	