"""Module managing the service page."""

import ehome

class Page(ehome.Page):
	"""Page displaying services and allowing to stop/start."""

	def __init__(self):
		ehome.Page.__init__(self, "services", "Services")

	def gen(self):
		pass

def init(server):
	pass

def config(map):
	pass

def get_pages():
	return [Page()]

def gen_init():
	return ""

def do_init(map):
	pass

def gen_config():
	return ""
