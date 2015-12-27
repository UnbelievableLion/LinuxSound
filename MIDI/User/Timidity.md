
##  Timidity 


Timidity is a "Software sound renderer (MIDI sequencer, MOD player)"


Its home page is [Maemo.org](http://maemo.org/packages/view/timidity/) 


Timidity can be used to play MIDI files by giving them on the command line

```

	
	  timidity rehab.mid
	
      
```


The default soundfonts used by Timidity are Gravis UltraSound patches,
from the `/usr/share/midi/freepats/`directory.
These soundfonts are missing many instruments, so should be
replaced by another such as the FluidSynth fonts.
The settings are made in the configurations file `/etc/timidity/timidity.cfg`

###  TiMidity as a server 


It can also be run as an ALSA server listening on a port
( [Using MIDI with UNIX](http://wiki.winehq.org/MIDI) ):

```

	
	  timidity -iAD -B2,8 -Os1l -s 44100
	
      
```


The "-iAD" option runs it as a Daemon process in the background as an
ALSA sequencer client. The "-B2,8" option selects the number of buffer
fragments. The "-Os1l" option selects ALSA output as PCM. The "-s"
option is the sample size.
(For the Raspberry Pi, I found that `-B0,12`worked better than `-B2,8`).


In this mode, ALSA can send messages to it.
The command

```

	
	  aconnect -0
	
      
```


will show output such as

```

	
	  client 14: 'Midi Through' [type=kernel]
	  0 'Midi Through Port-0'
	  laptop:/home/httpd/html/LinuxSound/MIDI/Python/pyPortMidi-0.0.3$aconnect -o
	  client 14: 'Midi Through' [type=kernel]
	  0 'Midi Through Port-0'
	  client 128: 'TiMidity' [type=user]
	  0 'TiMidity port 0 '
	  1 'TiMidity port 1 '
	  2 'TiMidity port 2 '
	  3 'TiMidity port 3 '
	
      
```


The "Midi Through" port is not useful but the Timidity ports are.
MIDI files can then be played by an ALSA sequencer such as

```

	
	  aplaymidi -p128:0 rehab.mid
	
      
```

###  Setting Timidity output device 


The default output for TiMidity can be changed using the `-O`option. TiMidity help ( `timidity -h`)
shows, for example,

```

	
	  Available output modes (-O, --output-mode option):
	  -Os          ALSA pcm device
	  -Ow          RIFF WAVE file
	  -Or          Raw waveform data
	  -Ou          Sun audio file
	  -Oa          AIFF file
	  -Ol          List MIDI event
	  -Om          Write MIDI file
	  -OM          MOD -> MIDI file conversion
	
      
```


For some of these modes the device name can also be set, using
the `-o`option. For example, to play a file using
the `hw:2`ALSA device, use

```

	
	  timidity -Os -o hw:2 ... 
	
      
```

###  TiMidity and Jack 


TiMidity can be run with Jack output using the `-Oj`option. In a user-based environment such as Ubuntu you may need
to stop or pause PulseAudio, start the Jack server and then run TiMidity.
PulseAudion may be paused by e.g.

```

	
pasuspender cat
	
      
```


in one terminal. In another, start the Jack daemon
using ALSA input and output

```

	
jackd -dalsa
	
      
```


In a third terminal, run TiMidity

```

	
timidity -Oj 54154.mid
	
      
```


The links may be shown graphically by also running `qjackctl`.
