#!/usr/bin/python3

import os, os.path
import time
import cherrypy
from mako.template import Template
from mako.lookup import TemplateLookup

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
TMPL = os.path.join(ROOT, "share/ehome/templates")

# awful fix
from cherrypy.lib.reprconf import _Builder3
def build_Constant(self, o):
	return o.value
_Builder3.build_Constant = build_Constant 

TOP_CONF = {
		'/': {
			'tools.sessions.on': True,
			'tools.staticdir.root': os.path.abspath(ROOT)
        },
		'/static': {
			'tools.staticdir.on': True,
			'tools.staticdir.dir': 'share/ehome/static'
		}
    }


class Page:
	"""Page composing the provided services."""

	def __init__(self, name, label):
		self.name = name
		self.label = label
		self.parent = None
		self.conf = None

	def configure(self, map):
		pass

	def get_template(self, id):
		return self.parent.get_template(id)

	def gen(self):
		return None

	def check(self):
		return self.parent.check()

	def get_conf(self, id, dflt = None):
		try:
			return self.conf[id]
		except KeyError:
			return dflt


class Dashboard(Page):
	"""Main dashboard."""

	def __init__(self):
		Page.__init__(self, "dashboard", "Dashboard")

	def gen(self):
		return "dashboard"


class LDAP(Page):
	"""User management using LDAP."""

	def __init__(self):
		Page.__init__(self, "ldap", "Users")

	def gen(self):
		return "LDAP"


def check_expire(f):
	def check(self):
		res = self.check()
		if res == None:
			return f(self)
		else:
			return res
	return check


class EHome:
	"""EHome server entry point."""

	def __init__(self, pages):

		# basic init
		self.tmpl_lookup = TemplateLookup(directories = [TMPL])
		self.timeout = 60 * 60
		self.pages = pages
		for page in pages:
			page.parent = self

		# setup tree with configuration
		cherrypy.config.update(TOP_CONF)
		app = cherrypy.tree.mount(self, '/', TOP_CONF)
		for page in self.pages:
			cherrypy.tree.mount(page, "/" + page.name, TOP_CONF)

		# configuration
		file_conf = os.path.join(ROOT, "etc/ehome/config.ini")
		if os.path.exists(file_conf):
			cherrypy.config.update(file_conf)
			app.merge(file_conf)
			self.configure(app.config)
			for page in self.pages:
				try:
					page.conf = app.config[page.name]
				except KeyError:
					page.conf = {}
				page.configure(app.config)

	def configure(self, conf):
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

	def run(self):
		cherrypy.engine.start()
		cherrypy.engine.block()


	@cherrypy.expose
	def index(self, msg = ""):

		# disable for debugging
		#return self.tmpl_lookup.get_template("index.html") \
		#	.render(msg = msg)

		# enable for deugging
		cherrypy.session['expiration'] = time.time()
		return self.main()

	@cherrypy.expose
	def login(self, user, pwd):
		cherrypy.log("DEBUG: expected %s:%s" % (self.user, self.pwd))
		cherrypy.log("DEBUG: login %s:%s" % (user, pwd));
		if user == self.user and pwd == self.pwd:
			cherrypy.session['expiration'] = time.time()
			return "<div class='success'>Success!</div>"
		else:
			return "<div class='failure'>Authentification error!</div>"

	@cherrypy.expose
	@check_expire
	def main(self):
		return self.tmpl_lookup.get_template("main.html").render(ehome = self)

	@cherrypy.expose
	def logout(self):
		if 'expiration' in cherrypy.session:
			del cherrypy.session['expiration']
		return self.index()

	def check(self):
		try:
			ct = time.time()
			et = cherrypy.session['expiration'] + self.timeout
			if ct > et:
				return self.index("Session expired!")
			else:
				return None
		except KeyError:
			return self.index("Please, log first.")


# startup
if __name__ == '__main__':
	EHome([
		Dashboard(),
		LDAP()
	]).run()

