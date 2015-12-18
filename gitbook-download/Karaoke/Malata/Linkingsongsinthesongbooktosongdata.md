#  Linking songs in the song book to song data 

The file MULATAS4.IDX, we have determined, holds a table of
      25 byte blocks starting at 0x800. The current knowledge of
      these blocks is


11

language (00 is GB2132, 07 is English)



15-17

song number in song book (read the hex number as decimal)


19-20

offset of song title into table at 0x5F000



25

length of title




The song data is spread across files MULTAK.DAT - MULTAK.DA4.
      At 0xd20 in MULTAK.DAT is a table of 4 bytes indexes.
      Each index translates into a starting location in the various
      data files. These are of type "simple" (probably MIDI data only)
      and "complex" (MIDI plus MP3).

The problem now is to link the song information to its data.

Using the starting points of each data file, we can extract, say,
      a few thousand bytes from each file. The correct length is at present
      unknown. I saved them them as files 1, 2, 3, ..., 15460.

With them all in separate files, I tried to see if any of them 
      were recognisable. Completely by fluke by running
 `strings`looking for Fool on the Hill (which I knew was on the disk), I hit upon song
      10397 by searching for "hill", with
 `bvi`showing
```

00000000  00 00 4F 4B 00 00 00 00 00 00 00 00 00 00 00 00 ..OK............
00000010  00 00 00 00 00 20 00 00 00 07 00 00 00 00 00 00 ..... ..........
00000020  00 00 91 06 00 00 20 11 00 00 77 48 41 54 00 64 ...... ...wHAT.d
00000030  52 45 41 4D 53 00 61 52 45 00 6D 41 44 45 00 6F REAMS.aRE.mADE.o
00000040  46 0F 6F 72 69 67 69 6E 61 6C 1A 0F 68 49 4C 4C F.original..hILL
00000050  41 52 59 00 64 55 46 46 20 20 20 52 20 25 C8 2E ARY.dUFF   R %..
      
```
This song isn't in my song book, but it is in the list I pulled out
      of MALATAS4.IDX:
```

00 00 00 77 64 61 6D 6F 00 04 07 00 00 05 02 04 42 01 87 CE F1 02 05 80 17  SongIndex 20442  ArtistIndex F102 10415: What Dreams Are Made Of
      
```
So song title 20442 has its song data in file 10397.

With this clue, doing something like
 `strings -f -n 30 *`quickly shows up other files with english text. Enough to draw up
      a table


ID

Song # in book

Index to data

Song title


S1

20247

10202
NEXT 100 YEARS

S2

20428

10383
Lovers

S3

20442

10397
What dreams are...

S4

20154

10109
Only sleeping

and this is just linear:
```

data index = song number - 10045
      
```
NB: this only works for some songs - I guess the English ones!
      If this pattern holds for all English songs, the earliest data
      file is (20001-10045) = 9956 and the last one is
      (20501-10045) = 10456.

