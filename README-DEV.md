# README for the development


## Installation Application

Delivering a RPi image is very good but some customization needs to be performed. We need to provide a Python installation application that will set up all in the right way.

The following should be asked although they can be at siome point autolmatically determined:

* Name of the administrator (default `admin`).
* Domainname of the server (default _hostname_).
* Data path (default `/`).

The data path will contain all user data files. As default, it will be `/`, i.e. the SD-card where the RPi is installed on, but it not clearly a long-term solution. With the _Data path_ parameter, the user can design an external disk.


## LDAP Configuration

LDAP server requires a specific password that is then used by LDAPCherry.

Idea: generate a random password that will be passed:

* At installation time for slapd.
* In the configuration file `/etc/ldapcherry/ldapcherry.ini` for LDAPCherry.

This procedure could be used for other type of configurations.



**IDEA**
Moreover, we can have several randomly determined passwords that will be invisible for the user but complex enough and variable to improve the overall security.

Notice that the `.ldif` configuration for user and groups needs to be customized. So a 


## To Do

So much...

* Save/restore system for user data.
* Save/restore system for system configuration.
* WebDAV server for configuration.
* Apache2 configuration.
* Application to monitor activity.


## Answers

* Non-interactive apt/dpkg:

	[https://askubuntu.com/questions/556385/how-can-i-install-apt-packages-non-interactively]

	DEBIAN_FRONTEND=noninteractive


## Problem of certificate
