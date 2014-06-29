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

import tablature
import time
import math
import functools

try:
    import pypm
except ImportError:
    print "PyPortMidi not installed, MIDI playback will not be available."

def if_mod_imported(mod, retval=None):
    '''Make a function do nothing if module is not imported'''
    def wrapper(f):
        if mod in globals():
            return f
        else:
            def wfun(*args, **kwds):
                return retval
            return wfun
    return wrapper

def dummy_handler():
    return True

class Player:
    port = None

    @if_mod_imported('pypm')
    def __init__(self, outport=None):
        # Handlers return a boolean indiciating wheter to continue playing
        # Override for custom handling.

        # Called after each chord played
        self.post_play_chord = dummy_handler
        #Called before each repetition
        self.before_repeat = dummy_handler

        pypm.Initialize()
        if outport is None:
            self.open_first_output()
        else:
            self.change_output(outport)

    @if_mod_imported('pypm')
    def __del__(self):
        self.port.Close()
        del self.port
        pypm.Terminate()
    
    @if_mod_imported('pypm')
    def open_first_output(self):
        for i in range(pypm.CountDevices()):
            outp = pypm.GetDeviceInfo(i)[3]
            if outp:
                self.port = pypm.Output(i, 0)
                break

    @if_mod_imported('pypm')
    def change_output(self, num):
        if not self.port:
            self.port.Close()
            del self.port
        self.port = pypm.Output(num, 0)
    
    @if_mod_imported('pypm', [])
    def list_outputs(self):
        ret = []
        for i in range(pypm.CountDevices()):
            interf,name,inp,outp,opened = pypm.GetDeviceInfo(i)
            if outp == 1:
                ret.append(str(i) + " " + name)
        return ret

    @if_mod_imported('pypm')
    def set_instrument(self, num):
        if not self.port:
            return
        self.port.WriteShort(0xC0, num)

    @if_mod_imported('pypm')
    def play(self, crange, continuous=False):
        if not self.port:
            return
        tuning = getattr(crange.tab, 'tuning', [76, 71, 67, 62, 57, 52])
        bpm = getattr(crange.tab, 'bpm', 120)
        channel = 0
        try:
            while True:
                if not self.before_repeat():
                    break
                bartime = (240./bpm)
                for c in crange.chords():
                    t = pypm.Time()
                    play_vibrato = False
                    for fr in c.strings.itervalues():
                        if 'vibrato' in fr.symbols:
                            play_vibrato = True
                            break
                    self.port.Write(
                        [[[144 + channel, tuning[s]+fr.fret, 100], t] 
                         for s, fr in c.strings.iteritems()])
                    if play_vibrato:
                        interval = c.duration * bartime / 20
                        for i in range(20):
                            self.port.WriteShort(224 + channel, 0,
                                    40 + int(15. * math.sin(float(i) / 0.95)))
                            time.sleep(interval)
                        self.port.WriteShort(224 + channel, 0, 40)
                    else:
                        time.sleep(c.duration * bartime)
                    t = pypm.Time()
                    self.port.Write(
                        [[[128 + channel, tuning[s]+fr.fret, 100], t] 
                         for s, fr in c.strings.iteritems()])
                    if not self.post_play_chord():
                        break
                if not continuous:
                    break
        except KeyboardInterrupt:
            self.port.Write(
                [[[144, tuning[s]+fr.fret, 0], t] 
                for s, fr in c.strings.iteritems()])

