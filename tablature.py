#Copyright (C) 2011  Paweł Stiasny

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

import fractions
from fractions import Fraction

class chord:
	def __init__(self, duration = Fraction('1/4')):
		self.strings = {}
		self.duration = duration

class bar:
	def __init__(self, sig_num = 4, sig_den = 4):
		self.chords = [chord()]
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
			return int(self.real_duration() / gcd)*2 + len(self.chords) + 2

class tablature:
	cursor_bar = 1
	cursor_chord = 1

	def __init__(self):
		self.bars = [bar()]

	def get_cursor_bar(self):
		return self.bars[self.cursor_bar-1]

	def get_cursor_chord(self):
		return self.bars[self.cursor_bar-1].chords[self.cursor_chord-1]
