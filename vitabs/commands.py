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

from fractions import Fraction
from tablature import Chord, Bar, Tablature, ChordRange, parse_position
import music
import string
import curses # KEY_*

def nmap_char(key):
    return nmap_key(ord(key))

def nmap_key(key):
    def decorate(f):
        if hasattr(f, 'normal_keys'):
            f.normal_keys.append(key)
        else:
            f.normal_keys = [key]
        return f
    return decorate

def motion(f):
    '''Mark as a motion command. A motion command should return a pair of (bar,
       chord) numbers and have no side-effects.'''
    f.motion_command = True
    return f

def nosidefx(f):
    '''Mark a command that doesn't change the file - not necessary for motions'''
    f.nosidefx = True
    return f

def map_command(command):
    def decorate(f):
        f.handles_command = command
        return f
    return decorate

@nmap_char('i')
def insert(ed, num):
    '''Create a new chord before the cursor and enter insert mode'''
    ed.tab.get_cursor_bar().chords.insert(
        ed.tab.cursor_chord - 1, Chord(ed.insert_duration))
    ed.move_cursor(new_chord = max(ed.tab.cursor_chord, 1))
    ed.insert_mode()

@nmap_char('a')
def append(ed, num):
    '''Create a new chord after the cursor and enter insert mode'''
    ed.tab.get_cursor_bar().chords.insert(
        ed.tab.cursor_chord, Chord(ed.insert_duration))
    ed.move_cursor(new_chord = ed.tab.cursor_chord + 1)
    ed.insert_mode()

@nmap_char('s')
def set_chord(ed, num):
    '''Enter insert mode at current position'''
    ed.insert_mode(free_motion=True)

def after_delete(ed):
    '''Take care of empty lists'''
    t = ed.tab
    if not t.bars:
        # empty tab
        t.bars = [Bar(first_chord_len=ed.insert_duration)]
    if t.cursor_bar > len(t.bars):
        t.cursor_bar = len(t.bars)
        t.cursor_chord = len(t.bars[t.cursor_bar-1].chords)
    elif t.cursor_chord > len(t.bars[t.cursor_bar-1].chords):
        t.cursor_chord = len(t.bars[t.cursor_bar-1].chords)
    ed.move_cursor()

@nmap_char('d')
def delete(ed, num, rng = None):
    '''Delete over a motion'''
    if rng is None:
        rng = ed.expect_range(num, whole_bar_cmd = ord('d'))
    if rng:
        ed.make_motion(rng.beginning)
        rng.delete_all()
        after_delete(ed)

@nmap_char('D')
def delete_to_end(ed, num):
    '''Delete to the end of the bar, same as d$'''
    pos = ed.tab.cursor_position()
    delete(ed, num, ChordRange(ed.tab, pos, go_bar_end(ed, num)))

@nmap_char('c')
def change(ed, num, rng = None):
    '''Delete over a motion and enter insert mode'''
    if rng is None:
        rng = ed.expect_range(num, whole_bar_cmd = ord('c'))
    if rng:
        ed.make_motion(rng.beginning)
        if not rng.whole_bars():
            rng.delete_all()
            insert(ed, None)
        else:
            rng.delete_all()
            if not ed.tab.bars:
                ed.tab.bars = [Bar(first_chord_len=ed.insert_duration)]
                ed.insert_mode()
            elif ed.tab.cursor_bar > len(ed.tab.bars):
                # deleting a bar at the end of the tab
                ed.tab.cursor_bar = len(ed.tab.bars)
                append_bar(ed, None)
            else:
                insert_bar(ed, None)

@nmap_char('C')
def change_to_end(ed, num):
    '''Change to the end of the bar, same as c$'''
    pos = ed.tab.cursor_position()
    change(ed, num, ChordRange(ed.tab, pos, go_bar_end(ed, num)))

@nmap_char('y')
@nosidefx
def yank(ed, num):
    import copy
    ed.yanked_bar = copy.deepcopy(ed.tab.get_cursor_bar())

@nmap_char('p')
def paste(ed, num):
    import copy
    if ed.yanked_bar:
        ed.tab.bars.insert(ed.tab.cursor_bar, copy.deepcopy(ed.yanked_bar))

@nmap_char('x')
@nmap_key(curses.KEY_DC)
def delete_chord(ed, num):
    '''Delete at current cursor position'''
    t = ed.tab
    del t.get_cursor_bar().chords[t.cursor_chord-1]
    if not t.bars[t.cursor_bar-1].chords:
        del t.bars[t.cursor_bar-1]
    after_delete(ed)

