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
gloco/optionparser.py

   option parser module
"""

import optparse

class GNUOptionParser(optparse.OptionParser):
    """
    A optparse.OptionParser compatible class with default GNU options


    The idea behind this is that user might want to add options simply by
    supplying the short option version. The built-in GNU option database
    will fill in all the other option components.
    """

    # Fill this up with a data structure that contains most GNU options

    gnu_options = [
        ("-v", "--version", "Display the version of this application and exit"),
        ]
    
    def __init__(self):
        optparse.OptionParser.__init__(self)

        for opt in GNUOptionParser.gnu_options:
            self.add_option(opt[0], opt[1], help=opt[2])


