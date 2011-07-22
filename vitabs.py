import curses
import fractions
from fractions import Fraction
import copy

from tablature import chord, bar, tablature
from editor import editor
import commands

st = "ready"


def ncmain(stdscr):
	#c = chord()
	#c.strings = {5:1, 4:3}
	#c2 = chord()
	#c2.strings = {5:0, 4:2}
	#c2.duration = Fraction('1/8')
	#b = bar()
	#b.chords = [c, c, c2, c2, c2, c2]
	#c3 = chord()
	#c3.strings = {4:1, 3:3}
	#c3.duration = Fraction('3/4')
	#b2 = bar()
	#b2.sig_num = 3
	#b2.chords = [c3]
	#t = tablature()
	#t.bars = [b,copy.deepcopy(b),b2]

	#ed = editor(stdscr, t)
	ed = editor(stdscr)
	commands.map_commands(ed)

	ed.normal_mode()

curses.wrapper(ncmain)
