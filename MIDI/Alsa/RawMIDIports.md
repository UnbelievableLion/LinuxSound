
##  Raw MIDI ports 


From [RawMidi interface](http://www.alsa-project.org/alsa-doc/alsa-lib/rawmidi.html) 


   > [The] RawMidi Interface is designed to write or read raw (unchanged) MIDI data over the MIDI line without any timestamps defined in interface.


###  Raw MIDI phyical devices 


The raw MIDI interface is typically used to manage hardware
MIDI devices. For example, if I plug in an Edirol SD-20
synthesizer to a USB port, it shows under `amidi`as

```

      
$amidi -l
Dir Device    Name
IO  hw:2,0,0  SD-20 Part A
IO  hw:2,0,1  SD-20 Part B
I   hw:2,0,2  SD-20 MIDI
      
    
```


These names use the same pattern as Alsa playback and record
devices of `hw:...`.

###  Raw MIDI virtual devices 


The Linux kernel module `snd_virmidi`can create
virtual raw MIDI devices. First add the modules
( [Using TiMidity++ with ALSA raw MIDI](https://wiki.allegro.cc/index.php?title=Using_TiMidity%2B%2B_with_ALSA_raw_MIDI) and [AlsaMidiOverview](http://alsa.opensrc.org/AlsaMidiOverview) )

```

      
modprobe snd-seq snd-virmidi
      
    
```


This will bring virtual devices both into the ALSA raw MIDI and into the
ALSA sequencer spaces:

```

      
$amidi -l
Dir Device    Name
IO  hw:3,0    Virtual Raw MIDI (16 subdevices)
IO  hw:3,1    Virtual Raw MIDI (16 subdevices)
IO  hw:3,2    Virtual Raw MIDI (16 subdevices)
IO  hw:3,3    Virtual Raw MIDI (16 subdevices)

$aplaymidi -l
 Port    Client name                      Port name
 14:0    Midi Through                     Midi Through Port-0
 28:0    Virtual Raw MIDI 3-0             VirMIDI 3-0
 29:0    Virtual Raw MIDI 3-1             VirMIDI 3-1
 30:0    Virtual Raw MIDI 3-2             VirMIDI 3-2
 31:0    Virtual Raw MIDI 3-3             VirMIDI 3-3
      
    
```

###  Mapping MIDI clients into MIDI raw space 


Some programs/APIs use the Alsa sequencer space; others
use the Alsa raw MIDI space. Virtual ports allow a client
using one space to use a client from a different space.


For example, TiMidity can be run as a sequencer client by

```

      
timidity -iA -B2,8 -Os -EFreverb=0
      
    
```


This only shows in the sequencer space, not in the
raw MIDI space, and
shows to `aconnect -o`as

```

      
$aconnect -o
client 14: 'Midi Through' [type=kernel]
    0 'Midi Through Port-0'
client 28: 'Virtual Raw MIDI 3-0' [type=kernel]
    0 'VirMIDI 3-0     '
client 29: 'Virtual Raw MIDI 3-1' [type=kernel]
    0 'VirMIDI 3-1     '
client 30: 'Virtual Raw MIDI 3-2' [type=kernel]
    0 'VirMIDI 3-2     '
client 31: 'Virtual Raw MIDI 3-3' [type=kernel]
    0 'VirMIDI 3-3     '
client 128: 'TiMidity' [type=user]
    0 'TiMidity port 0 '
    1 'TiMidity port 1 '
    2 'TiMidity port 2 '
    3 'TiMidity port 3 '
      
    
```


while `aconnect -i`shows the virtual ports as

```

      
$aconnect -i
client 0: 'System' [type=kernel]
    0 'Timer           '
    1 'Announce        '
client 14: 'Midi Through' [type=kernel]
    0 'Midi Through Port-0'
client 28: 'Virtual Raw MIDI 3-0' [type=kernel]
    0 'VirMIDI 3-0     '
client 29: 'Virtual Raw MIDI 3-1' [type=kernel]
    0 'VirMIDI 3-1     '
client 30: 'Virtual Raw MIDI 3-2' [type=kernel]
    0 'VirMIDI 3-2     '
client 31: 'Virtual Raw MIDI 3-3' [type=kernel]
    0 'VirMIDI 3-3     '
      
    
```


Virtual Raw MIDI 3-0 can then be connected to TiMidity  port 0
by

```

      
aconnect 28:0 128:0
      
    
```


Clients can then send MIDI messages to the raw MIDI device `hw:3,0`and TiMidity will synthesize them.
We will use this in the next chapter by showing how
to replace the default
Java synthesizer by TiMidity.
