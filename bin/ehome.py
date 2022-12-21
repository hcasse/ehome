#!/usr/bin/python3

import os, os.path
import time
import cherrypy

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
TMPL = os.path.join(ROOT, "share/ehome/templates")

# awful fix
from cherrypy.lib.reprconf import _Builder3
def build_Constant(self, o):
	return o.value
_Builder3.build_Constant = build_Constant 


class EHome:
	"""EHome server entry point."""

	def config(self, conf):
		try:
			self.conf = conf["ehome"]
		except KeyError:
			self.conf = {}
		self.user = self.get_conf("user", "ehome")
		self.pwd = self.get_conf("password", "ehome")

	def get_conf(self, id, dflt = None):
		try:
			return self.conf[id]
		except KeyError:
			return dflt

	@cherrypy.expose
	def index(self):
		return open(os.path.join(TMPL, 'index.html'))

	@cherrypy.expose
	def login(self, user, pwd):
		cherrypy.log("expected %s:%s" % (self.user, self.pwd))
		cherrypy.log("login %s:%s" % (user, pwd));
		if user == self.user and pwd == self.pwd:
			return "<div class='success'>Success!</div>"
			cherrypy.session['expiration'] = time.time()
		else:
			return "<div class='failure'>Authentification error!</div>"

	@cherrypy.expose
	def main(self):
		return open(os.path.join(TMPL, 'main.html'))


# startup
if __name__ == '__main__':

	conf = {

		# top level configuration
		'/': {
			'tools.sessions.on': True,
			'tools.staticdir.root': os.path.abspath(ROOT)
        },
		'/static': {
			'tools.staticdir.on': True,
			'tools.staticdir.dir': 'share/ehome/static'
		}

    }
    
	cherrypy.config.update(conf)
	gconf = os.path.join(ROOT, "etc/ehome/config.ini")
	ehome = EHome()
	app = cherrypy.tree.mount(ehome, '/', conf)
	if os.path.exists(gconf):
		cherrypy.config.update(gconf)
		app.merge(gconf)
	ehome.config(app.config)
	cherrypy.engine.start()
	cherrypy.engine.block()
