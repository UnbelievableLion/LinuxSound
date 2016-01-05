
##  Playing a file to an external MIDI synthesizer 


I have an Edirol Studio Canvas SD-20 synthesizer which I bought
for a few hundred Australian dollars. This plugs into a PC
through a USB port. Alsa recognises this by

```
$ amidi -l
Dir Device    Name
IO  hw:2,0,0  SD-20 Part A
IO  hw:2,0,1  SD-20 Part B
I   hw:2,0,2  SD-20 MIDI
```


The list of `MidiDevice.Info`device information
lists `hw:2,0,0`twice, once for input
and once for output, and similarly for the other values.
The device information can be identified by the `toString`method, which returns values such as `"SD20 [hw:2,0,0]"`.
From the device information the device can be found as before
using `MidiSystem.getMidiDevice(info)`.
The input and output devices can be distinguished by the number
of `maxOutputReceivers`it supports: zero means none,
while any other value (including minus one!) means it has
a MIDI receiver. Selecting an external receiver is done
by code like

```cpp
Receiver	synthReceiver = null;
		MidiDevice.Info[] devices;
		devices = MidiSystem.getMidiDeviceInfo();
		
		for (MidiDevice.Info info: devices) {
		    System.out.println("    Name: " + info.toString() + 
				       ", Decription: " +
				       info.getDescription() + 
				       ", Vendor: " +
				       info.getVendor());
		    if (info.toString().equals("SD20 [hw:2,0,0]")) {
			MidiDevice device = MidiSystem.getMidiDevice(info);
			if (device.getMaxReceivers() != 0) {
			    try {
				device.open();
				System.out.println("  max receivers: " + device.getMaxReceivers());
				receiver = device.getReceiver();
				System.out.println("Found a receiver");
				break;
			    } catch(Exception e) {}
			}
		    }
		}
```


Playing an audio file to my SD-20 is done by

