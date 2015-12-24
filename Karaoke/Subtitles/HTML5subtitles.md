
##  HTML5 subtitles 


HTML 5 has support for video types, although exactly what video
      format is supported by which brower is variable.
      Standard audio and video was discussed in the chapter
      on [ Streaming HTML5 ](../../Streaming/HTML5/) .


A more recent development has been to include subtitles in HTML5 video.
      Under Linux it is currently (June 2013) only supported by the Chromium
      browser. A tutorial is at [
	Video Subtitling and WebVTT:  HTML5 Doctor
      ](html5doctor.com/video-subtitling-and-webvtt/) and specified at [
	HTML5: 4.8.9 The track element
      ](http://dev.w3.org/html5/spec-preview/the-track-element.html) .


You need to prepare a file of timing and text instructions.
      The format shown in examples is as a .vtt file and can be

```

	
WEBVTT

1
00:00:01.000 --> 00:00:30.000  D:vertical A:start
This is the first line of text, displaying from 1-30 seconds

2
00:00:35.000 --> 00:00:50.000
And the second line of text
separated over two lines from 35 to 50 seconds
        
      
```


where the first line is "WEBVTT" and blocks of text are separated by
      blank lines.
      The format of VTT files is specified at [
	WebVTT: The Web Video Text Tracks Format
      ](http://dev.w3.org/html5/webvtt/) .


The HTML then references the A/V files and the subtitle file as in

```

	
    <video  controls>
      <source src="output.webm" controls>
      <track src="54154.vtt" kind="subtitles" srclang="en" label="English" default />
      <!-- fallback for rubbish browsers -->
    </video>
	
      
```


A screen capture is


![alt text](chrome.png)


There does no seem to be any mechanism for highlighting words
      progressively in a line.
      Possibly JavaScript may be able to do so, but at a cursory look it
      doesn't seem likely. This makes it not yet suitable for Karaoke.
