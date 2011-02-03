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
gloco/i18n.py

   i18n module
"""

import os
import gettext

from ConfigParser import ConfigParser

__all__ = ["GetTranslationFunction"]

def GetConfigEntry(section, option):
    c = ConfigParser()

    c.read(config_file_paths)
    if c.has_section(section):
        if c.has_option(section, option):
            return c.get(section, option)
    else:
        return None

def GetPathsBase():
    result = GetConfigEntry('Paths', 'Base')
    if result is None:
        result = '/usr'
    return result

def GetTranslationFunction():
    translation_directory = os.path.join(GetPathsBase(), 'share/locale')
    try:
        t = gettext.translation('', translation_directory)
        return t.gettext
    except:
        return str