@nmap_char('X')
def backwards_delete_chord(ed, num):
    '''Delete before current cursor position'''
    if ed.tab.cursor_chord > 1:
        ed.move_cursor_left()
        delete_chord(ed, num)

@nmap_char('q')
def set_duration(ed, num_arg):
    '''Decrease note length by half, with numeric argument set to 1/arg'''
    curch = ed.tab.get_cursor_chord()
    if num_arg:
        curch.duration = Fraction(1, num_arg)
    else:
        curch.duration = curch.duration * Fraction('1/2')
    ed.insert_duration = curch.duration
    ed.move_cursor()

@nmap_char('Q')
def increase_duration(ed, num):
    '''Increase note length twice'''
    curch = ed.tab.get_cursor_chord()
    curch.duration = curch.duration * 2
    ed.insert_duration = curch.duration
    ed.move_cursor()

@nmap_char('%')
def left_duration(ed, num):
    '''Apply duration of the chord to the left from the cursor and move right'''
    if ed.tab.cursor_chord > 1:
        ed.tab.get_cursor_chord().duration = \
                ed.tab.get_cursor_bar().chords[ed.tab.cursor_chord - 2].duration
        ed.move_cursor() # recalculate
    ed.move_cursor_right()

@nmap_char('o')
def append_bar(ed, num):
    '''Create a bar after the selected and enter insert mode'''
    curb = ed.tab.get_cursor_bar()
    bar = Bar(curb.sig_num, curb.sig_den)
    bar.chords[0].duration = ed.insert_duration
    ed.tab.bars.insert(ed.tab.cursor_bar, bar)
    ed.redraw_view() # necessery to calculate whether fits on page
    ed.move_cursor(ed.tab.cursor_bar + 1, 1)
    ed.insert_mode()

@nmap_char('O')
def insert_bar(ed, num):
    '''Create a bar before the selected and enter insert mode'''
    curb = ed.tab.get_cursor_bar()
    bar = Bar(curb.sig_num, curb.sig_den)
    bar.chords[0].duration = ed.insert_duration
    ed.tab.bars.insert(ed.tab.cursor_bar - 1, bar)
    ed.move_cursor(ed.tab.cursor_bar, 1)
    ed.insert_mode()

@nmap_char('G')
@motion
def go_end(ed, num):
    '''Go to last bar, with numeric argument go to the specified bar'''
    if num:
        return (min(len(ed.tab.bars), num), None)
    else:
        return (len(ed.tab.bars), None)

@nmap_char('g')
@motion
def go_beg(ed, num):
    return go_end(ed, 1)

@nmap_char('0')
@nmap_key(curses.KEY_HOME)
@motion
def go_bar_beg(ed, num):
    '''Go to the beginning of the bar'''
    if not num:
        # ed.move_cursor(new_chord = 1)
        return (ed.tab.cursor_bar, 1)

@nmap_char('$')
@nmap_key(curses.KEY_END)
@motion
def go_bar_end(ed, num):
    '''Go to the end of the bar'''
    return (ed.tab.cursor_bar, len(ed.tab.get_cursor_bar().chords))

@nmap_char('w')
@motion
def go_next_label(ed, num):
    '''Go to the next label'''
    pos = (len(ed.tab.bars), None)
    for barn in xrange(ed.tab.cursor_bar + 1, len(ed.tab.bars) + 1):
        if hasattr(ed.tab.bars[barn - 1], 'label'):
            pos = (barn, None)
            break
    return pos

@nmap_char('b')
@motion
def go_prev_label(ed, num):
    '''Go to the next label'''
    if hasattr(ed.tab.get_cursor_bar(), 'label') and ed.tab.cursor_chord == 1:
        search_range = xrange(1, ed.tab.cursor_bar)
    else:
        search_range = xrange(1, ed.tab.cursor_bar + 1)

    pos = (1, None)
    for barn in reversed(search_range):
        if hasattr(ed.tab.bars[barn - 1], 'label'):
            pos = (barn, None)
            break
    return pos

@nmap_char('I')
def insert_at_beg(ed, num):
    '''Enter insert mode at the beginning of the bar'''
    ed.make_motion(go_bar_beg(ed, None))
    insert(ed, num)

@nmap_char('A')
def append_at_end(ed, num):
    '''Enter insert mode at the end of the bar'''
    ed.make_motion(go_bar_end(ed, None))
    append(ed, num)

@nmap_char('J')
def join_bars(ed, num):
    '''Join current bar with the following'''
    if ed.tab.cursor_bar != len(ed.tab.bars):
        ed.tab.get_cursor_bar().chords.extend(
                ed.tab.bars[ed.tab.cursor_bar].chords)
        del ed.tab.bars[ed.tab.cursor_bar]

