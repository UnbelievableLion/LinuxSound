
##  Sound fonts 


The tools described in this chapter each include a software synthesizer.
      This produces audio as PCM data from the MID data fed to it.
      The MIDI data contains information about the instrument playing each
      note, and of course, every instrument sounds different.
      So the synthesizer must make use of mapping information from
      MIDI notes + instrument into PCM data.


The mapping is usually done using _soundfont_ files.
      There are various formats for this, of which the primary one
      is the [ 
	.sf2
      ](http://connect.creativelabs.com/developer/SoundFont/Forms/AllItems.aspx/) format.
      Some synthesizers (such as Timidity) can also use Gravis UltraSound
      patches, which are recorded real instruments.


Many soundfont files have been created. See for example [
	Links to SoundFonts and other similar files
      ](http://www.synthfont.com/links_to_soundfonts.html) (although many of the links are broken).

+ A common sound font is from FluidSynth, as `/usr/share/sounds/sf2/FluidR3_GM.sf2`.
	  This file is nearly 150Mbytes - soundfonts are not small!
+ JavaSound has a soundfont `soundbank-emg.sf2`.
	  This is considerably smaller at 1.9Mb!
+ Another popular soundfont is at [
	    GeneralUser_GS_1.44-MuseScore
	  ](http://www.schristiancollins.com/soundfonts/GeneralUser_GS_1.44-MuseScore.zip) by  S. Christian Collins.
	  This is not so large, at 31Mb.
+ A small soundfont is [
	    by  Tim Brechbill
	  ](http://mscore.svn.sourceforge.net/viewvc/mscore/trunk/mscore/share/sound/TimGM6mb.sf2) at 6Mb (linked from [
	    MuseScore - soundfonts
	  ](http://musescore.org/en/handbook/soundfont) )
+ A list of soundfonts is at [
	 	TiMidity++ Configuration File Package v2004/8/3
	   ](http://timidity.s11.xrea.com/files/readme_cfgp.htm) 

Possibly surprisingly, using different soundfonts doesn't seem 
      to make much difference to CPU usage - for FluidSynth they all
      use about 60-70% CPU on one song. They do, of course, sound
      different.
