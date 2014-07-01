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

"Input handling in command mode."

from curses.textpad import Textbox


class CommandEditor(Textbox):
    def __init__(self, win, editor):
        self.history_idx = len(editor.cmd_history) - 1
        self.stripspaces = False
        self.ed = editor
        self.complete_initial = self.complete_sequence = None
        Textbox.__init__(self, win)

    def _get_completions(self):
        self.complete_initial = txt = self.gather()[:-1]
        completions = [
            (cmd, fun.__doc__)
            for cmd, fun in self.ed.commands.iteritems()
            if cmd.startswith(txt)
        ]
        sorted_completions = sorted(completions)
        self.complete_sequence = iter(sorted_completions)
        return sorted_completions
    
    def _reset_completions(self):
        self.complete_initial = self.complete_sequence = None

    def do_command(self, ch):
        ed = self.ed

        if ch != 9:
            self._reset_completions()

        if ch == 9:  # tab
            if not self.complete_sequence:
                completions = self._get_completions()
                if completions:
                    txt = completions[0][0]

            if self.complete_sequence:
                try:
                    compl = next(self.complete_sequence)
                    txt = compl[0]
                except StopIteration:
                    txt = self.complete_initial
                    self._reset_completions()

            ed.status_line.clear()
            ed.status_line.addstr(0, 0, txt)
            return True
        elif ch == 4:  # C-d
            completions = [
                '{}: {}'.format(cmd, doc) if doc else cmd
                for cmd, doc in self._get_completions()
            ]
            ed.pager(completions)
            ed.status_line.clear()
            ed.status_line.addstr(0, 0, self.complete_initial)
            return True
        elif ch == 127:  # backspace
            return Textbox.do_command(self, 263)
        elif ch == 259:  # up
            ed.status_line.clear()
            ed.status_line.addstr(0, 0, ed.cmd_history[self.history_idx])
            self.history_idx = max(self.history_idx - 1, 0)
            return True
        elif ch == 258:  # down
            self.history_idx = min(self.history_idx + 1, len(ed.cmd_history) - 1)
            ed.status_line.clear()
            ed.status_line.addstr(0, 0, ed.cmd_history[self.history_idx])
            return True
        elif ch == 21:  # C-u
            ed.status_line.clear()
            return True
        elif ch == 23:  # C-w
            txt = self.gather()[:-1]
            try:
                last_space = txt.rindex(' ')
            except ValueError:
                last_space = 0
            ed.status_line.clear()
            ed.status_line.addstr(0, 0, txt[:last_space])
            return True
        else:
            #sys.stderr.write('do_command ' + str(ch) + '\r\n')
            #sys.stdout.write(txt)
            return Textbox.do_command(self, ch)

