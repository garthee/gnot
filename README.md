GNoT+
====
Visualize relational data, on the fly!
GNoT combines powerful JS visualizations to data in a PostgreSQL (also Redshift, Vertica, Greenplum, etc.), or MySQL database.

Demo
===
1. [Visualizing Jeopardy data with GNoT](https://www.evernote.com/shard/s4/sh/762f3b3d-e088-48b1-b3f0-372cf31d1831/825167a720abf0dd)
2. [More examples](http://ddmg1.csail.mit.edu:5000/render?submit=submit&query=module%3A+explore_examples)

Required
===
1. Python (2.7+, 3.x supported)
2. werkzeug and jinja2 (available in PIP)
3. ML SVM module also requires sklearn (available in PIP). Sklearn requires numpy and scipy.


Setup
====
1. Install werkzeug python library (werkzeug.pocoo.org), and other required libraries. Alternatively use <a href="https://store.continuum.io/cshop/anaconda/">Anaconda</a>.
2. Move .gnot_config to user home directory and edit the parameters.
3. Start the webserver (python webserver.py) from gnot directory.

If you have trouble accessing, see https://github.com/garthee/gnot/issues/2

Module Development
====
1. A module consists of two files: modules/mymodule.py, templates/mymodule.html
2. Requires an entry in modules/modules.json (with the details of the fields required and supported by mymodule)
3. Look at explore_calendar module for ideas.
4. Make sure mymodule.html extends layout.html (as in explore_calendar.html) to follow uniform templates and load standard .js libraries automatically.

Acknowledgement
====
GNoT builds on (and thus heavily benefits from) JS visualization libraries such as D3, NVD3, Crossfilter, DC, Rickshaw, VisualSearch, etc.
