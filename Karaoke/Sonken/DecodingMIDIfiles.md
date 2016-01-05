
##  Decoding MIDI files 


All files have a lyric block followed by a music block. The lyric block is compressed
and it has been discovered that this is LZW compression. This decompresses to a set
of 4-byte chunks. The first two bytes are characters of the lyric.
For 1-byte encodings such as English or Vietnamese, the first byte is one character
and the second is either zero or another character (two byts such as "\r\n").
For two byte encodings such as GB-2312, the two bytes form one character.


The next two bytes are the length of time the character string plays for.

###  Lyric block 


Each lyric block starts with strings such as "#0001
@@00@12
@Help Yourself
@
@@Tom Jones
"
The language code is in there as NN in "@00@NN". The song title, writer, singer are clear.
(Note: these characters are all 4 bytes apart!). For English it is "12" and so on.


Bytes 0 and 1 of each block are a character in the lyric. Bytes 2 and 3 are the duration
of each character. To turn them into MIDI data, the durations have to be turned into
start/stop of each character.


My Java program to do this is
SongExtracter.java

```cpp
import java.io.*;
import javax.sound.midi.*;
import java.nio.charset.Charset;

public class SongExtracter {
    private static final boolean DEBUG = false;

    private String[] dataFiles = new String[] {
	"DTSMUS00.DKD", "DTSMUS01.DKD", "DTSMUS02.DKD",
	"DTSMUS03.DKD", "DTSMUS04.DKD", "DTSMUS05.DKD",
	"DTSMUS06.DKD", "DTSMUS07.DKD"};
    private String superBlockFileName = dataFiles[0];
    private static final String DATADIR = "/home/newmarch/Music/karaoke/sonken/";
    private static final String SONGDIR ="/home/newmarch/Music/karaoke/sonken/songs/";
    //private static final String SONGDIR ="/server/KARAOKE/KARAOKE/Sonken/";
    private static final long SUPERBLOCK_OFFSET = 0x200;
    private static final long BLOCK_MULTIPLIER = 0x800;
    private static final long FILE_SIZE = 0x3F800000L;

    private static final int SIZE_UINT = 4;
    private static final int SIZE_USHORT = 2;

    private static final int ENGLISH = 12;

    public RawSong getRawSong(int songNumber) 
	throws java.io.IOException, 
	       java.io.FileNotFoundException {
	if (songNumber < 1) {
	    throw new FileNotFoundException();
	}

	// song number in files is one less than song number in books, so
	songNumber--;

	long locationIndexTable = getTableIndexFromSuperblock(songNumber);
	debug("Index table at %X\n", locationIndexTable);

	long locationSongDataBlock = getSongIndex(songNumber, locationIndexTable);

	// Now we are at the start of the data block
	return readRawSongData(locationSongDataBlock);

	//debug("Data block at %X\n", songStart);
    }

    private long getTableIndexFromSuperblock(int songNumber)
	throws java.io.IOException, 
	       java.io.FileNotFoundException {
	// index into superblock of table of song offsets
	int superBlockIdx = songNumber >> 8;

	debug("Superblock index %X\n", superBlockIdx);
	    
	File superBlockFile = new File(DATADIR + superBlockFileName);

        FileInputStream fstream = new FileInputStream(superBlockFile);

	fstream.skip(SUPERBLOCK_OFFSET + superBlockIdx * SIZE_UINT);
	debug("Skipping to %X\n", SUPERBLOCK_OFFSET + superBlockIdx*4);
	long superBlockValue = readUInt(fstream);

	// virtual address of the index table for this song
	long locationIndexTable = superBlockValue * BLOCK_MULTIPLIER;

	return locationIndexTable;
    }

    /*
     * Virtual address of song data block
     */
    private long getSongIndex(int songNumber, long locationIndexTable) 
	throws java.io.IOException, 
	       java.io.FileNotFoundException {
	// index of song into table of song ofsets
	int indexTableIdx = songNumber & 0xFF;
	debug("Index into index table %X\n", indexTableIdx);

	// translate virtual address to physical address
	int whichFile = (int) (locationIndexTable / FILE_SIZE);
	long indexTableStart =  locationIndexTable % FILE_SIZE;
	debug("Which file %d index into file %X\n", whichFile, indexTableStart);

	File songDataFile = new File(DATADIR + dataFiles[whichFile]);
        FileInputStream dataStream = new FileInputStream(songDataFile);
	dataStream.skip(indexTableStart + indexTableIdx * SIZE_UINT);
	debug("Song data index is at %X\n", indexTableStart + indexTableIdx*SIZE_UINT);

	long songStart = readUInt(dataStream) + indexTableStart;

	return songStart + whichFile * FILE_SIZE;
    }

    private RawSong readRawSongData(long locationSongDataBlock) 
	throws java.io.IOException {
	int whichFile = (int) (locationSongDataBlock / FILE_SIZE);
	long dataStart =  locationSongDataBlock % FILE_SIZE;
	debug("Which song file %d  into file %X\n", whichFile, dataStart);

	File songDataFile = new File(DATADIR + dataFiles[whichFile]);
        FileInputStream dataStream = new FileInputStream(songDataFile);
	dataStream.skip(dataStart);

	RawSong rs = new RawSong();
	rs.type = readUShort(dataStream);
	rs.compressedLyricLength = readUShort(dataStream);
	// discard next short
	readUShort(dataStream);
	rs.uncompressedLyricLength = readUShort(dataStream);
	debug("Type %X, cLength %X uLength %X\n", rs.type, rs.compressedLyricLength, rs.uncompressedLyricLength);

	// don't know what the next word is for, skip it
	//dataStream.skip(4);
	readUInt(dataStream);

	// get the compressed lyric
	rs.lyric = new byte[rs.compressedLyricLength];
	dataStream.read(rs.lyric);

	long toBoundary = 0;
	long songLength = 0;
	long uncompressedSongLength = 0;

	// get the song data
	if (rs.type == 0) {
	    // Midi file starts in 4 bytes time
	    songLength = readUInt(dataStream);
	    uncompressedSongLength = readUInt(dataStream);
	    System.out.printf("Song data length %d, uncompressed %d\n", 
			      songLength, uncompressedSongLength);
	    rs.uncompressedSongLength = uncompressedSongLength;

	    // next word is language again?
	    //toBoundary = 4;
	    //dataStream.skip(toBoundary);
	    readUInt(dataStream);
	} else {
	    // WMA starts on next 16-byte boundary
	    if( (dataStart + rs.compressedLyricLength + 12) % 16 != 0) {
		// dataStart already on 16-byte boundary, so just need extra since then
		toBoundary = 16 - ((rs.compressedLyricLength + 12) % 16);
		debug("Read lyric data to %X\n", dataStart + rs.compressedLyricLength + 12);
		debug("Length %X to boundary %X\n", rs.compressedLyricLength, toBoundary);
		dataStream.skip(toBoundary);
	    }
	    songLength = readUInt(dataStream);
	}

	rs.music = new byte[(int) songLength];
	dataStream.read(rs.music);

	return rs;
    }

    private long readUInt(InputStream is) throws IOException {
	long val = 0;
	for (int n = 0; n < SIZE_UINT; n++) {
	    int c = is.read();
	    val = (val << 8) + c;
	}
	debug("ReadUInt %X\n", val);
	return val;
    }

    private int readUShort(InputStream is) throws IOException {
	int val = 0;
	for (int n = 0; n < SIZE_USHORT; n++) {
	    int c = is.read();
	    val = (val << 8) + c;
	}
	debug("ReadUShort %X\n", val);
	return val;
    }

    void debug(String f, Object ...args) {
	if (DEBUG) {
	    System.out.printf("Debug: " + f, args);
	}
    }

    public Song getSong(RawSong rs) {
	Song song;
	if (rs.type == 0x8000) {
	    song = new WMASong(rs);
	} else {
	    song = new MidiSong(rs);
	}
	return song;
    }

    public static void main(String[] args) {
	if (args.length != 1) {
	    System.err.println("Usage: java SongExtractor <song numnber>");
	    System.exit(1);
	}

	SongExtracter se = new SongExtracter();
	try {
	    RawSong rs = se.getRawSong(Integer.parseInt(args[0]));
	    rs.dumpToFile(args[0]);

	    Song song = se.getSong(rs);
	    song.dumpToFile(args[0]);
	    song.dumpLyric();
	} catch(Exception e) {
	    e.printStackTrace();
	}
    }

    private class RawSong {
	/**
	 * type == 0x0 is Midi
	 * type == 0x8000 is WMA
	 */
	public int type;
	public int compressedLyricLength;
	public int uncompressedLyricLength;
	public long uncompressedSongLength; // only needed for compressed Midi
	public byte[] lyric;
	public byte[] music;

	public void dumpToFile(String fileName) throws IOException {
	    FileOutputStream fout = new FileOutputStream(SONGDIR + fileName + ".lyric");
	    fout.write(lyric);
	    fout.close();

	    fout = new FileOutputStream(SONGDIR + fileName + ".music");
	    fout.write(music);
	    fout.close();
	}
    }

    private class Song {
	public int type;
	public byte[] lyric;
	public byte[] music;
	protected Sequence sequence;
	protected int language = -1;

	public Song(RawSong rs) {
	    type = rs.type;
	    lyric = decodeLyric(rs.lyric,
				rs.uncompressedLyricLength);
	}

	/**
	 * Raw lyric is LZW compressed. Decompress it
	 */
	public byte[] decodeLyric(byte[] compressedLyric, long uncompressedLength) {
	    // uclen is short by at least 2 - other code adds 10 so we do too
	    // TODO: change LZW to use a Vector to build result so we don't have to guess at length
	    byte[] result = new byte[(int) uncompressedLength + 10];
	    LZW lzw = new LZW();
	    int len = lzw.expand(compressedLyric, compressedLyric.length, result);
	    System.out.printf("uncompressedLength %d, actual %d\n", uncompressedLength, len);
	    lyric = new byte[len];
	    System.arraycopy(result, 0, lyric, 0, (int) uncompressedLength);
	    return lyric;
	}

	public void dumpToFile(String fileName) throws IOException {
	    FileOutputStream fout = new FileOutputStream(SONGDIR + fileName + ".decodedlyric");
	    fout.write(lyric);
	    fout.close();
	    
	    fout = new FileOutputStream(SONGDIR + fileName + ".decodedmusic");
	    fout.write(music);
	    fout.close();
	    
	    fout = new FileOutputStream(SONGDIR + fileName + ".mid");
	    if (sequence == null)  {
		System.out.println("Seq is null");
	    } else {
		// type is MIDI type 0
		MidiSystem.write(sequence, 0, fout);
	    }
	}

	public void dumpLyric() {
	    for (int n = 0; n < lyric.length; n += 4) {
		if (lyric[n] == '\r') {
		    System.out.println();
		} else {
		    System.out.printf("%c", lyric[n] & 0xFF);
		}
	    }
	    System.out.println();
	    System.out.printf("Language is %X\n", getLanguageCode()); 
	}

	/**
	 * Lyric contains the language code as string @00@NN in header section
	 */
	public int getLanguageCode() {
	    int lang = 0;

	    // Look for @00@NN and return NN
	    for (int n = 0; n < lyric.length-20; n += 4) {
		if (lyric[n] == (byte) '@' &&
		    lyric[n+4] == (byte) '0' &&
		    lyric[n+8] == (byte) '0' &&
		    lyric[n+12] == (byte) '@') {
		    lang = ((lyric[n+16]-'0') << 4) + lyric[n+20]-'0';
		    break;
		}
	    }
	    return lang;
	}

	/**
	 * Lyric is in a language specific encoding. Translate to Unicode UTF-8.
	 * Not all languages are handled because I don't have a full set of examples
	 */
	public byte[] lyricToUnicode(byte[] bytes) {
	    if (language == -1) {
		language = getLanguageCode();
	    }
	    switch (language) {
	    case SongInformation.ENGLISH:
		return bytes;

	    case SongInformation.KOREAN: {
 		Charset charset = Charset.forName("gb2312");
		String str = new String(bytes, charset);
		bytes = str.getBytes();
		System.out.println(str);
		return bytes;
	    }

	    case SongInformation.CHINESE1:
	    case SongInformation.CHINESE2:
	    case SongInformation.CHINESE8:
	    case SongInformation.CHINESE131:
	    case SongInformation.TAIWANESE3:
	    case SongInformation.TAIWANESE7:
	    case SongInformation.CANTONESE:
		Charset charset = Charset.forName("gb2312");
		String str = new String(bytes, charset);
		bytes = str.getBytes();
		System.out.println(str);
		return bytes;
	    }
	    // language not handled
	    return bytes;
	}

	public void durationToOnOff() {

	}

	public Track createSequence() {
	    Track track;

	    try {
		sequence = new Sequence(Sequence.PPQ, 30);
	    } catch(InvalidMidiDataException e) {
		// help!!!
	    }
	    track = sequence.createTrack();
	    addLyricToTrack(track);
	    return track;
	}

	public void addMsgToTrack(MidiMessage msg, Track track, long tick) {
	    MidiEvent midiEvent = new MidiEvent(msg, tick);

	    
	    // No need to sort or delay insertion. From the Java API
	    // "The list of events is kept in time order, meaning that this
	    // event inserted at the appropriate place in the list"
	    track.add(midiEvent);
	}

	/**
	 * return byte as int, converting to unsigned if needed
	 */
	protected int ub2i(byte b) {
	    return  b >= 0 ? b : 256 + b;
	}

	public void addLyricToTrack(Track track) {
	    long lastDelay = 0;
	    int offset = 0;
	    int data0;
	    int data1;
	    final int LYRIC = 0x05;
	    MetaMessage msg;

	    while (offset < lyric.length-4) {
		int data3 = ub2i(lyric[offset+3]);
		int data2 = ub2i(lyric[offset+2]);
		data0 = ub2i(lyric[offset]);
		data1 = ub2i(lyric[offset+1]);

		long delay = (data3 << 8) + data2;

		offset += 4;
		byte[] data;
		int len;
		long tick;

		// 	System.out.printf("Lyric offset %X char %X after %d with delay %d made of %d %d\n", offset, data0, lastDelay, delay, lyric[offset-1], lyric[offset-2]);

		if (data1 == 0) {
		    data = new byte[] {(byte) data0}; //, (byte) MetaMessage.META};
		} else {
		    data = new byte[] {(byte) data0, (byte) data1}; // , (byte) MetaMessage.META};
		}
		data = lyricToUnicode(data);
		    
		msg = new MetaMessage();

		if (delay > 0) {
		    tick = delay;
		    lastDelay = delay;
		} else {
		    tick = lastDelay;
		}
		
		try {
		    msg.setMessage(LYRIC, data, data.length);
		} catch(InvalidMidiDataException e) {
		    e.printStackTrace();
		    continue;
		}
		addMsgToTrack(msg, track, tick);
	    }
	}

    }

    private class WMASong extends Song {

	public WMASong(RawSong rs) {
	    // We want to decode the lyric, but just copy the music data
	    super(rs);
	    music = rs.music;
	    createSequence();
	}

	public void dumpToFile(String fileName) throws IOException {
	    System.out.println("Dumping WMA to " + fileName + ".wma");
	    super.dumpToFile(fileName);
	    FileOutputStream fout = new FileOutputStream(fileName + ".wma");
	    fout.write(music);
	    fout.close();
	}

    }

    private class MidiSong extends Song {

        private String[] keyNames = {"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"};

	public MidiSong(RawSong rs) {
	    // We want the decoded lyric plus also need to decode the music
	    // and then turn it into a Midi sequence
	    super(rs);
	    decodeMusic(rs);
	    createSequence();
	}

	public void dumpToFile(String fileName) throws IOException {
	    System.out.println("Dumping Midi to " + fileName);
	    super.dumpToFile(fileName);
	}

        public String getKeyName(int nKeyNumber)
        {
	    if (nKeyNumber > 127)
                {
		    return "illegal value";
                }
	    else
                {
		    int     nNote = nKeyNumber % 12;
		    int     nOctave = nKeyNumber / 12;
		    return keyNames[nNote] + (nOctave - 1);
                }
        }

	public byte[] decodeMusic(RawSong rs) {
	    byte[]  compressedMusic = rs.music;
	    long uncompressedSongLength = rs.uncompressedSongLength;

	    // TODO: change LZW to use a Vector to build result so we don't have to guess at length
	    byte[] expanded = new byte[(int) uncompressedSongLength + 20];
	    LZW lzw = new LZW();
	    int len = lzw.expand(compressedMusic, compressedMusic.length, expanded);
	    System.out.printf("Uncompressed %d, Actual %d\n", compressedMusic.length, len);
	    music = new byte[len];
	    System.arraycopy(expanded, 0, music, 0, (int) len);


	    return music;
	}

	public Track createSequence() {
	    Track track = super.createSequence();
	    addMusicToTrack(track);
	    return track;
	}



	public void addMusicToTrack(Track track) {
	    int timeLine = 0;
	    int offset = 0;
	    int midiChannelNumber = 1;

	    /* From http://board.midibuddy.net/showpost.php?p=533722&postcount=31
	       Block of 5 bytes :
	       xx xx xx xx xx
	       1st byte = Delay Time
	       2nd byte = Delay Time when the velocity will be 0, 
	       this one will generate another midi event 
	       with velocity 0 (see above).
	       3nd byte = Event, for example 9x : Note On for channel x+1,
	       cx for PrCh, bx for Par, ex for Pitch Bend....
	       4th byte = Note
	       5th byte = Velocity
	    */
	    System.out.println("Adding music to track");
	    while (offset < music.length - 5) {

		int startDelayTime = ub2i(music[offset++]);
		int endDelayTime = ub2i(music[offset++]);
		int event = ub2i(music[offset++]);
		int data1 = ub2i(music[offset++]);
		int data2 = ub2i(music[offset++]);


		int tick = timeLine + startDelayTime;
		System.out.printf("Offset %X event %X timeline %d\n", offset, event & 0xFF, tick);

		ShortMessage msg = new ShortMessage();
		ShortMessage msg2 = null;

		try {
		    // For Midi event types see http://www.midi.org/techspecs/midimessages.php
		    switch (event & 0xF0) {
		    case ShortMessage.CONTROL_CHANGE:  // Control Change 0xB0
		    case ShortMessage.PITCH_BEND:  // Pitch Wheel Change 0xE0
			msg.setMessage(event, data1, data2);
			/*
			  writeChannel(midiChannelNumber, chunk[2], false);
			  writeChannel(midiChannelNumber, chunk[3], false);
			  writeChannel(midiChannelNumber, chunk[4], false);
			*/
			break;

		    case ShortMessage.PROGRAM_CHANGE: // Program Change 0xC0
		    case ShortMessage.CHANNEL_PRESSURE: // Channel Pressure (After-touch) 0xD0
			msg.setMessage(event, data1, 0);
			break;

		    case 0x00:
			// case 0x90:
			// Note on
			int note = data1;
			int velocity = data2;

			/* We have to generate a pair of note on/note off.
			   The C code manages getting the order of events
			   done correctly by keeping a list of note off events
			   and sticking them into the Midi sequence when appropriate.
			   The Java add() looks after timing for us, so we'll
			   generate a note off first and add it, and then do the note on
			*/
			System.out.printf("Note on %s at %d, off at %d at offset %X channel %d\n", 
					  getKeyName(note),
					  tick, tick + endDelayTime, offset, (event &0xF)+1);
			// ON
			msg.setMessage(ShortMessage.NOTE_ON | (event & 0xF),
				       note, velocity);

			// OFF
			msg2 = new ShortMessage();
			msg2.setMessage(ShortMessage.NOTE_OFF  | (event & 0xF), 
					note, velocity);

			break;

		    case 0xF0: // System Exclusive
			// We'll write the data as is to the buffer
			offset -= 3;
			// msg = SysexMessage();
			while (music[offset] != (byte) 0xF7) // bytes only go upto 127 GRRRR!!!
			    {
				//				writeChannel(midiChannelNumber, midiData[midiOffset], false);
				System.out.printf("sysex: %x\n", music[offset]);
				offset++;
				if (offset >= music.length) {
				    System.err.println("Run off end of array while processing Sysex");
				    break;
				}
			    }
			//			writeChannel(midiChannelNumber, midiData[midiOffset], false);
			offset++;
			System.out.printf("Ignoring sysex %02X\n", event);

			// ignore the message for now
			continue;
			// break;

		    default:
			System.out.printf("Unrecognized code %02X\n", event);
			continue;
		    }
		} catch(InvalidMidiDataException e) {
		    e.printStackTrace();
		}

		addMsgToTrack(msg, track, tick);
		if (msg2 != null ) {
		    if (endDelayTime <= 0) System.out.println("Start and end at same time");
		    addMsgToTrack(msg2, track, tick + endDelayTime);
		    msg2 = null;
		}

		timeLine = tick;
	    }
	}
    }
}
```


