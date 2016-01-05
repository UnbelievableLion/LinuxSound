
##  GStreamer 


GStreamer allows you to build "pipelines" that can be played using `gst-launch`.
It can play MIDI files by e.g.

```
gst-launch filesrc location="rehab.mid" ! decodebin ! alsasink
```
