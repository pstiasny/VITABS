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

import fractions
from fractions import Fraction
import symbols as syms

class Fret:
    def __init__(self, fret):
        self.fret = fret
        self.symbols = []
    
    def __repr__(self):
        '''A textual representation of the fret as displayed in the tab'''
        return syms.apply_symbols(self.fret, self.symbols)
    
class Chord:
    def __init__(self, duration = Fraction('1/4')):
        self.strings = {}
        self.duration = duration

class Bar:
    def __init__(self, sig_num=4, sig_den=4, first_chord_len=Fraction('1/4')):
        self.chords = [Chord(first_chord_len)]
        self.sig_num = sig_num
        self.sig_den = sig_den

    def required_duration(self):
        """Duration as specified by signature"""
        return Fraction(self.sig_num, self.sig_den)
    
    def real_duration(self):
        """Sum of chord durations"""
        return reduce(lambda a, b: a + b.duration, self.chords, 0)

    def gcd(self):
        """Greatest common denominator of chord durations"""
        return reduce(lambda a,b: fractions.gcd(a, b.duration), 
            self.chords, 0)

    def total_width(self, gcd):
        """Calculated width in characters"""
        d = self.real_duration()
        if d == 0:
            return 2
        else:
            return int(self.real_duration() / gcd) * 2 + len(self.chords) + 2

class Tablature:
    cursor_bar = 1
    cursor_chord = 1

    def __init__(self):
        self.bars = [Bar()]

    def get_cursor_bar(self):
        return self.bars[self.cursor_bar - 1]

    def get_cursor_chord(self):
        return self.bars[self.cursor_bar - 1].chords[self.cursor_chord - 1]
    
    def cursor_position(self):
        return self.cursor_bar, self.cursor_chord

    def last_position(self):
        barcount = len(self.bars)
        return barcount, len(self.bars[barcount - 1].chords)

class ChordRange:
    def __init__(self, tab, beginning, end):
        self.tab = tab

        if beginning[1]:
            self.beginning = beginning
        else:
            self.beginning = (beginning[0], 1)

        if end[1]:
            self.end = end
        else:
            self.end = (end[0], len(tab.bars[end[0] - 1].chords))
    
    def __repr__(self):
        return "{0} {1}".format(self.beginning, self.end)

    def is_single_bar(self):
        return self.beginning[0] == self.end[0]

    def whole_bars(self):
        '''False if the range doesn't span a whole bar at one of it's ends'''
        return (self.beginning[1] == 1 and
                self.end[1] == len(self.tab.bars[self.end[0] - 1].chords))

    def chords(self):
        '''Iterator over chords in the range'''
        first_bar = self.beginning[0] - 1
        first_chord = self.beginning[1] - 1
        last_bar = self.end[0] - 1 
        last_chord = self.end[1]

        if first_bar == last_bar:
            for c in self.tab.bars[first_bar].chords[first_chord:last_chord]:
                yield c
        else:
            for c in self.tab.bars[first_bar].chords[first_chord : ]:
                yield c

            for b in self.tab.bars[first_bar + 1 : last_bar]:
                for c in b.chords:
                    yield c

            for c in self.tab.bars[last_bar].chords[ : last_chord]:
                yield c
    
    def bars(self):
        for b in self.tab.bars[self.beginning[0] - 1 : self.end[0]]:
            yield b
    
    def delete_all(self):
        '''Delete the range of chords from the tablature'''
        first_bar = self.beginning[0] - 1
        first_chord = self.beginning[1] - 1
        last_bar = self.end[0] - 1 
        last_chord = self.end[1]

        if first_bar == last_bar:
            del self.tab.bars[first_bar].chords[first_chord : last_chord]
            if not self.tab.bars[first_bar].chords:
                del self.tab.bars[first_bar]
        else:
            del self.tab.bars[last_bar].chords[ : last_chord]
            if not self.tab.bars[last_bar].chords:
                del self.tab.bars[last_bar]
            
            del self.tab.bars[first_bar + 1 : last_bar]

            del self.tab.bars[first_bar].chords[first_chord : ]
            if not self.tab.bars[first_bar].chords:
                del self.tab.bars[first_bar]

def parse_position(tab, desc):
    if desc == '.':
        return tab.cursor_position()
    elif desc == '$':
        return tab.last_position()
    else:
        parts = desc.split(',')
        return (int(parts[0]),
                None if len(parts) == 1 else int(parts[1]))
