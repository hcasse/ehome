"""Module implemeting LDAP user page."""

import os
import re

import ehome
import ehome.init

SERVER = None
SECRET_PATH = ""

class Page(ehome.Page):
	"""User management using LDAP."""

	def __init__(self):
		ehome.Page.__init__(self, "ldap", "Users")

	def gen(self):
		return "LDAP"

def init(server):
	global SERVER
	SERVER= server
	global SECRET_PATH
	SECRET_PATH = os.path.join(server.get_root(), "etc/ldap.secret")

def config(map):
	pass

def get_pages():
	return [Page()]

def gen_init():
	return ""

def do_init(map):
	global SERVER

	# password
	pwd = ehome.make_password(16, ehome.ALL)
	ehome.init.write(SECRET_PATH, pwd)
	ehome.init.protect(SECRET_PATH)

	# set domain
	domain = "dc=" + SERVER.get_domain().replace(".", ",dc=")
	ehome.init.update_conf(
		os.path.join(SERVER.get_root(), "etc/ldap/ldap.conf"),
		[
			(
				re.compile("^\#?BASE\s+.*$"),
				lambda args: "BASE %s\n" % domain
			),
			(
				re.compile("^\#?URI\s+.*$"),
				lambda args: "URI ldap://localhost\n"
			)
		]
	)
	ehome.init.update_conf(
		os.path.join(SERVER.get_root(), "etc/ldap.conf"),
		[
			(
				re.compile("^rootbinddn\s+cn=admin,.*$"),
				lambda args: "rootbinddn cn=admin,%s\n" % domain
			),
			(
				re.compile("^base\s+.*"),
				lambda args: "base %s\n" % domain
			)
		]
	)


def gen_config():
	return ""
