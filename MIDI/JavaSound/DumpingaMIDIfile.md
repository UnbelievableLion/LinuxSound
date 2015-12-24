
##  Dumping a MIDI file 


These two programs from jsresources.org dump a MIDI file to the console.
      The `MidiSystem`creates a `Sequence`from a file.
      Each track of the sequence is looped through and each event within each
      track is examined. While it would be possible to print _in situ_ ,
      each event is passed to a `Receiver`object which in this case
      is `DumpReceiver`. That object could do anything, but in this case
      just prints the event to stdout.


DumpSequence.java is

```

      
      /*
 *	DumpSequence.java
 *
 *	This file is part of jsresources.org
 */

/*
 * Copyright (c) 1999, 2000 by Matthias Pfisterer
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

import javax.sound.midi.MidiSystem;
import javax.sound.midi.InvalidMidiDataException;
import javax.sound.midi.Sequence;
import javax.sound.midi.Track;
import javax.sound.midi.MidiEvent;
import javax.sound.midi.MidiMessage;
import javax.sound.midi.ShortMessage;
import javax.sound.midi.MetaMessage;
import javax.sound.midi.SysexMessage;
import javax.sound.midi.Receiver;




/**	<titleabbrev>DumpSequence</titleabbrev>
	<title>Displaying the content of a MIDI file</title>

	<formalpara><title>Purpose</title>
	<para>Dumps the decoded content of a MIDI file to the console.</para>
	</formalpara>

	<formalpara><title>Usage</title>
	<para>
	<cmdsynopsis><command>java DumpSequence</command>
	<arg choice="plain"><replaceable class="parameter">midifile</replaceable></arg>
	</cmdsynopsis>
	</para></formalpara>

	<formalpara><title>Parameters</title>
	<variablelist>
	<varlistentry>
	<term><replaceable class="parameter">midifile</replaceable></term>
	<listitem><para>the filename of the MIDI file that should be displayed</para></listitem>
	</varlistentry>
	</variablelist>
	</formalpara>

	<formalpara><title>Bugs, limitations</title>
	<para>Meta and system common events are not displayed in detail.</para>
	</formalpara>

	<formalpara><title>Source code</title>
	<para>
	<ulink url="DumpSequence.java.html">DumpSequence.java</ulink>,
	<ulink url="DumpReceiver.java.html">DumpReceiver.java</ulink>
	</para>
	</formalpara>

*/
public class DumpSequence
{
    private static String[]	sm_astrKeyNames = {"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"};

    private static Receiver		sm_receiver = new DumpReceiver(System.out, true);




    public static void main(String[] args)
    {
	/*
	 *	We check that there is exactely one command-line
	 *	argument. If not, we display the usage message and
	 *	exit.
	 */
	if (args.length != 1)
	    {
		out("DumpSequence: usage:");
		out("\tjava DumpSequence <midifile>");
		System.exit(1);
	    }
	/*
	 *	Now, that we're shure there is an argument, we take it as
	 *	the filename of the soundfile we want to play.
	 */
	String	strFilename = args[0];
	File	midiFile = new File(strFilename);

	/*
	 *	We try to get a Sequence object, which the content
	 *	of the MIDI file.
	 */
	Sequence	sequence = null;
	try
	    {
		sequence = MidiSystem.getSequence(midiFile);
	    }
	catch (InvalidMidiDataException e)
	    {
		e.printStackTrace();
		System.exit(1);
	    }
	catch (IOException e)
	    {
		e.printStackTrace();
		System.exit(1);
	    }

	/*
	 *	And now, we output the data.
	 */
	if (sequence == null)
	    {
		out("Cannot retrieve Sequence.");
	    }
	else
	    {
		out("---------------------------------------------------------------------------");
		out("File: " + strFilename);
		out("---------------------------------------------------------------------------");
		out("Length: " + sequence.getTickLength() + " ticks");
		out("Duration: " + sequence.getMicrosecondLength() + " microseconds");
		out("---------------------------------------------------------------------------");
		float	fDivisionType = sequence.getDivisionType();
		String	strDivisionType = null;
		if (fDivisionType == Sequence.PPQ)
		    {
			strDivisionType = "PPQ";
		    }
		else if (fDivisionType == Sequence.SMPTE_24)
		    {
			strDivisionType = "SMPTE, 24 frames per second";
		    }
		else if (fDivisionType == Sequence.SMPTE_25)
		    {
			strDivisionType = "SMPTE, 25 frames per second";
		    }
		else if (fDivisionType == Sequence.SMPTE_30DROP)
		    {
			strDivisionType = "SMPTE, 29.97 frames per second";
		    }
		else if (fDivisionType == Sequence.SMPTE_30)
		    {
			strDivisionType = "SMPTE, 30 frames per second";
		    }

		out("DivisionType: " + strDivisionType);

		String	strResolutionType = null;
		if (sequence.getDivisionType() == Sequence.PPQ)
		    {
			strResolutionType = " ticks per beat";
		    }
		else
		    {
			strResolutionType = " ticks per frame";
		    }
		out("Resolution: " + sequence.getResolution() + strResolutionType);
		out("---------------------------------------------------------------------------");
		Track[]	tracks = sequence.getTracks();
		for (int nTrack = 0; nTrack < tracks.length; nTrack++)
		    {
			out("Track " + nTrack + ":");
			out("-----------------------");
			Track	track = tracks[nTrack];
			for (int nEvent = 0; nEvent < track.size(); nEvent++)
			    {
				MidiEvent	event = track.get(nEvent);
				output(event);
			    }
			out("---------------------------------------------------------------------------");
		    }
		// TODO: getPatchList()
	    }
    }


    public static void output(MidiEvent event)
    {
	MidiMessage	message = event.getMessage();
	long		lTicks = event.getTick();
	sm_receiver.send(message, lTicks);
    }



    private static void out(String strMessage)
    {
	System.out.println(strMessage);
    }
}



/*** DumpSequence.java ***/


      
    
```


