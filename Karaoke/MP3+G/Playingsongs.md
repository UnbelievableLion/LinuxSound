
##  Playing songs 


Whenever a song is "played" its file path is written to standard output.
This makes it suitable for use in a pipeline such as

```cpp

VLC_OPTS="--play-and-exit --fullscreen"

java  SongTableSwing |
while read line
do
        if expr match "$line" ".*mp3"
        then
                vlc $VLC_OPTS "$line"
        elif expr match "$line" ".*zip"
        then
                rm -f /tmp/karaoke/*
                unzip -d /tmp/karaoke "$line"
                vlc $VLC_OPTS /tmp/karaoke/*.mp3
        fi
done
      
```
