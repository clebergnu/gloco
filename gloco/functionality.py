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
gloco/functionality.py

   functionality module
"""

import inspect

class Functionality:
    '''
    This class exposes some attributes of a function, making it somewhat more
    accessible to applications through.

    See doc/README.functionality for more info.
    '''
    def __init__(self, function):
        self.function = function
        
        self.shortname = function.__name__
        self.help = function.__doc__.strip()

        self.function_args, \
        self.function_kargs, \
        self.function_kwargs, \
        self.function_defaults = inspect.getargspec(self.function)

        self.args_defaults = self.__get_args_defaults()
        self.syntax = self.__auto_generate_syntax()


    def __get_args_defaults(self):
        '''
        Returns a dictionary, having as keys the arguments names and as
        values, either the default value or None if it does not have one
        '''
        d = {}
        for arg in self.function_args:
            d[arg] = None

        number_of_defaults = len(self.function_defaults)
        if number_of_defaults:
            args_with_default = self.function_args[-number_of_defaults:]
            d.update(zip(args_with_default, self.function_defaults))

        return d


    def __auto_generate_syntax(self):
        '''
        Automatically generate a syntax for this functionality
        '''
        required_parameters = " ".join(["%s" % arg for arg in self.args_defaults \
                                       if self.args_defaults[arg] == None])
        optional_parameters = " ".join(["[%s]" % arg for arg in self.args_defaults \
                                       if self.args_defaults[arg] != None])

        return "%s %s %s" % (self.shortname,
                             required_parameters,
                             optional_parameters)

    def __call__(self, args, kwargs):
        # FIXME:
        #    * Verify __call__ signature
        return self.function.__call__(args, kwargs)
    
if __name__ == '__main__':

    @Functionality
    def price(cost, profit, tax=1.17):
        '''
        Returns the price of a given product, with profit rate and tax
        '''
        return cost * profit * tax

    #price = Functionality(price)
    print 'Shortname:', price.shortname
    print 'Help:', price.help
    print 'Syntax:', price.syntax

    print price(10, 2.0)

    print type(price)
    print price

