
##  The data files 

###  General 


The files DTSMUS00.DKD - DTSMUS07.DKD contain the music files.
      There are two formats for the music: Microsoft WMA files and 
      MIDI files. In my song books some songs are marked as having
      a singer. These turn out to be the WMA files. Those without
      a singer are MIDI files.


The WMA files are just that. The MIDI files are slightly
      compressed and have to be decoded before they can be played.


Each song block has at the beginning a section containing the lyrics.
      These are compressed and have to be decoded.


The data for one song forms a record of contiguous bytes.
      These records are collected into blocks, also contiguous.
      The blocks are separate. There is a "super block" of pointers
      to these blocks. Part of the song number is an index into the
      super block, selecting the block. The rest of the song number
      is an index of the record in the block.

###  My route into this 


I came backwards into this and only arrived at understanding
      what others had accomplished after some time. So in case it
      helps any others, here is my route.


I used the Unix command `strings`to discover the
      songs information in DTSMUS10.DKD. On the other files it
      didn't seem to produce much. But there were ASCII strings
      in these files and
      some were repeated. So I wrote a shell pipeline to sort these
      strings and count them. The pipeline for one file was

```

	
	  strings DTSMUS05.DKD | sort |uniq -c | sort -n -r |less	
	
      
```


This produced results

```

	
	  1229 :^y|
	  1018 j?wK
	  843 ]/<
	  756  Seh
	  747  Ser
	  747 _\D+P
	  674 :^yt
	  234 IRI$	
	
      
```


The results weren't inspiring. But when I looked inside the files
      to see where "Ser" was occurring, I also saw:

```

	
	  q03C3E230  F6 01 00 00 00 02 00 16 00 57 00 69 00 6E 00 64 .........W.i.n.d
	  03C3E240  00 6F 00 77 00 73 00 20 00 4D 00 65 00 64 00 69 .o.w.s. .M.e.d.i
	  03C3E250  00 61 00 20 00 41 00 75 00 64 00 69 00 6F 00 20 .a. .A.u.d.i.o.
	  03C3E260  00 39 00 00 00 24 00 20 00 34 00 38 00 20 00 6B .9...$. .4.8. .k
	  03C3E270  00 62 00 70 00 73 00 2C 00 20 00 34 00 34 00 20 .b.p.s.,. .4.4.
	  03C3E280  00 6B 00 48 00 7A 00 2C 00 20 00 73 00 74 00 65 .k.H.z.,. .s.t.e
	  03C3E290  00 72 00 65 00 6F 00 20 00 31 00 2D 00 70 00 61 .r.e.o. .1.-.p.a
	  03C3E2A0  00 73 00 73 00 20 00 43 00 42 00 52 00 00 00 02 .s.s. .C.B.R....
	  03C3E2B0  00 61 01 91 07 DC B7 B7 A9 CF 11 8E E6 00 C0 0C .a..............
	  03C3E2C0  20 53 65 72 00 00 00 00 00 00 00 40 9E 69 F8 4D  Ser.......@.i.M	
	
      
```


Wow! _two byte_ characters!


The `strings`command has options to look at e.g. 2-byte 
      big-endian character strings. The command

```

	
	  strings -e b DTSMUS05.DKD
	
      
```


turned up

```

	
	  IsVBR
	  DeviceConformanceTemplate
	  WM/WMADRCPeakReference
	  WM/WMADRCAverageReference
	  WMFSDKVersion
	  9.00.00.2980
	  WMFSDKNeeded
	  0.0.0.0000
	
      
```


These are all part of the WMA format.


