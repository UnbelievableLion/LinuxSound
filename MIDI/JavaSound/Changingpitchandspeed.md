
##  Changing pitch and speed 


Changing the speed of playback of a MIDI file means changing
the  rate that MIDI messages are sent from the sequencer.
The Java sequencers have methods to control this such as `setTempoFactor`. The sequencer will respond to
this method by sending the messages at a different rate.


Changing the pitch of the notes can be done by altering the
pitch of the `NOTE_ON`and `NOTE_OFF`messages. The sequencer does not do this as it is unrelated
to time. The default MIDI `Receiver`just gets
MIDI messages and passes it onto its `Synthesizer`.
We can create our own `Receiver`and interpose
it between the default `Transmitter`and `Receiver`. This can examine MIDI messages
in transit and adjust the pitch of note on/off messages.


We look for input from the user of  ←, ↑, →, ↓ (ESC-[A, etc).
These then call the appropriate method. The program illustrating
this is an adaptation of the `SimpleMidiPlayer`given earlier in the chapter and is [AdaptableMidiPlayer.java](AdaptableMidiPlayer.java) :

```cpp

```
