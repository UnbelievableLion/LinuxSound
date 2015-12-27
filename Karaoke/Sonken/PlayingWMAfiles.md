
##  Playing WMA files 


WMA files are "evil."
They are based on two Microsoft proprietary formats. The first is
the Advanced Systems Format (ASF) file format which describes the "container"
for the music data. The second is the codec, Windows Media Audio 9.


The ASF is the primary problem. Microsoft have a [published specification](http://www.microsoft.com/en-us/download/details.aspx?id=14995) . This specification is strongly antagonistic
to anything open source. The license states that if you build an implementation
based on that specification then you:

+ cannot distribute the source code
+ can only distribute the object code
+ cannot distribute the object code except as part of a "Solution"
i.e. libraries seem to be banned
+ cannot distribute your object code for no charge
+ cannot set your license to allow derivative works

And what's more, you are not allowed to begin any new implementation after
January 1, 2012 - and it is already May, 2012!


Just to make it a little worse, Microsoft have [Patent 6041345
	"Active stream format for holding multiple media streams"](http://www.google.com/patents/US6041345) filed in Mar 7, 1997. The patent appears to cover the same ground as
many other such formats which were in existence at the time, so the
standing of this patent (were it to be challenged) is not clear.
However, it has been used to block the GPL-licensed project [VirtualDub](http://www.advogato.org/article/101.html) from supporting ASF. The status of patenting a file format is a little
suspect anyway, but may become a little clearer after Oracle wins or loses its claim
to patent the Java API.


The [FFmpeg project](http://ffmpeg.org/) has nevertheless done a
clean-room implementation of ASF, reverse-engineering the file format
and not using the ASF specification at all. It has also reverse-engineered
the WMA codec. This allows players such as mplayer and VLC to play ASF/WMA files.
FFmpeg itself can also convert from ASF/WMA to better formats such as Ogg Vorbis.


There is no Java handler for WMA files, and given the license there is unlikely
to be one unless it is based on FFmpeg.


The WMA files that I have extracted from the DVD have the following characteristics:

+ Each file has two channels
+ Each channel carries a mono signal
+ The right channel carries all of the instruments, backing vocals
and also the lead singer
+ The left channel carries all of the instruments and backing vocals
but not the lead singer

The Sonken player plays the right channel if no-one is singing into the
microphones, but switches to the left channel (effectively muting the lead
singer) as soon as someone sings into a microphone. Simple and effective.


The lyrics are still there in the track data as MIDI and can be extracted as
before. They can be played by a MIDI player. I have no idea (yet) how
to synchronise playing the MIDI and the WMA files.
