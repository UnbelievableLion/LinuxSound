
##  HTTP clients 

###  HTTP Browsers 


Point the browser to the URL of an audio file and it will pass
the content to a helper which will attempt to play the file.
The browser will choose the helper based on the file extension
of the URL, or based on the Content-Type of the file as delivered
in the HTTP header from the HTTP server.

###  mplayer 


MPlayer is HTTP-aware:
just give the URL of the file

```

	
mplayer http://localhost/audio/enigma/audio_01.ogg
	
      
```




###  VLC 


VLC is also HTTP-aware:
just give the URL of the file

```

	
vlc http://localhost/audio/enigma/audio_01.ogg
	
      
```



