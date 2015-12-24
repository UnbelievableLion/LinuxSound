
##  Overview 


The whole purpose of this book - from my point of view -
      is to document what is going on in Linux Sound in my path
      to building a Linux Karaoke system. I'm still on the way.
      This chapter looks at various explorations I have made using
      the material of previous chapters.


First, what are my goals?

+ Be able to play KAR files (one of the possible Karaoke file formats)
+ Show the lyrics at least one line at a time, highlighting the
	  characters when they should be sung
+ For Chinese songs, also show the Pinyin (English) form of
	  the lyrics as well as the Chinese characters
+ Play a movie in the background
+ Display the melody in some form
+ Show the notes actually sung against the melody
+ Score the results in some way

Nothing I have yet done gets anywhere near these goals.
      Let me pick out the highlights of my explorations so far:

+ The simplest "off the shelf" system is [
	    PyKaraoke
	  ](../User/) ,
	  with [
	    kmid
	  ](../User/) a close follower.
	  These play KAR files and highlight the lyrics but no more.
+ The simplest way to add microphone input to such a system is to
	  use an [external mixer](../User/) .
	  These can also do reverb and other effects
+ Jack and PulseAudio can trivially be used to add in microphone
	  input as play-through, but effects take more work
+  [
	    Java
	  ](../JavaSound/) is really cool for nearly everything - except latency
	  ruins it in the end
+  [FluidSynth](../FluidSynth/) can be hacked to
	  give hooks to hang Karaoke from. But it is CPU intensive
	  and doesn't leave room for much other processing
+  [TiMidity](../Timidity/) is a standalone system with
	  configurable backends. It can be configured to give a crude
	  Karaoke system. But it can be hacked to make it into a library
	  which gives it more potential. It is not as CPU intensive
	  as FluidSynth.
+ Playing a background movie can be done using FFMpeg and
	  a GUI such as [ Gtk ](../../Diversions/Gtk/) .
	  Gtk also has the mechanisms for overlaying highlighted lyrics
	  on top of the video, but Gtk 2 and Gtk 3 differ in the mechanism
+ TiMidity can be [combined](../Timidity/) with
	  FFMpeg and GtK to display hightlighted lyrics against a movie background
+ Scoring is still out of sight right now, although the Java library
	  TarsosDSP can give lots of information

The following chapters cover:

+ __ [ User level tools ](../User/) __:
Karaoke is an "audience participation" sound system,
	  in which the soundtrack and usually the melody are played 
	  along with a moving display of the lyrics. 
	  This chapter considers the features, formats and user-level 
	  tools for playing Karaoke.
+ __ [ Decoding the DKD files on the Songken Karaoke DVD ](../Sonken/) __:
This chapter is about getting the information off my Songken Karaoke DVD 
	  so that I can start writing programs to play the songs.
	  It is not directly involved in playing sound under Linux and can be skipped.
+ __ [ JavaSound ](../JavaSound/) __:
JavaSound has no direct support for Karaoke. This chapter looks at how to combine the JavaSound libraries with other libraries such as Swing to give a Karaoke player for MIDI files.
+ __ [ Subtitles ](../Subtitles/) __:
Many Karaoke systems use subtitles imposed over a movie of some kind. This chapter looks at how to do this with Linux systems. There are limited choices, but it is possible.
+ __ [ FluidSynth ](../FluidSynth/) __:
FluidSynth is an application for playing MIDI files and a library for MIDI applications. It does not have the hooks for playing Karaoke files. This chapter discusses an extension to FluidSynth which adds appropriate hooks, and then uses these to build a variety of Karaoke systems.
+ __ [ Timidity ](TiMidity) __:
TiMidity is designed as a standalone application with a particular kind of extensibility. Out of the box it can sort-of play Karaoke but not well. This chapter looks at how to work with TiMidity to build a Karaoke system.

Copyright © Jan Newmarch, jan@newmarch.name





"Programming and Using Linux Sound - in depth"by [Jan Newmarch](https://jan.newmarch.name) is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/) .


Based on a work at [https://jan.newmarch.name/LinuxSound/](https://jan.newmarch.name/LinuxSound/) .


If you like this book, please contribute using Flattr


or donate using PayPal
![alt text](https://www.paypalobjects.com/WEBSCR-640-20110401-1/en_AU/i/scr/pixel.gif)