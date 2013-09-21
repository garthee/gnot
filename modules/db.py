#!/usr/bin/python

import os
def export_sql(sql, config, reload = 0, header = None, view = None, addHeader = False):
	
	user = config.get('db_user', '')
	if len(user) > 0: user = '--username %s'%user
	
	passwd = config.get('db_pass', '')
	if len(passwd) > 0: passwd = '-p %s'%passwd
	
	host = config.get('db_host', '')
	if len(host) > 0: host = '-h %s'%host
	
	database = config['db_database']
	
	port = config.get('db_port', '')
	if len(port): port = '-p %s'%port
	
	schema = config.get('db_schema', '')
	if len(schema) > 0 : schema += '.'
	
	datfile = 'cache/%s.csv'%hex(hash(sql) & 0xffffffff)
	result = ''
	if reload > 0 or (not os.path.exists(os.path.realpath(datfile))):
		if view and len(view) > 0: 
			view_name = schema+'custom_view'
			view = "DROP VIEW IF EXISTS %s; CREATE VIEW %s as %s;"%(view_name,view_name,view)
			if config['db_system'] == 'mysql':
				view = 'mysql %s %s %s --database %s -e "%s" '%(database, user, passwd, host, view)
			elif config['db_system'] == 'psql':
				view = 'psql %s %s %s -d %s -c "%s"'%(port, host, user, database, view)
			
			print view
			ret = os.popen(view).close()
			if ret: result += ' Error creating view!'
			
		if header:
			os.popen("echo '%s' > %s"%(header, datfile))
		else:
			os.popen("touch %s"%(datfile))
		
		if addHeader:
			if config['db_system'] == 'mysql':
				sql = 'mysql %s %s %s --database %s -e "%s" | sed "s/\t/,/g" | grep -v "NULL" >> %s'%(database, user, passwd, host, sql, datfile)
			elif config['db_system'] == 'psql':
				sql = 'psql %s %s %s -d %s -c "copy (%s) to stdout with CSV HEADER" >> %s'%(port, host, user, database, sql, datfile)
			
		else:
			if config['db_system'] == 'mysql':
				sql = 'mysql %s %s %s --database %s -e "%s" | sed "s/\t/,/g" | grep -v "NULL" | tail -n +2 >> %s'%(database, user, passwd, host, sql, datfile)
			elif config['db_system'] == 'psql':
				sql = 'psql %s %s %s -d %s -c "copy (%s) to stdout with CSV" >> %s'%(port, host, user, database, sql, datfile)
			
		print sql
		ret = os.popen(sql).close()
		if ret: result += ' Error querying relation!'
		
	return (datfile, reload, result)
