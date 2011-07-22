from fractions import Fraction
from tablature import chord, bar, tablature

# a
def append(ed, num):
	ed.tab.get_cursor_bar().chords.insert(ed.tab.cursor_chord, chord())
	ed.move_cursor(new_chord = ed.tab.cursor_chord + 1, cache_lengths = False)
	ed.redraw_view()
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

# l
def set_duration(ed, num_arg):
	curch = ed.tab.get_cursor_chord()
	if num_arg:
		curch.duration = Fraction(1, num_arg)
	else:
		curch.duration = curch.duration * Fraction('1/2')
	ed.move_cursor()
	ed.redraw_view()

# L
def increase_duration(ed, num):
	curch = ed.tab.get_cursor_chord()
	curch.duration = curch.duration * 2
	ed.move_cursor()
	ed.redraw_view()

# o
def append_bar(ed, num):
	ed.tab.bars.insert(ed.tab.cursor_bar, bar())
	ed.move_cursor(ed.tab.cursor_bar + 1, 1)
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
	ed.move_cursor(new_chord = 1)

# $
def go_bar_end(ed, num):
	ed.move_cursor(new_chord = len(ed.tab.get_cursor_bar().chords))

# TODO: 0, $, I, A, O, gg

def map_commands(ed):
	ed.nmap[ord('a')] = append
	ed.nmap[ord('x')] = delete_chord
	ed.nmap[ord('l')] = set_duration
	ed.nmap[ord('L')] = increase_duration
	ed.nmap[ord('o')] = append_bar
	ed.nmap[ord('G')] = go_end
	ed.nmap[ord('0')] = go_bar_beg
	ed.nmap[ord('$')] = go_bar_end
