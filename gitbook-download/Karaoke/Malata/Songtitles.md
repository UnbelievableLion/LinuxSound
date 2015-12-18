#  Song titles 

The command
 `strings`shows that song titles are in
      several files, including
 `MALATAS4.IDX`.
      This seems to contain the most song titles, so I looked at that.

The block of song titles starts at 0x5F000. Before that is a bunch
      of nulls. To confirm this, the first song in my Malata songbook
      is "1001次吵架" and I can see the string "1001" as the first entry
      in that table.

This first song contains Chinese characters in the title, and the site
 [
	GB Code Table
      ] (http://www.ansell-uebersetzungen.com/gborder.html)
by Mary Ansell confirms that they are encoded using 
      GB2312.

The song titles are just concatenated, for example as
      "AlrightAmourAndyAngelAre You ReadyAsk For MoreBABY I'M YOUR MANBACK HOME".
      So there must be a table somewhere showing start and end of each title.
      I looked for any table giving offsets of the start of songs
      from 0x5F000. There is such a table, at 0x800! After playing with 
      that for a while, it turns out that this table consists
      of records of 25 bytes.
      I'm not sure of the start of the records from 0x800: 
      if I take a starting offset of one,
      then  bytes 19 and 20 hold the
      offset into the song title table while byte 25 is the length of the song title.
      But the offset could be higher.

The language appears to be specified in byte 11:

+  00 is Chinese (GB2132)
+  07 is English
+  01 is ???




The song number is a bit sneaky: in bytes 15-17 are 3 hexadecimal numbers.
      If they are concatenated then they are the song number.
      For example, for the song Medley One, the record is
```

00 00 00 6D 6F 00 00 00 00 04 07 20 00 02 02 01 35 01 7C A8 9E 02 02 00 0A
      
```
Bytes 15, 16, 17 are "02 01 35" (in hex) and this is the song number
      20135 for the Beatles "Medley One".

The earliest English song is 20001 "7Days" and the last one is
      20501 "Take Me To Your Heart"

We currently have
```

11    language
15-17 song number
19,20 offset into song title table
21,22 offset into artist name table?
25    length of title
      
```
e.g. for Medley One
```

00 00 00 6D 6F 00 00 00 00 04 07 20 00 02 02 01 35 01 7C A8 9E 02 02 00 0A
                              07          02 01 35 01 7C    9E 02
                              La          SongNumb SongT    Artis 
      
```
I don't at present know what else is in these records.

A program to list the titles is
 `SongTitles.java`:
```sh_cpp



import java.io.FileInputStream;
import java.io.*;
import java.nio.charset.Charset;



class SongTitles {
    //private static int BASE = 0x5F23A;
    private static long OFFSET = 1; // must be >= 1 or blows array bound
    private static long INDEX_BASE = 0x800 + OFFSET;
    private static long TITLE_BASE = 0x5F000;
    private static int NUM = 12000;
    private static int INDEX_SIZE = 25;
    private static int TITLE_OFFSET = (int) (19 - OFFSET);
    private static int LENGTH_TITLE = (int) (25 - OFFSET);
    private static int ARTIST_OFFSET = (int) (21 - OFFSET);
    private static int SONG_INDEX = (int) (15 - OFFSET);

    public static void main(String[] args) throws Exception {
	long nread = INDEX_BASE;
	byte[] titleBytes = new byte[512];
 	FileInputStream fstream = new FileInputStream(MALATAS4.IDX);
	fstream.skip(INDEX_BASE);

	byte[][] indexes = new byte[NUM][];
	long titleStart[] = new long[NUM];
	long titleEnd[] = new long[NUM];
	for (int n = 0; n < NUM; n++) {
	    indexes[n] = new byte[INDEX_SIZE];
	    fstream.read(indexes[n]);
	    if (isNull(indexes[n]))
		break;
	    // printIndex(indexes[n]);
	    nread += INDEX_SIZE;

	    if (isNull(indexes[n]))
		break;

	    byte b1 = indexes[n][TITLE_OFFSET];
	    byte b2 = indexes[n][TITLE_OFFSET+1];
	    // corect for negative
	    int first, second;
	    //System.out.printf(%X %X\n, firstB, secondB);
	    //first = firstB >= 0 ? firstB : 256 - firstB;
	    //second = secondB >= 0 ? secondB : 256 - secondB;

	    titleStart[n] = ((b1 >= 0 ? b1 : 256 + b1) << 8) + (b2 >= 0 ? b2 : 256 + b2); //first * 256 + second;
	    if (titleStart[n] > 0xfff) {
		// System.out.println(too big);
		titleStart[n] = 0xfff;
	    } else if (titleStart[n] < 0) {
		System.out.println(too small);
	    }

	    long end = indexes[n][LENGTH_TITLE];
	    if (end >= 0x80) {
		end -= 0x80;
		// System.out.println(End too big);
	    } else if (end < 0) {
		// System.out.println(End negative);
		end += 128;
	    }
	    titleEnd[n] = end;

	    /*
	    System.out.printf(Numbers %X %X %X %X\n, b1, b2, 
			      titleStart[n],
			      titleStart[n]+titleEnd[n]);
	    */
	}

	System.out.printf(Skip to %X\n, (TITLE_BASE - nread));
	fstream.skip(TITLE_BASE - nread);
	nread = TITLE_BASE;

	for (int n = 0; n < NUM-1; n++) {
	    // int len = (int) (titleStart[n+1]-titleStart[n]);
	    int len = (int) titleEnd[n];
	    //System.out.println(Reading  + len);
	    fstream.read(titleBytes, 0, len);

	    Charset charset = Charset.forName(gb2312);
	    String translated = new String(titleBytes, 0, len, charset);

	    printFullIndex(indexes[n]);
	    System.out.print( SongIndex );
	    printSongIndex(indexes[n]);
	    System.out.print( ArtistIndex );
	    printArtistIndex(indexes[n]);
	    System.out.println( + n + :  +translated);
	    //printIndex(indexes[n]);
	}

	/*
	fstream.skip(TITLE_BASE);

	byte[] bytes = new byte[NUM];
	fstream.read(bytes);

	Charset charset = Charset.forName(gb2312);
	String translated = new String(bytes, charset);

	System.out.println(translated);
	*/
    }

    private static void printFullIndex(byte[] bytes) {
	for (int n = 0; n < bytes.length; n++) {
	    System.out.printf(%02X , bytes[n]);
	}
    }

    private static void printArtistIndex(byte[] bytes) {
	System.out.printf(%02X%02X , 
			  bytes[ARTIST_OFFSET], 
			  bytes[ARTIST_OFFSET+1]);
    }

    private static void printSongIndex(byte[] bytes) {
	System.out.printf(%X%02X%02X , 
			  bytes[SONG_INDEX], 
			  bytes[SONG_INDEX+1], 
			  bytes[SONG_INDEX+2]);
    }
    
    private static void print1byte(byte[] bytes, int index) {
	System.out.printf(%02X , bytes[index]);
    }
    
    private static boolean isNull(byte[] bytes) {
	for (int n = 0; n < bytes.length; n++) {
	    if (bytes[n] != 0)
		return false;
	}
	return true;
    }
}
      
```


One table finishes at 0xF5260, maybe starting another at 0xF5800. 
      Another table starts at 0x88000 and finishes about 0x9ADF0.
      Another starts at 0x9B000 and finishes at 0x9B2B0
      I don't know what is in these tables.