with support classes LZW.java

```cpp
/**
 * Based on code by Mark Nelson
 * http://marknelson.us/1989/10/01/lzw-data-compression/
 */

public class LZW {


    private final int BITS = 12;                   /* Setting the number of bits to 12, 13*/
    private final int HASHING_SHIFT = (BITS-8);    /* or 14 affects several constants.    */
    private final int MAX_VALUE = (1 << BITS) - 1; /* Note that MS-DOS machines need to   */
    private final int MAX_CODE = MAX_VALUE - 1;    /* compile their code in large model if*/
    /* 14 bits are selected.               */

    private final int TABLE_SIZE = 5021;           /* The string table size needs to be a */
    /* prime number that is somewhat larger*/
    /* than 2**BITS.                       */
    private final int NEXT_CODE = 257;

    private long[] prefix_code = new long[TABLE_SIZE];;        /* This array holds the prefix codes   */
    private int[] append_character = new int[TABLE_SIZE];  /* This array holds the appended chars */
    private int[] decode_stack; /* This array holds the decoded string */

    private int input_bit_count=0;
    private long input_bit_buffer=0; // must be 32 bits
    private int offset = 0;

    /*
    ** This routine simply decodes a string from the string table, storing
    ** it in a buffer.  The buffer can then be output in reverse order by
    ** the expansion program.
    */
    /* JN: returns size of buffer used 
     */
    private int decode_string(int idx, long code)
    {
	int i;

	i=0;
	while (code > (NEXT_CODE - 1))
	    {
		decode_stack[idx++] = append_character[(int) code];
		code=prefix_code[(int) code];
		if (i++>=MAX_CODE)
		    {
			System.err.printf("Fatal error during code expansion.\n");
			return 0;
		    }
	    }

	decode_stack[idx]= (int) code;

	return idx;
    }

    /*
    ** The following two routines are used to output variable length
    ** codes.  They are written strictly for clarity, and are not
    ** particularyl efficient.
    */

    long input_code(byte[] inputBuffer, int inputLength, int dummy_offset, boolean firstTime)
    {
	long return_value;

	//int pOffsetIdx = 0;
	if (firstTime)
	    {
		input_bit_count = 0;
		input_bit_buffer = 0;
	    }

	while (input_bit_count <= 24 && offset < inputLength)
	    {
		/*
		input_bit_buffer |= (long) inputBuffer[offset++] << (24 - input_bit_count);
		input_bit_buffer &= 0xFFFFFFFFL;
		System.out.printf("input buffer %d\n", (long) inputBuffer[offset]);
		*/
		// Java doesn't have unsigned types. Have to play stupid games when mixing
		// shifts and type coercions
		long val = inputBuffer[offset++];
		if (val < 0) {
		    val = 256 + val;
		}
		// System.out.printf("input buffer: %d\n", val);
		//		if ( ((long) inpu) < 0) System.out.println("Byte is -ve???");
		input_bit_buffer |= (((long) val) << (24 - input_bit_count)) & 0xFFFFFFFFL;
		//input_bit_buffer &= 0xFFFFFFFFL;
		// System.out.printf("input bit buffer %d\n", input_bit_buffer);

		/*
		if (input_bit_buffer < 0) {
		    System.err.println("Negative!!!");
		}
		*/

		input_bit_count  += 8;
	    }

	if (offset >= inputLength && input_bit_count < 12)
	    return MAX_VALUE;

	return_value       = input_bit_buffer >>> (32 - BITS);
	input_bit_buffer <<= BITS;
	input_bit_buffer &= 0xFFFFFFFFL;
	input_bit_count   -= BITS;

	return return_value;
    }

    void dumpLyric(int data)
    {
	System.out.printf("LZW: %d\n", data);
	if (data == 0xd)
	    System.out.printf("\n");	      
    }

    /*
    **  This is the expansion routine.  It takes an LZW format file, and expands
    **  it to an output file.  The code here should be a fairly close match to
    **  the algorithm in the accompanying article.
    */

    public int expand(byte[] intputBuffer, int inputBufferSize, byte[] outBuffer)
    {
	long next_code = NEXT_CODE;/* This is the next available code to define */
	long new_code;
	long old_code;
	int character;
	int string_idx;
	
	int offsetOut = 0;


	prefix_code      = new long[TABLE_SIZE];
	append_character = new int[TABLE_SIZE];
	decode_stack     = new int[4000];

	old_code= input_code(intputBuffer, inputBufferSize, offset, true);  /* Read in the first code, initialize the */
	character = (int) old_code;          /* character variable, and send the first */
	outBuffer[offsetOut++] = (byte) old_code;       /* code to the output file                */
	//outTest(output, old_code);
	// dumpLyric((int) old_code);

	/*
	**  This is the main expansion loop.  It reads in characters from the LZW file
	**  until it sees the special code used to inidicate the end of the data.
	*/
	while ((new_code=input_code(intputBuffer, inputBufferSize, offset, false)) != (MAX_VALUE))
	    {
		// dumpLyric((int)new_code);
		/*
		** This code checks for the special STRING+CHARACTER+STRING+CHARACTER+STRING
		** case which generates an undefined code.  It handles it by decoding
		** the last code, and adding a single character to the end of the decode string.
		*/

		if (new_code>=next_code)
		    {
			if (new_code > next_code)
			    {
				System.err.printf("Invalid code: offset:%X new:%X next:%X\n", offset, new_code, next_code);
				break;
			    }

			decode_stack[0]= (int) character;
			string_idx=decode_string(1, old_code);
		    }
		else
		    {
			/*
			** Otherwise we do a straight decode of the new code.
			*/
			string_idx=decode_string(0,new_code);
		    }

		/*
		** Now we output the decoded string in reverse order.
		*/
		character=decode_stack[string_idx];
		while (string_idx >= 0)
		    {
			int data = decode_stack[string_idx--]; 
			outBuffer[offsetOut] = (byte) data;
			//outTest(output, *string--);

			if (offsetOut % 4 == 0) {
			    //dumpLyric(data);
			}

			offsetOut++;
		    }

		/*
		** Finally, if possible, add a new code to the string table.
		*/
		if (next_code > 0xfff)
		    {
			next_code = NEXT_CODE;
			System.err.printf("*");
		    }

		// test code
		if (next_code > 0xff0 || next_code < 0x10f)
		    {
			Debug.printf("%02X ", new_code);
		    }

		prefix_code[(int) next_code]=old_code;
		append_character[(int) next_code] = (int) character;
		next_code++;

		old_code=new_code;
	    }
	Debug.printf("offset out is %d\n", offsetOut);
	return offsetOut;
    }
}
```


