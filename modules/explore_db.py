import  json, csv, os
from collections import defaultdict
from db import export_sql
from werkzeug.wrappers import Request, Response

def render(vis, request, info):
	

	schema = vis.config.get('db_schema', '')
	if schema:
		sql = "SELECT table_schema || '.' || table_name,column_name FROM information_schema.columns WHERE table_schema='%s'"%(schema)
	else:
		if vis.config['db_system'] == 'mysql':
			sql = "SELECT table_name,column_name FROM information_schema.columns where table_schema='%s'"%vis.config['db_database']
		else:
			sql = "SELECT table_name,column_name FROM information_schema.columns"

	reload = int(request.args.get("reload", 0))
	(datfile, reload, result) = export_sql(sql, vis.config, reload, None, None)
	
	json_file = datfile.replace('csv', 'json')	
	table_list = defaultdict(list)
	
	reader = csv.DictReader(open(datfile, 'r'), fieldnames = ( "table","field" ) )
	for row in reader:
		table_list[row['table']].append(row['field'])

	module_list = json.loads(open(os.path.realpath('modules/modules.json'), 'r').read())
	data = {'modules': module_list, 'tables' : table_list}		
	return Response(json.dumps(data))
			

	