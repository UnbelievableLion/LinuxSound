
##  Playing songs with pykar 


One of the simplest ways to play Karaoke Midi files is by
      using [
	pykar
      ](http://www.kibosh.org/pykaraoke/) .
      Regrettably, the songs ripped fromt he Sonken disk do not
      play properly - this is a mixture of bugs in pykar and
      features required which are not supplied. 
      The problems and their solutions follow.

####  Tempo 


Many Midi files will set the tempo explicitly using the Meta
      Event Set Tempo, 0x51. These files often do not.
      Pykar expects a Midi file to include this event, and otherwise
      defaults to a tempo of zero beats per minute. As might be expected,
      this trhows out all timing calculations performed by
      PyKar.


As [
	The Sonic Spot](http://www.sonicspot.com/guide/midifiles.html) explains, 
      "If no set tempo event is present, 120 beats per minute is assumed"
      and gives a formula for calculating the appropriate tempo value,
      which is 60000000/120.


This requires one change to one PyKaraoke file: change
      line 190 of `pykar.py`from

```

sele.Tempo = [(0, 0)]
      
```


to

```

self.Tempo = [(0, 500000)]
      
```

####  Language encoding 


The file `pykdb.py`clains that `cp1252`is the default character encoding for Karaoke files,
      ans uses a font `DejaVuSans.tt`which is
      appropriate for displaying such characters.
      This encoding adds in various European symbols such as
      'á' in the top 128 bits of a byte, in addition
      to standard ASCII.


I'm not sure where PyKaraoke got that information from,
      but it certainly doesn't apply to Chinese Karaoke.
      I don't know what encodings Chinese, Japanese, Korean, etc
      use, but my code dumps them out as Unicode UTF-8.
      A suitable font for Unicode is Cyberbit.ttf.
      (See the Fonts chapter in my lecture notes on [
	Global Software](http://jan.newmarch.name/i18n/) ).


The file `pykdb.py`needs the lines

```

        self.KarEncoding = 'cp1252'  # Default text encoding in karaoke files
        self.KarFont = FontData("DejaVuSans.ttf")
      
```


changed to

```

        self.KarEncoding = 'utf-8'  # Default text encoding in karaoke files
        self.KarFont = FontData("Cyberbit.ttf")
      
```


and a copy of `Cyberbit.tt`copied to the directory `/usr/share/pykaraoke/fonts/`.

####  Songs with no notes 


Some songs on the disk have no MIDI notes, as this is all in 
      a WMA file. The MIDI file only has the lyrics.
      PyKaraoke only plays upto the last note, which is at zero!.
      So no lyrics are played.
