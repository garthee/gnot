import os, json, csv
from collections import defaultdict
from db import export_sql

def render(vis, request):
	info = {}

	schema = vis.config.get('db_schema', '')
	if schema:
		sql = "SELECT table_schema || '.' || table_name,column_name FROM information_schema.columns WHERE table_schema='%s'"%(schema)
	else:
		if vis.config['db_system'] == 'mysql':
			sql = "SELECT table_name,column_name FROM information_schema.columns where table_schema='%s'"%vis.config['db_database']
		else:
			sql = "SELECT table_name,column_name FROM information_schema.columns where table_schema='Public'"

	reload = int(request.args.get("reload", 0))
	(datfile, reload, result) = export_sql(sql, vis.config, reload, None, None)
	
	
	json_file = datfile.replace('csv', 'json')	
	table_list = defaultdict(list)
	if reload > 0 or (not os.path.exists(os.path.realpath(json_file))):
		#csv to json conversion
		try:
			reader = csv.DictReader(open(datfile, 'r'), fieldnames = ( "table","field" ) )
			for row in reader:
				table_list[row['table']].append(row['field'])
			table_list['table'] = table_list.keys()
			
			table_list['module'] = ['explore_calendar', 'explore_corr', 'explore_diff', 'explore_field', 'explore_graph', \
								'explore_scatter', 'explore_word', 'explore_flat_series', 'explore_long_series', 'explore_series']

			table_list['explore_calendar'] = {'xField':1}
			table_list['explore_corr'] = {'xField':1}
			table_list['explore_diff'] = {'xField':1}
			table_list['explore_field'] = {'xField':0}
			table_list['explore_graph'] = {'xField':0}
			table_list['explore_scatter'] = {'xField':0}
			table_list['explore_word'] = {'xField':0}
			table_list['explore_flat_series'] = {'xField':1}
			table_list['explore_long_series'] = {'xField':1}
			table_list['explore_series'] = {'xField':1}

			with open(json_file, 'w') as jf:
				json.dump(table_list, jf)
			
			
			
		except:
			info["message"].append("Couldn't find CSV file")
			info["message_class"] = "failure"
		
	
	
	info["message_class"] = "success"
	info["datfile"] = json_file
		
	return vis.render_template('explore.html', **info)

	