SongInformation.java

```cpp
public class SongInformation {


    // Public fields of each song record
    /**
     *  Song number in the file, one less than in songbook
     */
    public long number;

    /**
     * song title in Unicode
     */
    public String title;

    /**
     * artist in Unicode
     */
    public String artist;

    /**
     * integer value of language code
     */
    public int language;

    public static final int  KOREAN = 0;
    public static final int  CHINESE1 = 1;
    public static final int  CHINESE2 = 2;
    public static final int  TAIWANESE3 = 3 ;
    public static final int  JAPANESE = 4;
    public static final int  RUSSIAN = 5;
    public static final int  THAI = 6;
    public static final int  TAIWANESE7 = 7;
    public static final int  CHINESE8 = 8;
    public static final int  CANTONESE = 9;
    public static final int  ENGLISH = 0x12;
    public static final int  VIETNAMESE = 0x13;
    public static final int  PHILIPPINE = 0x14;
    public static final int  TURKEY = 0x15;
    public static final int  SPANISH = 0x16;
    public static final int  INDONESIAN = 0x17;
    public static final int  MALAYSIAN = 0x18;
    public static final int  PORTUGUESE = 0x19;
    public static final int  FRENCH = 0x20;
    public static final int  INDIAN = 0x21;
    public static final int  BRASIL = 0x22;
    public static final int  CHINESE131 = 131;
    public static final int  ENGLISH146 = 146;
    public static final int  PHILIPPINE148 = 148;

    public SongInformation(long number,
			   String title,
			   String artist,
			   int language) {
	this.number = number;
	this.title = title;
	this.artist = artist;
	this.language = language;
    }

    public String toString() {
	return "" + (number+1) + " (" + language + ") \"" + title + "\" " + artist;
    }

    public boolean titleMatch(String pattern) {
	// System.out.println("Pattern: " + pattern);
	return title.matches("(?i).*" + pattern + ".*");
    }

    public boolean artistMatch(String pattern) {
	return artist.matches("(?i).*" + pattern + ".*");
    }

    public boolean numberMatch(String pattern) {
	Long n;
	try {
	    n = Long.parseLong(pattern) - 1;
	    //System.out.println("Long is " + n);
	} catch(Exception e) {
	    //System.out.println(e.toString());
	    return false;
	}
	return number == n;
    }


    public boolean languageMatch(int lang) {
	return language == lang;
    }
}
```


