import fractions
from fractions import Fraction

class chord:
	duration = Fraction('1/4')

	def __init__(self):
		self.strings = {}

class bar:
	sig_num = 4
	sig_den = 4

	def __init__(self):
		self.chords = [chord()]

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
	bars = [bar()]
	cursor_bar = 1
	cursor_chord = 1

	def get_cursor_bar(self):
		return self.bars[self.cursor_bar-1]

	def get_cursor_chord(self):
		return self.bars[self.cursor_bar-1].chords[self.cursor_chord-1]
