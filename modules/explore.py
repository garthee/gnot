import re
from db import export_sql
from jinja2 import Markup

def render(vis, request, info):
	info["message"] = [] 
	
	# module independent user inputs
	table = request.args.get("table", '')
	where = request.args.get("where", '1=1')
	limit = request.args.get("limit", '1000') # 10 years max
	start = request.args.get("start", '0') # start at 0
	reload = int(request.args.get("reload", 0))
	view = request.args.get("view", '')
	field = request.args.get("field", "")

	orderBy = request.args.get("orderBy", '')
	groupBy = request.args.get("groupBy", '')
	if orderBy and len(orderBy)>0: orderBy = ' order by %s'%orderBy
	if groupBy and len(groupBy)>0: groupBy = ' group by %s'%groupBy
	
	# verify essential parameter details - smell test
	if len(table) == 0 or  len(field) == 0:
		info["message"].append("Table or Field missing")
		info["message_class"] = "failure"
	else:
		# prepare sql query
		sql = "select %s from %s where %s %s %s limit %s offset %s"%(field, table, where, groupBy, orderBy, limit, start)

		header =  None
		(datfile, reload, result) = export_sql(sql, vis.config, reload, header, view, True)
		
		if len(result) > 0:
			info["message"].append(result)
			info["message_class"] = "failure"
		else:
			info["message_class"] = "success"
			if reload > 0:
				info["message"].append("Loaded fresh.")
			else:
				info["message"].append("Loading from cache. Use reload=1 to reload.")
			
			# if success return data file
			info["datfile"] = datfile

	# prepare some messages
	info["message"] = Markup(''.join('<p>%s</p>'%m for m in info["message"] if len(m) > 0))
	
	pfield = request.args.get("pfield", [])
	info["title"] = "FIELDS: <em>%s</em> from <br />TABLE: <em>%s</em>"%(', '.join(pfield), table)
	info["title"] = Markup(info["title"])		
	
	# format the message to encode HTML characters
	info['query']= Markup(request.args.get('query', ''))
	

	