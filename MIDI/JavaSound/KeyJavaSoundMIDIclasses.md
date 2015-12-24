
##  Key JavaSound MIDI classes

+ The `MidiSystem`class is the entry point for all
	  MIDI classes.
+ A `MidiDevice`includes synthesizers, sequencers, 
	  MIDI input ports, and MIDI output ports
+ A `Transmitter`sends `MidiEvent`objects
	  to a `Receiver`. A `Transmitter`is the _source_ of MIDI events and a `Receiver`is a _consumer_ of events.
+ "A `Sequencer`is a device for capturing and playing back sequences of MIDI events. 
	  It has transmitters, because it typically sends the MIDI messages stored in the 
	  sequence to another device, such as a synthesizer or MIDI output port. 
	  It also has receivers, because it can capture MIDI messages and store them in a sequence."
	  ( [
	    Java Sound Programmers Manual: Chapter 8: Overview of the MIDI Package
	  ](http://docs.oracle.com/javase/7/docs/technotes/guides/sound/programmer_guide/chapter8.html#118852) )
+ "A `Synthesizer`is a device for generating sound. 
	  It's the only object in the javax.sound.midi package that produces audio data"
	  ( [
	    Java Sound Programmers Manual: Chapter 8: Overview of the MIDI Package
	  ](http://docs.oracle.com/javase/7/docs/technotes/guides/sound/programmer_guide/chapter8.html#118852) )