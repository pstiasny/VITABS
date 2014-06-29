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

templates = {
    'bend' : '{}b',
    'release' : '{}r',
    'hammer on' : 'h{}',
    'pull off' : 'p{}',
    'vibrato' : '{}~',
    'tremolo' : '{}"',
    'slide up' : '{}/',
    'slide down' : '{}\\'
}

keys = {
    ord('b') : 'bend',
    ord('r') : 'release',
    ord('H') : 'hammer on',
    ord('p') : 'pull off',
    ord('v') : 'vibrato',
    ord('t') : 'tremolo',
    ord('s') : 'slide up',
    ord('d') : 'slide down'
}

def apply_symbols(fretnum, symlist):
    st = str(fretnum)
    for s in symlist:
        try:
            st = templates[s].format(st)
        except KeyError:
            pass
    return st
