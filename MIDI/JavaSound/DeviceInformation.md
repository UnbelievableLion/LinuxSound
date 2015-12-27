
##  Device Information 


Device information is found by querying `MidiSystem`for its
list of `DeviceInfo`objects. Each information object contains
fields such as Name and Vendor. The actual device may be found using this
information object by `MidiSystem.getMidiDevice(info)`.
The device may then be queried for its receivers and transmitters and
its type as sequencer or synthesizer.


One annoying part is that you
cannot get a list of all the devices's transmitters and receivers, only those
that are _open_ . You can ask for the default transmitter and
receiver which will implicitly open them. So you can see that the list may
be empty before asking for the default, but will be non-empty afterwards
if there is a default! if there are no defaults, a `MidiUnavailableException`exception will be thrown.


The program is:

```cpp

	
      

import javax.sound.midi.*;
import java.util.*;

public class DeviceInfo {

    public static void main(String[] args) throws Exception {
	MidiDevice.Info[] devices;

	/*
	MidiDevice.Info[] info = p.getDeviceInfo();
	for (int m = 0; m < info.length; m++) {
	    System.out.println(info[m].toString());
	}
	*/

	System.out.println("MIDI devices:");
	devices = MidiSystem.getMidiDeviceInfo();
	for (MidiDevice.Info info: devices) {
	    System.out.println("    Name: " + info.toString() + 
			       ", Decription: " +
			       info.getDescription() + 
			       ", Vendor: " +
			       info.getVendor());
	    MidiDevice device = MidiSystem.getMidiDevice(info);
	    if (! device.isOpen()) {
		device.open();
	    }
	    if (device instanceof Sequencer) {
		System.out.println("        Device is a sequencer");
	    }
	    if (device instanceof Synthesizer) {
		System.out.println("        Device is a synthesizer");
	    }
	    System.out.println("        Open receivers:");
	    List<Receiver> receivers = device.getReceivers();
	    for (Receiver r: receivers) {
		System.out.println("            " + r.toString());
	    }
	    try {
		System.out.println("\n        Default receiver: " + 
				   device.getReceiver().toString());

		System.out.println("\n        Open receivers now:");
		receivers = device.getReceivers();
		for (Receiver r: receivers) {
		    System.out.println("            " + r.toString());
		}
	    } catch(MidiUnavailableException e) {
		System.out.println("        No default receiver");
	    }
	
	    System.out.println("\n        Open transmitters:");
	    List<Transmitter> transmitters = device.getTransmitters();
	    for (Transmitter t: transmitters) {
		System.out.println("            " + t.toString());
	    }
	    try {
		System.out.println("\n        Default transmitter: " + 
				   device.getTransmitter().toString());

		System.out.println("\n        Open transmitters now:");
		transmitters = device.getTransmitters();
		for (Transmitter t: transmitters) {
		    System.out.println("            " + t.toString());
		}
	    } catch(MidiUnavailableException e) {
		System.out.println("        No default transmitter");
	    }
	    device.close();
	}

	
	Sequencer sequencer = MidiSystem.getSequencer();
	System.out.println("Default system sequencer is " + 
			   sequencer.getDeviceInfo().toString());

	Synthesizer synthesizer = MidiSystem.getSynthesizer();
	System.out.println("Default system synthesizer is " + 
			   synthesizer.getDeviceInfo().toString());

    }
}
	
      
```


The output on my system is

```

	
MIDI devices:
    Name: Gervill, Decription: Software MIDI Synthesizer, Vendor: OpenJDK
        Device is a synthesizer
        Open receivers:

        Default receiver: com.sun.media.sound.SoftReceiver@72f2a824

        Open receivers now:
            com.sun.media.sound.SoftReceiver@72f2a824

        Open transmitters:
        No default transmitter
    Name: Real Time Sequencer, Decription: Software sequencer, Vendor: Oracle Corporation
        Device is a sequencer
        Open receivers:

        Default receiver: com.sun.media.sound.RealTimeSequencer$SequencerReceiver@c23c5ff

        Open receivers now:
            com.sun.media.sound.RealTimeSequencer$SequencerReceiver@c23c5ff

        Open transmitters:
        Default transmitter: com.sun.media.sound.RealTimeSequencer$SequencerTransmitter@4e13aa4e

        Open transmitters now:
            com.sun.media.sound.RealTimeSequencer$SequencerTransmitter@4e13aa4e
Default system sequencer is Real Time Sequencer
Default system synthesizer is Gervill
	
      
```
