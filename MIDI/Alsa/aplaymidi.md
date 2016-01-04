
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


The port numbers are the same as those used by `aconnect`.
These are not the Alsa device names (hw:0, etc) but are special
to the Alsa sequencer API.


It can then play a MIDI file to one of these ports as in

```

	
aplaymidi -p 128:0 54154.mid
	
      
```


The code can be found from [SourceArchive.com](http://alsa-utils.sourcearchive.com/documentation/1.0.8/aplaymidi_8c-source.html) 
