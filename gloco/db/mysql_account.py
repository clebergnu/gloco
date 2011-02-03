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
mysql_account.py

   MySQL Account Manager

   This module aims to simplify the creation of MySQL user accounts.

   In theory, one can subclass from MySQLAccount, and stuff in the desired
   privileges, given birth to a kind of 'Role'.
"""

import re
import sets

# This regex can be used to extract the privilege withou the trailling '_priv'
# name from user_priv_field_names, db_priv_field_names, etc
priv_name_without_trailing_priv_re = re.compile(r'([a-zA-Z_]+)(_priv)')

# This holds the name of fields (related to privileges) of the 'user' table in
# the mysql database
user_priv_field_names = ('Select_priv',
                         'Insert_priv',
                         'Update_priv',
                         'Delete_priv',
                         'Create_priv',
                         'Drop_priv',
                         'Reload_priv',
                         'Shutdown_priv',
                         'Process_priv',
                         'File_priv',
                         'Grant_priv',
                         'References_priv',
                         'Index_priv',
                         'Alter_priv',
                         'Show_db_priv',
                         'Super_priv',
                         'Create_tmp_table_priv',
                         'Lock_tables_priv',
                         'Execute_priv',
                         'Repl_slave_priv',
                         'Repl_client_priv',
                         'Create_view_priv',
                         'Show_view_priv',
                         'Create_routine_priv',
                         'Alter_routine_priv',
                         'Create_user_priv')

# This holds the name of fields (related to privileges) of the 'user' table in
# the mysql database
db_priv_field_names = ('Select_priv',
                       'Insert_priv',
                       'Update_priv',
                       'Delete_priv',
                       'Create_priv',
                       'Drop_priv',
                       'Grant_priv',
                       'References_priv',
                       'Index_priv',
                       'Alter_priv',
                       'Index_priv',
                       'Alter_priv',
                       'Create_tmp_table_priv',
                       'Lock_tables_priv',
                       'Create_view_priv',
                       'Show_view_priv',
                       'Create_routine_priv',
                       'Alter_routine_priv',
                       'Execute_priv')

# Table privileges is a special case, there's only two fields, named
# Table_priv and Column_priv. Both of them are sets, which can contain
# a composed number of privileges.
table_priv_field_values = ('Select',
                           'Insert',
                           'Update',
                           'Delete',
                           'Create',
                           'Drop',
                           'Grant',
                           'References',
                           'Index',
                           'Alter',
                           'Create View',
                           'Show view')

table_column_priv_field_values = ('Select',
                                  'Insert',
                                  'Update',
                                  'References')

# Make a union of all privilege field names
all_priv_field_names = sets.Set(user_priv_field_names)
all_priv_field_names.union(db_priv_field_names)

# Make a union of all privilege values for field which are sets
all_priv_field_values = sets.Set(table_priv_field_values)
all_priv_field_values.union(table_column_priv_field_values)

def __convert_from_value_to_field(value):
    """
    Converts a value of a privilege field (that is a set) to a field name.
    
    Our theory is: privilege values (which are in sets), can be transformed
    to privilege fields names by doing this operation:
    
    1) Replace spaces by underscores (_)
    2) Capitalizing the word
    3) Add a trailling '_priv'
    """
    value = value.replace(' ', '_').capitalize()
    value += '_priv'
    return value

def __convert_from_field_to_value(field):
    """
    Converts a field name to a value that can be used in a set field.

    This should to do the exact opposite of __convert_from_value_to_field
    """
    field = priv_name_without_trailing_priv_re.match(field).groups()[0]
    field = field.replace('_', ' ').title()
    return field

def __test_convert_from_values_to_fields():
    """
    Tests whether fields values can be converted to field names
    """
    for v in all_priv_field_values:
        v = __convert_from_value_to_field(v)
        assert v in all_priv_field_names

def __test_convert_from_fields_to_values():
    """
    Tests whether fields named can be converted to field values
    """
    for v in all_priv_field_names:
        v = __convert_from_field_to_value(v)
        # We cannot use an assertion here, because some field names
        # are not in the values. So, do a print of 'v' and check the results

def __test():
    __test_convert_from_values_to_fields()
    __test_convert_from_fields_to_values()

class MySQLTablePriv:
    """
    Represents a set of privileges a user has over an entire table.
    """
    def __init__(self, dbname, tablename, *privs):
        self.dbname = dbname
        self.tablename = tablename
        self.privs = []
        self.add_privs(*privs)

    def add_privs(self, *privnames):
        """
        Adds a given number of privileges to the table
        """
        for privname in privnames:
            if privname not in self.privs:
                self.privs.append(privname)
        
class MySQLDBPriv:
    """
    Represents a set of privileges a user has over an entire database.
    """
    def __init__(self, dbname, *privs):
        self.dbname = dbname
        self.privs = []
        self.add_privs(*privs)

    def add_privs(self, *privnames):
        """
        Adds a given number of privileges to the database
        """
        for privname in privnames:
            if privname not in self.privs:
                self.privs.append(privname)

class MySQLAccount:
    """
    Represents a complete set of privileges of a user
    """
    def __init__(self, username, password='', host='%'):
        self.username = username
        self.password = password
        self.host = host

        self.system_privs = []
        self.db_privs = []
        self.table_privs = []

        self.extra_sql_lines = []

    def add_priv(self, priv):
        """
        Adds one privilege, respecting it's type.

        This method calls the more specific add_*_priv family.
        """
        if isinstance(priv, MySQLTablePriv):
            self.add_table_priv(priv)
        elif isinstance(priv, MySQLDBPriv):
            self.add_db_priv(priv)
        elif isinstance(priv, str):
            self.add_system_priv(priv)
        else:
            raise TypeError, 'unkown privilege object type %s' % priv
    
    def add_privs(self, *privs):
        """
        Adds a variable number of privileges.
        """
        for priv in privs:
            self.add_priv(priv)

    def add_system_priv(self, priv):
        """
        Adds a system wide privilege
        """
        if priv not in self.system_privs:
            self.system_privs.append(priv)

    def add_db_priv(self, priv):
        """
        Adds a database wide privilege
        """        
        if priv not in self.db_privs:
            self.db_privs.append(priv)

    def add_table_priv(self, priv):
        """
        Adds a table wide privilege
        """        
        if priv not in self.table_privs:
            self.table_privs.append(priv)

    def build_new_user_sql(self):
        """
        Creates a SQL for creating a new user and all the privileges he has.
        """
        sql = []
        sql.append(self.__build_user_insert_sql())
        for line in self.__build_db_insert_sql():
            sql.append(line)
        for line in self.__build_table_insert_sql():
            sql.append(line)
        for line in self.extra_sql_lines:
            sql.append(line)
        sql.append('FLUSH PRIVILEGES')

        return "%s;" % ";\n".join(sql)


    def __build_user_insert_fields(self):
        """
        Builds the part of the SQL command for creating a new user that lists the
        fields used, that is, 'INSERT INTO user <this> VALUES (values)'
        """
        sql = '(Host, User, Password'
        if self.system_privs:
            sql += ', %s)' % ", ".join(self.system_privs)
        else:
            sql += ')'
        return sql

    def __build_user_insert_values(self):
        """
        Builds the part of the SQL command for creating a new user that lists the
        values used, that is, 'INSERT INTO user (fields) VALUES <this>'
        """
        sql = "('%(host)s', '%(username)s', PASSWORD('%(password)s')" % \
               {"host" : self.host,
                "username" : self.username,
                "password" : self.password}

        if self.system_privs:
            sql += ', %s)' % ", ".join(["'Y'" for priv in self.system_privs])
        else:
            sql += ')'

        return sql

    def __build_user_insert_sql(self):
        """
        Creates a SQL with the user wide privileges.
        """
        sql_template = 'INSERT INTO user %(fields)s VALUES %(values)s'

        return sql_template % {'fields' : self.__build_user_insert_fields(),
                               'values' : self.__build_user_insert_values()}

    def __build_db_insert_fields(self, dbpriv):
        """
        Builds the part of the SQL command for creating the user database privilege
        that lists the fields used, that is, 'INSERT INTO db <this> VALUES)...'

        @dbpriv: an instance of MySQLDBPriv
        """
        sql = '(Host, Db, User'
        if dbpriv.privs:
            sql += ', %s)' % ", ".join(dbpriv.privs)
        else:
            sql += ')'
        return sql

    def __build_db_insert_values(self, dbpriv):
        sql = "('%(host)s', '%(dbname)s', '%(username)s'" % \
               {"host" : self.host,
                "dbname" : dbpriv.dbname,
                "username" : self.username}

        if dbpriv.privs:
            sql += ', %s)' % ", ".join(['\'Y\'' for priv in dbpriv.privs])
        else:
            sql += ')'

        return sql

    def __build_table_insert_fields(self, tablepriv):
        """
        Builds the part of the SQL command for creating the user table privilege
        that lists the fields used, that is, 'INSERT INTO tables_priv <this>...'

        @tablepriv: an instance of MySQLTablePriv
        """
        sql = '(Host, Db, User, Table_name, Grantor, Table_priv, Column_priv)'
        return sql

    def __build_table_insert_values(self, tablepriv):
        sql = "('%(host)s', '%(dbname)s', '%(username)s', '%(tablename)s', " \
              "'%(grantor)s', '%(tablepriv)s', '')" % \
              {"host" : self.host,
               "dbname" : tablepriv.dbname,
               "username" : self.username,
               "tablename" : tablepriv.tablename,
               "grantor" : "mysql_account.py",
               "tablepriv" : ",".join(tablepriv.privs)}
        return sql

    def __build_db_insert_sql(self):
        """
        Creates a SQL with the database wide privileges
        """
        sql_template = 'INSERT INTO db %(fields)s VALUES %(values)s'

        sql_lines = []
        for dbpriv in self.db_privs:
            sql = sql_template % \
                  {'fields' : self.__build_db_insert_fields(dbpriv),
                   'values' : self.__build_db_insert_values(dbpriv)}
            sql_lines.append(sql)

        return sql_lines

    def __build_table_insert_sql(self):
        """
        Creates a SQL with the table wide privileges
        """
        sql_template = 'INSERT INTO tables_priv %(fields)s VALUES %(values)s'

        sql_lines = []
        for tablepriv in self.table_privs:
            sql = sql_template % \
                  {'fields' : self.__build_table_insert_fields(tablepriv),
                   'values' : self.__build_table_insert_values(tablepriv)}
            sql_lines.append(sql)

        return sql_lines

class DatabaseAdminRole(MySQLAccount):
    """
    Implements a MySQL account that has FULL permission on a given database
    """
    def __init__(self, username, password, host, db):
        MySQLAccount.__init__(self, username, password, host)
        self.add_db_priv(MySQLDBPriv(db, *db_priv_field_names))

if __name__ == '__main__':

    def some_role():
        acc = MySQLAccount('username', 'password', '%')
        acc.add_privs('Select_priv',
                      MySQLDBPriv('db1', 'Select_priv'), 
                      MySQLTablePriv('db2', 'table1', 'Select', 'Insert'))
        return acc
    
    acc = some_role()
    print acc.build_new_user_sql()
            
