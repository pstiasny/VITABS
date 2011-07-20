import curses

from fractions import Fraction
from tablature import chord, bar, tablature

class editor:
	cursor_prev_bar_x = 2
	st = ''

	def __init__(self, stdscr, tab = tablature()):
		self.stdscr = stdscr
		self.tab = tab
		self.nmap = {}
		
		print '\033]0;' + 'VITABS' + '\007' # set xterm title
		self.status_line = curses.newwin(0, 0, stdscr.getmaxyx()[0]-1, 0)

		self.redraw_view()
		self.move_cursor(1,1)
		curses.doupdate()

	#def add_normal_maps(self, nmaps):
	#	

	def draw_bar(self, y, x, bar):
		'''Render a single bar at specified position'''
		stdscr = self.stdscr
		stdscr.vline(y, x-1, curses.ACS_VLINE, 6)
		gcd = bar.gcd()
		total_width = bar.total_width(gcd)
		for i in range(6):
			stdscr.hline(y+i, x, curses.ACS_HLINE, total_width)
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
		self.stdscr.clear()
		self.draw_tab(self.tab) # merge theese functions?
		self.stdscr.noutrefresh()

	def move_cursor(self, new_bar=None, new_chord=None):
		'''Set new cursor position'''
		if not new_bar: new_bar = self.tab.cursor_bar
		if not new_chord: new_chord = self.tab.cursor_chord
		self.st = "move to bar " + str(new_bar) + " chord " + str(new_chord)
		if new_bar != self.tab.cursor_bar or self.cursor_prev_bar_x == None:
			self.cursor_prev_bar_x = 2
			i = 1
			for b in self.tab.bars:
				if i >= new_bar: 
					break
				self.cursor_prev_bar_x = self.cursor_prev_bar_x + b.total_width(b.gcd()) + 1
				i = i + 1
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
		self.cy = 2
		self.cx = self.cursor_prev_bar_x + offset

	def move_cursor_left(self):
		if self.tab.cursor_chord == 1:
			if self.tab.cursor_bar > 1:
				self.move_cursor(self.tab.cursor_bar-1, 
						len(self.tab.bars[self.tab.cursor_bar-2].chords))
		else:
			self.move_cursor(self.tab.cursor_bar, self.tab.cursor_chord-1)	
	
	def move_cursor_right(self):
		if self.tab.cursor_chord == len(self.tab.get_cursor_bar().chords):
			if self.tab.cursor_bar < len(self.tab.bars):
				self.move_cursor(self.tab.cursor_bar+1, 1)
		else:
			self.move_cursor(self.tab.cursor_bar, self.tab.cursor_chord+1)
	
	def insert_mode(self):
		'''Switch to insert mode and listen for keys'''
		string = 0
		while True:
			curses.setsyx(self.cy + string, self.cx)
			curses.doupdate()
			c = self.stdscr.getch()
			if c == 27: # ESCAPE
				break
			if c in range( ord('0'), ord('9')+1 ):
				curch = self.tab.get_cursor_chord()
				if string in curch.strings and curch.strings[string] < 10:
					st_dec = curch.strings[string] * 10 
					curch.strings[string] = st_dec + c - ord('0')
				else:
					curch.strings[string] = c - ord('0')
				self.redraw_view()
			if c == curses.KEY_DC:
				if self.tab.get_cursor_chord().strings[string]:
					del self.tab.get_cursor_chord().strings[string]
					self.redraw_view()
			if c == curses.KEY_UP:
				string = max(string - 1, 0)
			if c == curses.KEY_DOWN:
				string = min(string + 1, 5)

	def command_mode(self):
		'''Read a command'''
		# TODO: actual commands
		curses.echo()
		self.status_line.clear()
		self.status_line.addstr(0, 0, ":")
		st = self.status_line.getstr(0, 1)
		curses.noecho()
		self.st = st

	def normal_mode(self):
		'''Enter normal mode, returns on quit'''
		num_arg = None
		t = self.tab

		while True:
			self.status_line.clear()
			self.status_line.addstr(0, 0, self.st)
			self.status_line.noutrefresh()
			curses.setsyx(self.cy, self.cx)
			curses.doupdate()
			# TODO: accept multi-char commands
			c = self.stdscr.getch()

			if c in self.nmap:
				self.nmap[c](self, num_arg)

			elif c == curses.KEY_RIGHT or c == ord('l'): # l for length!
				self.move_cursor_right()
			elif c == curses.KEY_LEFT or c == ord('h'):
				self.move_cursor_left()
			elif c == ord('q'):
				break
			elif c == ord(':'): 
				self.command_mode()

			if c in range( ord('0'), ord('9') ):
				# read a numeric argument
				if num_arg:
					num_arg = num_arg*10 + c - ord('0')
				else:
					num_arg = c - ord('0')
				self.st = str(num_arg)
			else:
				# reset after a command
				num_arg = None

			if c == 27: # ESCAPE
				st = ''
