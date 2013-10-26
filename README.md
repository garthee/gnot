GNoT
====

Rapid DB Visualization by Garthee


Setup
====
1. Install werkzeug python library (werkzeug.pocoo.org)
2. Move .gnot_config to user home directory and edit the parameters
3. Start the webserver (python webserver.py)

Module Development
====
1. A module consists of two files: modules/mymodule.py, templates/mymodule.html
2. Requires an entry in modules/modules.json (with the details of the fields required and supported by mymodule)
3. Look at explore_calendar module for ideas. It is well commented.
4. Make sure mymodule.html extends layout.html (as in explore_calendar.html) to follow uniform templates and load standard .js libraries automatically.
