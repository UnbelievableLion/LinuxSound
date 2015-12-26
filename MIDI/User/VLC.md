
##  VLC 


VLC is a general purpose media player. 
      There is a [
	VLC module](https://wiki.videolan.org/Midi) to handle MIDI files using
      FluidSynth.
      To get this working on a Debian system you first need to
      intall the `vlc-plugin-fluidsynth`package.
      Then in Advanced Options of VLC, choose Codecs-Audio Codecs-FluidSynth.
      You will need to set the soundfont, eg. to `/usr/share/sounds/sf2/FluidR3_GM.sf2`.
