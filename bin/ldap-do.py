#!/usr/bin/python3

import argparse
import ldap
import subprocess

SERVER_ADDR="ldap://localhost"

DOMAIN = "phoebe"
ADMIN = "admin"
PASSWORD = "otawa31"
PEOPLE = "people"
GROUPS = "groups"

LDAP_DOMAIN = "dc=" + DOMAIN.replace(".", ",dc=")

parser = argparse.ArgumentParser(
	prog = "EHome LDAP",
	description = "shortcut for ugly LDAP commands"
)
parser.add_argument('names', nargs="*")
parser.add_argument('--list-users', action="store_true",
	help="Displays users.")
parser.add_argument('--list-groups', action="store_true",
	help="Displays groups.")
parser.add_argument('--list-all', action="store_true",
	help="Displays the whole DB.")
parser.add_argument('--members-of', action="store_true",
	help="List members of a group.")
parser.add_argument('--groups-of', action="store_true",
	help="List groups of a user.")
parser.add_argument('--list-db', action="store_true",
	help="List the whole database.")
parser.add_argument('--add-group', action="store_true",
	help="[USER GROUP] add the user to the group.")
args = parser.parse_args()


def people_cn(people):
	return "cn=%s,ou=people,%s" % (people, LDAP_DOMAIN)


def group_cn(group):
	return "cn=%s,ou=groups,%s" % (group, LDAP_DOMAIN)

def utf8(s):
	return s.encode("UTF8")


# connect
l = ldap.initialize(SERVER_ADDR)
l.simple_bind_s(
	"cn=%s,%s" % (ADMIN, LDAP_DOMAIN),
	"%s" % PASSWORD
)

if args.list_all:
	res = l.search_s(LDAP_DOMAIN, ldap.SCOPE_SUBTREE)
	for (cn, obj) in res:
		classes = obj["objectClass"]
		if b"posixGroup" in classes:
			print(cn, str(obj["gidNumber"][0], "UTF8"), "groups")
		elif b"posixAccount" in classes:
			print(cn, str(obj["uidNumber"][0], "UTF8"), "people")

elif args.list_users:
	res = l.search_s("ou=%s,%s" % (PEOPLE, LDAP_DOMAIN), ldap.SCOPE_SUBTREE)
	for (cn, obj) in res:
		classes = obj["objectClass"]
		if b"posixAccount" in classes:		
			print(cn, str(obj["uidNumber"][0], "UTF8"))

elif args.list_groups:
	res = l.search_s("ou=%s,%s" % (GROUPS, LDAP_DOMAIN), ldap.SCOPE_SUBTREE)
	for (cn, obj) in res:
		classes = obj["objectClass"]
		if b"posixGroup" in classes:		
			print(cn, str(obj["gidNumber"][0], "UTF8"))

elif args.members_of:
	for name in args.names:
		res = l.search_s(group_cn(name), ldap.SCOPE_SUBTREE)
		for (cn, obj) in res:
			print(cn, ":", obj["memberUid"])

elif args.groups_of:
	#for name in args.names:
	#	res = l.search_s(people_cn(name), ldap.SCOPE_SUBTREE)
	#	for (cn, obj) in res:
	#		print(cn, ":", obj["memberUid"])
	pass

elif args.list_db:
	res = l.search_s(LDAP_DOMAIN, ldap.SCOPE_SUBTREE)
	for (cn, obj) in res:
		print(cn, obj)

elif args.add_group:
	people = people_cn(args.names[0])
	group = group_cn(args.names[1])
	print(people, group)
	l.modify_s(group, [(ldap.MOD_ADD, 'memberUid', [utf8(people)])])

