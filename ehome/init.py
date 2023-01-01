import cherrypy
import os
import stat
import subprocess


class Error(Exception):
	"""Error that can be raised at initialization time."""
	pass

def run(cmd):
	r = subprocess.run(cmd, shell=True)
	if r.returncode != 0:
		cherry_py.log("init.run(%s): returncode=%d" % (cmd, r.returncode))
		raise Error()

def protect(path):
	os.chmod(path, stat.S_IRUSR|stat.S_IWUSR)

def write(path, content):
	try:
		with open(path, "w") as out:
			out.write(content)
			out.close()
	except OSError as e:
		cherrypy.log("write(%s): %s" % (path, e))
		raise Error()


def update_conf(path, mods):
	"""Update a configuration file. mods is a list of pairs (re, f) where re is a regular expresison to match a line and f is called if the line match is succesful with the result of the match."""
	tmp_path = path + "~"
	try:
		s = os.stat(path)

		# write the new version
		with open(tmp_path, "w") as out:
			with open(path) as inp:
				for l in inp:
					for (re, f) in mods:
						r = re.match(l)
						if r != None:
							l = f(r)
							break
					out.write(l)
				inp.close()
			out.close()

		# replace the old version by the new one
		os.remove(path)
		os.rename(tmp_path, path)
		os.chmod(path, s.st_mode)
		os.chown(path, s.st_uid, s.st_gid)
		
	except (OSError, FileNotFoundError) as e:
		cherrypy.log("write(%s): %s" % (path, e))
		raise Error()

	
