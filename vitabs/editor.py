# Copyright (C) 2011  Pawel Stiasny

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import curses
import pickle
import os
import os.path

from fractions import Fraction
from tablature import Fret, Chord, Bar, Tablature, ChordRange
import symbols
import music
from player import Player

class Editor:
    screen_initiated = False
    cursor_prev_bar_x = 2
    insert_duration = Fraction('1/4')
    st = ''
    file_name = None
    terminate = False
    visible_meta = 'meter'
    continuous_playback = False
    yanked_bar = None
    string = 0

    def __init__(self, stdscr, tab = Tablature()):
        self.root = stdscr
        self.tab = tab
        self.nmap = {}
        self.motion_commands = {}
        self.commands = {}

        self.player = Player()

    def init_screen(self):
        screen_height, screen_width = self.root.getmaxyx()
        self.stdscr = curses.newwin(screen_height - 1, 0, 0, 0)
        self.stdscr.keypad(1)

        if self.file_name:
            self.set_term_title(self.file_name + ' - VITABS')
        else:
            self.set_term_title('[unnamed] - VITABS')

        self.status_line = curses.newwin(0, 0, screen_height - 1, 0)
        self.status_line.scrollok(False)

        self.first_visible_bar = self.tab.cursor_bar
        self.redraw_view()
        self.cy = 2
        self.move_cursor()
        curses.doupdate()

        self.screen_initiated = True
    
    def make_motion_cmd(self, f):
        '''Turn a motion command into a normal mode command'''
        def motion_wrap(ed, num):
            m = f(ed, num)
            if m is not None:
                ed.make_motion(f(ed, num))
        motion_wrap.__name__ = f.__name__
        motion_wrap.__doc__ = f.__doc__
        motion_wrap.nosidefx = True
        return motion_wrap

    def mark_changed(self):
        if not getattr(self.tab, 'changed', False):
            if self.file_name:
                self.set_term_title(self.file_name + ' + - VITABS')
            else:
                self.set_term_title('[unnamed] + - VITABS')
        self.tab.changed = True

    def register_handlers(self, module):
        '''Add commands defined in the module'''
        for f in module.__dict__.itervalues():
            if hasattr(f, 'normal_keys'):
                if getattr(f, 'motion_command', False):
                    for k in f.normal_keys:
                        self.nmap[k] = self.make_motion_cmd(f)
                        self.motion_commands[k] = f
                else:
                    for k in f.normal_keys:
                        self.nmap[k] = f
            if hasattr(f, 'handles_command'):
                self.commands[f.handles_command] = f
            
    def load_tablature(self, filename):
        '''Unpickle tab from a file'''
        try:
            if os.path.isfile(filename):
                infile = open(filename, 'rb')
                self.tab = pickle.load(infile)
                infile.close()
            else:
                self.tab = Tablature()
            self.file_name = filename
            self.set_term_title(filename + ' - VITABS')
            self.st = '{0} ({1} bars, tuning: {2})'.format(
                filename, len(self.tab.bars),
                music.tuning_str(getattr(self.tab, 'tuning', music.standard_E)))
        except:
            self.st = 'Error: Can\'t open the specified file'

    def save_tablature(self, filename):
        '''Pickle tab to a file'''
        if hasattr(self.tab, 'changed'):
            self.tab.changed = False
            delattr(self.tab, 'changed')
        try:
            outfile = open(filename, 'wb')
            pickle.dump(self.tab, outfile)
            outfile.close()
            self.file_name = filename
        except:
            self.st = 'Error: Can\'t save'
        self.set_term_title(filename + ' - VITABS')
    
    def set_term_title(self, text):
        '''Atempt to change virtual terminal window title'''
        import sys
        try:
            term = os.environ['TERM'] 
            if 'xterm' in term or 'rxvt' in term:
                sys.stdout.write('\033]0;' + text + '\007')
                sys.stdout.flush()
        except:
            pass

    def draw_bar(self, y, x, bar):
        '''Render a single bar at specified position'''
        stdscr = self.stdscr
        screen_width = self.stdscr.getmaxyx()[1]
        stdscr.vline(y, x - 1, curses.ACS_VLINE, 6)
        gcd = bar.gcd()
        total_width = bar.total_width(gcd)
        for i in range(6):
            stdscr.hline(y + i, x, curses.ACS_HLINE, total_width)
        x += 1
        for chord in bar.chords:
            for i in chord.strings.keys():
                if x < screen_width:
                    stdscr.addstr(y+i, x, str(chord.strings[i]), curses.A_BOLD)
            # should it really be here?
            if self.visible_meta == 'length':
                dstr = music.len_str(chord.duration)
                if x + len(dstr) < screen_width:
                    stdscr.addstr(y - 1, x, dstr)
            width = int(chord.duration / gcd)
            x = x + width*2 + 1
        if x + 1 < screen_width:
            stdscr.vline(y, x + 1, curses.ACS_VLINE, 6)
        return x + 2

    def draw_bar_meta(self, y, x, bar, prev_bar, index):
        '''Print additional bar info at specified position'''
        if self.visible_meta == 'meter':
            if (prev_bar == None 
                    or bar.sig_num != prev_bar.sig_num 
                    or bar.sig_den != prev_bar.sig_den):
                self.stdscr.addstr(
                    y, x, 
                    str(bar.sig_num) + '/' + str(bar.sig_den))
        elif self.visible_meta == 'number':
            self.stdscr.addstr(y, x, str(index))
        elif self.visible_meta == 'label':
            if hasattr(bar, 'label'):
                self.stdscr.addstr(y, x, bar.label)

    def draw_tab(self, t):
        '''Render the whole tablature'''
        x = 2
        y = 1
        prev_bar = None
        screen_height, screen_width = self.stdscr.getmaxyx()
        for i, tbar in enumerate(t.bars[self.first_visible_bar - 1 : ]):
            bar_width = tbar.total_width(tbar.gcd())
            if x + bar_width >= screen_width and x != 2:
                x = 2
                y += 8
            if y + 8 > screen_height:
                break
            self.draw_bar_meta(y, x, tbar, prev_bar, self.first_visible_bar + i)
            x = self.draw_bar(y + 1, x, tbar)
            self.last_visible_bar = i + self.first_visible_bar

            prev_bar = tbar
    
    def redraw_view(self):
        '''Redraw tab window'''
        self.stdscr.erase()
        self.draw_tab(self.tab) # merge theese functions?
        self.stdscr.noutrefresh()
    
    def term_resized(self):
        '''Called when the terminal window is resized, updates window sizes'''
        height, width = self.root.getmaxyx()
        self.status_line.mvwin(height - 1, 0)
        self.stdscr.resize(height - 1, width)
        self.redraw_view()
        self.move_cursor()
    
    def redraw_status(self):
        '''Update status bar'''
        width = self.status_line.getmaxyx()[1]
        self.status_line.erase()
        # general purpose status line
        self.status_line.addstr(0, 0, self.st)
        # position indicator
        self.status_line.addstr(
            0, width - 8, 
            '{0},{1}'.format(self.tab.cursor_bar, self.tab.cursor_chord))
        # note length indicator
        self.status_line.addstr(
            0, width - 16,
            str(self.tab.get_cursor_chord().duration))
        # meter incomplete indicator
        cb = self.tab.get_cursor_bar()
        if cb.real_duration() != cb.required_duration():
            self.status_line.addstr(0, width - 18, 'M')
        self.status_line.noutrefresh()

    def pager(self, lines):
        '''Display a list of lines in a paged fashion'''
        self.root.scrollok(True)
        self.root.clear()
        i = 0
        h = self.root.getmaxyx()[0]
        for line in lines:
            self.root.addstr(i, 1, line)
            i += 1
            if i == h - 1:
                self.root.addstr(i, 0, '<Space> NEXT PAGE')
                self.root.refresh()
                while self.get_char() != ord(' '): pass
                self.root.clear()
                i = 0
        self.root.addstr(h - 1, 0, '<Space> CONTINUE')
        while self.get_char(self.root) != ord(' '): pass
        self.root.scrollok(False)
        self.root.clear()
        self.redraw_view()

    def move_cursor(self, new_bar=None, new_chord=None, cache_lengths=False):
        '''Set new cursor position'''
        if not new_bar: new_bar = self.tab.cursor_bar
        if not new_chord: new_chord = self.tab.cursor_chord
        if not cache_lengths: self.cursor_prev_bar_x = None

        # make sure the cursor stays inside the visible bar range
        if new_bar < self.first_visible_bar or new_bar > self.last_visible_bar:
            self.first_visible_bar = new_bar
            self.redraw_view()

        newbar_i = self.tab.bars[new_bar - 1]
        
        # calculate the width of preceeding bars
        screen_height, screen_width = self.stdscr.getmaxyx()
        if new_bar != self.tab.cursor_bar or self.cursor_prev_bar_x == None:
            self.cursor_prev_bar_x = 2
            self.cy = 2
            if new_bar > self.first_visible_bar:
                for b in self.tab.bars[self.first_visible_bar - 1 : new_bar - 1]:
                    barw = b.total_width(b.gcd()) + 1

                    self.cursor_prev_bar_x += barw

                    if (self.cursor_prev_bar_x > screen_width and
                            self.cursor_prev_bar_x != 2 + barw):
                        self.cursor_prev_bar_x = 2 + barw
                        self.cy += 8

                # should the cursor bar be wrapped?
                newbar_w = newbar_i.total_width(newbar_i.gcd()) + 1
                if newbar_w + self.cursor_prev_bar_x > screen_width:
                    self.cursor_prev_bar_x = 2
                    self.cy += 8

        # width of preceeding chords
        offset = 1
        gcd = newbar_i.gcd()
        for c in newbar_i.chords[:new_chord - 1]:
            offset += int(c.duration / gcd)*2 + 1

        self.tab.cursor_bar = new_bar
        self.tab.cursor_chord = new_chord
        self.cx = self.cursor_prev_bar_x + offset
    
    def make_motion(self, pos):
        self.move_cursor(pos[0], 1 if pos[1] is None else pos[1],
                         cache_lengths=True)

    def go_left(self, num=1):
        '''Returns position pair [num] chords left from the cursor'''
        if self.tab.cursor_chord <= num:
            if self.tab.cursor_bar > 1:
                return (self.tab.cursor_bar - 1, 
                        len(self.tab.bars[self.tab.cursor_bar - 2].chords))
            else:
                return (1, 1)
        else:
            return (self.tab.cursor_bar, self.tab.cursor_chord - num)

    def move_cursor_left(self):
        self.make_motion(self.go_left())

    def go_right(self, num=1):
        '''Returns position pair [num] chords right from the cursor'''
        if self.tab.cursor_chord + num > len(self.tab.get_cursor_bar().chords):
            if self.tab.cursor_bar < len(self.tab.bars):
                return (self.tab.cursor_bar + 1, 1)
            else:
                return self.tab.last_position()
        else:
            return (self.tab.cursor_bar, self.tab.cursor_chord + num)

    def move_cursor_right(self):
        self.make_motion(self.go_right())
    
    def play_range(self, fro, to):
        def redraw_playback_status():
            self.st = 'Playing... <CTRL-C> to abort'
            self.redraw_status()
            curses.setsyx(self.cy - 1, self.cx)
            curses.doupdate()

        def move_to_beginning():
            self.move_cursor(fro[0], fro[1])
            redraw_playback_status()
            return True

        def update_playback_status():
            self.move_cursor_right()
            redraw_playback_status()
            return True

        p = self.player
        p.before_repeat = move_to_beginning
        p.post_play_chord = update_playback_status
        p.set_instrument(getattr(self.tab, 'instrument', 24))
        p.play(ChordRange(self.tab, fro, to), self.continuous_playback)
        self.st = ''

    def get_char(self, parent=None):
        '''Get a character from terminal, handling things like terminal
        resize'''
        if parent is None:
            parent = self.stdscr
        c = parent.getch()
        if c == curses.KEY_RESIZE:
            self.term_resized()
        return c

    def insert_mode(self, free_motion=False):
        '''Switch to insert mode and listen for keys'''
        if free_motion:
            self.st = '-- REPLACE --'
        else:
            self.st = '-- INSERT --'

        self.redraw_view()

        insert_beg = self.tab.cursor_position()
        insert_end = insert_beg

        while True:
            self.redraw_status()
            curses.setsyx(self.cy + self.string, self.cx)
            curses.doupdate()

            c = self.get_char()
            if c == 27: # ESCAPE
                self.st = ''
                break

            elif ord('0') <= c <= ord('9'):
                curch = self.tab.get_cursor_chord()
                string = self.string
                if string in curch.strings and curch.strings[string].fret < 10:
                    st_dec = curch.strings[string].fret * 10 
                    curch.strings[string].fret = st_dec + c - ord('0')
                else:
                    curch.strings[string] = Fret(c - ord('0'))
                self.redraw_view()
            elif c == curses.KEY_DC or c == ord('x'):
                if self.string in self.tab.get_cursor_chord().strings:
                    del self.tab.get_cursor_chord().strings[self.string]
                    self.redraw_view()

            elif c == curses.KEY_UP or c == ord('k'):
                self.string = max(self.string - 1, 0)
            elif c == curses.KEY_DOWN or c == ord('j'):
                self.string = min(self.string + 1, 5)
            elif c == ord('E'): self.string = 5
            elif c == ord('A'): self.string = 4
            elif c == ord('D'): self.string = 3
            elif c == ord('G'): self.string = 2
            elif c == ord('B'): self.string = 1
            elif c == ord('e'): self.string = 0

            elif c == ord(' '):
                # TODO: don't repeat yourself...
                self.tab.get_cursor_bar().chords.insert(
                        self.tab.cursor_chord, 
                        Chord(self.insert_duration))
                self.redraw_view()
                self.move_cursor_right()
                self.move_cursor()
                insert_end = (insert_end[0], insert_end[1] + 1)

            elif (c == curses.KEY_RIGHT or c == ord('l')) and not free_motion:
                right = (self.tab.cursor_bar, self.tab.cursor_chord + 1)
                if right > insert_end:
                    self.tab.get_cursor_bar().chords.insert(
                            self.tab.cursor_chord, 
                            Chord(self.insert_duration))
                    self.redraw_view()
                    insert_end = right
                self.make_motion(right)
                self.move_cursor()

            elif (c == curses.KEY_LEFT or c == ord('h')) and not free_motion:
                left = self.go_left()
                if left >= insert_beg:
                    self.make_motion(left)

            elif c == curses.KEY_RIGHT or c == ord('l') and free_motion:
                self.move_cursor_right()

            elif (c == curses.KEY_LEFT or c == ord('h')) and free_motion:
                self.move_cursor_left()

            try:
                # try to find a symbol in key -> symbol dict
                sym = symbols.keys[c]
                fr = self.tab.get_cursor_chord().strings[self.string]
                if sym in fr.symbols:
                    fr.symbols.remove(sym)
                else:
                    fr.symbols.append(sym)
                self.redraw_view()
            except KeyError:
                pass

    def exec_command(self, args, apply_to=None):
        cmd = args[0]
        try:
            if apply_to is not None:
                try:
                    self.commands[cmd](self, args, apply_to=apply_to)
                except TypeError:
                    self.st = 'Command does not accept range'
            else:
                self.commands[cmd](self, args)
        except KeyError:
            self.st = 'Invalid command'

    def command_mode(self):
        '''Read a command'''
        import sys
        curses.echo()
        self.status_line.erase()
        self.status_line.addstr(0, 0, ":")
        try:
            line = self.status_line.getstr(0, 1) 
        except KeyboardInterrupt:
            line = ''
        words = line.split(' ')
        cmd = words[0]
        curses.noecho()
        if cmd:
            try:
                self.exec_command(words)
            except:
                exc = sys.exc_info()
                self.st = "Exception: " + str(exc[0].__name__) + ": " + \
                str(exc[1])
        self.redraw_view()

    def _is_number(self, char):
        return (ord('0') <= char <= ord('9'))
    
    def _parse_numeric_arg(self, c, num_arg):
        if num_arg:
            num_arg = num_arg * 10 + c - ord('0')
        elif c != ord('0'):
            num_arg = c - ord('0')
        return num_arg

    def expect_range(self, num=None, whole_bar_cmd=None):
        '''Get a motion command and return a range from cursor position to
           motion'''
        num_motion = None
        c = self.get_char()
        while self._is_number(c) and (c != ord('0') or num_motion):
            num_motion = self._parse_numeric_arg(c, num_motion)
            c = self.get_char()
        if num_motion and num: total_num = num * num_motion
        elif num_motion: total_num = num_motion
        else: total_num = num

        cur = self.tab.cursor_position()
        if whole_bar_cmd and c == whole_bar_cmd:
            return ChordRange(self.tab,
                    (cur[0], 1),
                    (cur[0], None))
        try:
            dest = self.motion_commands[c](self, total_num)
            if dest:
                if dest > cur:
                    return ChordRange(self.tab, cur, dest)
                else:
                    return ChordRange(self.tab, dest, cur)
        except KeyError:
            return None

    def normal_mode(self):
        '''Enter normal mode, returns on quit'''
        num_arg = None
        t = self.tab
        
        while True:
            if self.terminate:
                break

            self.redraw_status()
            self.st = ''
            curses.setsyx(self.cy - 1, self.cx)
            curses.doupdate()
            # TODO: accept multi-char commands
            try:
                c = self.get_char()

                if c in self.nmap:
                    cmd = self.nmap[c]
                    cmd(self, num_arg)
                    if not (getattr(cmd, 'nosidefx', False)):
                        self.mark_changed()
                        self.redraw_view()

                if self._is_number(c):
                    num_arg = self._parse_numeric_arg(c, num_arg)
                    if num_arg: self.st = str(num_arg)
                else:
                    # reset after a command
                    num_arg = None

                if c == 27: # ESCAPE
                    self.st = ''

            except KeyboardInterrupt:
                self.st = 'Use :q<Enter> to quit'
