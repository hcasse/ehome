# README for the development


## Installation Application

Delivering a RPi image is very good but some customization needs to be performed. We need to provide a Python installation application that will set up all in the right way.

The following should be asked although they can be at siome point autolmatically determined:

* Name of the administrator (default `sysadmin`).
* Domainname of the server (default _hostname_).
* Data path (default `/`).

The data path will contain all user data files. As default, it will be `/`, i.e. the SD-card where the RPi is installed on, but it not clearly a long-term solution. With the _Data path_ parameter, the user can design an external disk.


## LDAP Configuration

LDAP server requires a specific password that is then used by LDAPCherry.

Idea: generate a random password that will be passed:

* At installation time for slapd.
* In the configuration file `/etc/ldapcherry/ldapcherry.ini` for LDAPCherry.

This procedure could be used for other type of configurations.

Things to know:

* Configuration is all in /etc/ldap.conf.
* Administrator password is in /etc/ldap.secret root:root -rw-------
* Default user name seems to be `People` and group `Group`. Maybe there is another system based on `posixAccount` and `posixGroup` but it is good idea to stick to OS convention.

[Website](https://computingforgeeks.com/how-to-configure-ubuntu-as-ldap-client/) gives detail about LDAP configuration with PAM. But this can be done before PAM complete configuration:

* `/etc/nsswitch.conf`
* `/etc/pam.d/common-password`
* `/etc/pamd.d/common-session`

It could be a good idea to have a module to update `/etc` configurations.

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


## Initialization process

The distribution is first created with a user "ehome" which password is "*ehome*" (as a sudoer). As soon as administrator is created, this account is removed.



## Modules

### Ehome

**Preparation:**

* APT modules:
	* `apache2`
	* `python3`
	* `python3-cherrypy`
	* `python3-ldap`
	* `python3-mako`

* Create `/etc/ehome/htpasswd`

	$ htpasswd -c /etc/ehome/htpasswd

* Create `ehome` user and add it to sudo users.

	$ adduser ehome
	$ usermod -aG sudo ehome

* Set up the service

	$ cp share/ehome/system/ehome.service /etc/systemd/system/
	$ systemctl enable radicale
	$ systemctl start radicale


**Initialization:**

1. Create "admin" user in "/etc/passwd"

	$ adduser --uid 1000 --ingroup admin --home /admin --disabled-login
	$ usermod -aG sudo admin
	$ cat 'admin:password' | chpasswd
		
2. Remove old `ehome`user:

	$ deluser --remove-home ehome

3. Set domain name.

	$ hostnamectl set-hostname domain



### LDAP

Let _DCD_ the hostname with `dc=` notation.

**Preparation :**

* APT installation

	* `ldap-utils`
	* `libnss-ldap`
	* `libpam-ldap`
	* `slapd`

* Generate LDAP password: _LPWD_.

* Customize LDAP DB:

	$ ldapadd -x -D cn=admin,dc-domain -W -f init.ldif

With `init.ldif` produced from `share/ehome/templates/init.ldif`.

* `/etc/nsswicth.conf` -- add `ldap` at end of lines `passwd:` and `group:`.

* `/etc/pam.d/common-password` -- remove `use_ok` in line:

	password [success=1 user_unknown=ignore default=die] pam_ldap.so try_first_pass

* `/etc/pam.d/common-session` -- append line
	
		session optional pam_mkhomedir.so skel=/etc/skel umask=077

See [Computing for geeks](https://computingforgeeks.com/how-to-configure-ubuntu-as-ldap-client/)).


**Initialization :**

	$ echo 'LPWD' > /etc/ldap.secret
	$ chmod go-rwx /etc/ldap.secret

	* update `BASE` of `/etc/ldap/ldap.conf` to DCD.
	* update `roobinddn` of `/etc/ldap.conf` to DCD.


### Radicale

**Preparation:**

* Compilation ([Radicale](https://radicale.org/))

	$ git clone https://github.com/Kozea/Radicale.git
	$ cd radicale
	$ python3 setup.py install

* Radicale -- copy `/share/ehome/confs/radicale.conf` in `/etc/radicale/config`.

*. Copy `share/ehome/system/radicale.service`to `/etc/systemd/system/`.

* Create a user `radicale`

	$ useradd --system --user-group --home-dir / --shell /sbin/nologin radicale

* Perform commands.


**Initialization:**


**Activation**

	$ systemctl enable radicale
	$ systemctl start radicale



## Lists


### Configuration files


### Port mapping

  * 5232 -- Radicale
  * 8888 -- ehome



## API

Module interface:

* `init`(server) -- called at startup.
* `config`(map) -- called at configuration time.
* `finish`() -- called if the server is stopped.
* `get_pages`() -- get the pages for the module (if any).
* `gen_init`() -- generate HTML code for initialization.
* `do_init`(map) -- called when the initial user has started (after server initialization).
* `gen_config`() -- generate content of configuration file.

A normal cycle is:

1. `init`(server)
2. `config`(map)
3. `get_pages`()
...
4. `finish`()

At initialiation time:
1. `init`(server)
2. `gen_init`()
3. `do_init`(map)
4. `get_pages`()
...
5. `finish`()


## Answers

* Non-interactive apt/dpkg:

	[https://askubuntu.com/questions/556385/how-can-i-install-apt-packages-non-interactively]

	DEBIAN_FRONTEND=noninteractive


## Useful

* Access to documentation of cherrypy

	$ pydoc cherrypy
	


## References

  * [Computing for Geeks](https://computingforgeeks.com)
