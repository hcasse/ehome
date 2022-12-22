#!/usr/bin/python3

import cherrypy
from mako.template import Template
from mako.lookup import TemplateLookup
import os, os.path
import re
import time

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
TMPL = os.path.join(ROOT, "share/ehome/templates")

# regular expressions
CPUINFO_RE = re.compile("^processor\s*:\s*([0-9]+)")
STAT_RE = re.compile("^cpu([0-9]+)\s+(.*)")

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


class Core:

	def __init__(self, num):
		self.num = num
		self.load = 0
		self.stats = [0] * 8
		self.old_stats = None

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
		"""Get Mako templote for the given identifier."""
		return self.parent.get_template(id)

	def gen(self):
		"""Generate the display for this page."""
		return None

	def get_conf(self, id, dflt = None):
		try:
			return self.conf[id]
		except KeyError:
			return dflt

	def expired(self):
		return self.parent.expired()

	def expire(self):
		return self.parent.expire()

	def get_update_time(self):
		"""Get the update time in ms."""
		return 0


class Dashboard(Page):
	"""Main dashboard."""

	def __init__(self):
		Page.__init__(self, "dashboard", "Dashboard")
		self.cores = []
		for l in open("/proc/cpuinfo"):
			r = CPUINFO_RE.match(l)
			if r != None:
				self.cores.append(Core(int(r.group(1))))
		self.get_stats()

	def get_stats(self):
		for l in open("/proc/stat"):
			r = STAT_RE.match(l)
			if r != None:
				core = self.cores[int(r.group(1))]
				core.old_stats = core.stats
				core.stats = [int(x) for x in r.group(2).split()]
				total = sum(core.stats) - sum(core.old_stats)
				idle = core.stats[3] - core.old_stats[3]
				core.load = 100. * (total - idle) / total

	def gen(self):
		self.get_stats()
		return self.get_template("dashboard.html").render(cores = self.cores)

	def get_update_time(self):
		return 1000


class LDAP(Page):
	"""User management using LDAP."""

	def __init__(self):
		Page.__init__(self, "ldap", "Users")

	def gen(self):
		return "LDAP"


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

	def expired(self):
		try:
			ct = time.time()
			et = cherrypy.session['expiration'] + self.timeout
			if ct > et:
				self.msg = "Session expired!"
				return True
			else:
				return False
		except KeyError:
			self.msg = "Please, log first."
			return True

	def expire(self):
		return self.index(self.msg)

	def get_template(self, id):
		return self.tmpl_lookup.get_template(id)

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
	def logout(self):
		if 'expiration' in cherrypy.session:
			del cherrypy.session['expiration']
		return self.index()

	@cherrypy.expose
	def main(self):
		if self.expired():
			return self.expire()
		return self.tmpl_lookup.get_template("main.html").render(ehome = self)

	@cherrypy.expose
	def content(self, tab):
		if self.expired():
			return self.expire()
		for page in self.pages:
			if page.name == tab:
				return page.gen()
		cherrypy.log("Bad accessed page: %s" % tab)
		return "Error."


# startup
if __name__ == '__main__':
	EHome([
		Dashboard(),
		LDAP()
	]).run()