DmpReceiver.java is

```

      
      /*
 *	DumpReceiver.java
 *
 *	This file is part of jsresources.org
 */

/*
 * Copyright (c) 1999 - 2001 by Matthias Pfisterer
 * Copyright (c) 2003 by Florian Bomers
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

import	java.io.PrintStream;

import	javax.sound.midi.MidiSystem;
import	javax.sound.midi.InvalidMidiDataException;
import	javax.sound.midi.Sequence;
import	javax.sound.midi.Track;
import	javax.sound.midi.MidiEvent;
import	javax.sound.midi.MidiMessage;
import	javax.sound.midi.ShortMessage;
import	javax.sound.midi.MetaMessage;
import	javax.sound.midi.SysexMessage;
import	javax.sound.midi.Receiver;



/**	Displays the file format information of a MIDI file.
 */
public class DumpReceiver
	implements	Receiver
{

	public static long seByteCount = 0;
	public static long smByteCount = 0;
	public static long seCount = 0;
	public static long smCount = 0;

	private static final String[]		sm_astrKeyNames = {"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"};

	private static final String[]		sm_astrKeySignatures = {"Cb", "Gb", "Db", "Ab", "Eb", "Bb", "F", "C", "G", "D", "A", "E", "B", "F#", "C#"};
	private static final String[]		SYSTEM_MESSAGE_TEXT =
	{
		"System Exclusive (should not be in ShortMessage!)",
		"MTC Quarter Frame: ",
		"Song Position: ",
		"Song Select: ",
		"Undefined",
		"Undefined",
		"Tune Request",
		"End of SysEx (should not be in ShortMessage!)",
		"Timing clock",
		"Undefined",
		"Start",
		"Continue",
		"Stop",
		"Undefined",
		"Active Sensing",
		"System Reset"
	};

	private static final String[]		QUARTER_FRAME_MESSAGE_TEXT =
	{
		"frame count LS: ",
		"frame count MS: ",
		"seconds count LS: ",
		"seconds count MS: ",
		"minutes count LS: ",
		"minutes count MS: ",
		"hours count LS: ",
		"hours count MS: "
	};

	private static final String[]		FRAME_TYPE_TEXT =
	{
		"24 frames/second",
		"25 frames/second",
		"30 frames/second (drop)",
		"30 frames/second (non-drop)",
	};

	private PrintStream		m_printStream;
	private boolean			m_bDebug;
	private boolean			m_bPrintTimeStampAsTicks;



	public DumpReceiver(PrintStream printStream)
	{
		this(printStream, false);
	}


	public DumpReceiver(PrintStream printStream,
			    boolean bPrintTimeStampAsTicks)
	{
		m_printStream = printStream;
		m_bDebug = false;
		m_bPrintTimeStampAsTicks = bPrintTimeStampAsTicks;
	}



	public void close()
	{
	}



	public void send(MidiMessage message, long lTimeStamp)
	{
		String	strMessage = null;
		if (message instanceof ShortMessage)
		{
			strMessage = decodeMessage((ShortMessage) message);
		}
		else if (message instanceof SysexMessage)
		{
			strMessage = decodeMessage((SysexMessage) message);
		}
		else if (message instanceof MetaMessage)
		{
			strMessage = decodeMessage((MetaMessage) message);
		}
		else
		{
			strMessage = "unknown message type";
		}
		String	strTimeStamp = null;
		if (m_bPrintTimeStampAsTicks)
		{
			strTimeStamp = "tick " + lTimeStamp + ": ";
		}
		else
		{
			if (lTimeStamp == -1L)
			{
				strTimeStamp = "timestamp [unknown]: ";
			}
			else
			{
				strTimeStamp = "timestamp " + lTimeStamp + " us: ";
			}
		}
		m_printStream.println(strTimeStamp + strMessage);
	}



	public String decodeMessage(ShortMessage message)
	{
		String	strMessage = null;
		switch (message.getCommand())
		{
		case 0x80:
			strMessage = "note Off " + getKeyName(message.getData1()) + " velocity: " + message.getData2();
			break;

		case 0x90:
			strMessage = "note On " + getKeyName(message.getData1()) + " velocity: " + message.getData2();
			break;

		case 0xa0:
			strMessage = "polyphonic key pressure " + getKeyName(message.getData1()) + " pressure: " + message.getData2();
			break;

		case 0xb0:
			strMessage = "control change " + message.getData1() + " value: " + message.getData2();
			break;

		case 0xc0:
			strMessage = "program change " + message.getData1();
			break;

		case 0xd0:
			strMessage = "key pressure " + getKeyName(message.getData1()) + " pressure: " + message.getData2();
			break;

		case 0xe0:
			strMessage = "pitch wheel change " + get14bitValue(message.getData1(), message.getData2());
			break;

		case 0xF0:
			strMessage = SYSTEM_MESSAGE_TEXT[message.getChannel()];
			switch (message.getChannel())
			{
			case 0x1:
				int	nQType = (message.getData1() & 0x70) >> 4;
				int	nQData = message.getData1() & 0x0F;
				if (nQType == 7)
				{
					nQData = nQData & 0x1;
				}
				strMessage += QUARTER_FRAME_MESSAGE_TEXT[nQType] + nQData;
				if (nQType == 7)
				{
					int	nFrameType = (message.getData1() & 0x06) >> 1;
					strMessage += ", frame type: " + FRAME_TYPE_TEXT[nFrameType];
				}
				break;

			case 0x2:
				strMessage += get14bitValue(message.getData1(), message.getData2());
				break;

			case 0x3:
				strMessage += message.getData1();
				break;
			}
			break;

		default:
			strMessage = "unknown message: status = " + message.getStatus() + ", byte1 = " + message.getData1() + ", byte2 = " + message.getData2();
			break;
		}
		if (message.getCommand() != 0xF0)
		{
			int	nChannel = message.getChannel() + 1;
			String	strChannel = "channel " + nChannel + ": ";
			strMessage = strChannel + strMessage;
		}
		smCount++;
		smByteCount+=message.getLength();
		return "["+getHexString(message)+"] "+strMessage;
	}



	public String decodeMessage(SysexMessage message)
	{
		byte[]	abData = message.getData();
		String	strMessage = null;
		// System.out.println("sysex status: " + message.getStatus());
		if (message.getStatus() == SysexMessage.SYSTEM_EXCLUSIVE)
		{
			strMessage = "Sysex message: F0" + getHexString(abData);
		}
		else if (message.getStatus() == SysexMessage.SPECIAL_SYSTEM_EXCLUSIVE)
		{
			strMessage = "Continued Sysex message F7" + getHexString(abData);
			seByteCount--; // do not count the F7
		}
		seByteCount += abData.length + 1;
		seCount++; // for the status byte
		return strMessage;
	}



	public String decodeMessage(MetaMessage message)
	{
		byte[]	abMessage = message.getMessage();
		byte[]	abData = message.getData();
		int	nDataLength = message.getLength();
		String	strMessage = null;
		//System.out.println("data array length: " + abData.length);
		switch (message.getType())
		{
		case 0:
		        int	nSequenceNumber;
		        if (abData.length == 0)
			    nSequenceNumber = 0;
		        else
			    nSequenceNumber = ((abData[0] & 0xFF) << 8) | (abData[1] & 0xFF);
			strMessage = "Sequence Number: " + nSequenceNumber;
			break;

		case 1:
			String	strText = new String(abData);
			strMessage = "Text Event: " + strText;
			break;

		case 2:
			String	strCopyrightText = new String(abData);
			strMessage = "Copyright Notice: " + strCopyrightText;
			break;

		case 3:
			String	strTrackName = new String(abData);
			strMessage = "Sequence/Track Name: " +  strTrackName;
			break;

		case 4:
			String	strInstrumentName = new String(abData);
			strMessage = "Instrument Name: " + strInstrumentName;
			break;

		case 5:
			String	strLyrics = new String(abData);
			if (strLyrics.equals("\r\n"))
			    strLyrics = "\\n";
			strMessage = "Lyric: " + strLyrics;
			break;

		case 6:
			String	strMarkerText = new String(abData);
			strMessage = "Marker: " + strMarkerText;
			break;

		case 7:
			String	strCuePointText = new String(abData);
			strMessage = "Cue Point: " + strCuePointText;
			break;

		case 0x20:
			int	nChannelPrefix = abData[0] & 0xFF;
			strMessage = "MIDI Channel Prefix: " + nChannelPrefix;
			break;

		case 0x2F:
			strMessage = "End of Track";
			break;

		case 0x51:
			int	nTempo = ((abData[0] & 0xFF) << 16)
					| ((abData[1] & 0xFF) << 8)
					| (abData[2] & 0xFF);           // tempo in microseconds per beat
			float bpm = convertTempo(nTempo);
			// truncate it to 2 digits after dot
			bpm = (float) (Math.round(bpm*100.0f)/100.0f);
			strMessage = "Set Tempo: "+bpm+" bpm";
			break;

		case 0x54:
			// System.out.println("data array length: " + abData.length);
			strMessage = "SMTPE Offset: "
				+ (abData[0] & 0xFF) + ":"
				+ (abData[1] & 0xFF) + ":"
				+ (abData[2] & 0xFF) + "."
				+ (abData[3] & 0xFF) + "."
				+ (abData[4] & 0xFF);
			break;

		case 0x58:
			strMessage = "Time Signature: "
				+ (abData[0] & 0xFF) + "/" + (1 << (abData[1] & 0xFF))
				+ ", MIDI clocks per metronome tick: " + (abData[2] & 0xFF)
				+ ", 1/32 per 24 MIDI clocks: " + (abData[3] & 0xFF);
			break;

		case 0x59:
			String	strGender = (abData[1] == 1) ? "minor" : "major";
			strMessage = "Key Signature: " + sm_astrKeySignatures[abData[0] + 7] + " " + strGender;
			break;

		case 0x7F:
			// TODO: decode vendor code, dump data in rows
			String	strDataDump = getHexString(abData);
			strMessage = "Sequencer-Specific Meta event: " + strDataDump;
			break;

		default:
			String	strUnknownDump = getHexString(abData);
			strMessage = "unknown Meta event: " + strUnknownDump;
			break;

		}
		return strMessage;
	}



	public static String getKeyName(int nKeyNumber)
	{
		if (nKeyNumber > 127)
		{
			return "illegal value";
		}
		else
		{
			int	nNote = nKeyNumber % 12;
			int	nOctave = nKeyNumber / 12;
			return sm_astrKeyNames[nNote] + (nOctave - 1);
		}
	}


	public static int get14bitValue(int nLowerPart, int nHigherPart)
	{
		return (nLowerPart & 0x7F) | ((nHigherPart & 0x7F) << 7);
	}



	private static int signedByteToUnsigned(byte b)
	{
		return b & 0xFF;
	}

	// convert from microseconds per quarter note to beats per minute and vice versa
	private static float convertTempo(float value) {
		if (value <= 0) {
			value = 0.1f;
		}
		return 60000000.0f / value;
	}



	private static char hexDigits[] = 
	   {'0', '1', '2', '3', 
	    '4', '5', '6', '7', 
	    '8', '9', 'A', 'B', 
	    'C', 'D', 'E', 'F'};

	public static String getHexString(byte[] aByte)
	{
		StringBuffer	sbuf = new StringBuffer(aByte.length * 3 + 2);
		for (int i = 0; i < aByte.length; i++)
		{
			sbuf.append(' ');
			sbuf.append(hexDigits[(aByte[i] & 0xF0) >> 4]);
			sbuf.append(hexDigits[aByte[i] & 0x0F]);
			/*byte	bhigh = (byte) ((aByte[i] &  0xf0) >> 4);
			sbuf.append((char) (bhigh > 9 ? bhigh + 'A' - 10: bhigh + '0'));
			byte	blow = (byte) (aByte[i] & 0x0f);
			sbuf.append((char) (blow > 9 ? blow + 'A' - 10: blow + '0'));*/
		}
		return new String(sbuf);
	}
	
	private static String intToHex(int i) {
		return ""+hexDigits[(i & 0xF0) >> 4]
		         +hexDigits[i & 0x0F];
	}

	public static String getHexString(ShortMessage sm)
	{
		// bug in J2SDK 1.4.1
		// return getHexString(sm.getMessage());
		int status = sm.getStatus();
		String res = intToHex(sm.getStatus());
		// if one-byte message, return
		switch (status) {
			case 0xF6:			// Tune Request
			case 0xF7:			// EOX
	    		// System real-time messages
			case 0xF8:			// Timing Clock
			case 0xF9:			// Undefined
			case 0xFA:			// Start
			case 0xFB:			// Continue
			case 0xFC:			// Stop
			case 0xFD:			// Undefined
			case 0xFE:			// Active Sensing
			case 0xFF: return res;
		}
		res += ' '+intToHex(sm.getData1());
		// if 2-byte message, return
		switch (status) {
			case 0xF1:			// MTC Quarter Frame
			case 0xF3:			// Song Select
					return res;
		}
		switch (sm.getCommand()) {
			case 0xC0:
			case 0xD0:
					return res;
		}
		// 3-byte messages left
		res += ' '+intToHex(sm.getData2());
		return res;
	}
}



/*** DumpReceiver.java ***/


      
    
```


