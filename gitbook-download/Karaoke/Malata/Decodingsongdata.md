#  Decoding song data 

It would be easy if all songs contained English text in the data. 
      But I only found the above four. So the rest must be encoded
      in some way.

A couple that I looked at seemed a bit messy. So I settled 
      (for no particular reason) on Don Gibson's "Oh Lonesome Me".
      By playing the song on the Malata, the headers were
```

Oh Lonesome Me
ORIGINAL:
Don Gibson
      
```
while the lyrics are
```

Every body's goin'
out and havin' fun
I'm just a fool
for stayin' home
and havinnone
      
```
Running
 `bvi`on the data file gives
```

00000000  00 00 4F 4B 00 00 00 00 00 00 00 00 00 00 00 00 ..OK............
00000010  00 00 00 00 00 20 00 00 00 07 00 00 00 00 00 00 ..... ..........
00000020  00 00 6D 05 00 00 33 0F 00 00 7C 5B 13 7F 5C 5D ..m...3...|[..\]
00000030  56 40 5C 5E 56 13 7E 56 1C 7C 61 7A 74 7A 7D 72 V@\^V.~V.|aztz}r
00000040  7F 09 1C 77 5C 5D 13 74 5A 51 40 5C 5D 1C 33 33 ...w\].tZQ@\].33
00000050  33 1F 33 36 27 37 33 33 32 33 33 33 05 30 30 32 3.36'7332333.002
00000060  33 33 3D 0B 35 3A 32 33 33 7F 17 37 3C 32 33 32 33=.5:233..7<232
      
```


From the songs with English, I know the song title starts at 0x2A,
      and we have to do this match:
```

7C 5B 13 7F 5C 5D 56 40 5C 5E 56 13 7E 56 1C 7C 61 7A 74 7A 7D 72
O  h     L  o  n  e  s  o  m  e     M  e  /  O  R  I  G  I  N  A

7F 09 1C 77 5C 5D 13 74 5A 51 40 5C 5D 1C 33 33
L  :  /  D  o  n     G  i  b  s  o  n  /
      
```
The obvious thing to try is a substitution cipher: for example,
      the 'o's are encoded as 0x5c while the 'O's are 0x7c.
      It's a game of pattern matching, and the answer is the following
      piece of C code
```sh_cpp

#include <stdio.h>

int main(int argc, char **argv) {
    FILE *fp;
    FILE *ofp;

    if (argc == 1) {
	fp = stdin;
	ofp = stdout;
    } else if (argc == 2) {
	fp = fopen(argv[1], r);
	ofp = stdout;
    } else {
	fp = fopen(argv[1], r);
	ofp = fopen(argv[2], w);
    }

    char ch;
    int n = 0;
    
    while (n++ < 1500) {
	ch = getc(fp);

	switch (ch) {
	case 0x13: ch =  ; break;

	case 0x52: ch = a; break;
	case 0x51: ch = b; break;
	case 0x50: ch = c; break;

	case 0x57: ch = d; break;
	case 0x56: ch = e; break;
	case 0x55: ch = f; break;
	case 0x54: ch = g; break;

	case 0x5B: ch = h; break;
	case 0x5A: ch = i; break;
	case 0x59: ch = j; break;
	case 0x58: ch = k; break;

	case 0x5F: ch = l; break;
	case 0x5E: ch = m; break;
	case 0x5D: ch = n; break;
	case 0x5C: ch = o; break;

	case 0x43: ch = p; break;
	case 0x42: ch = q; break;
	case 0x41: ch = r; break;
	case 0x40: ch = s; break;

	case 0x47: ch = t; break;
	case 0x46: ch = u; break;
	case 0x45: ch = v; break;
	case 0x44: ch = w; break;

	case 0x4A: ch = y; break;

	    // These arent organised yet
	    //case 0x: ch = ; break;

	case 0x72: ch = A; break;
	case 0x71: ch = B; break;
	case 0x70: ch = C; break;

	case 0x77: ch = D; break;
	case 0x76: ch = E; break;
	case 0x75: ch = F; break;
	case 0x74: ch = G; break;

	case 0x7B: ch = H; break;
	case 0x7A: ch = I; break;
	case 0x79: ch = J; break;
	case 0x78: ch = K; break;

	case 0x7F: ch = L; break;
	case 0x7E: ch = M; break;
	case 0x7D: ch = N; break;
	case 0x7C: ch = O; break;

	case 0x63: ch = P; break;
	case 0x62: ch = Q; break;
	case 0x61: ch = R; break;
	case 0x60: ch = S; break;

	case 0x67: ch = T; break;
	case 0x66: ch = U; break;
	case 0x65: ch = V; break;
	case 0x64: ch = W; break;

	case 0x6B: ch = X; break;
	case 0x6A: ch = Y; break;
	case 0x69: ch = Z; break;

	case 0x09: ch = :; break;

	case 0x14: ch = \; break;

	default: ch = .; break;
	}
	putc(ch, ofp);
    }
    fclose(ofp);
    exit(0);
}

      
```
The substitutions here are grouped in fours, but of course there
      is no reason why they should be. (This is repeated in some
      other decodings, but not all.).

