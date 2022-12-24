"""Module managing the service page."""

import ehomelib

class Page(ehomelib.Page):
	"""Page displaying services and allowing to stop/start."""

	def __init__(self):
		ehomelib.Page.__init__(self, "services", "Services")

	def gen(self):
		pass



