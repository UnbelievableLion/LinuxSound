
##  FluidSynth 


 `fluidsynth`is a command line MIDI player.
      It runs under ALSA with a command line

```

	
	  fluidsynth -a alsa -l <soundfont> <files...>
	
      
```


The soundfont is set explicitly on the command line, so can be
      set to another soundfont.


 `qsynth`is a GUI interface to `fluidsynth`.


You can use FluidSynth to convert MIDI files to WAV files by

```

	
	  fluidsynth -F out.wav /usr/share/sounds/sf2/FluidR3_GM.sf2 myfile.mid
	
      
```

###  Fluidsynth as a server 


Fluidsynth can be run as a server in the same way as TiMidity.
      Use

```

	
fluidsynth --server --audio-driver=alsa /usr/share/sounds/sf2/FluidR3_GM.sf2
	
      
```


Then `a connect -o`will show the ports and it can
      be played to by e.g.

```

	
amidi -p 128:0 <midi-file>
	
      
```