@nmap_char('|')
def split_bar(ed, num):
    '''Split bar after the cursor position'''
    cbar = ed.tab.get_cursor_bar()
    end_part = cbar.chords[ed.tab.cursor_chord : ]
    cbar.chords = cbar.chords[ : ed.tab.cursor_chord]
    new_bar = Bar(cbar.sig_num, cbar.sig_den)
    new_bar.chords = end_part
    ed.tab.bars.insert(ed.tab.cursor_bar, new_bar)

@nmap_char('j')
@nmap_key(curses.KEY_DOWN)
@motion
def go_next_bar(ed, num):
    if not num: num = 1
    return (min(len(ed.tab.bars), ed.tab.cursor_bar + num), None)

@nmap_char('k')
@nmap_key(curses.KEY_UP)
@motion
def go_prev_bar(ed, num):
    if not num: num = 1
    return (max(1, ed.tab.cursor_bar - num), 1)

@nmap_char('h')
@nmap_key(curses.KEY_LEFT)
@motion
def go_left(ed, num):
    if num is None:
        return ed.go_left()
    else:
        return ed.go_left(num)

@nmap_char('l')
@nmap_key(curses.KEY_RIGHT)
@motion
def go_right(ed, num): 
    if num is None:
        return ed.go_right()
    else:
        return ed.go_right(num)

@nmap_key(curses.KEY_NPAGE) # Page-Down
@nosidefx
def scroll_bars(ed, num):
    '''Scroll the screen by one bar'''
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

@nmap_key(curses.KEY_PPAGE) # Page-Up
@nosidefx
def scroll_bars_backward(ed, num):
    '''Scroll the screen by one bar backwards'''
    if num:
        scroll_bars(ed, -num)
    else:
        scroll_bars(ed, -1)

@nmap_char('r')
@nosidefx
def play(ed, num):
    '''Play over a motion'''
    r = ed.expect_range(num, whole_bar_cmd=ord('r'))
    if r:
        ed.play_range(r.beginning, r.end)

@nmap_char('E')
@nosidefx
def play_all(ed, num):
    ed.play_range((1,1), ed.tab.last_position())

@nmap_char('e')
@nosidefx
def play_to_end(ed, num):
    ed.play_range(ed.tab.cursor_position(), ed.tab.last_position())

@nmap_char('?')
@nosidefx
def display_nmaps(ed, num):
    def make_line():
        for c, f in ed.nmap.items():
            if f.__doc__:
                yield '{0}  {1}: {2}'.format(
                    curses.keyname(c), f.__name__, f.__doc__)
            else:
                yield '{0}  {1}'.format(
                    curses.keyname(c), f.__name__, f.__doc__)
    ed.pager(make_line())

@nmap_char(':')
@nosidefx
def enter_command_mode(ed, num):
    ed.command_mode()


@map_command('for')
def apply_to_range(ed, params):
    '''Apply a command to the specified chord range'''
    if len(params) < 4:
        ed.st = 'Not enough arguments'
    else:
        first = last = None
        try:
            first = parse_position(ed.tab, params[1])
            last = parse_position(ed.tab, params[2])
        except:
            ed.st = 'Invalid arguments'

        if first is not None and last is not None:
            r = ChordRange(ed.tab, first, last)
            ed.exec_command(params[3:], apply_to=r)

def find_label(ed, label):
    for i, b in enumerate(ed.tab.bars):
        if hasattr(b, 'label') and b.label == label:
            return (i + 1, None)
    return None

@map_command('label')
def set_bar_label(ed, params, apply_to=None):
    if len(params) == 2:
        l = find_label(ed, params[1])
        if l:
            ed.make_motion(l)
        else:
            ed.tab.get_cursor_bar().label = params[1]
    elif len(params) == 1:
        if hasattr(ed.tab.get_cursor_bar(), 'label'):
            ed.st = ed.tab.get_cursor_bar().label
        else:
            lpos = go_prev_label(ed, None)
            ed.st = getattr(ed.tab.bars[lpos[0] - 1], 'label', 'No label.')
    else:
        ed.st = 'Single word label required'

@map_command('nolabel')
def remove_bar_label(ed, params, apply_to=None):
    del ed.tab.get_cursor_bar().label

@map_command('meter')
def set_bar_meter(ed, params, apply_to=None):
    try:
        sig_num, sig_den = int(params[1]), int(params[2])
        if apply_to is None:
            curb = ed.tab.get_cursor_bar()
            curb.sig_num, curb.sig_den = sig_num, sig_den
        else:
            for b in apply_to.bars():
                b.sig_num, b.sig_den = sig_num, sig_den
    except:
        ed.st = 'Invalid argument'

