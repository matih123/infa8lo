#!/usr/bin/python3.7

production = False

if production:
	activate_this = '/srv/www/infa8lo/infa8lo/venv/bin/activate_this.py'
	with open(activate_this) as file_:
	    exec(file_.read(), dict(__file__=activate_this))

	import sys
	import logging
	logging.basicConfig(stream=sys.stderr)
	sys.path.insert(0,"/srv/www/infa8lo/")

	from infa8lo import app as application

else:
	from infa8lo import app
