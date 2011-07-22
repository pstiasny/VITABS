#!/usr/bin/python2

import sys
import curses
import fractions
from fractions import Fraction
import copy

from tablature import chord, bar, tablature
from editor import editor
import commands

def ncmain(stdscr):
	ed = editor(stdscr)
	commands.map_commands(ed)
	if len(sys.argv) > 1:
		ed.load_tablature(sys.argv[1])
		ed.redraw_view()
		ed.move_cursor()
	ed.normal_mode()

curses.wrapper(ncmain)
#stdscr = curses.initscr()
#curses.noecho()
#curses.cbreak()
#ncmain(stdscr)
#curses.nocbreak(); stdscr.keypad(0); curses.echo()
#curses.endwin()
