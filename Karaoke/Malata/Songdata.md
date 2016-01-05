
##  Song data 


Most of this section was discovered by [thanth](http://karaoke-engineering.996290.n3.nabble.com/Arirang-MIDI-Karaoke-DVD-storage-file-struct-and-MP3-Extraction-td467.html) .
However, he only deals with a single data file, and as the Malata has
more, it becomes more complex.


There are four data files: MULTAK.DAT, MULTAK.DA1, MULTAK.DA2
and MULTAK.DA3. The primary data file is MULTAK.DAT, and this contains
tables of pointers to song data. The other files seem to just contain
the song data.


The number of songs (minus one) is in byte-swapped order at 0x14E in
MULTAK.DAT. In my files, this is "FB 3D" which when swapped to
"3D FB" is one less than the number of songs, 0x3DFC (15868).
This was identified by thanth.


Starting at 0xD20 is a table of 4 byte numbers (prefixed by
"FF 00 FF FF" which are indexes into the table of song data.
If the bytes are "b0 b1 b2 b3" then thanth discovered that
the song data starts at

```
(((b0 * 0x3C) + b1) * 0x48 +b2) * 0x800 + 0x10000
```





Actually, it is more complex than that: for the songs with data
on the first disk MULTAK.DAT this is the case. The table also
contains pointers to data in the other files, and for these
the formula is

```
(((b0 * 0x3C) + b1) * 0x48 +b2) * 0x800
```


That is, the data in these later files starts immediately
with no offset.


The file for each song is given in the top half of the fourth byte
of the song index: (b3 >> 4), where zero is MULTAK.DAT,
one is MULTAK.DA1, etc.


At the locations of the song data pointers is either
the phrase "OK" which means a
"simple song" or "FF FF" which means "complex song",
according to thanth. Simple songs just contain
lyrics and MIDI data, while complex songs also have
MP3 data. I haven't yet found any information about the
size of the data for each song.


The program `SongData.java`splits the MULTAK
files into individual song data files. It only saves a
part of the data for each song, since I don't know where the
data finishes.

```cpp
import java.io.FileInputStream;
import java.io.*;
import java.nio.charset.Charset;



class SongData {
    private static int MAX_SONGS = 20000;

    private static long OFFSET = 0;
    private static long INDEX_BASE = 0xD20 + OFFSET;

    private static long MULTAK_SIZES[] = {0x2441D800, 
					  943441920,
					  943405056, 
					  943812608,
					  58099712};
    //private long offset = 0x10000;

    private enum SongType {
	SIMPLE, COMPLEX;
    }

    private static long TITLE_BASE = 0x5F000;
    private static int NUM = 12000;
    private static int INDEX_SIZE = 25;
    private static int TITLE_OFFSET = (int) (19 - OFFSET);
    private static int LENGTH_TITLE = (int) (25 - OFFSET);
    private static int ARTIST_OFFSET = (int) (21 - OFFSET);
    private static int SONG_INDEX = (int) (15 - OFFSET);

    private class SongStart {
	public long start;
	public int fileNumber;
	public int songNumber;
	public byte[] indexBytes;
	public byte[] data;
	public SongType type;
    }


    public static void main(String[] args) throws Exception {
	new SongData();
    }

    public SongData() throws Exception {
	long nread = INDEX_BASE;
	long index;
	int[] bytes;
	int[] ibytes = new int[4];
	int numSongs = 0;

	SongStart songStarts[] = new SongStart[MAX_SONGS];

 	FileInputStream fstream = new FileInputStream("MULTAK.DAT");
	fstream.skip(INDEX_BASE);
	bytes = read4(fstream);
	long lval = 0;
	int currentFileNumber = 0;

	while (numSongs < MAX_SONGS) {
	    // System.out.printf("%X\n", index);
	    bytes = read4(fstream);
	    if (isNull(bytes)) {
		System.out.printf("Read %d songs\n", numSongs);
		break;
	    }

	    if (isFF00FFFF(bytes)) {
		// these seem to occur sometimes e.g. at A8B8
		continue;
	    }

	    songStarts[numSongs] = new SongStart();
	    songStarts[numSongs].songNumber = numSongs;
	    songStarts[numSongs].fileNumber = bytes[3] >> 4;
	    if ((bytes[3] & 0xF) == 0xA) {
		songStarts[numSongs].type = SongType.COMPLEX;
	    } else {
		songStarts[numSongs].type = SongType.SIMPLE;
	    }
	    songStarts[numSongs].start = songStart(bytes);

	    /*
	    // update fileNumber number?
	    if (numSongs > 0 && 
		songStarts[numSongs-1].start > songStarts[numSongs].start) {

		offset = 0;
		// may need to reset this since offset may have changed
		songStarts[numSongs].start = songStart(bytes);
		currentFileNumber++;
	    }
	    */

	    // songStarts[numSongs].fileNumber = currentFileNumber;
	    System.out.printf("Song %d starts %X fileNumber %X (", 
			      numSongs, 
			      songStarts[numSongs].start,
			      songStarts[numSongs].fileNumber);
	    printBytes(bytes);
	    System.out.println(')');

	    numSongs++;
	}
	fstream.close();

	for (int n = 0; n < numSongs; n++) {
	    System.out.printf("Number %d start %X bytes ",
			      n, songStarts[n].start);
	    getSongFromStart(songStarts[n]);
	    System.out.println();

	    saveSong(songStarts[n]);
	}
	    
	/*
	fstream =  new FileInputStream("MULTAK.DAT");
	long totalRead = 0;
	for (int n = 0; n < MAX_SONGS; n++) {
	    fstream.skip(songStarts[n] - totalRead);
	    totalRead = songStarts[n];
	    System.out.printf("Skipped to %X %X\n", songStarts[n], totalRead);
	    // check next song
	    bytes = read4(fstream);
	    totalRead += 4;

	    for (n = 0; n < 4; n++) {
		System.out.printf("   %X\n", bytes[n]);
		ibytes[n] = (bytes[n] >= 0 ? bytes[n] : 256 + bytes[n]);
	    }

	    lval = 0;
	    for (n = 0; n < 4; n++) {
		lval = (lval << 8) + bytes[n];
	    }
	    System.out.printf("  next bytes %X\n", lval);
	}  
	*/

    }

    private int[] read4(FileInputStream f) throws Exception {
	byte[] bytes = new byte[4];
	int[] ibytes = new int[4];
	long ret = 0;

	f.read(bytes);
	
	// ensure they are unsigned bytes
	for (int n = 0; n < 4; n++) {
	    ibytes[n] = (bytes[n] >= 0 ? bytes[n] : 256 + bytes[n]);
	}
	return ibytes;
    }

    private long songStart(int[] indexBytes) {
	long offset;

	int fileNumber = indexBytes[3] >> 4;
	if (fileNumber == 0)
	    offset = 0x10000;
	else
	    offset = 0;

	long idx =  ((indexBytes[0] * 0x3C) + 
		     indexBytes[1]) * 0x4B + indexBytes[2];
	return idx * 0x800 + offset;
    }

    private void getSongFromStart(SongStart songInfo) throws Exception {
	String fname;
	
	if (songInfo.fileNumber == 0) {
	    fname = "MULTAK.DAT";
	} else {
	    fname = "MULTAK.DA" + songInfo.fileNumber;
	}

 	FileInputStream fstream = new FileInputStream(fname);
	fstream.skip(songInfo.start);
	int[] bytes = read4(fstream);
	if (bytes[0] == 0xFF && bytes[1] == 0xFF) {
	    songInfo.type = SongType.COMPLEX;
	} else {
	    songInfo.type = SongType.SIMPLE;
	}
	songInfo.data = new byte[0x4B00];
	fstream.read(songInfo.data);
	fstream.close();
    }

    private void saveSong(SongStart songInfo) throws Exception {
	String fname = "songs/" + songInfo.songNumber;
 	FileOutputStream fstream = new FileOutputStream(fname);
	if (songInfo.type == SongType.SIMPLE)
	    fstream.write(new byte[] {0, 0, 'O', 'K'});
	else
	    fstream.write(new byte[] {(byte)0xFF, (byte)0xFF, 0, 0});

	fstream.write(songInfo.data);
	fstream.close();
    }

    private boolean greaterThanEqual(int[] x, int[] y) {
	for (int n = 0; n < x.length; n++) {
	    if (x[n] < y[n]) {
		return false;
	    }
	}
	return true;
    }

    private void printFullIndex(byte[] bytes) {
	for (int n = 0; n < bytes.length; n++) {
	    System.out.printf("%02X ", bytes[n]);
	}
    }

    private void printArtistIndex(byte[] bytes) {
	System.out.printf("%02X%02X ", 
			  bytes[ARTIST_OFFSET], 
			  bytes[ARTIST_OFFSET+1]);
    }

    private void printSongIndex(byte[] bytes) {
	System.out.printf("%X%02X%02X ", 
			  bytes[SONG_INDEX], 
			  bytes[SONG_INDEX+1], 
			  bytes[SONG_INDEX+2]);
    }
    
    private void print1byte(byte[] bytes, int index) {
	System.out.printf("%02X ", bytes[index]);
    }

    private void printBytes(int[] bytes) {
	for (int n = 0; n < bytes.length; n++) {
	    System.out.printf("%02X ", bytes[n]);
	}
    }
    
    private boolean isNull(int[] bytes) {
	for (int n = 0; n < bytes.length; n++) {
	    if (bytes[n] != 0)
		return false;
	}
	return true;
    }

    private boolean isFF00FFFF(int[] bytes) {
	if (bytes[0] == 0xFF &&
	    bytes[2] == 0xFF &&
	    bytes[3] == 0xFF)
	    return true;
	else
	    return false;
    }
}
```



