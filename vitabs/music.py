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

notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

standard_E = [76, 71, 67, 62, 57, 52]

length_names = {
    1 : 'W',
    Fraction('1/2') : 'H',
    Fraction('1/4') : 'Q',
    Fraction('1/8') : 'E',
    Fraction('1/16') : 'S'
}

def midi_to_note_name(note_num):
    return notes[(note_num - 24) % len(notes)] + \
            str((note_num - 24) / len(notes))

def tuning_str(tuning):
    if tuning == standard_E:
        return 'Standard E'
    return ' '.join(reversed([midi_to_note_name(n) for n in tuning]))

def len_str(length):
    try:
        return length_names[length]
    except KeyError:
        try:
            return length_names[length / Fraction('3/2')] + '.'
        except KeyError:
            try:
                return length_names[length * Fraction('3/2')] + '3'
            except KeyError:
                return str(length)

