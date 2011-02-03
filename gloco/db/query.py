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
gloco/db/query.py

   Database query module
"""

__all__ = ['DbQuery']

from conn import DbConn

from gloco.ext.db.resultset import getdict

class DbQuery:
    """
    Simple class that performs a database query.
    """
    def __init__(self, sql=None):
        cnc = DbConn()
        cnc.connect()
        self.cursor = cnc.real_conn.cursor()

        if sql:
            self.execute(sql)

    def execute(self, query, params=None):
        self.cursor.execute(query, params)

    def fetchdict(self):
        return getdict(self.cursor.fetchall(), self.cursor.description)

if __name__ == '__main__':
    from gloco.db import default_db_config

    default_db_config['db'] = 'test'
    qry = DbQuery()
    qry.execute('SHOW TABLES')
    for row in qry.cursor.fetchall():
        for field in row:
            print field
            # field is a table name
            qry2 = DbQuery()
            qry2.execute('SELECT * FROM %s' % field)
            print qry2.cursor.fetchall()

