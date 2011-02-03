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
gloco/db/connection.py

   Database connection module
"""

__all__ = ['DbConn']

from gloco.db import * 

class DbConn(object):
    """
    A Database Connection.
    """

    global default_db_config
    
    def __init__(self, config=default_db_config):
        self.config = config

        if driver_name_to_module.has_key(config['driver']):
            python_module = driver_name_to_module[config['driver']]
        else:
            python_module = driver
            
        self.real_driver = __import__(python_module)

    def connect(self, host=None, user=None, passwd=None, db=None):
        """
        Connects to the database. The real connection object, as created
        and returned by the driver, is stored in self.real_conn.

        It returns True if the connection suceeds and False otherwise.
        """

        # Use default values if not supplied as parameters
        if not host:
            host = self.config['host']
        if not user:
            user = self.config['user']
        if not passwd:
            passwd = self.config['passwd']
        if not db:
            db = self.config['db']        

        try:
            self.real_conn = self.real_driver.connect(host = host,
                                                      user = user,
                                                      passwd = passwd,
                                                      db = db)
            return True
        except:
            return False

if __name__ == '__main__':
    conn = DbConn()
    if conn.connect():
        print conn.real_conn
