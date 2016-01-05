
##  Play MIDI files 


The FluidSynth API consists of

+ A sequencer created using `new_fluid_player`
+ A synthesizer created using `new_fluid_synth`
+ An audio player created using `new_fluid_audio_driver`which runs in a separate thread
+ A "settings" object which can be used to control many features
of the other components, created by `new_fluid_settings`and modified by calls such as `fluid_settings_setstr`




A typical program to play a sequence of MIDI files using ALSA follows.
It creates the various objects, sets the audio player to use ALSA
and then adds each soundfont and MIDI file to the player.
The call to `fluid_player_play`then plays each MIDI file
in turn.
This program is just a repeat of the program seen in the chapter
on [FluidSynth MIDI](../../MIDI/FluidSynth/) .

```cpp
#include <fluidsynth.h>
#include <fluid_midi.h>


int main(int argc, char** argv)
{
    int i;
    fluid_settings_t* settings;
    fluid_synth_t* synth;
    fluid_player_t* player;
    fluid_audio_driver_t* adriver;

    settings = new_fluid_settings();
    fluid_settings_setstr(settings, "audio.driver", "alsa");
    synth = new_fluid_synth(settings);
    player = new_fluid_player(synth);

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



