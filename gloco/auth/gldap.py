# -*- Mode: Python; coding: iso-8859-1 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2005 Cleber Rosa <cleber@tallawa.org>
## All rights reserved
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307,
## USA.
##
## Author(s): Cleber Rosa <cleber@tallawa.org>
##
"""
gloco/auth/gldap.py

   ldap authentication class
"""

import ldap

from base import AuthBase

class AuthLdap(AuthBase):
    def __init__(self, user, passwd, host, **kwargs):
        AuthBase.__init__(self, user, passwd, host, **kwargs)

    def auth(self):
        try:
            conn = ldap.open(self.host)
            conn.simple_bind_s(self.user, self.passwd)
            return True
        except ldap.LDAPError:
            return False

    def set_timeout(self, seconds):
        # ldap has two TIMEOUTs available:
        # ldap.OPT_TIMEOUT and ldap.OPT_NETWORK_TIMEOUT
        # The first one seem to be more general, maybe this is a FIXME
        ldap.set_option(ldap.OPT_TIMEOUT, seconds)

if __name__ == '__main__':
    a = AuthLdap(raw_input('User: '),
                 raw_input('Password: '),
                 raw_input('Host: '))

    print a.auth()
