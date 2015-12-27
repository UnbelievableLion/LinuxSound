
##  VLC 


VLC is an immensely flexible media player. It relies on a large set of plugins
to enhance its basic core functionality. We saw in an earlier chapter that
if a directory contains both an MP3 and a CDG file with the same basename
then by asking it to play the MP3 file it will also show the CDG video.


Common expectations of Karaoke players are that you can adjust the speed and pitch.
Currently VLC cannot adjust pitch, but it does have a plugin to adjust speed
(while keeping the pitch unchanged). This plugin can be accessed by the [Lua](http://www.videolan.org/developers/vlc/share/lua/intf/cli.lua) interface to VLC.
Once set up, you can send commands such as

```

	
rate 1.04	  
	
      
```


across standard input from the process that started VLC (such as a
command line shell). This will change the speed and leave the pitch
unchanged.


Setting up VLC to accept Lua commands from stdin can be done by the command options

```

	
vlc -I luaintf --lua-intf cli ...
	
      
```


Note that this takes away the standard GUI controls (menus, etc) and
controls VLC from stdin only.


At present, it is not simple to add pitch control to VLC.
Take a deep breath:

+ Turn off PulseAudio and start Jack
+ Run `jack-rack`and install the `TAP_pitch`filter
+ Run VLC with Jack output
+ Using `qjackctl`hook VLC to output through `jack-rack`, which outputs to system
+ Control pitch through the `jack-rack`GUI