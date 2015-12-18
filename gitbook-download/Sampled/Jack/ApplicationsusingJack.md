#  Applications using Jack 

There are many pieces of software using Jack, described in
 [
	Applications using JACK
      ] (http://jackaudio.org/applications)


###  mplayer 

To run
 `mplayer`using Jack, add the
      option
 `-ao jack`:
```

	
mplayer -ao jack 54154.mp3
	
      
```



 `mplayer`used in this way will connect to the
      Jack
 `system`output device. To output to
      another Jack application such as
 `jack-rack`,
      append the output application to the audio output command
```

	
mplayer -ao jack:port=jack_rack 54154.mp3
	
      
```


###  VLC 

VLC will play to Jack output if the
 [Jack module] (https://wiki.videolan.org/Documentation:Modules/jack/)
is included.
      This is available as a downloadable Debian package
 `vlc-plugin-jack`. You can check if you have it by
      seeing if jack is listed as a module in
 `vlc --list`shows ALSA but not Jack.

Play a file using Jack by e.g.
```

	
vlc --aout jack 54154.mp3
	
      
```
You should be able to connect to a particular Jack application
      using the option
 `--jack-connect-regex ` `<` `string` `>`.

###  TiMidity

TiMidity is a MIDI player discussed later. It can play
      to Jack output devices by
```

	
timidity -Oj 54154.mid
	
      
```


###  Jack-supplied programs 

Jack comes with a large number of clients:
```

	
jack_alias                  jack_midisine
jack_bufsize                jack_monitor_client
jack_connect                jack_multiple_metro
jack_control                jack_net_master
jack_cpu                    jack_net_slave
jack_cpu_load               jack_netsource
jackd                       jack_rec
jackdbus                    jack_samplerate
jack_disconnect             jack_server_control
jack_evmon                  jack_session_notify
jack_freewheel              jack_showtime
jack_iodelay                jack_simple_client
jack_latent_client          jack_simple_session_client
jack_load                   jack_test
jack_lsp                    jack_thru
jack_metro                  jack_transport
jack_midi_dump              jack_unload
jack_midi_latency_test      jack_wait
jack_midiseq                jack_zombie
	
      
```
For many of these the source code is available in the Jack
      source code distribution and there is a
 `man`page for each one.

Running, say,
 `jack_thru`connects the
      system capture ports to the
 `jack_thru`input ports and the
 `jack_thru`output
      ports to the system playback ports. You can 
      then do things such as disconnect ports using "client:port"
      for the port name as in
```

	
jack_disconnect jack_thru:output_1 system:playback_1
	
      
```
These command line tools allow you to do the same kind
      of actions as
 `qjackctl`

###  Other Jack programs 

The page
 [
	Applications using JACK
      ] (http://jackaudio.org/applications)
lists many applications using Jack.

The page
 [
	Jack MIDI Apps
      ] (http://apps.linuxaudio.org/apps/categories/jack_midi)
at linuxaudio.org
      lists many MIDI applications using Jack