```cpp
/*
 *	ExternalMidiPlayer.java
 *
 *	This file adapted from SimpleMidiPlayer of jsresources.org
 */

/*
 * Copyright (c) 1999 - 2001 by Matthias Pfisterer
 * Copyright (c) 2015 Jan Newmarch
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * - Redistributions of source code must retain the above copyright notice,
 *   this list of conditions and the following disclaimer.
 * - Redistributions in binary form must reproduce the above copyright
 *   notice, this list of conditions and the following disclaimer in the
 *   documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 */

/*
|<---            this code is formatted to fit into 80 columns             --->|
*/

import java.io.File;
import java.io.IOException;

import javax.sound.midi.InvalidMidiDataException;
import javax.sound.midi.MidiSystem;
import javax.sound.midi.MidiUnavailableException;
import javax.sound.midi.MetaEventListener;
import javax.sound.midi.MetaMessage;
import javax.sound.midi.Sequence;
import javax.sound.midi.Sequencer;
import javax.sound.midi.Synthesizer;
import javax.sound.midi.Receiver;
import javax.sound.midi.Transmitter;
import javax.sound.midi.MidiChannel;
import javax.sound.midi.ShortMessage;
import javax.sound.midi.MidiDevice;
import javax.sound.midi.MidiDeviceReceiver;



/**	<titleabbrev>SimpleMidiPlayer</titleabbrev>
	<title>Playing a MIDI file (easy)</title>

	<formalpara><title>Purpose</title>
	<para>Plays a single MIDI file.</para></formalpara>

	<formalpara><title>Usage</title>
	<para>
	<cmdsynopsis>
	<command>java SimpleMidiPlayer</command>
	<arg choice="plain"><replaceable>midifile</replaceable></arg>
	</cmdsynopsis>
	</para></formalpara>

	<formalpara><title>Parameters</title>
	<variablelist>
	<varlistentry>
	<term><option><replaceable>midifile</replaceable></option></term>
	<listitem><para>the name of the MIDI file that should be
	played</para></listitem>
	</varlistentry>
	</variablelist>
	</formalpara>

	<formalpara><title>Bugs, limitations</title>

	<para>This program always uses the default Sequencer and the default
	Synthesizer to play on. For using non-default sequencers,
	synthesizers or to play on an external MIDI port, see
	<olink targetdoc="MidiPlayer"
	targetptr="MidiPlayer">MidiPlayer</olink>.</para>
	</formalpara>

	<formalpara><title>Source code</title>
	<para>
	<ulink url="SimpleMidiPlayer.java.html">SimpleMidiPlayer.java</ulink>
	</para>
	</formalpara>

*/
public class ExternalMidiPlayer
{
	/*
	  These variables are not really intended to be static in a
	  meaning of (good) design. They are used by inner classes, so they
	  can't just be automatic variables. There were three possibilities:

	  a) make them instance variables and instantiate the object they
	  belong to. This is clean (and is how you should do it in a real
	  application), but would have made the example more complex.

	  b) make them automatic final variables inside main(). Design-wise,
	  this is better than static, but automatic final is something that
	  is still like some black magic to me.

	  c) make them static variables, as it is done here. This is quite bad
	  design, because if you have global variables, you can't easily do
	  the thing they are used for two times in concurrency without risking
	  indeterministic behaviour. However, it makes the example easy to
	  read.
	 */
	private static Sequencer	sm_sequencer = null;
	private static Synthesizer	sm_synthesizer = null;
        private static Receiver receiver = null;


	public static void main(String[] args) throws MidiUnavailableException
	{
		/*
		 *	We check if there is no command-line argument at all
		 *	or the first one is '-h'.
		 *	If so, we display the usage message and
		 *	exit.
		 */
		if (args.length == 0 || args[0].equals("-h"))
		{
			printUsageAndExit();
		}

		String	strFilename = args[0];
		File	midiFile = new File(strFilename);

		/*
		 *	We read in the MIDI file to a Sequence object.
		 *	This object is set at the Sequencer later.
		 */
		Sequence	sequence = null;
		try
		{
			sequence = MidiSystem.getSequence(midiFile);
		}
		catch (InvalidMidiDataException e)
		{
			/*
			 *	In case of an exception, we dump the exception
			 *	including the stack trace to the console.
			 *	Then, we exit the program.
			 */
			e.printStackTrace();
			System.exit(1);
		}
		catch (IOException e)
		{
			/*
			 *	In case of an exception, we dump the exception
			 *	including the stack trace to the console.
			 *	Then, we exit the program.
			 */
			e.printStackTrace();
			System.exit(1);
		}

		/*
		 *	Now, we need a Sequencer to play the sequence.
		 *	Here, we simply request the default sequencer.
		 *      With an argument of false, it does not create
		 *      a default syntesizer. With an argument of true
		 *      it is already linked to the default synthesizer
		 */
		try
		{
			sm_sequencer = MidiSystem.getSequencer(false);
		}
		catch (MidiUnavailableException e)
		{
			e.printStackTrace();
			System.exit(1);
		}
		if (sm_sequencer == null)
		{
			out("SimpleMidiPlayer.main(): can't get a Sequencer");
			System.exit(1);
		}

		/*
		 *	There is a bug in the Sun jdk1.3/1.4.
		 *	It prevents correct termination of the VM.
		 *	So we have to exit ourselves.
		 *	To accomplish this, we register a Listener to the Sequencer.
		 *	It is called when there are "meta" events. Meta event
		 *	47 is end of track.
		 *
		 *	Thanks to Espen Riskedal for finding this trick.
		 */
		sm_sequencer.addMetaEventListener(new MetaEventListener()
			{
				public void meta(MetaMessage event)
				{
					if (event.getType() == 47)
					{
						sm_sequencer.close();
						if (sm_synthesizer != null)
						{
							sm_synthesizer.close();
						}
						System.exit(0);
					}
				}
			});

		/*
		 *	The Sequencer is still a dead object.
		 *	We have to open() it to become live.
		 *	This is necessary to allocate some ressources in
		 *	the native part.
		 */
		/*
		try
		{
		    sm_sequencer.open();
		}
		catch (MidiUnavailableException e)
		{
			e.printStackTrace();
			System.exit(1);
		}
		*/
		/*
		 *	Next step is to tell the Sequencer which
		 *	Sequence it has to play. In this case, we
		 *	set it as the Sequence object created above.
		 */
		try
		{
			sm_sequencer.setSequence(sequence);
		}
		catch (InvalidMidiDataException e)
		{
			e.printStackTrace();
			System.exit(1);
		}

		/*
		 *	Now, we set up the destinations the Sequence should be
		 *	played on.
		 */
		Receiver	synthReceiver = null;
		MidiDevice.Info[] devices;
		devices = MidiSystem.getMidiDeviceInfo();
		
		for (MidiDevice.Info info: devices) {
		    System.out.println("    Name: " + info.toString() + 
				       ", Decription: " +
				       info.getDescription() + 
				       ", Vendor: " +
				       info.getVendor());
		    if (info.toString().equals("SD20 [hw:2,0,0]")) {
			MidiDevice device = MidiSystem.getMidiDevice(info);
			if (device.getMaxReceivers() != 0) {
			    try {
				device.open();
				System.out.println("  max receivers: " + device.getMaxReceivers());
				receiver = device.getReceiver();
				System.out.println("Found a receiver");
				break;
			    } catch(Exception e) {}
			}
		    }
		}
		
		if (receiver == null) {
		    System.out.println("Reeciver is null");
		    System.exit(1);
		}
		try
		    {
			Transmitter	seqTransmitter = sm_sequencer.getTransmitter();
			seqTransmitter.setReceiver(receiver);
		    }
		catch (MidiUnavailableException e)
		    {
			e.printStackTrace();
		    }

		/*
		 *	Now, we can start over.
		 */
		sm_sequencer.open();
		sm_sequencer.start();

		try {
		    Thread.sleep(5000);
		} catch (InterruptedException e) {
		    // TODO Auto-generated catch block
		    e.printStackTrace();
		}
		
	}



	private static void printUsageAndExit()
	{
		out("SimpleMidiPlayer: usage:");
		out("\tjava SimpleMidiPlayer <midifile>");
		System.exit(1);
	}



	private static void out(String strMessage)
	{
		System.out.println(strMessage);
	}
}



/*** SimpleMidiPlayer.java ***/
```
