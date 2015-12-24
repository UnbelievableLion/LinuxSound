
##  Conclusion


This chapter has looked at PulseAudio. This is currently the standard sound
      system for consumer Linux. There are a number of utilities for exploring PulseAudio.
      There are two APIs: the simple API and the asynchronous API. The chapter has looked
      at playing and recording using these APIs. Some other aspects of PulseAudio were also
      examined.


Latency is not a goal, and it is not designed for real-time audio.
      However, you can request that the latency be made small, and if PulseAudio
      can do it will give you reasonable performance. However, PulseAudio makes
      no guarantees about latency, so if a maximum latency is critical then PulseAudio
      may not be suitable.


PulseAudio is presently built on top of ALSA and usually interacts by making
      itself the default ALSA plugin.


Copyright © Jan Newmarch, jan@newmarch.name





"Programming and Using Linux Sound - in depth"by [Jan Newmarch](https://jan.newmarch.name) is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/) .


Based on a work at [https://jan.newmarch.name/LinuxSound/](https://jan.newmarch.name/LinuxSound/) .


If you like this book, please contribute using Flattr


or donate using PayPal
![alt text](https://www.paypalobjects.com/WEBSCR-640-20110401-1/en_AU/i/scr/pixel.gif)