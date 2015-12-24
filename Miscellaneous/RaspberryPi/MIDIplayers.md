
##  MIDI players 

###  Timidity 


Timidity hits upto 90% CPU. It can't play MIDI files on the RPi properly using the
      soft float dsitro, but is just about okay on the hard float distro.


To make the RPi usable, in the `timidity.cfg`file uncomment the lines

```

	
## If you have a slow CPU, uncomment these:
#opt EFresamp=d         #disable resampling
#opt EFvlpf=d           #disable VLPF
#opt EFreverb=d         #disable reverb
#opt EFchorus=d         #disable chorus
#opt EFdelay=d          #disable delay
#opt anti-alias=d       #disable sample anti-aliasing
#opt EWPVSETOZ          #disable all Midi Controls
#opt p32a               #default to 32 voices with auto reduction
#opt s32kHz             #default sample frequency to 32kHz
#opt fast-decay         #fast decay notes
	
      
```


This brings the CPU usage down to about 30%.
      (Thanks to [
	Chivalry Timber](http://chivalrytimberz.wordpress.com/2012/12/03/pi-lights/) ).

###  PyKaraoke 


This only uses 40% of the CPU and plays okay, even giving a GUI on the soft float distro.

###  Fluidsynth/Qsynth 


This just sat there doing not very at all using soft float Debian wheezy out of the box.
      I spent some time with the FluidSynth team investigating possibilities.

####  Images 


The soft float image is unusable. You need to use the hard float image.

####  Scheduling 


Sometimes fluidsynth complains about not being able to reset the scheduler. [
	Aere Greenway
      ](http://lists.gnu.org/archive/html/fluid-dev/2012-10/msg00018.html) suggests making the following security changes:


   > You need to create a file (whose name starts with your user-ID) 
	in the following folder:  /etc/security/limits.d
	For example, my user-ID is aere, so the filename I use is: aere.conf
	The file needs to contain the following lines:
```

	  
aere - rtprio 85
aere - memlock unlimited
	  
	
```


> Except, substitute your user-ID in place of "aere".




This is necessary, but not sufficient
      It did help with the
      Raspbian hard-float image, but only a little: some MIDI files played fine
      while others broke up badly.

####  Analysis tools 


The simplest tool to analyse performance is `perf`.
      This will give a breakdown of the percentage of CPU usage for
      the function calls within a program.


 `perf`averages the results over an execution period.
      The MIDI songs I tried only misplayed in parts, not over the whole
      song. `perf`can however be run as a separate process
      to sample every second
      by the command

```

	
perf top -d 1
	
      
```


You can then observe function calls over one second periods.


This didn't reveal much in this instance, but may be helpful in other
      cases.


The command `pidstat`can be run by e.g.

```

	
pidstat -C fluidsynth -r -u 5
	
      
```


to give CPU and memory usage every 5 seconds. it is similar to `top`but just writes figures for the command to stdout. The output can be massaged
      using shell scripts and shown as a histogram using GNU octave.
      This shows that the distortion occurs when CPU usage hits over 100% (don't
      ask me how!). Memory usage is fine, around 40%.

#### Non-causes


The following were suggested as causes of the problems, but ultimately discarded

+ Fluidsynth can be configured to use either doubles or floats.
	  The default is doubles, and these are slow on Arm chips.
	  Switching to floats didn't remove the problem peaks in CPU use
+ Fluidsynth uses soundfont files and these are quite large: about 40M
	  is typical. Switching to smaller fonts didn't help - memory use was
	  not the problem
+ Buffering is small in fluidsynth. The "-z" parameter can be used to make
	  it larger. Buffering was not the problem and changing it didn't help
+ A number of operations are known to be expensive in CPU.
	  Fluidsynth supports a number of interpolation algorithms
	  and these can be set using its command interpreter by e.g.
	  "interp 0" to turn off interpolation.
	  Other expensive operations include reverb, polyphony and chorus.
	  Mucking around with any of these in isolation proved fruitless.



#### Solutions


The two solutions that I have found are

+ polyphony=64 and reverb=false; or
+ rate=22050


