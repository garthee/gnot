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
	
	if len(table) == 0 or len(field) == 0:
		info["message"].append("table or field missing.")
		info["message_class"] = "failure"
	else:
		field = re.findall(r'[^,]*\([^\)]*\)[^,]*|[^,]+', field)
		(fieldA, fieldB) = field[:2]
		sql = "select %s, %s, count(*) from (select * from %s where %s)"%(fieldA,fieldB, table, where) + \
		 " as a where %s is not null and %s is not null group by 1,2 order by 3 desc limit %s offset %s"%(fieldA, fieldB, limit, start)
		
		info["title"] = "Interactions between %s on %s in %s"%(fieldA, fieldB, table)
		
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
		
	info["message"] = Markup(''.join('<p>%s</p>'%m for m in info["message"] if len(m) > 0))