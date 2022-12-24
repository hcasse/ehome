"""Module implemeting LDAP user page."""

import ehomelib

class Page(ehomelib.Page):
	"""User management using LDAP."""

	def __init__(self):
		ehomelib.Page.__init__(self, "ldap", "Users")

	def gen(self):
		return "LDAP"

