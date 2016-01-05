
##  Playing a KAR file 


KAR files ripped of the Sonken player may have audio plus
lyrics, or lyrics only with the audio in a linked WMA files.
The MIDI player `timidity`can be used to play
the KAR part, but for WMA files another player such as `mplayer`is needed.


An annoying part of `timidity`is that you cannot set the
Jack output device to connect to. So you need to wait till it has
registered with Jack, and then call `jack-connect`to link it to `jack-rack`.


The shell script is `playKar`:

```sh
#!/bin/bash
set -x

HTTP=http:/

echo Fetching $*

[ ! -d /tmp/karaoke ] && mkdir /tmp/karaoke
rm -f /tmp/karaoke/*
wget "${HTTP}$*" -O /tmp/karaoke/tmp.kar

WMAFILE="${*/.kar/.wma}"
echo wget "${HTTP}${WMAFILE}" -O /tmp/karaoke/tmp.wma > /tmp/out0
wget "${HTTP}${WMAFILE}" -O /tmp/karaoke/tmp.wma

if [ -s "/tmp/karaoke/tmp.wma" ]
then
    bash ./playMplayer /tmp/karaoke/tmp.wma &
    cd ../timidity
    ./TiMidity++-2.14.0/timidity/timidity -d. -ix --trace --trace-text-meta /tmp/karaoke/tmp.kar &
    cd ../Karaoke
    sleep 3
    jack_disconnect TiMidity:port_1 system:playback_1
    jack_disconnect TiMidity:port_2 system:playback_2

    wait %1
    killall mplayer
    # WMA file
#    java -jar WMAPlayer.jar /tmp/karaoke/tmp.kar  > /dev/null 2> /dev/null
else
    # pykar /tmp/karaoke/tmp.kar > /dev/null 2> /dev/null
    # give pykar time to give up audio card
    #sleep 4

    cd ../timidity
    ./TiMidity++-2.14.0/timidity/timidity -d. -ix --trace --trace-text-meta /tmp/karaoke/tmp.kar &
    sleep 3
    jack_disconnect TiMidity:port_1 system:playback_1
    jack_disconnect TiMidity:port_2 system:playback_2
    jack_connect TiMidity:port_1 jack_rack:in_1
    jack_connect TiMidity:port_2 jack_rack:in_2
fi
    wait %1
    cd ../Karaoke
fi
```



