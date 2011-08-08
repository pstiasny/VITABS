VITABS Manual
=============

VITABS is a guitar tab editor inspired by the legendary Vi text editor and
its highly successful clone, Vim.  It was created as an alternative to
GUI-based editors, with convenient editing and fast keyboard entry in mind.
It also tries to adhere to the philosophy of doing one thing well.  VITABS is
not a composition application, music typesetting software nor music theory
teacher.  Other applications doing these things well are available.

If you are familiar with Vim, you should be able to understand this editors
interface concept quickly.  If you're not, but you are looking for a free,
convienient tab editor -- read on.  This manual tries to explain how to use
the editor, covering basic concepts, more advanced convenience features and
programming interface.

[TOC]


Getting VITABS
---------------
You can get the latest development source at projects github at 
<https://github.com/PawelStiasny/VITABS>.  Use git to dowload the latest version

    git clone git://github.com/PawelStiasny/VITABS.git

To install, execute the following as root:

    cd VITABS
    python2 setup.py install

An up-to-date version of this manual should be available in the `doc`
directory.


Starting VITABS
---------------
To launch the application you need Python 2 and the curses library.

Start the program in the terminal

    python2 vitabs.py


Interface overview
------------------
When you first start VITABS, a single empty bar (this is your new tablature)
and the status line (the last line in the terminal) shall be displayed.  You
are now in normal mode, as opposed to command and insert modes - these will be
discussed later on.

### The status line
By default, the status line displays 3 indicators: the bar-meter indicator,
the note length indicator and the position indicator.

    M 1/4     1,1

The *bar-meter* indicator - `M` - is visible when the bar selected by the
cursor is not complete, i.e. bar's meter does not match total duration of notes
in it.

The *note length* presents length of note or chord indicated by the cursor.

The *position* indicator displays cursor position in the form `bar,chord`.
This is similar to cursor position in Vi.  Internally, VITABS refers to
every cursor position, including single notes, as chords, as this makes no
difference for the internal representaion.  This convention will be used
in the manual from this point.

### Listing available normal mode commands
To see what commands are available in the normal mode, press `?`.

### Command mode
VITABS features a command mode (but not as powerful as the one in Vim).  To
start typying a command, press `:`.  To execute, press Enter.  To abort, press
`Ctrl-C`.

#### Ranges
Some commands can be applied to a range of chords/bars.  This is achieved by
the `:for` command:

    :for [from] [to] [command] [command arguments...]

where `from` and `to` can be:

* `[bar number]` to include the whole bar
* `[bar number],[chord number]`
* `.` current cursor position
* `$` end of the tablature

e.g. `:for 1 $ meter 3 4` changes meter for the whole tablature to 3/4.

### Getting out of VITABS
Write `:q` and press Enter to exit.

### Analogies and differences with Vim
VITABS treats bars analogically to Vi lines and chords analogically to
charactes.  That said, most of motion and editing commands work as expected
regarding these analogies.

The major difference is the behavior of insert mode, in which vertical movement
commands toggle between guitar strings instead of moving between the bars and
right arrow creates a new chord after the cursor.


Navigation commands
--------------------
To move around the tablature, you can use the arrow keys and Home/End keys.
However, it is also possible to use Vi-like keys, including:

`h`, `j`, `k`, `l` correspond to left, down, up, right

`0` and `$` move to the beginning and end of the bar

`g` and `G` move to the beginning and end of the tablature

`G` with a numeric argument moves to the specified bar, e.g. `10G` goes to the
10th bar.


Inserting
---------
The following commands create an empty chord at specified position and enter
insert mode:

* `i` before cursor
* `a` after cursor
* `I` at the beginning of the bar
* `A` at the end of the bar

additionally, the `s` command enters insert mode at cursor position. allowing
to edit the selected chord.

To create a new bar after the currently selected and enter insert mode press
`o`. Press `O` to do the same before the selected bar.

### The insert mode
After you used one of the the above commands, the editor will switch to the
insert mode.  This is indicated in the status line by the following message

    -- INSERT --

Now you can enter new notes and modify the selected chord.  You can use the
up/down arrow keys to move between the strings, however it is faster to jump
between them by referring to them by their open-string note (in standard
tuning): `E`, `A`, `D`, `G`, `B`, `e`.  Enter fret numbers using the usual
number keys.  Press `x` or `delete` to remove the number from the current
string.

Pressing the right arrow will insert another empty chord after the cursor and
move to it.  If you instead want to edit one of the existing chords, exit
insert mode first, then move to the desired position and use the `s` command.

After you are done inserting, press `ESC` to exit insert mode and return to
normal mode.

#### Special symbols
The following keys set/unset symbols for the selected string:

* `b`: bend
* `r`: release
* `h`: hammer on
* `p`: pull off
* `v`: vibrato
* `t`: tremolo
* `s`: slide up
* `d`: slide down


Note lengths
------------
To change the duration of the selected chord you can use

* `q` to decrease the length twice
* `Q` to incerease twice

To set a specified length of 1/[natural number] write that number followed
by `q`, e.g. if you want to set the selected chord to quarter notes, you would
enter

    4q

This way you specify a numeric argument to the `q` command.

To set a specified range for the selected chord:

    :len [numerator] [denominator]

This command accept a range.

### Insert length

    :ilen [numerator] [denominator]

This command will cause all following chords created with an insert command
to have the specified initial length.


Removing
--------
`x` deletes a single chord at the cursor.

`d{motion}` deletes over a motion, e. g. `0d$` would delete the whole bar.


Playback
--------
You need to have PyPortMidi installed on your system for playback to work.

By default, VITABS will connect to the first available MIDI port.  If you wish
to use a different output port, the command `:midiouts` will list available
outputs with their indices.  Use the following command to use the preferred
port:

    :midiout [port index]

`E` plays the whole track and `e` plays from the current cursor position to the
end of the track.

`r{motion}` plays over the given motion, e.g. `0r$` would play the whole bar.

`Ctrl-c` stops playback.


Tablature attributes
--------------------
### Instrument
    :tabset instrument [midi program number]

### Tuning
    :tabset tuning [notes]

`notes` is a coma-separated list of midi note values from lowest to highest

### Tempo
    :tabset bpm [bpm]


Bar attributes
--------------
### Meter

    :meter [numerator] [denominator]

sets meter for the current bar.  Accepts range.


View manipulation
-----------------
The `:meta` command will set what kind of information is displayed over each
bar

* `:meta meter` display bar meter
* `:meta number` display bar numbers


Working with files
------------------
### Opening
Use the command

    :e [file name]

to open an exisitng file.  If the file doesn't exist, it will be created when
you use the `:w` command.

You can also open a file by specifying it as a command line argument to
vitabs.py.

### Saving
Use

    :w [file name]

to save the current tablature with the given name.  When saving the next time,
you can write only

    :w

and the previous file name will be used.

