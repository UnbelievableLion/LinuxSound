# jack_connect

The programs
 `jack_connect`and
 `jack_disconnect`canbe used to reconfigure connections between clients. For example,
      the MIDI player
 `TiMidity`will connect its output ports to the first
      available Jack input ports, which are generally the system ports connected
      to the sound card. If you wish to connect
 `TiMidity`to, say,
 `jack-rack`then its output ports have to be first disconnected
      and then connected to the correct ones. On the other hand,
 `jack-rack`does not connect to anything by default
      so may need to be connected to the system ports. This is done by e.g.
```sh_cpp

jack_disconnect TiMidity:port_1 system:playback_1
jack_disconnect TiMidity:port_2 system:playback_2

jack_connect TiMidity:port_1 jack_rack:in_1
jack_connect TiMidity:port_2 jack_rack:in_2

jack_connect jack_rack:out_1 system:playback_1
jack_connect jack_rack:out_2 system:playback_2
      
```


