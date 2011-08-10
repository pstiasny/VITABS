VITABS composition tool
=======================

This document explains how to use the (experimental) `vitabs-song` utility
providing higher-level song structure description and manipulation.  The utility
uses a plain text format describing the structure of the song to process VITABS
tablature and output a complete song (currently only playback is supported, in
the future probably also export to MIDI files and maybe more).  The description
is stored in a text file (in this manual called `vtsong`).  The format is
designed to be simple and human readable, so it can be used both for processing
and as a refernce for playing the song.


Project structure
-----------------
Consider you are writing a song called X.  For now you have a single track
called `rhythm_guitar`.  When you are finished, directory structure will look
like this:

    x/
      rhythm_guitar.vit
      vtsong

`rhythm_guitar.vit` is your VITABS tablature containing all the riffs.  Don't
put repitions in the tablature.  Instead, use labels to mark riffs and other
song structure elements you desire.  If you don't know how to use labels, see
the *Editing and navigating the song structure* section in the main manual.
When done, save your tablature (the .vit extension is necesarry for
`vitabs-song`).  You can now exit VITABS or suspend it with `Ctrl-Z`.  Next, you
will create the vtsong file.


Describing a song
-----------------
Let's say you have some riffs in your tablature (`rhythm_guitar.vit`) labelled
`riff1`, `riff2` and `riff3`.  You want to play each of them twice and repeat
from the beginning.  Here is an example that does that:

    # My song called "X"
	tracks: rhythm_guitar
    
    rhythm_guitar riff1 x2
    rhythm_guitar riff2 x2
    rhythm_guitar riff3 x2
    
    rhythm_guitar riff1 x2
    rhythm_guitar riff2 x2
    rhythm_guitar riff3 x2

You would write this down in a text editor of your choice and save as `vtsong`
in directory containing `rhythm_guitar.vit`.  Now you can listen to the whole
song.  Make sure you are in the song's directory and execute this command to play:

    vitabs-song vtsong

You can also specify the output MIDI port.  See `vitabs-song --help` for
possible options.


vtsong file format
------------------
Empty lines and lines beginning with `#` are ignored.

The file begins with a `tracks:` keyword, a space and then a space-separated
list of tracks names follows.  Each track name is a VITABS tablature filename
with the .vit extension removed.

The following lines are of the format:

    [track] [label] x[repetitions]


