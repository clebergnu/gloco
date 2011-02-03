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
gloco/app.py

   app module
"""

import gloco.i18n
import gloco.paths
import gloco.optionparser
import gloco.commandline
import gloco.gui

class AppBase:
    """
    Base class that defines a general application.
    """
    
    def __init__(self, shortname, description, authors=[]):
        self._app_shortname = shortname
        self._app_description = description
        self._app_authors = authors

        self._main_function = None
        self._main_function_args = None

        self.__init_optionparser()

    def __init_optionparser(self):
        """
        Initializes a default option parser class for this application.
        """
        # TODO:
        #  * Make this operational, so that it really gets called and used
        self._optionparser = gloco.optionparser.GNUOptionParser()

    def get_app_info_dict(self):
        return {'app_shortname' : self._app_shortname,
                'app_description' : self._app_description,
                'app_authors' : "\n".join(self._app_authors)}

    def set_main_function(self, function, *args):
        self._main_function = function
        self._main_function_args = args

    def show_help(self):
        """
        Shows text/dialog with help on using the application.
        """
        raise NotImplementedError


    def show_about(self):
        """
        Shows text/dialog about the application.
        """
        raise NotImplementedError
    

    def run(self):
        """
        Runs the application by calling the main function.
        """
        if self._main_function:
            self._main_function(self._main_function_args)

class AppConsole(AppBase):
    """
    App that is supposed to run on a console
    """
    def __init__(self, shortname, description, authors=[]):
        AppBase.__init__(self, shortname, description, authors)

    def show_help(self):
        self._optionparser.print_help()

    def show_about(self):
        print """\
%(app_shortname)s - %(app_description)s
Copyright (C) %(app_authors)s\n""" % self.get_app_info_dict()

        
class AppGUI(AppBase):
    """
    App that is supposed to run on a graphical environment
    """
    def __init__(self, shortname, description, authors=[]):
        AppBase.__init__(self, shortname, description, authors)

    def show_help(self):
        pass

    def show_about(self):
        about_dialog = AboutDialog()
        about_dialog.run()

if gloco.gui.gui_available():
    from gloco.gui import AboutDialog
    
    App = AppGUI
else:
    App = AppConsole

# GlocoApp is a global instance of App, which is automatically consulted
# by various modules
GlocoApp = None

if __name__ == '__main__':
    a = App('hello', 'hello application',
            ['Cleber Rosa <cleber@tallawa.org>'])
    a.show_about()
    a.show_help()
    a.run()
