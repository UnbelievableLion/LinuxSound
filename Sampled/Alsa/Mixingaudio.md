
##  Mixing audio 

###  Mixing using dmix 


ALSA contains a plugin `dmix`which is enabled by default.
This performs mixing of multiple audio input signals into an
output signal in software.
A description of this is given in [The Dmix Howto](http://alsa.opensrc.org/Dmix) .
Basically, each application that wishes to write audio to ALSA should use
the plugin `plug:dmix`instead of a hardware device such as `hw:0`. For example, the `alsa_playback`program
discussed earlier can be called multiple times and have the ALSA inputs mixed together
as in

```

	
alsa_playback plug:dmix tmp1.s16 &
alsa_playback plug:dmix tmp2.s16 &
alsa_playback plug:dmix tmp3.s16
	
      
```




###  Mixing using PulseAudio 


PulseAudio isn't covered until the mext chapter, because it is generally
considered to be a sound server, acting in the layer _above_ ALSA.
However, there is also an ALSA plugin module whereby PulseAudio can appear
as a plugin device _below_ ALSA! So ALSA can write output to the
PulseAudio plugin, which can process it using the full capabilities of PulseAudio,
which then feeds it back down into ALSA for rendering on a hardware
device.


One of these capabilities is that PulseAudio contains a mixer.
So two (or more) applications can send audio to the PulseAudio plugin which
will then mix the signals and then send them back to ALSA.


The PulseAudio plugin can appear as the PCM devices `pulse`or as `default`. So the following three outputs will be mixed
by PulseAudio and rendered by ALSA.

```

	
alsa_playback default tmp1.s16 &
alsa_playback pulse tmp2.s16 &
alsa_playback default tmp3.s16
	
      
```




###  Simple mixer API - volume control


ALSA has a separate API for the mixer module. In fact, there are two:
the [[asynchronous] Mixer Interface](http://www.alsa-project.org/alsa-doc/alsa-lib/group___mixer.html) and the [Simple Mixer Interface](http://www.alsa-project.org/alsa-doc/alsa-lib/group___simple_mixer.html) .
For now, we shall just consider the simple interface.


The ALSA mixer does not have a great deal of functionality apart from mixing.
Basically, it can get and set volumes on channels or globally.
Setting the volume is illustrated by the following program,
based on a function by [trenki](http://stackoverflow.com/users/619295/trenki) at [Set ALSA master volume from C code](http://stackoverflow.com/questions/6787318/set-alsa-master-volume-from-c-code) :

```cpp

/*
 *
 * From http://stackoverflow.com/questions/6787318/set-alsa-master-volume-from-c-code
 */

#include <alsa/asoundlib.h>
#include <alsa/mixer.h>



void SetAlsaMasterVolume(long volume)
{
    long min, max;
    snd_mixer_t *handle;
    snd_mixer_selem_id_t *sid;
    const char *card = "default";
    const char *selem_name = "Master";

    snd_mixer_open(&handle, 0);
    snd_mixer_attach(handle, card);
    snd_mixer_selem_register(handle, NULL, NULL);
    snd_mixer_load(handle);

    snd_mixer_selem_id_alloca(&sid);
    snd_mixer_selem_id_set_index(sid, 0);
    snd_mixer_selem_id_set_name(sid, selem_name);
    snd_mixer_elem_t* elem = snd_mixer_find_selem(handle, sid);

    snd_mixer_selem_get_playback_volume_range(elem, &min, &max);
    snd_mixer_selem_set_playback_volume_all(elem, volume * max / 100);

    snd_mixer_close(handle);
}


main(int argc, char **args) {
    long volume = 0;
    char buf[128];

    while (1) {
	puts("Enter an integer 0-100\n");
	fgets(buf, 128, stdin);
	volume = atoi(buf);
	SetAlsaMasterVolume(volume);
    }
    exit(0);
}


      
```
