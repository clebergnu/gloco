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
gloco/shell.py

   shell module
"""

import cmd
import sys

import gloco.app

class Shell(cmd.Cmd):
    '''
    A command line interpreter, based on the 'cmd' module of the  standard
    python library.
    '''
    positive_answers = ('', 'y', 'Y')

    def __init__(self):
        cmd.Cmd.__init__(self)

        if gloco.app.GlocoApp:
            self.app_name = gloco.app.GlocoApp.shortname
        else:
            self.app_name = sys.argv[0]

        self.readline_initialized = False



    def __init_readline(self):
        '''
        Initializes the readline library
        '''
        if self.use_rawinput and self.completekey:
            if not self.readline_initialized:
                try:
                    import readline
                    self.old_completer = readline.get_completer()
                    readline.set_completer(self.complete)
                    readline.parse_and_bind(self.completekey+": complete")
                    self.readline_initialized = True
                except ImportError:
                    pass


    def __cleanup_readline(self):
        '''
        Cleans-up readline, restoring previous settings
        '''
        if self.use_rawinput and self.completekey:
            if self.readline_initialized:
                import readline
                readline.set_completer(self.old_completer)


    def __print_intro(self, intro):
        '''
        Prints the intro text
        '''
        if intro is not None:
            self.intro = intro
        if self.intro:
            self.stdout.write(str(self.intro)+"\n")


    def cmdloop(self, intro=None):
        '''
        Just like cmd.Cmd.cmdloop, this repeatedly issues a prompt, accepting
        input.

        It then calls onecmd, which will parse the given line, and find out the
        command to dispatch, calling it with rest of the line as the argument.
        '''
        self.preloop()                  # Hook
        self.__init_readline()
        self.__print_intro(intro)
        stop = None        
        try:
            while not stop:
                if self.cmdqueue:
                    line = self.cmdqueue.pop(0)
                else:
                    if self.use_rawinput:
                        try:
                            line = raw_input(self.prompt)
                        except EOFError:
                            line = 'EOF'
                    else:
                        self.stdout.write(self.prompt)
                        self.stdout.flush()
                        line = self.stdin.readline()
                        if not len(line):
                            line = 'EOF'
                        else:
                            line = line[:-1] # chop \n
                line = self.precmd(line)
                stop = self.onecmd(line)
                stop = self.postcmd(stop, line)
            self.postloop()             # Hook
        finally:
            self.__cleanup_readline()

    def do_EOF(self, line):
        '''
        This implements the default action on EOF, quitting the application
        '''
        self.stdout.write('\n')
        
        return True
    
if __name__ == '__main__':
    s = Shell()
    s.cmdloop()
