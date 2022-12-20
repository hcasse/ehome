#!/usr/bin/python3

import os, os.path

import cherrypy


class EHome:

	@cherrypy.expose
	def index(self):
		return open('templates/index.html')

	@cherrypy.expose
	def login(self, user, pwd):
		if user == "coucou" and pwd == "caca":
			return open('templates/success.html')
		else:
			return open('templates/failed.html')

if __name__ == '__main__':
	conf = {

		# top level configuration
		'/': {
			'tools.sessions.on': True,
			'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
		'/static': {
			'tools.staticdir.on': True,
			'tools.staticdir.dir': './static'
		}

    }
	cherrypy.quickstart(EHome(), '/', conf)
