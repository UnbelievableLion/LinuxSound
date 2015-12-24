
##  Introduction 


Videos often accompany audio. Karaoke oftens overlays the video
      with lyrics. Building an application to include video as well
      as audio takes us into the realm of graphical user interfaces
      (GUIs). This is a complex area in its own right, and deserves
      (and has!) many books, including my own from many years back on
      the X Window System and Motif.


Motif lost its status as a major GUI for Linux/Unix systems
      a long time ago. There are many alternatives now, including
      Gtk (Gimp toolkit), tcl/Tk, Java Swing, KDE, XFCE, ...
      They each have their own adherents, domains of use, quirks,
      idiosyncrasies, ... No single GUI will satisfy everyone.


In this chapter I deal with Gtk. The reasons are threefold:

+ It has a C library. It also has a Python library which
	  is nice and I might use it one day. Most importantly it
	  is _not_ C++ based - C++ is one of my least 
	  favourite languages. I once came across a quote (source
	  lost) that "C++ is a laboratory experiment that escaped"
	  and I completely agree with that assessment
+ It has good support for i18n (internationalisation).
	  I want to be able to play Chinese Karaoke files, so this
	  is important to me
+ It is not Java-based. Don't get me wrong, I really like Java
	  and have been programming in it for years.
	  The MIDI API is pretty good, and of course everything
	  else such as i18n is great. But for MIDI it is a CPU
	  hog and is unusable on low powered devices such as the
	  Raspberry Pi, and generally the audio/video API has not
	  progressed in years

Nevertheless, as I struggled to get my head around Gtk,
      versions 2.0 versus 3.0, Cairo, Pango, Glib, etc.
      I thought it might have been easier just to fix the Java
      MIDI engine! This was not a pleasant experience,
      as the sequel will show :-(.
