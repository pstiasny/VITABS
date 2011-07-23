#Copyright (C) 2011  Pawel Stiasny

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

from fractions import Fraction
from tablature import chord, bar, tablature
import string
import curses # KEY_*

# i
def insert(ed, num):
	ed.tab.get_cursor_bar().chords.insert(ed.tab.cursor_chord-1,
			chord(ed.insert_duration))
	ed.move_cursor(new_chord = max(ed.tab.cursor_chord, 1))
	ed.redraw_view()
	ed.insert_mode()

# a
def append(ed, num):
	ed.tab.get_cursor_bar().chords.insert(ed.tab.cursor_chord,
			chord(ed.insert_duration))
	ed.move_cursor(new_chord = ed.tab.cursor_chord + 1)
	ed.redraw_view()
	ed.insert_mode()

# s - this one should delete under cursor
def set_chord(ed, num):
	ed.insert_mode()

# x
def delete_chord(ed, num):
	t = ed.tab
	del t.get_cursor_bar().chords[t.cursor_chord-1]
	if not t.bars[t.cursor_bar-1].chords:
		del t.bars[t.cursor_bar-1]
	if not t.bars:
		# empty tab
		t.bars = [bar()]
	if t.cursor_bar > len(t.bars):
		t.cursor_bar = len(t.bars)
		t.cursor_chord = len(t.bars[t.cursor_bar-1].chords)
	elif t.cursor_chord > len(t.bars[t.cursor_bar-1].chords):
		t.cursor_chord = len(t.bars[t.cursor_bar-1].chords)
	ed.move_cursor()
	ed.redraw_view()

# q
def set_duration(ed, num_arg):
	curch = ed.tab.get_cursor_chord()
	if num_arg:
		curch.duration = Fraction(1, num_arg)
	else:
		curch.duration = curch.duration * Fraction('1/2')
	ed.move_cursor()
	ed.redraw_view()

# Q
def increase_duration(ed, num):
	curch = ed.tab.get_cursor_chord()
	curch.duration = curch.duration * 2
	ed.move_cursor()
	ed.redraw_view()

# o
def append_bar(ed, num):
	curb = ed.tab.get_cursor_bar()
	ed.tab.bars.insert(ed.tab.cursor_bar, bar(curb.sig_num, curb.sig_den))
	ed.move_cursor(ed.tab.cursor_bar + 1, 1)
	ed.redraw_view()
	ed.insert_mode()

# O
def insert_bar(ed, num):
	curb = ed.tab.get_cursor_bar()
	ed.tab.bars.insert(ed.tab.cursor_bar - 1, bar(curb.sig_num, curb.sig_den))
	ed.move_cursor(ed.tab.cursor_bar, 1)
	ed.redraw_view()
	ed.insert_mode()

# G
def go_end(ed, num):
	if num:
		ed.move_cursor(min(len(ed.tab.bars), num), 1)
	else:
		ed.move_cursor(len(ed.tab.bars), 1)

# 0
def go_bar_beg(ed, num):
	if not num:
		ed.move_cursor(new_chord = 1)

# $
def go_bar_end(ed, num):
	ed.move_cursor(new_chord = len(ed.tab.get_cursor_bar().chords))

# I
def insert_at_beg(ed, num):
	go_bar_beg(ed, None)
	insert(ed, num)

# A
def append_at_end(ed, num):
	go_bar_end(ed, None)
	append(ed, num)

# j
def go_next_bar(ed, num):
	if not num: num = 1
	ed.move_cursor(min(len(ed.tab.bars), ed.tab.cursor_bar + num), 1)

# k
def go_prev_bar(ed, num):
	if not num: num = 1
	ed.move_cursor(max(1, ed.tab.cursor_bar - num), 1)

# Page-Down
def scroll_bars(ed, num):
	if num == None: num = 1
	first = ed.first_visible_bar 
	first += num
	first = min(max(first, 1), len(ed.tab.bars))
	ed.first_visible_bar = first
	ed.redraw_view()
	if ed.tab.cursor_bar < first:
		ed.move_cursor(first, 1)
	elif ed.tab.cursor_bar > ed.last_visible_bar:
		ed.move_cursor(ed.last_visible_bar, 1)
	else:
		ed.move_cursor()

# Page-Up
def scroll_bars_backward(ed, num):
	if num:
		scroll_bars(ed, -num)
	else:
		scroll_bars(ed, -1)

# TODO: I, A, gg

def set_bar_meter(ed, params):
	try:
		curb = ed.tab.get_cursor_bar()
		curb.sig_num, curb.sig_den = int(params[1]), int(params[2])
		ed.redraw_view()
	except:
		ed.st = 'Invalid argument'

def set_insert_duration(ed, params):
	try:
		ed.insert_duration = Fraction(int(params[1]), int(params[2]))
	except:
		ed.st = 'Invalid argument'

def edit_file(ed, params):
	try:
		ed.load_tablature(params[1])
		ed.move_cursor()
		ed.redraw_view()
	except IndexError:
		ed.st = 'File name not specified'

def write_file(ed, params):
	try:
		ed.save_tablature(params[1])
	except IndexError:
		if ed.file_name:
			ed.save_tablature(ed.file_name)
		else:
			ed.st = 'File name not specified'

def quit(ed, params):
	ed.terminate = True

def exec_python(ed, params):
	'''Execute a python expression from the command line'''
	exec string.join(params[1:], ' ') in {'ed':ed}

def map_commands(ed):
	ed.nmap[ord('i')] = insert
	ed.nmap[ord('a')] = append
	ed.nmap[ord('x')] = delete_chord
	ed.nmap[ord('q')] = set_duration
	ed.nmap[ord('Q')] = increase_duration
	ed.nmap[ord('o')] = append_bar
	ed.nmap[ord('O')] = insert_bar
	ed.nmap[ord('G')] = go_end
	ed.nmap[ord('0')] = go_bar_beg
	ed.nmap[ord('$')] = go_bar_end
	ed.nmap[ord('I')] = insert_at_beg
	ed.nmap[ord('A')] = append_at_end
	ed.nmap[curses.KEY_NPAGE] = scroll_bars
	ed.nmap[curses.KEY_PPAGE] = scroll_bars_backward
	ed.nmap[ord('s')] = set_chord
	ed.nmap[ord('h')] = ed.nmap[curses.KEY_LEFT] = \
			lambda ed, num: ed.move_cursor_left()
	ed.nmap[ord('l')] = ed.nmap[curses.KEY_RIGHT] = \
			lambda ed, num: ed.move_cursor_right()
	ed.nmap[ord('j')] = ed.nmap[curses.KEY_DOWN] = go_next_bar
	ed.nmap[ord('k')] = ed.nmap[curses.KEY_UP] = go_prev_bar
	ed.nmap[ord(':')] = lambda ed, num: ed.command_mode()
	
	ed.commands['meter'] = set_bar_meter
	ed.commands['ilen'] = set_insert_duration
	ed.commands['python'] = exec_python

	ed.commands['e'] = edit_file
	ed.commands['w'] = write_file
	ed.commands['q'] = quit
