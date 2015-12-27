
##  aplaymidi 


The program `aplaymidi`will play to a backend MIDI synthesizer such as `TiMidity`. It requires a port name, which can be found by

```

       
aplaymidi -l
       
     
```


with output such as

```

       
 Port    Client name                      Port name
 14:0    Midi Through                     Midi Through Port-0
128:0    TiMidity                         TiMidity port 0
128:1    TiMidity                         TiMidity port 1
128:2    TiMidity                         TiMidity port 2
128:3    TiMidity                         TiMidity port 3
131:0    aseqdump                         aseqdump
       
     
```


It can then play a MIDI file to one of these ports as in

```

	
aplaymidi -p 128:0 54154.mid
	
      
```


The code can be found from [SourceArchive.com](http://alsa-utils.sourcearchive.com/documentation/1.0.8/aplaymidi_8c-source.html) 

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
