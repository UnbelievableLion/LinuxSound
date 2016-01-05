
##  Sound tools 

###  sox 


SoX is the Swiss Army knife of sound processing programs.


Its home page is [SoX - Sound eXchange](http://sox.sourceforge.net/) 

###  FFmpeg/avconv 


ffmpeg is generally used as a converter from one format to another.
There is a nice series of tutorials at [A FFmpeg Tutorial For Beginners](http://linuxers.org/tutorial/ffmpeg-tutorial-beginners) by shredder12


It can also be used to record from ALSA devices such as hw:0 or the default device.
Recording from hw:0 can be done by

```
ffmpeg -f alsa -i hw:0 test.mp3
```


and from the default ALSA input by

```
ffmpeg -f alsa -i default test.mp3
```


There was a fork some years ago of ffmpeg to give avconv.
avconv is the default on Ubuntu systems. There are
some differences between the two, not enough to
justify the nuisance factor to us users.

###  GStreamer 


GStreamer allows you to build "pipelines" that can be played using `gst-launch`.
For example, to play an MP3 file using ALSA you would have the pipeline

```
gst-launch filesrc location="concept.mp3" ! decodebin ! alsasink
```


The pipelines can do more complex tasks such as format conversion, mixing, etc.
A tutorial is [Multipurpose multimedia processing with GStreamer](http://www.ibm.com/developerworks/aix/library/au-gstreamer.html?ca=dgr-lnxw07GStreamer) by Maciej Katafiasz


It can also play MIDI files by e.g.

```
gst-launch filesrc location="rehab.mid" ! decodebin ! alsasink
```
