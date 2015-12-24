
##  Extending FluidSynth with callbacks 


Callbacks are functions registered with an application which
      are called when certain events occur. In order to build a Karaoke
      player we need to know

+ When a file is loaded so that we can extract all of the lyrics
	  from it for display at the right times.
+ When each Meta Lyric or Text event occurs as output from
	  a sequencer, so that we can see what lyric is about to be
	  sung.




The first of these is fairly straightforward: FluidSynth
      has a function `fluid_player_load`which will
      load a file. We can change the code to add a suitable callback into that
      function which will give us access to the loaded MIDI file.


Getting Lyric or Text events out of a sequencer is not so easy, since they
      are never meant to appear! The MIDI specification allows these
      event types within a MIDI file, but they are not wire-types so
      should never be sent from a sequencer to a synthesizer.
      The Java MIDI API makes them available by an out-of-band call
      to a Meta event handler. FluidSynth just throws them away.


On the other hand, FluidSynth already has a callback to handle
      MIDI events sent from the sequencer to the synthesizer. It is
      the function `fluid_synth_handle_midi_event`and is set by the call `fluid_player_set_playback_callback`.
      What we need to do is to firstly alter the 
      existing FluidSynth code so that Lyric and
      Text events are passed through, and then insert a new playback
      callback that will intercept those events and do something
      with them while passing on all other events to the default
      handler. The default handler will ignore any such events
      anyway, so it does not need to be changed.


I have added one new function to FluidSynth, `fluid_player_set_onload_callback`and added appropriate code to pass on some Meta
      events. Then it is a matter of writing an onload
      callback to walk through the MIDI data from the parsed
      input file, and writing a suitable MIDI event callback
      to handle the intercepted Meta events while passing the rest
      through to the default handler.


These changes have been made to give a new source
      package [
	fluidsynth-1.1.6-karaoke.tar.bz2
      ](fluidsynth-1.1.6-karaoke.tar.bz2) .
      If you just want to work from a patch file, that is [
	fluid.patch
      ](fluid.patch) .
      The patch has been submitted to the FluidSynth
      maintainers.





To build from this package, do the same as you normally
      would:

```

	
tar jxf fluidsynth-1.1.6-karaoke.tar.bz2
cd fluidsynth-1.1.6
./configure
make clean
make
	
      
```


To get ALSA support, you will need to have installed
      the `libasound2-dev`package, and similarly
      for Jack or other packages. You probably won't have  many
      of them installed, so
      don't run `make install`or you will overwrite
      the normal `fluidsynth`package which will 
      probably have more features.


The previous program modified to just print out
      the lyric lines and the lyric events as they occur
      is `karaoke_player.c`:

```

#include <fluidsynth.h>
#include <fluid_midi.h>

/**
 * This MIDI event callback filters out the TEXT and LYRIC events
 * and passes the rest to the default event handler.
 * Here we just print the text of the event, more
 * complex handling can be done
 */
int event_callback(void *data, fluid_midi_event_t *event) {
    fluid_synth_t* synth = (fluid_synth_t*) data;
    int type = fluid_midi_event_get_type(event);
    int chan = fluid_midi_event_get_channel(event);
    if (synth == NULL) printf("Synth is null\n");
    switch(type) {
    case MIDI_TEXT:
	printf("Callback: Playing text event %s (length %d)\n", 
	       (char *) event->paramptr, event->param1);
	return  FLUID_OK;

    case MIDI_LYRIC:
	printf("Callback: Playing lyric event %d %s\n", 
	       event->param1, (char *) event->paramptr);
	return  FLUID_OK;
    }
    return fluid_synth_handle_midi_event( data, event);
}

/**
 * This is called whenever new data is loaded, such as a new file.
 * Here we extract the TEXT and LYRIC events and just print them
 * to stdout. They could e.g. be saved and displayed in a GUI
 * as the events are received by the event callback.
 */ 
int onload_callback(void *data, fluid_player_t *player) {
    printf("Load callback, tracks %d \n", player->ntracks);
    int n;
    for (n = 0; n < player->ntracks; n++) {
	fluid_track_t *track = player->track[n];
	printf("Track %d\n", n);
	fluid_midi_event_t *event = fluid_track_first_event(track);
	while (event != NULL) {
	    switch (event->type) {
	    case MIDI_TEXT:
	    case MIDI_LYRIC:
		printf("Loaded event %s\n", (char *) event->paramptr);
	    }
	    event = fluid_track_next_event(track);
	}
    }
    return FLUID_OK;
}

int main(int argc, char** argv)
{
    int i;
    fluid_settings_t* settings;
    fluid_synth_t* synth;
    fluid_player_t* player;
    fluid_audio_driver_t* adriver;
    settings = new_fluid_settings();
    fluid_settings_setstr(settings, "audio.driver", "alsa");
    fluid_settings_setint(settings, "synth.polyphony", 64);
    synth = new_fluid_synth(settings);
    player = new_fluid_player(synth);

    /* Set the MIDI event callback to our own functions rather than the system default */
    fluid_player_set_playback_callback(player, event_callback, synth);

    /* Add an onload callback so we can get information from new data before it plays */
    fluid_player_set_onload_callback(player, onload_callback, NULL);

    adriver = new_fluid_audio_driver(settings, synth);
    /* process command line arguments */
    for (i = 1; i < argc; i++) {
        if (fluid_is_soundfont(argv[i])) {
	    fluid_synth_sfload(synth, argv[1], 1);
        } else {
            fluid_player_add(player, argv[i]);
        }
    }
    /* play the midi files, if any */
    fluid_player_play(player);
    /* wait for playback termination */
    fluid_player_join(player);
    /* cleanup */
    delete_fluid_audio_driver(adriver);
    delete_fluid_player(player);
    delete_fluid_synth(synth);
    delete_fluid_settings(settings);
    return 0;
}


      
```





Assuming the new fluidsynth package is in an immediate subdirectory,
      to compile the program you will need  to pick up the local 
      includes and libraries

```

	
gcc -g -I fluidsynth-1.1.6/include/ -I fluidsynth-1.1.6/src/midi/ -I fluidsynth-1.1.6/src/utils/ -c -o karaoke_player.o karaoke_player.c

gcc karaoke_player.o -Lfluidsynth-1.1.6/src/.libs -l fluidsynth -o karaoke_player
	
      
```





To run the program, you will also need to pick up the local library
      and the soundfont file:

```

	
export LD_LIBRARY_PATH=./fluidsynth-1.1.6/src/.libs/
./karaoke_player /usr/share/soundfonts/FluidR3_GM.sf2 54154.mid
	
      
```





The output for a typical `KAR`file is

```

	
Load callback, tracks 1 
Track 0
Loaded event #
Loaded event 0
Loaded event 0
Loaded event 0
Loaded event 1
Loaded event 

...

Callback: Playing lyric event 2 #
Callback: Playing lyric event 2 0
Callback: Playing lyric event 2 0
Callback: Playing lyric event 2 0
Callback: Playing lyric event 2 1
Callback: Playing lyric event 3 
	
      
```



