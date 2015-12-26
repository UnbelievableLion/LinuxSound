
##  MIDI from data file


Here is where I am currently stuck.
      The data files are _not_ MIDI files.
      For example, song 10383 Lovers by Abba is

```

00000000  00 00 4F 4B 00 00 00 00 00 00 00 00 00 00 00 00 ..OK............
00000010  00 00 00 00 00 24 00 00 00 07 00 00 00 00 00 00 .....$..........
00000020  00 00 77 07 00 00 00 12 00 00 4C 6F 76 65 72 73 ..w.......Lovers
00000030  2F 4F 52 49 47 49 4E 41 4C 3A 2F 41 62 62 61 2F /ORIGINAL:/Abba/
00000040  28 4C 69 76 65 20 41 20 4C 69 74 74 6C 65 20 4C (Live A Little L
00000050  6F 6E 67 65 72 29 2F 00 00 00 56 00 06 EB 0A 00 onger)/...V.....
00000060  00 01 00 00 00 36 05 01 01 00 00 17 2A 06 02 01 .....6......*...
00000070  00 00 38 2A 04 03 01 00 00 46 36 05 04 01 00 00 ..8*.....F6.....
00000080  88 39 05 05 01 00 00 A8 36 05 06 01 00 00 F1 2A .9......6......*
00000090  04 07 01 00 01 16 53 02 08 01 00 01 24 42 04 09 ......S.....$B..
000000A0  01 00 01 32 23 06 11 CA 00 0D 5B 00 0D 62 81 80 ...2#.....[..b..
000000B0  05 82 9D 09 30 07 18 07 18 07 18 07 18 07 00 26 ....0..........&
000000C0  01 5C 00 53 04 69 04 74 06 20 00 64 07 6F 05 77 .\.S.i.t. .d.o.w
000000D0  05 6E 07 20 00 61 09 6E 07 64 09 20 00 6C 0B 69 .n. .a.n.d. .l.i
000000E0  09 73 08 74 08 65 09 6E 08 5E 01 00 1D 01 1E 26 .s.t.e.n.^.....&
      
```





This isn't a MIDI file. From my Sonken, I have a MIDI file for this
      song (obviously not the same recording) which looks like

```

00000000  4D 54 68 64 00 00 00 06 00 01 00 03 00 1E 4D 54 MThd..........MT
00000010  72 6B 00 00 00 2B 00 FF 03 0C 53 6F 66 74 20 4B rk...+....Soft K
00000020  61 72 61 6F 6B 65 00 FF 01 13 40 4B 4D 49 44 49 araoke....@KMIDI
00000030  20 4B 41 52 41 4F 4B 45 20 46 49 4C 45 00 FF 2F  KARAOKE FILE../
00000040  00 4D 54 72 6B 00 00 1A 5E 00 FF 01 05 40 4C 45 .MTrk...^....@LE
00000050  4E 47 00 FF 01 1E 40 54 4C 6F 76 65 72 73 28 4C NG....@TLovers(L
00000060  69 76 65 20 61 20 4C 69 74 74 6C 65 20 4C 6F 6E ive a Little Lon
00000070  67 65 72 29 00 FF 01 02 40 54 8A 5B FF 01 02 5C ger)....@T.[...\
00000080  53 06 FF 01 01 69 06 FF 01 01 74 09 FF 01 01 20 S....i....t....
00000090  06 FF 01 01 64 06 FF 01 01 6F 06 FF 01 01 77 06 ....d....o....w.
000000A0  FF 01 01 6E 07 FF 01 01 20 07 FF 01 01 61 07 FF ...n.... ....a..
000000B0  01 01 6E 07 FF 01 01 64 0A FF 01 01 20 07 FF 01 ..n....d.... ...
000000C0  01 6C 07 FF 01 01 69 07 FF 01 01 73 0A FF 01 01 .l....i....s....
000000D0  74 0A FF 01 01 65 0A FF 01 01 6E 00 FF 01 01 5C t....e....n....\
      
```


and this _is_ a conforming MIDI file.


Just looking at the lyric part, MIDI files require

```

<delta> FF 01 <string length>
      
```


It is likely that the Malata just has

```

<delta>  single-char
      
```


That's easy to adjust - if we know where they lyrics stop!


The lyrics start after a sequence "18 07 18 07 18 07 18 07 00 26".


A much trickier problem is that the lyrics are not contiguous!
      They should be

```

Sit down and listen
'cause I've got
good news for you
It was in the
papers today
      
```


But if we look at the file, lines 2 and 4 are missing:

```

000000C0  01 5C 00 53 04 69 04 74 06 20 00 64 07 6F 05 77 .\.S.i.t. .d.o.w
000000D0  05 6E 07 20 00 61 09 6E 07 64 09 20 00 6C 0B 69 .n. .a.n.d. .l.i
000000E0  09 73 08 74 08 65 09 6E 08 5E 01 00 1D 01 1E 26 .s.t.e.n.^.....&
000000F0  01 67 05 6F 05 6F 05 64 07 20 00 6E 08 65 05 77 .g.o.o.d. .n.e.w
00000100  04 73 07 20 00 66 09 6F 07 72 09 20 00 79 09 6F .s. .f.o.r. .y.o
00000110  05 75 06 5E 01 00 10 01 33 26 01 70 0D 61 0C 70 .u.^....3&.p.a.p
      
```


