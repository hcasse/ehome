import random

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


# password generation

DIGITS = "0123456789"
LOWCASE = "abcdefghijklmnopqrstuvwxyz"
HIGHCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
SYMBOLS = "@#$%=:?./|~>*()<[]{})"
ALL = DIGITS + LOWCASE + HIGHCASE + SYMBOLS

def make_password(length, *css):
	"""Generate a pasword of the given length with the given characters
	sets (s1, s2, s3, ..., sn) with one character of s1, one of s2, ...
	and the remaining of sn."""

	# generate characters
	res = ""
	last = None
	for cs in css:
		res = res + random.choice(cs)
		last = cs
	for i in range(len(res), length):
		res = res + random.choice(last)

	# move their position
	for n in range(0, random.randint(0, length)):
		i = random.randint(0, length-1)
		j = random.randint(0, length-1)
		i, j = min(i, j), max(i, j)
		if i != j:
			res = res[:i] + res[j] + res[i+1:j] + res[i] + res[j+1:]

	return res


def test():
	return make_password(10, DIGITS, SYMBOLS, HIGHCASE, LOWCASE, ALL)
