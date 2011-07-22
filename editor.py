import curses
import pickle
import os
import os.path

from fractions import Fraction
from tablature import chord, bar, tablature

class editor:
	cursor_prev_bar_x = 2
	insert_duration = Fraction('1/4')
	st = ''
	file_name = None
	terminate = False

	def __init__(self, stdscr, tab = tablature()):
		screen_height, screen_width = stdscr.getmaxyx()
		self.root = stdscr
		self.stdscr = curses.newwin(screen_height - 1, 0, 0, 0)
		self.stdscr.keypad(1)
		self.tab = tab
		self.nmap = {}
		self.commands = {}
		
		self.set_term_title('VITABS')
		self.status_line = curses.newwin(0, 0, screen_height - 1, 0)
		self.status_line.scrollok(False)

		self.redraw_view()
		self.cy = 2
		self.move_cursor(1,1)
		curses.doupdate()

	#def add_normal_maps(self, nmaps):
	#	

	def load_tablature(self, filename):
		try:
			if os.path.isfile(filename):
				infile = open(filename, 'rb')
				self.tab = pickle.load(infile)
				infile.close()
			else:
				self.tab = tablature()
			self.file_name = filename
			self.set_term_title(filename + ' - VITABS')
		except:
			self.st = 'Error: Can\'t open the specified file'

	def save_tablature(self, filename):
		try:
			outfile = open(filename, 'wb')
			pickle.dump(self.tab, outfile)
			outfile.close()
			self.file_name = filename
		except:
			self.st = 'Error: Can\'t save'
		self.set_term_title(filename + ' - VITABS')
	
	def set_term_title(self, text):
		try:
			term = os.environ['TERM'] 
			if 'xterm' in term or 'rxvt' in term:
				print '\033]0;' + text + '\007'
		except:
			pass

	def draw_bar(self, y, x, bar):
		'''Render a single bar at specified position'''
		stdscr = self.stdscr
		stdscr.vline(y, x-1, curses.ACS_VLINE, 6)
		gcd = bar.gcd()
		total_width = bar.total_width(gcd)
		#stdscr.attron(curses.A_REVERSE)
		for i in range(6):
			stdscr.hline(y+i, x, curses.ACS_HLINE, total_width)
		#stdscr.attroff(curses.A_REVERSE)
		x = x + 1
		for chord in bar.chords:
			for i in chord.strings.keys():
				stdscr.addstr(y+i, x, str(chord.strings[i]), curses.A_BOLD)
			width = int(chord.duration / gcd)
			x = x + width*2 + 1
		stdscr.vline(y, x+1, curses.ACS_VLINE, 6)
		return x+2

	def draw_bar_meta(self, y, x, bar, prev_bar):
		'''Print additional bar info at specified position'''
		if (prev_bar == None 
				or bar.sig_num != prev_bar.sig_num 
				or bar.sig_den != prev_bar.sig_den):
			self.stdscr.addstr(y, x, str(bar.sig_num) + '/' + str(bar.sig_den))

	def draw_tab(self, t):
		'''Render the whole tablature'''
		x = 2
		y = 1
		prev_bar = None
		screen_height, screen_width = self.stdscr.getmaxyx()
		for tbar in t.bars:
			bar_width = tbar.total_width(tbar.gcd())
			if bar_width >= screen_width - 2:
				# should split the bar
				self.st = 'bar too long, not displaying'
			else:
				if x + bar_width >= screen_width:
					x = 2
					y = y + 8
				if y > screen_height:
							break
				self.draw_bar_meta(y, x, tbar, prev_bar) 
				x = self.draw_bar(y+1, x, tbar)
			prev_bar = tbar
	
	def redraw_view(self):
		'''Redraw tab window'''
		self.stdscr.erase()
		self.draw_tab(self.tab) # merge theese functions?
		self.stdscr.noutrefresh()
	
	def term_resized(self):
		height, width = self.root.getmaxyx()
		self.status_line.mvwin(height - 1, 0)
		self.stdscr.resize(height - 1, width)
		self.redraw_view()
	
	def redraw_status(self):
		'''Update status bar'''
		width = self.status_line.getmaxyx()[1]
		self.status_line.erase()
		# general purpose status line
		self.status_line.addstr(0, 0, self.st)
		# position indicator
		self.status_line.addstr(0, width - 8, 
				 '{0},{1}'.format(self.tab.cursor_bar, self.tab.cursor_chord))
		self.status_line.addstr(0, width - 16,
				str(self.tab.get_cursor_chord().duration))
		# meter incomplete indicator
		cb = self.tab.get_cursor_bar()
		if cb.real_duration() != cb.required_duration():
			self.status_line.addstr(0, width - 18, 'M')
		self.status_line.noutrefresh()

	def move_cursor(self, new_bar=None, new_chord=None, cache_lengths=False):
		'''Set new cursor position'''
		if not new_bar: new_bar = self.tab.cursor_bar
		if not new_chord: new_chord = self.tab.cursor_chord
		if not cache_lengths: self.cursor_prev_bar_x = None

		#self.st = "move to bar " + str(new_bar) + " chord " + str(new_chord)

		# calculate the width of preceeding bars
		screen_height, screen_width = self.stdscr.getmaxyx()
		if new_bar != self.tab.cursor_bar or self.cursor_prev_bar_x == None:
			self.cursor_prev_bar_x = 2
			self.cy = 2
			i = 1
			for b in self.tab.bars:
				barw = b.total_width(b.gcd()) + 1
				if self.cursor_prev_bar_x + barw > screen_width:
					self.cursor_prev_bar_x = 2
					self.cy = self.cy + 8

				if i >= new_bar: 
					break

				if self.cursor_prev_bar_x + barw <= screen_width:
					self.cursor_prev_bar_x = self.cursor_prev_bar_x + barw
				i = i + 1

		# width of preceeding chords
		offset = 1
		i = 1
		b = self.tab.bars[new_bar - 1]
		gcd = b.gcd()
		for c in b.chords:
			if i >= new_chord:
				break
			offset = offset + int(c.duration / gcd)*2 + 1
			i = i + 1

		self.tab.cursor_bar = new_bar
		self.tab.cursor_chord = new_chord
		self.cx = self.cursor_prev_bar_x + offset

	def move_cursor_left(self):
		if self.tab.cursor_chord == 1:
			if self.tab.cursor_bar > 1:
				self.move_cursor(self.tab.cursor_bar-1, 
						len(self.tab.bars[self.tab.cursor_bar-2].chords),
						cache_lengths=True)
		else:
			self.move_cursor(self.tab.cursor_bar, self.tab.cursor_chord-1,
					cache_lengths=True)	
	
	def move_cursor_right(self):
		if self.tab.cursor_chord == len(self.tab.get_cursor_bar().chords):
			if self.tab.cursor_bar < len(self.tab.bars):
				self.move_cursor(self.tab.cursor_bar+1, 1, cache_lengths=True)
		else:
			self.move_cursor(self.tab.cursor_bar, self.tab.cursor_chord+1, 
					cache_lengths=True)
	
	def insert_mode(self):
		'''Switch to insert mode and listen for keys'''
		string = 0
		self.st = '-- INSERT --'
		while True:
			self.redraw_status()
			curses.setsyx(self.cy + string, self.cx)
			curses.doupdate()
			c = self.stdscr.getch()
			if c == 27: # ESCAPE
				self.st = ''
				break
			elif c == curses.KEY_RESIZE:
				self.term_resized()
			elif c in range( ord('0'), ord('9')+1 ):
				curch = self.tab.get_cursor_chord()
				if string in curch.strings and curch.strings[string] < 10:
					st_dec = curch.strings[string] * 10 
					curch.strings[string] = st_dec + c - ord('0')
				else:
					curch.strings[string] = c - ord('0')
				self.redraw_view()
			elif c == curses.KEY_DC:
				if self.tab.get_cursor_chord().strings[string]:
					del self.tab.get_cursor_chord().strings[string]
					self.redraw_view()
			elif c == curses.KEY_UP:
				string = max(string - 1, 0)
			elif c == curses.KEY_DOWN:
				string = min(string + 1, 5)
			elif c == curses.KEY_RIGHT:
				self.tab.get_cursor_bar().chords.insert(
						self.tab.cursor_chord, chord(self.insert_duration))
				self.move_cursor(new_chord = self.tab.cursor_chord + 1)
				self.redraw_view()

	def command_mode(self):
		'''Read a command'''
		curses.echo()
		self.status_line.erase()
		self.status_line.addstr(0, 0, ":")
		line = self.status_line.getstr(0, 1) 
		words = line.split(' ')
		cmd = words[0]
		curses.noecho()
		# scrolling bug
		self.stdscr.clear()
		self.redraw_view()
		try:
			self.commands[cmd](self, words)
		except KeyError:
			self.st = 'Invalid command'

	def normal_mode(self):
		'''Enter normal mode, returns on quit'''
		num_arg = None
		t = self.tab

		while True:
			if self.terminate:
				break

			self.redraw_status()
			self.st = ''
			curses.setsyx(self.cy, self.cx)
			curses.doupdate()
			# TODO: accept multi-char commands
			c = self.stdscr.getch()

			if c == curses.KEY_RESIZE:
				self.term_resized()
				
			if c in self.nmap:
				self.nmap[c](self, num_arg)

			if c in range( ord('0'), ord('9') ):
				# read a numeric argument
				if num_arg:
					num_arg = num_arg*10 + c - ord('0')
					self.st = str(num_arg)
				elif c != ord('0'):
					num_arg = c - ord('0')
					self.st = str(num_arg)
			else:
				# reset after a command
				num_arg = None

			if c == 27: # ESCAPE
				self.st = ''

			if c == ord('?'): self.st = self.stdscr.getkey()
