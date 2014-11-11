import re
from db import export_sql
from jinja2 import Markup

def render(vis, request, info):
	info["message"] = [] 
	
	# module independent user inputs
	table = request.args.get("table", '')
	where = request.args.get("where", '1=1')
	limit = request.args.get("limit", '1000') # 10 years max
	if limit:limit = ' limit %s'%limit 
	start = request.args.get("start", '0') # start at 0
	reload = int(request.args.get("reload", 0))
	view = request.args.get("view", '')
	
	#module dependent user inputs
	latitude = request.args.get("latitude", '')
	longitude = request.args.get("longitude", '')
	field = request.args.get("field", '')
	mapField = request.args.get("mapField", " '1' ")
	
	pfield = request.args.get("pfield", [])
	
	groupBy =  request.args.get("groupBy", '')
	if groupBy and len(groupBy) > 0: groupBy = ' group by %s '%groupBy

	orderBy = request.args.get("orderBy", '')	
	if orderBy and len(orderBy)>0: orderBy = ' order by %s '%orderBy
		
	# verify essential parameter details - smell test
	if len(table) == 0 or len(latitude) == 0 or len(longitude) == 0:
		info["message"].append("Table or latitude or longitude missing")
		info["message_class"] = "failure"
	else:
		# prepare sql query
		sql = "select row_number() over (order by 1,2) as rnum, * from (select %s,%s,%s,%s from %s where %s %s %s %s offset %s) as a"%(latitude,longitude,mapField,field, table, where, groupBy, orderBy, limit, start)

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
			
			# if success return data file
			info["datfile"] = datfile

	# prepare some messages
	
	info["message"] = Markup(''.join('<p>%s</p>'%m for m in info["message"] if len(m) > 0))
	
	info["title"] = "LATITUDE: <em>%s</em> and <br />LONGITUDE:<em>%s</em> and <br />FIELDS: <em>%s</em> from <br />TABLE: <em>%s</em>"%(latitude, longitude, ','.join(pfield), table)
	info["title"] = Markup(info["title"])
	
	divs = ['<div class="chart"><div class="title">%s<a href="javascript:reset(%d)" class="reset" style="display: none;">reset</a></div></div>'%(pfield[d], d) for d in range(len(pfield))]
	info['divs'] = Markup(''.join(divs))
	info["fieldY"] = pfield[0] if len(pfield) > 0 else "Y"	
	
	# format the message to encode HTML characters
	info['query']= Markup(request.args.get('query', ''))
	

	