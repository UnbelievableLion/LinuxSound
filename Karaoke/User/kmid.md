
##  kmid 


>  ` kmid `is a KDE-based Karaoke player. It plays the song
and shows where in the lyrics you are. A screen dump of "Smoke gets in your
eyes" looks like


![alt text](kmid.png)


kmid uses either Timidity or Fluidsynth as MIDI backend.


>  `kmid`plays the soundtrack and displays the lyrics. It does not act as a
proper Karaoke system by also playing the singer's input. But `kmid`can use the PulseAudio system, so you can simultaneously play other programs.
In particular, you can have `kmid`running in one window, while `pa-mic-2-speaker`is running in another. PulseAudio
will mix the two output streams and play both sources together.
Of course, there will no scoring possible in such a system without
extra work.
