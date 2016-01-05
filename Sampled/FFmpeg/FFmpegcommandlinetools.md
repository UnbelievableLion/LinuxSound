
##  FFmpeg command line tools 


The principal FFmpeg tool is `ffmpeg`itself.
The simplest use is as a converter from one  format
to another as in

```
ffmpeg -i file.ogg file.mp3
```


which will convert an Ogg container of Vorbis codec data to an
MPEG container of MP2 codec data.


Internally, `ffmpeg`uses a pipeline of modules

```example
_______              ______________               _________              ______________            ________
|       |            |              |             |         |            |              |          |        |
| input |  demuxer   | encoded data |   decoder   | decoded |  encoder   | encoded data |  muxer   | output |
| file  | ---------> | packets      |  ---------> | frames  | ---------> | packets      | -------> | file   |
|_______|            |______________|             |_________|            |______________|          |________|
```


(Figure from [ffmpeg Documentation](http://ffmpeg.org/ffmpeg.html) .)
The muxer/demuxer, decoder/encoder can all be set using options if the defaults are not
appropriate.


Other commands are

+  `ffprobe`to give information about a file
+  `ffplay`a simple media player
+  `ffserver`a media server