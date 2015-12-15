#  Sampled audio players 

###  MPlayer

MPlayer plays fine on the default ALSA modules, for mp3, ogg and wav.

###  VLC 

VLC attempts to play wav files, but it is very broken up on the soft float distro. 
      CPU usage is up around 90% and it is
      quite unplayable. The hard float distro can play wav, mp3 and ogg.

###  Alsaplayer 

The program
 `alsaplayer`can attempt to play files in formats such as Ogg-Vorbis
      and MP3.
      However, CPU usage hits as high as 80% on the soft float at which point the 
      sound falls to pieces. The hard float distro is okay.

###  OmxPlayer 

The RPi has GPU, and this can be used
      by omxplayer. It can play Ogg-Vorbis files with only 12% CPU usage and looks to be
      a good candidate for audio as well as video.

###  Is it X using the CPU? 

Apparently not just X: gnome-player works fine.

