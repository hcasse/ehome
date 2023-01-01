"""Module implementing dashboard page."""

import re
import ehome

CPUINFO_RE = re.compile("^processor\s*:\s*([0-9]+)")
STAT_RE = re.compile("^cpu([0-9]+)\s+(.*)")

class Core:

	def __init__(self, num):
		self.num = num
		self.load = 0
		self.stats = [0] * 8
		self.old_stats = None


class Page(ehome.Page):
	"""Main dashboard."""

	def __init__(self):
		ehome.Page.__init__(self, "dashboard", "Dashboard")
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


