
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


Copyright © Jan Newmarch, jan@newmarch.name





"Programming and Using Linux Sound - in depth"by [Jan Newmarch](https://jan.newmarch.name) is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/) .


Based on a work at [https://jan.newmarch.name/LinuxSound/](https://jan.newmarch.name/LinuxSound/) .


If you like this book, please contribute using Flattr


or donate using PayPal
![alt text](https://www.paypalobjects.com/WEBSCR-640-20110401-1/en_AU/i/scr/pixel.gif)