and Debug.java

```cpp
public class Debug {

    public static final boolean DEBUG = false;

    public static void println(String str) {
	if (DEBUG) {
	    System.out.println(str);
	}
    }

    public static void printf(String format, Object... args) {
	if (DEBUG) {
	    System.out.printf(format, args);
	}
    }
}
```


To compile these, run

```
javac SongExtracter.java LZW.java Debug.java SongInformation.java
```


and run by

```
java SongExtracter <song number >
```


The program to convert these MIDI files to Karaoke KAR files is
KARConverter.java

```cpp
/*
 * KARConverter.java
 *
 * The output from decodnig the Sonken data is not in
 * the format required by the KAR "standard".
 * e.g. we need @T for the title,
 * and LYRIC events need to be changed to TEXT events
 * Tempo has to be changed too
 *
 */

import java.io.File;
import java.io.FileOutputStream;
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




public class KARConverter {
    private static int LYRIC = 5;
    private static int TEXT = 1;

    private static boolean firstLyricEvent = true;

    public static void main(String[] args) {
	if (args.length != 1) {
	    out("KARConverter: usage:");
	    out("\tjava KARConverter <file>");
	    System.exit(1);
	}
	/*
	 *	args[0] is the common prefix of the two files
	 */
	File	inFile = new File(args[0] + ".mid");
	File	outFile = new File(args[0] + ".kar");

	/*
	 *	We try to get a Sequence object, which the content
	 *	of the MIDI file.
	 */
	Sequence	inSequence = null;
	Sequence	outSequence = null;
	try {
	    inSequence = MidiSystem.getSequence(inFile);
	} catch (InvalidMidiDataException e) {
	    e.printStackTrace();
	    System.exit(1);
	} catch (IOException e) {
	    e.printStackTrace();
	    System.exit(1);
	}

	if (inSequence == null) {
	    out("Cannot retrieve Sequence.");
	} else {
	    try {
		outSequence = new Sequence(inSequence.getDivisionType(),
					   inSequence.getResolution());
	    } catch(InvalidMidiDataException e) {
		e.printStackTrace();
		System.exit(1);
	    }
		    
	    createFirstTrack(outSequence);
	    Track[]	tracks = inSequence.getTracks();
	    fixTrack(tracks[0], outSequence);
	}
	FileOutputStream outStream = null;
	try {
	    outStream = new FileOutputStream(outFile);
	    MidiSystem.write(outSequence, 1, outStream);
	} catch(Exception e) {
	    e.printStackTrace();
	    System.exit(1);
	}
    }


    public static void fixTrack(Track oldTrack, Sequence seq) {
	Track lyricTrack = seq.createTrack();
	Track dataTrack = seq.createTrack();

	int nEvent = fixHeader(oldTrack, lyricTrack);
	System.out.println("nEvent " + nEvent);
	for ( ; nEvent < oldTrack.size(); nEvent++) {
	    MidiEvent event = oldTrack.get(nEvent);
	    if (isLyricEvent(event)) {
		event = convertLyricToText(event);
		lyricTrack.add(event);
	    } else {
		dataTrack.add(event);
	    }
	}
    }

    public static int fixHeader(Track oldTrack, Track lyricTrack) {
	int nEvent;

	// events at 0-10 are meaningless
	// events at 11, 12 should be the language code,
	// but maybe at 12, 13
	nEvent = 11;
	MetaMessage lang1 = (MetaMessage) (oldTrack.get(nEvent).getMessage());
	String val = new String(lang1.getData());
	if (val.equals("@")) {
	    // try 12
	    lang1 = (MetaMessage) (oldTrack.get(++nEvent).getMessage());
	}		
	MetaMessage lang2 = (MetaMessage) (oldTrack.get(++nEvent).getMessage());
	String lang = new String(lang1.getData()) +
	    new String(lang2.getData());
	System.out.println("Lang " + lang);
	byte[] karLang = getKARLang(lang);

	MetaMessage msg = new MetaMessage();
	try {
	    msg.setMessage(TEXT, karLang, karLang.length);
	    MidiEvent evt = new MidiEvent(msg, 0L);
	    lyricTrack.add(evt);
	} catch(InvalidMidiDataException e) {
	}

	// song title is next
	StringBuffer titleBuff = new StringBuffer();
	for (nEvent = 15; nEvent < oldTrack.size(); nEvent++) {
	    MidiEvent event = oldTrack.get(nEvent);
	    msg = (MetaMessage) (event.getMessage());
	    String contents = new String(msg.getData());
	    if (contents.equals("@")) {
		break;
	    }
	    if (contents.equals("\r\n")) {
		continue;
	    }
	    titleBuff.append(contents);
	}
	String title = "@T" + titleBuff.toString();
	System.out.println("Title '" + title +"'");
	byte[] titleBytes = title.getBytes();

	msg = new MetaMessage();
	try {
	    msg.setMessage(TEXT, titleBytes, titleBytes.length);
	    MidiEvent evt = new MidiEvent(msg, 0L);
	    lyricTrack.add(evt);
	} catch(InvalidMidiDataException e) {
	}

	
	// skip the next 2 @'s
	for (int skip = 0; skip < 2; skip++) {
	    for (++nEvent; nEvent < oldTrack.size(); nEvent++) {
		MidiEvent event = oldTrack.get(nEvent);
		msg = (MetaMessage) (event.getMessage());
		String contents = new String(msg.getData());
		if (contents.equals("@")) {
		    break;
		}
	    }
	}

	// then the singer
	StringBuffer singerBuff = new StringBuffer();
	for (++nEvent; nEvent < oldTrack.size(); nEvent++) {
	    MidiEvent event = oldTrack.get(nEvent);
	    if (event.getTick() != 0) {
		break;
	    }
	    if (! isLyricEvent(event)) {
		break;
	    }

	    msg = (MetaMessage) (event.getMessage());
	    String contents = new String(msg.getData());
	    if (contents.equals("\r\n")) {
		continue;
	    }
	    singerBuff.append(contents);
	}
	String singer = "@T" + singerBuff.toString();
	System.out.println("Singer '" + singer +"'");

	byte[] singerBytes = singer.getBytes();

	msg = new MetaMessage();
	try {
	    msg.setMessage(1, singerBytes, singerBytes.length);
	    MidiEvent evt = new MidiEvent(msg, 0L);
	    lyricTrack.add(evt);
	} catch(InvalidMidiDataException e) {
	}

	return nEvent;
    }

    public static boolean isLyricEvent(MidiEvent event) {
	if (event.getMessage() instanceof MetaMessage) {
	    MetaMessage msg = (MetaMessage) (event.getMessage());
	    if (msg.getType() == LYRIC) {
		return true;
	    }
	}
	return false;
    }

    public static MidiEvent convertLyricToText(MidiEvent event) {
	if (event.getMessage() instanceof MetaMessage) {
	    MetaMessage msg = (MetaMessage) (event.getMessage());
	    if (msg.getType() == LYRIC) {
		byte[] newMsgData = null;
		if (firstLyricEvent) {
		    // need to stick a \ at the front
		    newMsgData = new byte[msg.getData().length + 1];
		    System.arraycopy(msg.getData(), 0, newMsgData, 1, msg.getData().length);
		    newMsgData[0] = '\\';
		    firstLyricEvent = false;
		} else {
		    newMsgData = msg.getData();
		    if ((new String(newMsgData)).equals("\r\n")) {
			newMsgData = "\\".getBytes();
		    }
		}
		try {
		    /*
		    msg.setMessage(TEXT, 
				   msg.getData(), 
				   msg.getData().length);
		    */
		    msg.setMessage(TEXT, 
				   newMsgData, 
				   newMsgData.length);
		} catch(InvalidMidiDataException e) {
		    e.printStackTrace();
		}
	    }
	}
	return event;
    }

    public static byte[] getKARLang(String lang) {
	System.out.println("lang is " + lang);
	if (lang.equals("12")) {
	    return "@LENG".getBytes();
	}
	
	// don't know any other language specs, so guess
	if (lang.equals("01")) {
	    return "@LCHI".getBytes();
	}
	if (lang.equals("02")) {
	    return "@LCHI".getBytes();
	}
	if (lang.equals("08")) {
	    return "@LCHI".getBytes();
	}
	if (lang.equals("09")) {
	    return "@LCHI".getBytes();
	}
	if (lang.equals("07")) {
	    return "@LCHI".getBytes();
	}
	if (lang.equals("")) {
	    return "@L".getBytes();
	}
	if (lang.equals("")) {
	    return "@LENG".getBytes();
	}
	if (lang.equals("")) {
	    return "@LENG".getBytes();
	}
	if (lang.equals("")) {
	    return "@LENG".getBytes();
	}
	if (lang.equals("")) {
	    return "@LENG".getBytes();
	}
	if (lang.equals("")) {
	    return "@LENG".getBytes();
	}


	return ("@L" + lang).getBytes();
    }


    public static void copyNotesTrack(Track oldTrack, Sequence seq) {
	Track newTrack = seq.createTrack();

	for (int nEvent = 0; nEvent < oldTrack.size(); nEvent++)
	    {
		MidiEvent event = oldTrack.get(nEvent);

		newTrack.add(event);
	    }
    }

    public static void createFirstTrack(Sequence sequence) {
	Track track = sequence.createTrack();
	MetaMessage msg1 = new MetaMessage();
	MetaMessage msg2 = new MetaMessage();

	byte data[] = "Soft Karaoke".getBytes();
	try {
	    msg1.setMessage(3, data, data.length);
	} catch(InvalidMidiDataException e) {
	    e.printStackTrace();
	    return;
	}
	MidiEvent event = new MidiEvent(msg1, 0L);
	track.add(event);

	data = "@KMIDI KARAOKE FILE".getBytes();
	try {
	    msg2.setMessage(1, data, data.length);
	} catch(InvalidMidiDataException e) {
	    e.printStackTrace();
	    return;
	}
	MidiEvent event2 = new MidiEvent(msg2, 0L);
	track.add(event2);
    }

    public static void output(MidiEvent event)
    {
	MidiMessage	message = event.getMessage();
	long		lTicks = event.getTick();
    }



    private static void out(String strMessage)
    {
	System.out.println(strMessage);
    }
}



/*** KARConverter.java ***/
```
