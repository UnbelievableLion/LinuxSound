
##  Streaming vs downloading 


If you download a file from the Web, then you can play it once it has finished
downloading. This means that play is delayed until the entire file has been
saved into the local file file system. On the other hand, since it is now local
it can play without worrying about network delays. A simple shell script to
illustrate this is

```

	
wget -O tmp  http://localhost/audio/enigma/audio_01.ogg
mplayer tmp
rm tmp
	
      
```





The alternative is to read the resource from the Web and hand it as it is
received to a player, using some sort of pipeline. This is fine as long as the
pipeline is large enough to buffer enough of the resource that it can cope
with network delays. It is illustrated by

```

	
wget -O -  http://localhost/audio/enigma/audio_01.ogg | mplayer -
	
      
```


(Yes, I know, mplayer can stream URLs directly - I'm using this way it for the point
I'm making.).

***

***


Copyright © Jan Newmarch, jan@newmarch.name


<a href="http://creativecommons.org/licenses/by-sa/4.0/" rel="license">
<img alt="Creative Commons License" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" style="border-width:0"/>
</a>


"Programming and Using Linux Sound - in depth"by [Jan Newmarch](https://jan.newmarch.name) is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/) .


Based on a work at [https://jan.newmarch.name/LinuxSound/](https://jan.newmarch.name/LinuxSound/) .


If you like this book, please contribute using PayPal


<a href="https://www.paypal.com/cgi-bin/webscr?cmd=_donations&amp;business=jan%40newmarch%2ename&amp;lc=AU&amp;item_name=LinuxSound&amp;currency_code=AUD&amp;bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted">
<img src="https://www.paypalobjects.com/WEBSCR-640-20110401-1/en_AU/i/btn/btn_donateCC_LG.gif"/>
</a>


Or Flattr me:


<a href="https://flattr.com/submit/auto?user_id=jannewmarch&amp;url=http://jan.newmarch.name&amp;title=Linux%20Sound&amp;description=Programming%20and%20Using%20Linu%20Sound&amp;language=en_GB&amp;tags=linux,sound,alsa,pulseaudio,JavaSound,MIDI&amp;category=text">
<img alt="Flattr this book" src="https://api.flattr.com/button/flattr-badge-large.png"/>
</a>
