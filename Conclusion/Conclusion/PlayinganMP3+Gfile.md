
##  Playing an MP3+G file 


An Mp3+G pair is pulled off the server as a ZIP file.
After unzipping, it can be played by `vlc`. `vlc`can use a Lua interface to which you
can send commands such as "faster", "slower".


The script is `playZip`

```sh
#!/bin/bash

VLC_OPTS=" -I luaintf --lua-intf cli   --play-and-exit --aout jack"

HTTP=http:/

[ ! -d /tmp/karaoke ] && mkdir /tmp/karaoke
rm -f /tmp/karaoke/*
wget "${HTTP}$*" -O /tmp/karaoke/tmp.zip
unzip -d /tmp/karaoke /tmp/karaoke/tmp.zip
rm /tmp/karaoke/tmp.zip
vlc $VLC_OPTS /tmp/karaoke/*.??3
```



