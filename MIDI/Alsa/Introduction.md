
##  Introduction 


ALSA suplies a sequencer that can receive MIDI events and play them
      according to the timing information in the events. The clients
      taht can send such events are file readers such as `aplaymidi`or other sequencers. Clients can also read events as they should be played.
      Possible clients include splitters, routers or soft synthesizers such as
      Timidity.


Timidity can be run as ALSA sequencer client.
      From [
	The TiMidity Howto - Using TiMidity as the ALSA sequencer client
      ](http://linux-audio.com/TiMidity-howto.html) 

```

	
timidity -iA -B2,8 -Os -EFreverb=0
	
      
```


On my computer this produced

```

	
Requested buffer size 2048, fragment size 1024
ALSA pcm 'default' set buffer size 2048, period size 680 bytes
TiMidity starting in ALSA server mode
Opening sequencer port: 129:0 129:1 129:2 129:3
	
      
```


and then sat there waiting for a connection to be made.


FluidSynth can also be used as a server 
      ( [
	Ted's Linux MIDI Guide
      ](http://tedfelix.com/linux/linux-midi.html) ):

```

	
 fluidsynth --server --audio-driver=alsa -C0 -R1 -l /usr/share/soundfonts/FluidR3_GM.sf2 
	
      
```


The ALSA sequencer seds MIDI "wire" events. This does not include
      MIDI file events such as Text or Lyric Meta-events. This makes it
      pretty useless for a MIDI player. It is possible to modify the
      file reader `aplaymid`to send Meta Events to, say,
      a listener (like the Java MetaEventListener), but as these come
      from the file reader rather than the sequencer they generally arrive well
      before the time they will get sequenced to be played. Pity.


Programs such as `pykaraoke`make use of the ALSA sequencer.
      However, in order to get the timing of the lyrics right it includes
      a MIDI file parser and basically acts as a second sequencer just to
      extract and display the Text/Lyric events.
