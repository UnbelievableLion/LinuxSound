
##  Changing the soundbank 


The soundbank is a set of "sounds" encoded in some way that
are used to generate the music played. The default sound
synthesizer for Java is the      Gervill synthesizer,
and this looks for its default soundbank in `$HOME/.gervill/soundbank-emg.sf2`.
This default soundbank is tiny, only 1.9MBytes in size,
and sounds, well, poor quality.


DaWicked1 in [Better Java-midi instrument sounds for Linux](http://www.minecraftforum.net/forums/mapping-and-modding/mapping-and-modding-tutorials/1571330-better-java-midi-instrument-sounds-for-linux) offers two methods to improve this: the simpler is to replace the
soundfont with a better one such as the Fluidsynth font,
using the default name.


The second method is programmatic and probably
better as it allows more flexibility and choice at
runtime.