There are several sites with legal free MIDI files. The file [
	Amy Winehouse - Rehab
      ](http://files.mididb.com/amy-winehouse/rehab.mid) gives the result

```

	
---------------------------------------------------------------------------
File: rehab.mid
---------------------------------------------------------------------------
Length: 251475 ticks
Duration: 216788738 microseconds
---------------------------------------------------------------------------
DivisionType: PPQ
Resolution: 480 ticks per beat
---------------------------------------------------------------------------
Track 0:
-----------------------
tick 0: Time Signature: 4/4, MIDI clocks per metronome tick: 24, 1/32 per 24 MIDI clocks: 8
tick 0: Key Signature: C major
tick 0: SMTPE Offset: 32:0:0.0.0
tick 0: Set Tempo: 145.0 bpm
tick 0: End of Track
---------------------------------------------------------------------------
Track 1:
-----------------------
tick 0: Sequence/Track Name: amy winehouse - rehab
tick 0: Instrument Name: GM Device
tick 40: Sysex message: F0 7E 7F 09 01 F7
tick 40: End of Track
---------------------------------------------------------------------------
Track 2:
-----------------------
tick 0: MIDI Channel Prefix: 1
tick 0: Sequence/Track Name: amy winehouse - rehab
tick 0: Instrument Name: GM Device  2
tick 480: [B1 79 00] channel 2: control change 121 value: 0
tick 485: [B1 0A 40] channel 2: control change 10 value: 64
tick 490: [B1 5D 14] channel 2: control change 93 value: 20
tick 495: [B1 5B 00] channel 2: control change 91 value: 0
tick 500: [B1 0B 7F] channel 2: control change 11 value: 127
tick 505: [B1 07 69] channel 2: control change 7 value: 105
tick 510: [E1 00 40] channel 2: pitch wheel change 8192
tick 515: [B1 00 00] channel 2: control change 0 value: 0
tick 520: [C1 22] channel 2: program change 34
...
	
      
```