Following application of that substitution, the file looks like
```

00000000  2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E ................
00000010  2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E ................
00000020  2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 4F 68 20 4C 6F 6E ..........Oh Lon
00000030  65 73 6F 6D 65 20 4D 65 2E 4F 52 49 47 49 4E 41 esome Me.ORIGINA
00000040  4C 3A 2E 2E 6F 6E 20 47 69 62 73 6F 6E 2E 2E 2E L:..on Gibson...
00000050  2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E ................
00000060  2E 2E 2E 2E 2E 2E 2E 2E 2E 4C 2E 2E 2E 2E 2E 2E .........L......
00000070  2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E ................
00000080  2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E ................
00000090  45 2E 76 2E 65 2E 72 2E 79 2E 20 2E 62 2E 6F 2E E.v.e.r.y. .b.o.
000000A0  64 2E 79 2E 27 2E 73 2E 20 2E 67 2E 6F 2E 69 2E d.y.'.s. .g.o.i.
000000B0  6E 2E 27 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 49 2E 27 n.'..........I.'
000000C0  2E 6D 2E 20 2E 6A 2E 75 2E 73 2E 74 2E 20 2E 61 .m. .j.u.s.t. .a
000000D0  2E 20 2E 66 2E 6F 2E 6F 2E 6C 2E 2E 2E 2E 2E 2E . .f.o.o.l......
000000E0  2E 2E 2E 61 2E 6E 2E 64 2E 20 2E 68 2E 61 2E 76 ...a.n.d. .h.a.v
000000F0  2E 2E 2E 69 2E 6E 2E 6E 2E 6F 2E 6E 2E 65 2E 2E ...i.n.n.o.n.e..
00000100  2E 2E 2E 2E 2E 2E 2E 2E 68 2E 6F 2E 77 2E 20 2E ........h.o.w. .
00000110  2E 2E 73 2E 68 2E 65 2E 20 2E 73 2E 65 2E 74 2E ..s.h.e. .s.e.t.
00000120  20 2E 2E 2E 6D 2E 65 2E 20 2E 66 2E 72 2E 65 2E  ...m.e. .f.r.e.
00000130  65 2E 2E 2E 2E 2E 2E 2E 2E 2E 2E 54 2E 68 2E 61 e..........T.h.a
00000140  2E 74 2E 20 2E 6D 2E 69 2E 73 2E 74 2E 61 2E 6B .t. .m.i.s.t.a.k
      
```
Which is much more readable! it doesn't quite follow the lyrics
      though - an issue for later.

The next occurrence of this substitution cipher is at file
      10281, song number 20326 "Give me all night" 
      so there are other substitutions used,
      of course! Then at 10326, song number 20371 "Stand By Your Man"

So then I tried another song, California dreaming, song 20088, file 10043.
      That was pretty straightforward. Other songs using this substitution
      are 20033 Heartbreaker, file 9988, 20082 Another Girl, file 10037,
      20213 Don't talk, file 10168, 20382 Things we Said Today, file 10336.
      I also tried some others: no pattern as to song numbers.

However, the label for the substitution pattern appears
      to be byte 0x26. Here we another coincidence: the byte which
      is mapped to the space character ' ' is 0x20 less than byte
      0x26. e.g. the substitution for songs like file 10337 is
```sh_cpp

        switch (ch) {
        case 0x95: ch = ' '; break;

        case 0xD4: ch = 'a'; break;
        case 0xD7: ch = 'b'; break;
        case 0xD6: ch = 'c'; break;

        case 0xD1: ch = 'd'; break;
        case 0xD0: ch = 'e'; break;
        case 0xD3: ch = 'f'; break;
        case 0xD2: ch = 'g'; break;

        case 0xDD: ch = 'h'; break;
        case 0xDC: ch = 'i'; break;
        case 0xDF: ch = 'j'; break;
        case 0xDE: ch = 'k'; break;

        case 0xD9: ch = 'l'; break;
        case 0xD8: ch = 'm'; break;
        case 0xDB: ch = 'n'; break;
        ...
      
```
and byte 0x26 for that file is 0xB5, and 0x20 = 0xB5 - 0x95.
      Maybe the pattern is just based on these bytes (e.g. what is
      byte 0x27 - an index into pattern types?).

To be followed up...

There is one critival issue in this: it isn't only the English
      alphabetic characters that are encoded: others are too.
      But I have no clues as to what the other 65000+ Unicode
      characters should be!

