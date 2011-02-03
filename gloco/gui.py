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
gloco/gui.py

    gui related functionality module
"""

__all__ = ["gui_available", "AboutDialog"]

def gui_available():
    """
    Wheter or not there's a Graphical User Interface and Toolkit available.
    """
    try:
        import gtk
    except:
        return False
    return True

if gui_available():
    import gtk

    major, minor, release = gtk.gtk_version
    assert major == 2

    if minor >= 6:
        AboutDialog = gtk.AboutDialog
    else:
        AboutDialog = gtk.Dialog