@map_command('instrument')
def set_instrument(ed, params):
    instruments = {
        'classical' : 24,
        'accoustic' : 25,
        'jazz' : 26,
        'clean' : 27,
        'overdrive' : 29,
        'distortion' : 30
    }

    try:
        if params[1] in instruments:
            ed.tab.instrument = instruments[params[1]]
        else:
            ed.tab.instrument = int(params[1])
    except:
        ed.st = 'Invalid argument'

@map_command('tabset')
def set_tablature_attribute(ed, params):
    '''Set a given tablature attribute'''
    # add sanity tests
    argtypes = { 
        'instrument':int,
        'bpm':float,
        'tuning':lambda arg: [int(note) for note in arg.split(',')]
    }

    if len(params) == 3 and params[1] in argtypes.keys():
        setattr(ed.tab, params[1], argtypes[params[1]](params[2]))
    else:
        ed.st = 'Invalid argument'

@map_command('tuning')
def tuning(ed, params):
    if len(params) == 1:
        pass
    elif len(params) == 2:
        # standard E shifted
        shift = int(params[1])
        ed.tab.tuning = [n + shift for n in music.standard_E]
    elif len(params) == 7:
        # individual strings
        ed.tab.tuning = reversed([str(s) for s in params[1:]])
    else:
        ed.st = 'Invalid argument'
        return
    # display tuning
    ed.st = music.tuning_str(getattr(ed.tab, 'tuning', music.standard_E))

@map_command('ilen')
def set_insert_duration(ed, params):
    try:
        ed.insert_duration = Fraction(int(params[1]), int(params[2]))
    except:
        ed.st = 'Invalid argument'

@map_command('len')
def cmd_set_duration(ed, params, apply_to=None):
    try:
        d = Fraction(int(params[1]), int(params[2]))
        ed.insert_duration = d

        if apply_to is None:
            ed.tab.get_cursor_chord().duration = d
        else:
            for c in apply_to.chords():
                c.duration = d

        ed.move_cursor()
    except:
        ed.st = 'Invalid argument'

@map_command('bartotal')
def bar_total(ed, params):
    '''Display a sum of bars note lengths'''
    ed.st = str(ed.tab.get_cursor_bar().real_duration())

@map_command('midiouts')
def list_midi_outputs(ed, params):
    ed.pager(ed.player.list_outputs())

@map_command('midiout')
def change_output(ed, params):
    try:
        ed.player.change_output(int(params[1]))
    except:
        ed.player.open_first_output()
        ed.st = 'Could not open given port'

@map_command('nonstop')
def enable_continuous_playback(ed, params):
    if len(params) == 2 and params[1] == 'off':
        ed.continuous_playback = False
    else:
        ed.continuous_playback = True

@map_command('m')
def set_visible_meta(ed, params):
    possible_meta = ['meter', 'number', 'label', 'length']

    if len(params) == 1:
        try:
            i = possible_meta.index(ed.visible_meta)
            ed.visible_meta = possible_meta[(i + 1) % len(possible_meta)]
        except KeyError:
            ed.visible_meta = possible_meta[0]
        ed.st = ed.visible_meta

    elif len(params) == 2 and params[1] in possible_meta:
        ed.visible_meta = params[1]

    else:
        ed.st = 'Invalid argument'

@map_command('e!')
def edit_file(ed, params):
    import os.path
    try:
        ed.load_tablature(os.path.expanduser(params[1]))
        ed.move_cursor()
    except IndexError:
        ed.st = 'File name not specified'

@map_command('e')
def soft_edit_file(ed, params):
    if getattr(ed.tab, 'changed', False):
        ed.st = 'The file has changed. Use :e! to force.'
    else:
        edit_file(ed, params)

@map_command('w')
def write_file(ed, params):
    import os.path
    try:
        ed.save_tablature(os.path.expanduser(params[1]))
    except IndexError:
        if ed.file_name:
            ed.save_tablature(ed.file_name)
        else:
            ed.st = 'File name not specified'

@map_command('q!')
def quit(ed, params):
    ed.terminate = True

@map_command('q')
def soft_quit(ed, params):
    if getattr(ed.tab, 'changed', False):
        ed.st = 'The file has changed. Use :q! to force.'
    else:
        quit(ed, params)

@map_command('wq')
def write_and_quit(ed, params):
    if ed.file_name:
        write_file(ed, params)
        quit(ed, params)
    else:
        ed.st = 'New file, use :w [file name]'

@map_command('python')
def exec_python(ed, params):
    '''Execute a python expression from the command line'''
    exec string.join(params[1 : ], ' ') in {'ed' : ed}

