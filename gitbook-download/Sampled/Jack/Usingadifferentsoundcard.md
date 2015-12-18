#  Using a different soundcard 

The default ALSA device for Jack will be hw:0.
      If you wish to use a different soundcard then you can
      spcecify this when starting Jack as in
```

	
jackd -dalsa -dhw:0
	
      
```


I have a USB Sound Blaster card, which requires some extra
      parameters
```

	
jackd -dalsa -dhw:2 -r 48000 -S
	
      
```
This doesn't work great - I get a regular "ticking" sound.

Without the
 `-S`(16-bit) flag I just get the
      cryptic
```

	
ALSA: cannot set hardware parameters for playback
	
      
```
Alternatively, I can run
```

	
jackd -dalsa -dplughw:2 -r 48000
	
      
```
When I start it this way, Jack advises against using
      ALSA plug devices but it works best so far.