According to Gary Kessler's [
	FILE SIGNATURES TABLE
      ](http://www.garykessler.net/library/file_sigs.html) , 
      the signature of a WMA file is given by the header

```

	
	  30 26 B2 75 8E 66 CF 11
	  A6 D9 00 AA 00 62 CE 6C	
	
      
```


and that pattern does occur, with the above strings appearing some time later.


The spec for the ASF/WMA file format is at [
	Advanced Systems Format (ASF) Specification
      ](http://www.microsoft.com/download/en/details.aspx?displaylang=en&id=14995) although you are advised not to read it in case you want to do anything
      open source with such files.


So on that basis I could indentify the start of WMA files.
      The 4 bytes preceding each WMA file are the length of the
      file. From that I could find the _end_ of the file,
      which turned out to be the start of a record for the _next_ record containing some stuff and
      then the next WMA file.


In these records I could see patterns I couldn't understand,
      but also from byte 36 on I could see strings like

```

	
	  AIN'T IT FUNNY HOW TIME SLIPS AWAY, Str length: 34


	  00000000  10 50 41 10 50 49 10 50 4E 10 50 27 10 50 54 10 .PA.PI.PN.P'.PT.
	  00000010  50 20 11 F1 25 12 71 05 04 61 05 05 51 21 13 01 P ..%.q..a..Q!..
	  00000020  02 05 91 2B 10 20 48 10 50 4F 10 50 57 13 40 00 ...+. H.PO.PW.@.
	  00000030  12 61 02 12 01 02 04 D1 05 04 51 3B 05 31 05 04 .a........Q;.1..
	  00000040  C1 29 10 20 50 10 51 45 10 21 28 10 21 1E 10 21 .). P.QE.!(.!..!
	  00000050  3A 14 F1 05 13 31 02 10 C1 0E 11 A1 58 15 A0 00 :....1......X...
	  00000060  15 70 00 13 A0 A9                               .p....
	
      
```


Can you see "A.I.N.'.T" ( as ".PA.PI.PN.P'.PT")?


But I couldn't figure out what the encoding was or how to
      find the table of song starts. That's when I was ready to look at
      the earlier stuff and understand how it applied to me.
      ( [
	Understanding the HOTDOG files on DVD of California electronics
      ](http://old.nabble.com/Understanding-the-HOTDOG-files-on-DVD-of-California-electronics-td11359745.html) , [
	Decoding JBK 6628 DVD Karaoke Disc
      ](http://old.nabble.com/Decoding-JBK-6628-DVD-Karaoke-Disc-td12261269.html) and [
	Karaoke Huyndai 99
      ](http://board.midibuddy.net/showpost.php?p=533722&postcount=31) ).

###  The super block 


The file DTSMUS00.DKD starts with a bunch of nulls. At 0x200 it starts
      to kick in with data. This was identified as the start of a "table
      of tables" i.e. a superblock. Each entry in this superblock
      is a 4-byte integer, which turns out to be an index to tables
      in the data files. The superblock is terminated by a
      sequence of nulls (for me at 0x5F4) and there are  less than 256 indexes 
      in the table.


The value of these superblock entries seems to have changed in
      different versions. In the JBK disk and also on mine, the
      values have to be multiplied by 0x800 to give a "virtual offset"
      in the data files.


To give meaning to this: on my disk at 0x200 is

```

	
	  00000200  00 00 00 01 00 00 08 6C 00 00 0F C1 00 00 17 7A 
	  00000210  00 00 1E 81 00 00 25 21 00 00 2B 8D 00 00 32 B7 
	
      
```


So the table values are 0x1, 0x86C, 0xFC1, 0x177A, ...
      The "virtual addresses" are  0x800, 
      0x436000 (0x86C * 0x800) and so on.
      If you go to these addresses, then before the address is a bunch of nulls,
      and at that address is data.


Why I call them virtual addresses is because there are 8 data files
      on my DVD and most addresses are larger than any of the files.
      The files in my case are all 1065353216L (except the last) bytes.
      The "obvious" solution works:  
      the file number is address / file size, and the offset into
      the file is address % file size. You can check this by
      looking for the nulls before the address of each block.

###  Song start tables 


Each of the tables indexed from the super block is a table
      of song indexes. Each  table contains 4-byte indexes.
      Each table has at most 0x100 entries, or is terminated by a
      zero index.  Each index is the offset from the table start 
      of the beginning of a song entry.

###  Locating song entry from song number 


Given a song number such as 54154 "Here Comes The Sun" we can now find
      the song entry. Reduce the song number by one to 54153. It is a 16-bit
      number. The top 8 bits are the index of the song index table
      in the superblock.
      The bottom 8 bits are the index of the song entry in the song index table.


Pseudocode:

```

	
	  songNumber = get number for song from DTSMUS20.DKD
	  superBlockIdx = songNumber >>
	  indexTableIdx = songNumber & 0xFF

	  seek(DTSMUS00.DKD, superBlockIdx) 
	  superBlockValue = read 4-byte int from DTSMUS00.DKD

	  locationIndexTable = superBlockValue * 0x800
	  fileNumber = locationIndexTable / fileSize
	  indexTableStart = locationIndexTable % fileSize
	  entryLocation = indexTableStart + indexTableIdx 

	  seek(fileNumber, entryLocation)
	  read song entry
	
      
```

###  Song entries 


Each song entry has a header and is followed by two blocks that I
      call the information block and the song data block.
      Each header block has a 2-byte type code and a 2-byte integer length.
      The type code is either 0x0800 or 0x0000. The code signals the encoding
      of the song data: 0x0800 is a WMA file while 0x0000 is a MIDI
      file.


If the type code is 0x0 such as the Beatles "Help!" (song number 51765)
      then the information block has the length in the header block and starts
      12 bytes further in.
      The song data block immediately follows this.


If the type code is 0x8000 then the information block starts 4 bytes in
      for the length given in the header. The song block starts on the next
      16-byte boundary from the end of the information block.


The song block starts with a 4-byte header which is the length of the
      song data for all types.

###  Song data 


If the song type is 0x8000 then the song data is a WMA file.
      All songs looked at have a singer included in this file.


If the song type is 0x0 then (from the book) there is no singer
      in the songs looked at.
      The file is encoded, and decodes to a MIDI file.