For the missing line 2, there is some sort of pointer 
      "09 6E 08 5E 01 00 1D 01 1E 26",
      and it turns out that the missing lines are elsewhere:

```

00000790  68 19 5E 01 00 81 C9 1A FF 85 21 26 02 27 02 63 h.^.......!&.'.c
000007A0  03 61 02 75 03 73 02 65 04 20 00 49 04 27 04 76 .a.u.s.e. .I.'.v
000007B0  03 65 05 20 00 67 0A 6F 08 74 08 5E 02 00 10 02 .e. .g.o.t.^....
000007C0  4C 26 02 49 06 74 08 20 00 77 09 61 07 73 09 20 L&.I.t. .w.a.s.
000007D0  00 69 07 6E 06 20 00 74 07 68 04 65 04 5E 02 00 .i.n. .t.h.e.^..
      
```





The Malata displays two lines at a time.
      All of the first lines form a chunk. The second lines form another
      chunk, later on. I haven't found an offset or length
      to say where this second chunk occurs.
      Each line appears to consist of a delta value (I guess) 
      for the delay of the lyric, followed by a lyric character.


Between lines is a section that starts with the character
      '^' and finishes with the character '&'.
      I haven't any idea what is in these sections apart from two
      observations:

+ The character 0xFF appears twice: the first time it
	  signals a shift from first line lyrics to second line
	  lyrics. The next time it occurs it signals the end
	  of the lyrics.
+ Several times the sequence  "09 6E 08 5E 01 00 1D 01 1E 26"
	  occurs. This seems to signal a long break (e.g. for a solo)
	  in the lyrics. In the "Lovers" song this occurs several times:
	  it occurs in the first line, but sometimes the second line
	  is played immediately, sometimes it is delayed until after
	  the next first line is played.
	  I haven't resolved this yet :-(




The file `printLyrics.c`gives a  dump fo the lyrics
      for songs like Lovers (non-coded lyrics) plus the
      deltas (assumed) and the stuff between lines

