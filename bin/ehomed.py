#!/usr/bin/python3

# system imports
import cherrypy
from cherrypy._cpserver import Server
from mako.template import Template
from mako.lookup import TemplateLookup
import os, os.path
import sys
import time
import urllib.parse as url

# get basic configuration
VERSION = "0.1"
HOME = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
TMPL = os.path.join(HOME, "share/ehome/templates")

try:
	ROOT = os.environ["EHOME_ROOT"]
except KeyError:
	ROOT = ""
CONFIG_PATH = os.path.join(ROOT, "etc/ehome/config.ini")

try:
	DEBUG = os.environ["EHOME_DEBUG"] == "yes"
except KeyError:
	DEBUG = False
if DEBUG:
	sys.path.append(HOME)


# Server states
MODE_INIT = 0
MODE_LOGOUT = 1
MODE_USER = 2
MODE_ADMIN = 3


# ehome imports
import ehome
import ehome.dashboard as dashboard
import ehome.ldap as ldap
import ehome.services as services
import ehome.init as init


# awful fix
from cherrypy.lib.reprconf import _Builder3
def build_Constant(self, o):
	return o.value
_Builder3.build_Constant = build_Constant 

TOP_CONF = {
		'global': {
			"server.socket_port": 8888
		},
		'/': {
			'tools.sessions.on': True,
			'tools.staticdir.root': os.path.abspath(HOME)
        },
		'/static': {
			'tools.staticdir.on': True,
			'tools.staticdir.dir': 'share/ehome/static'
		}
    }


class EHome:
	"""EHome server entry point."""

	def reset(self):
		self.admin = "sysadmin"
		self.password = ""
		self.domain = ""
		self.port = 8888

	def __init__(self, modules):

		# basic init
		self.tmpl_lookup = TemplateLookup(directories = [TMPL])
		self.timeout = 60 * 60
		self.version = VERSION
		self.reset()
		self.pages = None
		self.modules = modules
		for module in modules:
			module.init(self)

		# setup tree with configuration
		cherrypy.config.update(TOP_CONF)
		app = cherrypy.tree.mount(self, '/', TOP_CONF)

		# set the mode
		cherrypy.log("CONFIG_PATH = %s" % CONFIG_PATH)
		self.initialized = os.path.exists(CONFIG_PATH)
		self.just_initialized = False

		# configuration
		if self.initialized:
			cherrypy.config.update(CONFIG_PATH)
			app.merge(CONFIG_PATH)
			self.config(app.config)
			for module in self.modules:
				try:
					module.config(app.config[module.__name__])
				except KeyError:
					module.config({})

	def make_pages(self):
		"""Prepare the pages for the main display."""
		self.pages = []
		self.page_map = {}
		for module in self.modules:
			for page in module.get_pages():
				page.parent = self
				self.pages.append(page)
				self.page_map[page.name] = page
				cherrypy.tree.mount(page, "/" + page.name, TOP_CONF)

	def config(self, conf):
		try:
			self.conf = conf["ehome"]
		except KeyError:
			self.conf = {}
		self.user = self.get_conf("admin", "admin")
		self.password = self.get_conf("password", "")
		self.domain = self.get_conf("domain", "")

	def get_conf(self, id, dflt = None):
		try:
			return self.conf[id]
		except KeyError:
			return dflt

	def run(self):
		cherrypy.engine.start()
		cherrypy.engine.block()

	def expired(self):
		if not self.initialized:
			raise cherrypy.HTTPError(401, 'Initialize first!')
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

	def get_root(self):
		return ROOT

	def get_domain(self):
		return self.domain

	def start_session(self, user):
		"""Called to start a session."""
		cherrypy.session['user'] = user
		cherrypy.session['expiration'] = time.time()

	def end_session(self):
		"""Called to clear a session."""
		for key in ['user', 'expiration']:
			if key in cherrypy.session:
				del cherrypy.session[key]

	@cherrypy.expose
	def index(self, msg = ""):
		if not self.initialized:
			return self.tmpl_lookup.get_template("init.html") \
				.render(modules = self.modules, ehome=self)
		elif DEBUG:
			self.start_session(self.admin)
			return self.main()
		else:
			return self.tmpl_lookup.get_template("login.html") \
				.render(msg = msg)

	@cherrypy.expose
	def login(self, user, pwd):
		if user == self.admin and pwd == self.password:
			self.start_session(user)
			return "<div class='success'>Success!</div>"
		else:
			return "<div class='failure'>Authentification error!</div>"

	@cherrypy.expose
	def logout(self):
		self.end_session()
		return self.index()

	@cherrypy.expose
	def main(self):
		if self.expired():
			return self.expire()
		if self.pages == None:
			self.make_pages()
		return self.get_template("main.html").render(ehome = self)

	@cherrypy.expose
	def content(self, tab):
		if self.expired():
			return self.expire()
		try:
			return self.page_map[tab].gen()
		except KeyError:
			cherrypy.log("Bad accessed page: %s" % tab)
			return "Error."

	def forbidden(self):
		"""Called when a forbidden URL is requested."""
		raise cherrypy.HTTPError(401, 'Forbidden access!')

	@cherrypy.expose
	def init(self, **args):
		cherrypy.log("initialization: %s" % args)

		# basic checks
		try:
			remote = cherrypy.request.headers["Remote-Addr"]
			if remote != "127.0.0.1" and not remote.startswith("192.168."):
				return self.forbidden()
		except KeyError:
			return self.forbidden()

		# record the configuration configuration
		try:

			# get the configuration
			self.admin = args["admin"]
			self.password = args["password"]
			self.domain = args["domain"]
			port = int(args["port"])
			if port < 8000 or port > 65535:
				cherrypy.log("bad port number: %d" % port)
				raise init.Error()
			port_updated = False
			if port != self.port:
				self.port = port
				port_updated = True
				cherrypy.log("new port: %s" % port)

			# initialize the modules
			for module in self.modules:
				module.do_init(args)

			# create admin user
			if not DEBUG:
				init.run('adduser %s --uid 1000 --ingroup --home /admin --disabled-login' \
					% self.admin)
				init.run('usermod -aG sudo %s' % self.admin)
				init.run("cat '%s:%s | chpasswd" % (self.admin, self.password))

			# other initialization
			if not DEBUG:
				init.run("deluser --remove-gome ehome")
				init.run("hostnamectl set-hostname %s" % self.domain)

			# finally create the configuration
			init.write(
				CONFIG_PATH,
				self.get_template("config.ini").render(ehome = self)
			)
			init.protect(CONFIG_PATH)
			self.initialized = True

			# new server for new port
			if port_updated:
				old_server = cherrypy.server
				cherrypy.server = Server()
				cherrypy.server.socket_port = self.port
				cherrypy.server.subscribe()
				cherrypy.server.start()

				def clean():
					old_server.stop()
					old_server.unsubscribe()
					cherrypy.engine.unsubscribe("on_end_request", clean)
				cherrypy.engine.subscribe("on_end_request", clean)

			# redirect to start
			self.start_session(self.admin)
			u = url.urlparse(cherrypy.request.base)
			raise cherrypy.HTTPRedirect("%s://%s:%s" % (u.scheme, u.hostname, self.port))
			
		except (KeyError, ValueError, init.Error) as e:
			self.reset()
			cherrypy.log("init error: %d" % e)
			raise cherrypy.HTTPError(400, 'error at initialization')


# startup
if __name__ == '__main__':
	EHome([
		dashboard,
		services,
		ldap
	]).run()
