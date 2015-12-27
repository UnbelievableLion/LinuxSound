
##  KAR file format 


> There is no formal standard for Karaoke MIDI files.
There is a widely accepted industry format called
the MIDI Karaoke Type 1 file format.


> From [MIDI Karaoke Frequently Asked Questions](http://gnese.free.fr/Projects/KaraokeTime/Fichiers/karfaq.html) 


   > 

> > What is the MIDI Karaoke Type 1 (.KAR) file format? A:
A MIDI Karaoke file is a Standard MIDI File type 1 that
contains a separate track with lyrics of the song entered
as text events. Load one of the MIDI karaoke files into a
sequencer to examine the contents of the tracks of the file.
The first track contains text events that are used to make the
file recognizable as the MIDI Karaoke file. @KMIDI KARAOKE
FILE text event is used to for that purpose. The optional text
event @V0100 denotes the format version number. Anything
starting with @I is any information you want to include in the file.


> > The second track contains the text meta events for the
lyrics of the song. The first event is @LENGL. It
identifies the language of the song, in this case English.
The next couple of events start with @T which identifies
the title of the songs. You can have up to three events like
these. The first event should contain the title of the song.
Some programs (ex. Soft Karaoke) read this event to get the
name of the song to be displayed in the File Open dialog box.
The second event usually contains the performer or author
of the song. The third event can contain any copyright
information or anything else.


> > The rest of the second track contains the words of the song.
Each event is the syllable that is supposed to be sung at the
time of the event. If the text starts with \, it means to
clear the screen and show the words at the top of the screen.
If the text starts with /, it means to go to the next line.


> > Important note: There can be only 3 lines per screen
in a .kar file for Soft Karaoke being able to play the file
correctly. In other words, there can be only two / (forward
slashes) beginning each line in a line of lyrics.
The next line has to start with \ (back slash).




> There are several weaknesses in this format:

> + The list of possible languages is not specified,
only English
> + The encoding of text is not specified (e.g. Unicode UTF-8?))
> + There is no means of identifying the channel carrying
the melody