
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

***


Copyright © Jan Newmarch, jan@newmarch.name


<a href="http://creativecommons.org/licenses/by-sa/4.0/" rel="license">
<img alt="Creative Commons License" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" style="border-width:0"/>
</a>


"Programming and Using Linux Sound - in depth"by [
  Jan Newmarch
](https://jan.newmarch.name) is licensed under a [
  Creative Commons Attribution-ShareAlike 4.0 International License
](http://creativecommons.org/licenses/by-sa/4.0/) .


Based on a work at [
  https://jan.newmarch.name/LinuxSound/
](https://jan.newmarch.name/LinuxSound/) .


If you like this book, please contribute using PayPal


<a href="https://www.paypal.com/cgi-bin/webscr?cmd=_donations&amp;business=jan%40newmarch%2ename&amp;lc=AU&amp;item_name=LinuxSound&amp;currency_code=AUD&amp;bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted">
<img src="https://www.paypalobjects.com/WEBSCR-640-20110401-1/en_AU/i/btn/btn_donateCC_LG.gif"/>
</a>


Or Flattr me:


<a href="https://flattr.com/submit/auto?user_id=jannewmarch&amp;url=http://jan.newmarch.name&amp;title=Linux%20Sound&amp;description=Programming%20and%20Using%20Linu%20Sound&amp;language=en_GB&amp;tags=linux,sound,alsa,pulseaudio,JavaSound,MIDI&amp;category=text">
<img alt="Flattr this book" src="https://api.flattr.com/button/flattr-badge-large.png"/>
</a>