```cpp

#include <stdio.h>

#define NUM_LINES 100
#define LINE_LEN 25

typedef enum {BEFORE_SONG, IN_SONG_AND_LINE, IN_SONG_BETWEEN} state_t;

state_t state = BEFORE_SONG;
int half = 1;

FILE *fp;
FILE *ofp;

unsigned char prev_ch, curr_ch;
unsigned char lines[NUM_LINES][LINE_LEN];
unsigned char separator[NUM_LINES][LINE_LEN];
unsigned char deltas[NUM_LINES][LINE_LEN];

unsigned char *first_lines, 
    *second_lines,
    *first_separators,
    *second_separators,
    *first_deltas,
    *second_deltas;

int max_lines;

void read1() {
    prev_ch = curr_ch;
    curr_ch = getc(fp);
    // fprintf(ofp, "%X %X\n", prev_ch, curr_ch);
}

void read2() {
  prev_ch = getc(fp);  
  curr_ch = getc(fp);
    // fprintf(ofp, "%X %X\n", prev_ch, curr_ch);
}


void printLine(unsigned char *line) {
    fprintf(ofp, "%2d: ", (line - lines[0])/LINE_LEN);
    int m = 0;
    for (m = 0; m < LINE_LEN; m++) {
	if (line[m] != 0) {
	    putc(line[m], ofp);
	} else {
	    putc(' ', ofp);
	}
    }
}

void printDeltas(unsigned char *deltas) {
    int m, max;

    for (max = LINE_LEN-1; max >= 0; max--) {
	if (deltas[max] != 0)
	    break;
    }
	       
    for (m = 0; m <= max; m++) {
	fprintf(ofp, "%2X ", deltas[m]);
    }

    for (m = max+1; m < LINE_LEN; m++) {
	fprintf(ofp, "   ");
    }	
}

void printSeparator(unsigned char *sep) {
    int m, max;

    for (max = LINE_LEN-1; max >= 0; max--) {
	if (sep[max] != 0)
	    break;
    }
	       
    for (m = 0; m <= max; m++) {
	fprintf(ofp, "%2X ", sep[m]);
    }
    
}

int endSection(unsigned char *sep) {
    // does this sep end with 00 26, a break in the music?
    int m, max;

    for (max = LINE_LEN-1; max >= 0; max--) {
	if (sep[max] != 0)
	    break;
    }
	       
    if ((max >= 1) && (sep[max] == 0x26) && (sep[max-1] == 0))
	return 1;
    return 0;
}

int main(int argc, char **argv) {
    int inSong = 0;
    // int lineNo = 0;
    int inLine = 0;

    bzero(lines, NUM_LINES*LINE_LEN* sizeof(unsigned char));
    bzero(separator, NUM_LINES*LINE_LEN* sizeof(unsigned char));
    bzero(deltas, NUM_LINES*LINE_LEN* sizeof(unsigned char));

    int lineNo = 0;
    int charNo = 0;

    if (argc == 1) {
	fp = stdin;
	ofp = stdout;
    } else if (argc == 2) {
	fp = fopen(argv[1], "r");
	ofp = stdout;
    } else {
	fp = fopen(argv[1], "r");
	ofp = fopen(argv[2], "w");
    }

    int n = 0;
    
    while ((n++ < 6000) && (half <= 2)) {
	
	switch (state) {
	case BEFORE_SONG:
	    read2();
	    if ((prev_ch == 0) && (curr_ch == '&')) {
		state = IN_SONG_AND_LINE;
	    }
	    break;
	case IN_SONG_AND_LINE:
	    read2();
	    if (curr_ch == '^') {
		state = IN_SONG_BETWEEN;
		putc('\n', ofp);

		fprintf(ofp, "%d: ", lineNo);

		charNo = 0;
		separator[lineNo][charNo++] = prev_ch;
		separator[lineNo][charNo++] = curr_ch;


	    } else {
		if (curr_ch != 0) {
		    putc(curr_ch, ofp);
		    lines[lineNo][charNo] = curr_ch;
		    deltas[lineNo][charNo] = prev_ch;
		    charNo++;
		}
	    }
	    break;
	case IN_SONG_BETWEEN:
	    read1();
	    if (curr_ch == '&') {
		state = IN_SONG_AND_LINE;

		separator[lineNo][charNo++] = curr_ch;

		charNo = 0;
		lineNo += 1;
	    }  else if (curr_ch == 0xFF) {
		if (half == 1) {
		    // the 2nd half
		    fprintf(ofp, "\n\nStarting 2nd half\n\n");
		    // discard extra
		    //getc(fp);
		    //lineNo = -1;
		    max_lines = lineNo;
		    half = 2;
		} else {
		    half = 3;
		}
	    } else {
		separator[lineNo][charNo++] = curr_ch;
	    }
	    break;
	}
    }

    fprintf(ofp, "\n\nDumping lines\n\n");
    
    first_lines = lines[0];
    second_lines = lines[0] + (max_lines+1) * LINE_LEN;

    first_deltas = deltas[0];
    second_deltas = deltas[0] + (max_lines+1) * LINE_LEN;

    first_separators = separator[0];
    second_separators = separator[0] + (max_lines+1) * LINE_LEN;

    for (n = 0; n < max_lines; n++) {
	fprintf(ofp, "%2d: ", n);
	/*
	if (lines[n][0] == 0) {
	    break;
	}
	*/
	//printLine(lines[n]);
	printLine(first_lines);
	first_lines += LINE_LEN;

	fprintf(ofp, "\n   ");

	//printDeltas(deltas[n]);
	printDeltas(first_deltas);
	first_deltas += LINE_LEN;

	//printSeparator(separator[n]);
	printSeparator(first_separators);
	first_separators += LINE_LEN;
	putc('\n', ofp);

	if (endSection(first_separators - LINE_LEN)) {
	    fprintf(ofp, "Break occurring in first line\n");
	    //continue;
	}

	fprintf(ofp, "%2d: ", n + max_lines + 1);
	//printLine(lines[n + max_lines + 1]);
	printLine(second_lines);
	second_lines += LINE_LEN;


	fprintf(ofp, "\n   ");
	//printDeltas(deltas[n + max_lines + 1]);
	printDeltas(second_deltas);
	second_deltas += LINE_LEN;

	//printSeparator(separator[n + max_lines + 1]);
	printSeparator(second_separators);
	second_separators += LINE_LEN;

	if (endSection(second_separators - LINE_LEN)) {
	    fprintf(ofp, "Break occurring in second line\n");
	    //continue;
	}

	/*
	for (m = 0; m < LINE_LEN/2; m++) {
	    fprintf(ofp, "%2X ", separator[n][m]);
	}
	*/
	putc('\n', ofp);
    }
    

    fclose(ofp);
    exit(0);
}


      
```


it prints out stuff like

```

 0:  0: \Sit down and listen     
    1  0  4  4  6  0  7  5  5  7  0  9  7  9  0  B  9  8  8  9                 8 5E  1  0 1D  1 1E 26 
47: 47: 'cause I've got          
    2  2  3  2  3  2  4  0  4  4  3  5  0  A  8                                8 5E  2  0 10  2 4C 26 
 1:  1: good news for you        
    1  5  5  5  7  0  8  5  4  7  0  9  7  9  0  9  5                          6 5E  1  0 10  1 33 26 
48: 48: It was in the            
    2  6  8  0  9  7  9  0  7  6  0  7  4                                      4 5E  2  0 10  2 80 C8 26 
 2:  2: papers today             
    1  D  C  5  5  5  7  0 14 10 11 10                                        11 5E  1  0 10  1 80 A7 26 
49: 49: Some physician           
    2  5  5  5  7  0  B  9  8  D  C  6  7  6                                   6 5E  2  0 10  2 80 96 26 
 3:  3: had made a discovery     
    1  4  5  6  0  5  3  4  4  0 1B  0  E  6  5  8  9  8 11  8                 4 5E  1  0 10  1 3F 26 
      
```


That's the data - not sure what information it is conveying.
