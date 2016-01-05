
##  Using TiMidity instead of the default Gervill synthesizer 


The softsynth TiMidity can be run as a backend synthesizer using
the Alsa sequencer by

```
$timidity -iA -B2,8 -Os -EFreverb=0

Opening sequencer port: 128:0 128:1 128:2 128:3
```


(and similarly for Fluidsynth.). This is opened on ports 128:0 etc.


Unfortunately this is not directly visible to JavaSound which expects
either the default Gervill synthesizer or a raw MIDI synthesizer such
as a hardware synthesizer. As discussed in the [MIDI Alsa]( ../Alsa/) chapter, we can fix this by
using Alsa raw MIDI ports.


We add raw MIDI ports by

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


Virtual Raw MIDI port  3-0 can then be connected to TiMidity  port 0
by

```
aconnect 28:0 128:0
```


The final step in playing to TiMidity is to change one line
of [AdaptableMidiPlayer.java](AdaptableMidiPlayer.java) from

```
if (info.toString().equals("SD20 [hw:2,0,0]")) {
```


to

```
if (info.toString().equals("VirMIDI [hw:3,0,0]")) {
```
