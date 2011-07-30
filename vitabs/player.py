#Copyright (C) 2011  Pawel Stiasny

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

import tablature
import pypm
import time

class player:
	def __init__(self):
		pypm.Initialize()
		self.open_first_output()

	def __del__(self):
		del self.port
		pypm.Terminate()

	def open_first_output(self):
		for i in range(pypm.CountDevices()):
			interf,name,inp,outp,opened = pypm.GetDeviceInfo(i)
			if outp:
				self.port = pypm.Output(i, 0)
				break

	def play(self, chords, tuning):
		for c in chords:
			self.port.Write([[[144, tuning[s]+n, 100], pypm.Time()] for s, n in c.strings.iteritems()])
			time.sleep(c.duration * 2.)
			self.port.Write([[[144, tuning[s]+n, 0], pypm.Time()] for s, n in c.strings.iteritems()])

	
