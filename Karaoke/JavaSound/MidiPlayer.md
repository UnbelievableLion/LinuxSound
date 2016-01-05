
##  MidiPlayer 


The MidiPlayer creates a Sequence from the file.
Sequence information is required at many places, and so rather
than pass the sequence in parameters, it is stored in a singleton
(static) object, a SequenceInformation. This makes the sequence effectively
a global object to the system.


The player then gets the default sequencer and transmits MIDI events
to two Receiver objects: the default synthesizer to play the events
and a DisplayReceiver to manage all the GUI handling. The Sequencer
method getTransmitter() is mis-named: each time it is called it returns
a _new_ transmitter, each playing the same events to their
respective receivers.
From [Java SE Documentation: Chapter 10: Transmitting and Receiving MIDI Messages](http://docs.oracle.com/javase/7/docs/technotes/guides/sound/programmer_guide/chapter10.html) 


   > This code [in their example] introduces a dual invocation of the MidiDevice.getTransmitter method,
assigning the results to inPortTrans1 and inPortTrans2. As mentioned earlier,
a device can own multiple transmitters and receivers. Each time
MidiDevice.getTransmitter() is invoked for a given device, another transmitter
is returned, until no more are available, at which time an exception will be thrown.



That way, the sequencer can send to two receivers.


Receivers do not get MetaMessages. These contain information such as Text or Lyric
events. The DisplayReceiver is registered as an MetaEventListener so that it can manage
these events as well as other events.


The MidiPlayer is:

```cpp
import javax.sound.midi.MidiSystem;
import javax.sound.midi.InvalidMidiDataException;
import javax.sound.midi.Sequence;
import javax.sound.midi.Receiver;
import javax.sound.midi.Sequencer;
import javax.sound.midi.Transmitter;
import javax.sound.midi.MidiChannel;
import javax.sound.midi.MidiDevice;
import javax.sound.midi.Synthesizer;
import javax.sound.midi.ShortMessage;
import javax.sound.midi.SysexMessage;

import java.io.File;
import java.io.IOException;

public class MidiPlayer {

    private DisplayReceiver receiver;

    public  void playMidiFile(String strFilename) throws Exception {
	File	midiFile = new File(strFilename);

	/*
	 *	We try to get a Sequence object, loaded with the content
	 *	of the MIDI file.
	 */
	Sequence	sequence = null;
	try {
	    sequence = MidiSystem.getSequence(midiFile);
	}
	catch (InvalidMidiDataException e) {
	    e.printStackTrace();
	    System.exit(1);
	}
	catch (IOException e) {
	    e.printStackTrace();
	    System.exit(1);
	}

	if (sequence == null) {
	    out("Cannot retrieve Sequence.");
	} else {
	    SequenceInformation.setSequence(sequence);
	    playMidi(sequence);
	}
    }

    public  void playMidi(Sequence sequence) throws Exception {

        Sequencer sequencer = MidiSystem.getSequencer(true);
        sequencer.open();
        sequencer.setSequence(sequence); 

	receiver = new DisplayReceiver(sequencer);
	sequencer.getTransmitter().setReceiver(receiver);
	sequencer.addMetaEventListener(receiver);

	if (sequencer instanceof Synthesizer) {
	    Debug.println("Sequencer is also a synthesizer");
	} else {
	    Debug.println("Sequencer is not a synthesizer");
	}
        //sequencer.start();

	/*
	Synthesizer synthesizer = MidiSystem.getSynthesizer();  
	synthesizer.open();  

	if (synthesizer.getDefaultSoundbank() == null) {
	    // then you know that java sound is using the hardware soundbank
	    Debug.println("Synthesizer using h/w soundbank");
	} else Debug.println("Synthesizer using s/w soundbank");


	Receiver synthReceiver = synthesizer.getReceiver();  
	Transmitter seqTransmitter = sequencer.getTransmitter();  
	seqTransmitter.setReceiver(synthReceiver); 
	MidiChannel[] channels = synthesizer.getChannels(); 
	Debug.println("Num channels is " + channels.length);
	*/
        sequencer.start();

	/* default synth doesn't support pitch bending
	Synthesizer synthesizer = MidiSystem.getSynthesizer();  
	MidiChannel[] channels = synthesizer.getChannels(); 
	for (int i = 0; i < channels.length; i++) {
	    System.out.printf("Channel %d has bend %d\n", i, channels[i].getPitchBend());
	    channels[i].setPitchBend(16000);
	    System.out.printf("Channel %d now has bend %d\n", i, channels[i].getPitchBend());
	}
	*/

	/* set volume - doesn't work */
	/*
	for (int i = 0; i < channels.length; i++) {
	    channels[i].controlChange(7, 0);
	}
	*/
	/*
	System.out.println("Turning notes off");
	for (int i = 0; i < channels.length; i++) {
	    channels[i].allNotesOff();
	    channels[i].allSoundOff();
	}
	*/

	/* set volume - doesn't work either */
	/*
	try {
	    Thread.sleep(5000);
	} catch (InterruptedException e) {
	    // TODO Auto-generated catch block
	    e.printStackTrace();
	}
	
	if (synthReceiver == MidiSystem.getReceiver()) 
	    System.out.println("Reciver is default");
	else
	    System.out.println("Reciver is not default");
	System.out.println("Receiver is " + synthReceiver.toString());
	//synthReceiver = MidiSystem.getReceiver();
	System.out.println("Receiver is now " + synthReceiver.toString());
	ShortMessage volMessage = new ShortMessage();
	int midiVolume = 1;
	for (Receiver rec: synthesizer.getReceivers()) {
	    System.out.println("Setting vol on recveiver " + rec.toString());
	for (int i = 0; i < channels.length; i++) {
	    try {
		// volMessage.setMessage(ShortMessage.CONTROL_CHANGE, i, 123, midiVolume);
		volMessage.setMessage(ShortMessage.CONTROL_CHANGE, i, 7, midiVolume);
	    } catch (InvalidMidiDataException e) {
		e.printStackTrace();
}
	    synthReceiver.send(volMessage, -1);
	    rec.send(volMessage, -1);
	}
	}
	System.out.println("Changed midi volume");
	*/
	/* master volume control using sysex */
	/* http://www.blitter.com/~russtopia/MIDI/~jglatt/tech/midispec/mastrvol.htm */
	/*
	SysexMessage sysexMessage = new SysexMessage();
	/* volume values from http://www.bandtrax.com.au/sysex.htm */
	/* default volume 0x7F * 128 + 0x7F from */
	/*
	byte[] data = {(byte) 0xF0, (byte) 0x7F, (byte) 0x7F, (byte) 0x04, 
		       (byte) 0x01, (byte) 0x0, (byte) 0x7F, (byte) 0xF7};
	sysexMessage.setMessage(data, data.length);
	synthReceiver.send(sysexMessage, -1);
	for (Receiver rec: synthesizer.getReceivers()) {
	    System.out.println("Setting vol on recveiver " + rec.toString());
	    rec.send(sysexMessage, -1);
	}
	*/
     }


    public DisplayReceiver getReceiver() {
	return receiver;
    }

    private static void out(String strMessage)
    {
	System.out.println(strMessage);
    }
}
```
