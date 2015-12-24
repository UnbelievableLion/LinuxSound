
##  Converting MP3+G to video files 


> The tool `ffmpeg`can merge the audio and
      video to a single video file by e.g.

```

        
ffmpeg -i Track1.cdg -i Track1.mp3 -y Track1.avi
        
      
```


> or

```

        
avconv -i Track1.cdg -i Track1.mp3 test.avi
avconv -i test.avi -c:v libx264 -c:a copy outputfile.mp4
        
      
```


> to create an AVI file containing both video and audio.
      This can be played by vlc, mplayer, rhythmbox, etc.


> There is a program [
        cdg2video](http://code.google.com/p/cdg2video/) .
      While it is last dated February, 2011, changes in the FFMpeg
      internals means that it no longer compiles. Even if you fix
      the obvious changes, there are a huge number of complaints
      from the C compiler about the use of deprecated FFMpeg
      functions.
