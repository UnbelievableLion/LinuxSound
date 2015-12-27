
##  Programming ALSA 


There are several tutorials, including [A Tutorial on Using the ALSA Audio API](http://equalarea.com/paul/alsa-audio.html) by Paul Davis (who is the lead on Jack).


An overview of the API is at [PCM (digital audio) interface](http://www.alsa-project.org/alsa-doc/alsa-lib/pcm.html) .
The ALSA API is large and complex. It is not clear to me how it all hangs together
or what part to use where. Jeff Tranter [Introduction to Sound Programming with ALSA](http://www.linuxjournal.com/article/6735) states


   > 

> The ALSA API can be broken down into the major interfaces it supports:

> + Control interface: a general-purpose facility for managing registers of
sound cards and querying the available devices.
> + PCM interface: the interface for managing digital audio capture and playback.
[...]  it is the one most
commonly used for digital audio applications.
> + Raw MIDI interface: supports MIDI (Musical Instrument Digital Interface),
a standard for electronic musical instruments. This API provides access to a
MIDI bus on a sound card. The raw interface works directly with the MIDI events,
and the programmer is responsible for managing the protocol and timing.
> + Timer interface: provides access to timing hardware on sound cards used for
synchronizing sound events.
> + Sequencer interface: a higher-level interface for MIDI programming and sound
synthesis than the raw MIDI interface. It handles much of the MIDI protocol and timing.
> + Mixer interface: controls the devices on sound cards that route signals and control
volume levels. It is built on top of the control interface.


###  Hardware device information 


Finding information about hardware cards and devices is a multi-step operation.
The hardware cards first have to be identified. This is done using the [Control interface](http://www.alsa-project.org/alsa-doc/alsa-lib/group___control.html) functions. The ones used are

```

	
snd_card_next
snd_ctl_open
snd_ctl_pcm_next_device
snd_ctl_card_info_get_id
snd_ctl_card_info_get_name
	
      
```





Cards are identified by an integer from zero upwards. The _next_ card number is found using `snd_card_next`, and the first card
is found using a seed value of -1. The card is then opened using its ALSA
name such as hw:0, hw:1, etc by `snd_ctl_open`which fills in a `handle`value. In turn, this handle is used to fill in card
information using `snd_ctl_card_info`and fields are extracted
from that using functions such as `snd_ctl_card_info_get_name`.
In the program that follows, this gives information such as

```

	
card 0: PCH [HDA Intel PCH]
	
      
```





For further information you need to switch to the PCM functions for the card.
The function linking the control and PCM interfaces is `snd_ctl_pcm_info`which fills in a structure of type `snd_pcm_info_t`with PCM-related
information. Unfortunately, this function is documented neither in the Control
Interface nor the PCM interface sections of the ALSA documentation but is instead in the Files section
under [control.c](http://www.alsa-project.org/alsa-doc/alsa-lib/control_8c.html) The structure `snd_pcm_info_t`is barely documented in the [PCM Interface](http://www.alsa-project.org/alsa-doc/alsa-lib/group___p_c_m.html#g2226bdcc6e780543beaadc319332e37b) section, and only has  a few fields of interest.
(see [here for the structure](http://www.qnx.com/developers/docs/6.4.0/neutrino/audio/libs/snd_pcm_info_t.html) ). These fields are accessed using the PCM functions `snd_pcm_info_get_id`and `snd_pcm_info_get_name`.


The main value of the `snd_pcm_info_t`structure is that it is the principal
parameter into the functions of the [PCM Stream](http://www.alsa-project.org/alsa-doc/alsa-lib/group___p_c_m___info.html) .
In particular this allows you to get devices and subdevices and information about them.


The program to find and display card and hardware device information is
aplay-l.c:

```cpp

/**
 * aplay-l.c
 *
 * Code from aplay.c
 *
 * does the same as aplay -l
 * http://alsa-utils.sourcearchive.com/documentation/1.0.15/aplay_8c-source.html
 */

/*
 * Original notice:
 *
 *  Copyright (c) by Jaroslav Kysela <perex@perex.cz>
 *  Based on vplay program by Michael Beck
 *
 *
 *   This program is free software; you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation; either version 2 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with this program; if not, write to the Free Software
 *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <alsa/asoundlib.h>
#include <locale.h>

// used by gettext for i18n, not needed here
#define _(STR) STR

static void device_list(snd_pcm_stream_t stream)
{
      snd_ctl_t *handle;
      int card, err, dev, idx;
      snd_ctl_card_info_t *info;
      snd_pcm_info_t *pcminfo;
      snd_ctl_card_info_alloca(&info);
      snd_pcm_info_alloca(&pcminfo);

      card = -1;
      if (snd_card_next(&card) < 0 || card < 0) {
            error(_("no soundcards found..."));
            return;
      }
      printf(_("**** List of %s Hardware Devices ****\n"),
             snd_pcm_stream_name(stream));
      while (card >= 0) {
            char name[32];
            sprintf(name, "hw:%d", card);
            if ((err = snd_ctl_open(&handle, name, 0)) < 0) {
                  error("control open (%i): %s", card, snd_strerror(err));
                  goto next_card;
            }
            if ((err = snd_ctl_card_info(handle, info)) < 0) {
                  error("control hardware info (%i): %s", card, snd_strerror(err));
                  snd_ctl_close(handle);
                  goto next_card;
            }
            dev = -1;
            while (1) {
                  unsigned int count;
                  if (snd_ctl_pcm_next_device(handle, &dev)<0)
                        error("snd_ctl_pcm_next_device");
                  if (dev < 0)
                        break;
                  snd_pcm_info_set_device(pcminfo, dev);
                  snd_pcm_info_set_subdevice(pcminfo, 0);
                  snd_pcm_info_set_stream(pcminfo, stream);
                  if ((err = snd_ctl_pcm_info(handle, pcminfo)) < 0) {
                        if (err != -ENOENT)
                              error("control digital audio info (%i): %s", card, snd_strerror(err));
                        continue;
                  }
                  printf(_("card %i: [%s,%i] %s [%s], device %i: %s [%s]\n"),
			 card, name, dev, snd_ctl_card_info_get_id(info), snd_ctl_card_info_get_name(info),
                        dev,
                        snd_pcm_info_get_id(pcminfo),
                        snd_pcm_info_get_name(pcminfo));
                  count = snd_pcm_info_get_subdevices_count(pcminfo);
                  printf( _("  Subdevices: %i/%i\n"),
                        snd_pcm_info_get_subdevices_avail(pcminfo), count);
                  for (idx = 0; idx < (int)count; idx++) {
                        snd_pcm_info_set_subdevice(pcminfo, idx);
                        if ((err = snd_ctl_pcm_info(handle, pcminfo)) < 0) {
                              error("control digital audio playback info (%i): %s", card, snd_strerror(err));
                        } else {
                              printf(_("  Subdevice #%i: %s\n"),
                                    idx, snd_pcm_info_get_subdevice_name(pcminfo));
                        }
                  }
            }
            snd_ctl_close(handle);
      next_card:
            if (snd_card_next(&card) < 0) {
                  error("snd_card_next");
                  break;
            }
      }
}


main (int argc, char *argv[])
{
  device_list(SND_PCM_STREAM_CAPTURE);
  device_list(SND_PCM_STREAM_PLAYBACK);
}

      
```





The output from running `aplay-l`on my system is

```

	
**** List of CAPTURE Hardware Devices ****
card 0: [hw:0,0] PCH [HDA Intel PCH], device 0: STAC92xx Analog [STAC92xx Analog]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
**** List of PLAYBACK Hardware Devices ****
card 0: [hw:0,0] PCH [HDA Intel PCH], device 0: STAC92xx Analog [STAC92xx Analog]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 1: [hw:1,3] NVidia [HDA NVidia], device 3: HDMI 0 [HDMI 0]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 1: [hw:1,7] NVidia [HDA NVidia], device 7: HDMI 1 [HDMI 1]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 1: [hw:1,8] NVidia [HDA NVidia], device 8: HDMI 2 [HDMI 2]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
	
      
```

###  PCM device information


PCM alias information may be found from the devices by `aplay -L`.
This uses the "hints" mechanism from the device API.
Note that the program is responsible for freeing memory allocated
by the ALSA library. This means that if a string or table is returned then not
only do you have to walk through the string/table but you have to retain
a pointer to the start of the string/table so that it can be freed.


The source for this is aplay-L.c:

```cpp

/**
 * aplay-L.c
 *
 * Code from aplay.c
 * does aplay -L
 * http://alsa-utils.sourcearchive.com/documentation/1.0.15/aplay_8c-source.html
 */

/*
 * Original notice:
 *
 *  Copyright (c) by Jaroslav Kysela <perex@perex.cz>
 *  Based on vplay program by Michael Beck
 *
 *
 *   This program is free software; you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation; either version 2 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with this program; if not, write to the Free Software
 *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
 *
 */


#include <stdio.h>
#include <stdlib.h>
#include <alsa/asoundlib.h>
#include <locale.h>

#define _(STR) STR

static void pcm_list(snd_pcm_stream_t stream )
{
      void **hints, **n;
      char *name, *descr, *descr1, *io;
      const char *filter;

      if (snd_device_name_hint(-1, "pcm", &hints) < 0)
            return;
      n = hints;
      filter = stream == SND_PCM_STREAM_CAPTURE ? "Input" : "Output";
      while (*n != NULL) {
            name = snd_device_name_get_hint(*n, "NAME");
            descr = snd_device_name_get_hint(*n, "DESC");
            io = snd_device_name_get_hint(*n, "IOID");
            if (io != NULL && strcmp(io, filter) == 0)
                  goto __end;
            printf("%s\n", name);
            if ((descr1 = descr) != NULL) {
                  printf("    ");
                  while (*descr1) {
                        if (*descr1 == '\n')
                              printf("\n    ");
                        else
                              putchar(*descr1);
                        descr1++;
                  }
                  putchar('\n');
            }
            __end:
                  if (name != NULL)
                        free(name);
            if (descr != NULL)
                  free(descr);
            if (io != NULL)
                  free(io);
            n++;
      }
      snd_device_name_free_hint(hints);
}


main (int argc, char *argv[])
{
  printf("*********** CAPTURE ***********\n");
  pcm_list(SND_PCM_STREAM_CAPTURE);

  printf("\n\n*********** PLAYBACK ***********\n");
  pcm_list(SND_PCM_STREAM_PLAYBACK);
}

      
```





The outputfrom running `aplay-L`on my system is

```

	
*********** CAPTURE ***********
default
    Default
sysdefault:CARD=PCH
    HDA Intel PCH, STAC92xx Analog
    Default Audio Device
front:CARD=PCH,DEV=0
    HDA Intel PCH, STAC92xx Analog
    Front speakers
surround40:CARD=PCH,DEV=0
    HDA Intel PCH, STAC92xx Analog
    4.0 Surround output to Front and Rear speakers
surround41:CARD=PCH,DEV=0
    HDA Intel PCH, STAC92xx Analog
    4.1 Surround output to Front, Rear and Subwoofer speakers
surround50:CARD=PCH,DEV=0
    HDA Intel PCH, STAC92xx Analog
    5.0 Surround output to Front, Center and Rear speakers
surround51:CARD=PCH,DEV=0
    HDA Intel PCH, STAC92xx Analog
    5.1 Surround output to Front, Center, Rear and Subwoofer speakers
surround71:CARD=PCH,DEV=0
    HDA Intel PCH, STAC92xx Analog
    7.1 Surround output to Front, Center, Side, Rear and Woofer speakers
hdmi:CARD=NVidia,DEV=0
    HDA NVidia, HDMI 0
    HDMI Audio Output
hdmi:CARD=NVidia,DEV=1
    HDA NVidia, HDMI 1
    HDMI Audio Output
hdmi:CARD=NVidia,DEV=2
    HDA NVidia, HDMI 2
    HDMI Audio Output


*********** PLAYBACK ***********
null
    Discard all samples (playback) or generate zero samples (capture)
pulse
    PulseAudio Sound Server
default
    Default
sysdefault:CARD=PCH
    HDA Intel PCH, STAC92xx Analog
    Default Audio Device
front:CARD=PCH,DEV=0
    HDA Intel PCH, STAC92xx Analog
    Front speakers
surround40:CARD=PCH,DEV=0
    HDA Intel PCH, STAC92xx Analog
    4.0 Surround output to Front and Rear speakers
surround41:CARD=PCH,DEV=0
    HDA Intel PCH, STAC92xx Analog
    4.1 Surround output to Front, Rear and Subwoofer speakers
surround50:CARD=PCH,DEV=0
    HDA Intel PCH, STAC92xx Analog
    5.0 Surround output to Front, Center and Rear speakers
surround51:CARD=PCH,DEV=0
    HDA Intel PCH, STAC92xx Analog
    5.1 Surround output to Front, Center, Rear and Subwoofer speakers
surround71:CARD=PCH,DEV=0
    HDA Intel PCH, STAC92xx Analog
    7.1 Surround output to Front, Center, Side, Rear and Woofer speakers
	
      
```





Note that this does not include the "plug" devices such as "plughw:0".
The list of plug devices does not seem to be accessible.

###  Configuration space information 


In addition to general  characteristics, each PCM device is able to
support a range of parameters such as the number of channels, sampling
rates, etc. The full set and range of parameters form the "configuration space"
of each device. For example, a device may support between 2 and 6 channels
and a number of different sampling rates. These two parameters form a
2-dimensional space. The full set form an N-dimensional space.


ALSA has functions to query this space and to set values within this space.
The space is initialised by `snd_pcm_hw_params_any`.
To find the possible values of parameters there are functions `snd_pcm_hw_params_get...`.


The different parameters are

+ __Channels__: The number of channels supported - zero for mono, etc
+ __Rate__: The sampling rate in hertz, that is, samples per second.
Typically CD audio has a sampling rate of 44,100hz per
channel, so that
each channel has 44,100 samples per second
+ __Frames__: Each frame contains one sample for each channel.
Stereo audio will contain 2 samples in each frame.
The frame rate is the same as the sampling rate.
That is, suppose the sampling rate for stereo audio
is 44,100hz. Then each channel will have 44,100
samples per second. But there will also be 44,100
frames per second, so that the overall density
of the two channels will be 88,200 samples per second.
+ __Period time__: The time in microseconds between hardware interrupts to refresh the
buffer
+ __Period size__: The number of frames in between each hardware interrupt.
These are related in the following way:
```

Period time = period size x time per frame
            = period size x time per sample
            = period size / sampling rate
	  
```
So for example if the sampling rate is 48000hz stereo
and the period size is 8192 frames, then the time between
hardware interrupts is 8192 / 48000 seconds = 170.5 millseconds
+ __Periods__: Number of periods per buffer
+ __Buffer time__: Time for one buffer
+ __Buffer size__: Size of the buffer in frames. Again there is a relationship
```

Time of one buffer =  buffer size in frames x time for one frame
                   = buffer size x number of channels x time for one sample
                   = buffer size x number of channels / sample rate
	  
```
The buffer size should be a multiple of the period size, and is typically
twice as big.

For further examples, see [FramesPeriods](http://www.alsa-project.org/main/index.php/FramesPeriods) 


A program to find the range of values of various parameters from the
initial state is device-info.c:

```cpp

/**
 * Jan Newmarch
 */

#include <stdio.h>
#include <stdlib.h>
#include <alsa/asoundlib.h>
	      

void info(char *dev_name, snd_pcm_stream_t stream) {
  snd_pcm_hw_params_t *hw_params;
  int err;
  snd_pcm_t *handle;
  unsigned int max;
  unsigned int min;
  unsigned int val;
  unsigned  int dir;
  snd_pcm_uframes_t frames;

  if ((err = snd_pcm_open (&handle, dev_name, stream, 0)) < 0) {
    fprintf (stderr, "cannot open audio device %s (%s)\n", 
	     dev_name,
	     snd_strerror (err));
    return;
  }
		   
  if ((err = snd_pcm_hw_params_malloc (&hw_params)) < 0) {
    fprintf (stderr, "cannot allocate hardware parameter structure (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
				 
  if ((err = snd_pcm_hw_params_any (handle, hw_params)) < 0) {
    fprintf (stderr, "cannot initialize hardware parameter structure (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
  
  if ((err = snd_pcm_hw_params_get_channels_max(hw_params, &max)) < 0) {
    fprintf (stderr, "cannot  (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
  printf("max channels %d\n", max);

  if ((err = snd_pcm_hw_params_get_channels_min(hw_params, &min)) < 0) {
    fprintf (stderr, "cannot get channel info  (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
  printf("min channels %d\n", min);

  /*
  if ((err = snd_pcm_hw_params_get_sbits(hw_params)) < 0) {
      fprintf (stderr, "cannot get bits info  (%s)\n",
	       snd_strerror (err));
      exit (1);
  }
  printf("bits %d\n", err);
  */

  if ((err = snd_pcm_hw_params_get_rate_min(hw_params, &val, &dir)) < 0) {
    fprintf (stderr, "cannot get min rate (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
  printf("min rate %d hz\n", val);

  if ((err = snd_pcm_hw_params_get_rate_max(hw_params, &val, &dir)) < 0) {
    fprintf (stderr, "cannot get max rate (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
  printf("max rate %d hz\n", val);

  
  if ((err = snd_pcm_hw_params_get_period_time_min(hw_params, &val, &dir)) < 0) {
    fprintf (stderr, "cannot get min period time  (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
  printf("min period time %d usecs\n", val);

  if ((err = snd_pcm_hw_params_get_period_time_max(hw_params, &val, &dir)) < 0) {
    fprintf (stderr, "cannot  get max period time  (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
  printf("max period time %d usecs\n", val);

  if ((err = snd_pcm_hw_params_get_period_size_min(hw_params, &frames, &dir)) < 0) {
    fprintf (stderr, "cannot  get min period size  (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
  printf("min period size in frames %d\n", frames);

  if ((err = snd_pcm_hw_params_get_period_size_max(hw_params, &frames, &dir)) < 0) {
    fprintf (stderr, "cannot  get max period size (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
  printf("max period size in frames %d\n", frames);

  if ((err = snd_pcm_hw_params_get_periods_min(hw_params, &val, &dir)) < 0) {
    fprintf (stderr, "cannot  get min periods  (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
  printf("min periods per buffer %d\n", val);

  if ((err = snd_pcm_hw_params_get_periods_max(hw_params, &val, &dir)) < 0) {
    fprintf (stderr, "cannot  get min periods (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
  printf("max periods per buffer %d\n", val);

  if ((err = snd_pcm_hw_params_get_buffer_time_min(hw_params, &val, &dir)) < 0) {
    fprintf (stderr, "cannot get min buffer time (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
  printf("min buffer time %d usecs\n", val);

  if ((err = snd_pcm_hw_params_get_buffer_time_max(hw_params, &val, &dir)) < 0) {
    fprintf (stderr, "cannot get max buffer time  (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
  printf("max buffer time %d usecs\n", val);

  if ((err = snd_pcm_hw_params_get_buffer_size_min(hw_params, &frames)) < 0) {
    fprintf (stderr, "cannot get min buffer size (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
  printf("min buffer size in frames %d\n", frames);

  if ((err = snd_pcm_hw_params_get_buffer_size_max(hw_params, &frames)) < 0) {
    fprintf (stderr, "cannot get max buffer size  (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
  printf("max buffer size in frames %d\n", frames);
}

main (int argc, char *argv[])
{
  int i;
  int err;
  int buf[128];
  FILE *fin;
  size_t nread;
  unsigned int rate = 44100;	

  if (argc != 2) {
    fprintf(stderr, "Usage: %s card\n", argv[0]);
    exit(1);
  }

  printf("*********** CAPTURE ***********\n");
  info(argv[1], SND_PCM_STREAM_CAPTURE);

  printf("*********** PLAYBACK ***********\n");
  info(argv[1], SND_PCM_STREAM_PLAYBACK);

  exit (0);
}

      
```





The output from `device-info hw:0`on my system is

```

	
*********** CAPTURE ***********
max channels 2
min channels 2
min rate 44100 hz
max rate 192000 hz
min period time 83 usecs
max period time 11888617 usecs
min period size in frames 16
max period size in frames 524288
min periods per buffer 2
max periods per buffer 32
min buffer time 166 usecs
max buffer time 23777234 usecs
min buffer size in frames 32
max buffer size in frames 1048576
*********** PLAYBACK ***********
max channels 2
min channels 2
min rate 44100 hz
max rate 192000 hz
min period time 83 usecs
max period time 11888617 usecs
min period size in frames 16
max period size in frames 524288
min periods per buffer 2
max periods per buffer 32
min buffer time 166 usecs
max buffer time 23777234 usecs
min buffer size in frames 32
max buffer size in frames 1048576
	
      
```





This program works with any ALSA device, including the "plug" devices.
The output from `device-info plughw:0`shows how the software
wrapper can give a wider range of possible values:

```

	
*********** CAPTURE ***********
max channels 10000
min channels 1
min rate 4000 hz
max rate -1 hz
min period time 83 usecs
max period time 11888617 usecs
min period size in frames 0
max period size in frames -1
min periods per buffer 0
max periods per buffer -1
min buffer time 1 usecs
max buffer time -1 usecs
min buffer size in frames 1
max buffer size in frames -2
*********** PLAYBACK ***********
max channels 10000
min channels 1
min rate 4000 hz
max rate -1 hz
min period time 83 usecs
max period time 11888617 usecs
min period size in frames 0
max period size in frames -1
min periods per buffer 0
max periods per buffer -1
min buffer time 1 usecs
max buffer time -1 usecs
min buffer size in frames 1
max buffer size in frames -2
	
      
```





It can also be run with alias devices, such as `device-info surround40`.

###  ALSA initialisation 


A line-by-line breakdown is at [ALSA Tutorial Part 1 - Initialization](http://soundprogramming.net/programming_apis/alsa_tutorial_1_initialization) This explains much of the common code in the programs that follow.

###  Capture audio to a file 


The following program is from Paul Davis [A Tutorial on Using the ALSA Audio API](http://equalarea.com/paul/alsa-audio.html) alsa_capture.c:

```cpp

/**
 * alsa_capture.c
 */

/**
 * Paul Davis
 * http://equalarea.com/paul/alsa-audio.html#howto
 */

/**
 * Jan Newmarch
 */

#include <stdio.h>
#include <stdlib.h>
#include <alsa/asoundlib.h>
#include <signal.h>

#define BUFSIZE 128
#define RATE 44100

FILE *fout = NULL;

/*
 * quit on ctrl-c
 */
void sigint(int sig) {
  if (fout != NULL) {
    fclose(fout);
  }
  exit(1);
}
	      
main (int argc, char *argv[])
{
  int i;
  int err;
  short buf[BUFSIZE];
  snd_pcm_t *capture_handle;
  snd_pcm_hw_params_t *hw_params;
  snd_pcm_format_t rate = RATE;	
  int nread;

  if (argc != 3) {
    fprintf(stderr, "Usage: %s cardname file\n", argv[0]);
    exit(1);
  }

  if ((fout = fopen(argv[2], "w")) == NULL) {
    fprintf(stderr, "Can't open %s for writing\n", argv[2]);
    exit(1);
  }


  signal(SIGINT, sigint);
	
  if ((err = snd_pcm_open (&capture_handle, argv[1], SND_PCM_STREAM_CAPTURE, 0)) < 0) {
    fprintf (stderr, "cannot open audio device %s (%s)\n", 
	     argv[1],
	     snd_strerror (err));
    exit (1);
  }
		   
  if ((err = snd_pcm_hw_params_malloc (&hw_params)) < 0) {
    fprintf (stderr, "cannot allocate hardware parameter structure (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
				 
  if ((err = snd_pcm_hw_params_any (capture_handle, hw_params)) < 0) {
    fprintf (stderr, "cannot initialize hardware parameter structure (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
	
  if ((err = snd_pcm_hw_params_set_access (capture_handle, hw_params, SND_PCM_ACCESS_RW_INTERLEAVED)) < 0) {
    fprintf (stderr, "cannot set access type (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
	

  if ((err = snd_pcm_hw_params_set_format (capture_handle, hw_params, SND_PCM_FORMAT_S16_LE)) < 0) {
    fprintf (stderr, "cannot set sample format (%s)\n",
	     snd_strerror (err));
    exit (1);
  }

  if ((err = snd_pcm_hw_params_set_rate_near (capture_handle, hw_params, &rate, 0)) < 0) {
    fprintf (stderr, "cannot set sample rate (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
  fprintf(stderr, "rate set to %d\n", rate);
	
  if ((err = snd_pcm_hw_params_set_channels (capture_handle, hw_params, 2)) < 0) {
    fprintf (stderr, "cannot set channel count (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
	
  if ((err = snd_pcm_hw_params (capture_handle, hw_params)) < 0) {
    fprintf (stderr, "cannot set parameters (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
	
  snd_pcm_hw_params_free (hw_params);
	
  /*
  if ((err = snd_pcm_prepare (capture_handle)) < 0) {
    fprintf (stderr, "cannot prepare audio interface for use (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
  */
	
  while (1) {
    if ((nread = snd_pcm_readi (capture_handle, buf, BUFSIZE)) < 0) {
      fprintf (stderr, "read from audio interface failed (%s)\n",
	       snd_strerror (err));
      /* recover */
      snd_pcm_prepare(capture_handle);
    } else {
      fwrite(buf, sizeof(short), nread, fout);
    }
  }
	
  snd_pcm_close (capture_handle);
  exit(0);
}

      
```




###  Playback audio from a file 


In order to capture or play audio, a device must first be opened as
in previous examples. A configuration space is then created and the
space is narrowed by setting values on the various parameters.
The access type determines if the samples are interleaved or other.
The format determines the size of samples and whether little- or big-endian.
All of these will return an error if the requested value cannot be set.


Some parameters need care in setting. For example, there is a range of possible
values for the sampling rate, but not all of these may be supported.
A particular rate may be requested using `snd_pcm_hw_params_set_rate`.
But if a
requested rate is not possible then an error will be returned. There are
several ways of avoiding this:

+ Try a number of rates till you get one that is supported
+ Test if a rate is supported by `snd_pcm_hw_params_test_rate`
+ Request ALSA to give
the nearest supported rate by `snd_pcm_hw_params_set_rate_near`.
The actual rate chosen is set in the rate parameter
+ Instead of a hardware device such as "hw:0" use a plug device such as
"plughw:0" which will support many more values by resampling




Finally, once parameters are set for the configuration space, the restricted space
is installed onto the device by `snd_pcm_hw_params`


The calls on PCm devices will cause state changes to take place in the device.
After opening, the device is in the state `SND_PCM_STATE_OPEN`.
After setting the hardware configuration, the device is in the state `SND_PCM_STATE_PREPARE`.
Applications can use the `snd_pcm_start`call, write or read data.
The state may drop to `SND_PCM_STATE_XRUN`if an overrun or
underrun occurs, and then a call to `snd_pcm_prepare`is needed
to restore it to `SND_PCM_STATE_PREPARE`.


The call to `readi`reads interlaced data.


The following program is from Paul Davis [A Tutorial on Using the ALSA Audio API](http://equalarea.com/paul/alsa-audio.html) alsa_playback.c:

```cpp

/**
 * alsa_playback.c
 */

/**
 * Paul Davis
 * http://equalarea.com/paul/alsa-audio.html#howto
 */

/**
 * Jan Newmarch
 */

#include <stdio.h>
#include <stdlib.h>
#include <alsa/asoundlib.h>
	      
main (int argc, char *argv[])
{
  int i;
  int err;
  int buf[128];
  snd_pcm_t *playback_handle;
  snd_pcm_hw_params_t *hw_params;
  FILE *fin;
  size_t nread;
  unsigned int rate = 44100;	

  if (argc != 3) {
    fprintf(stderr, "Usage: %s card file\n", argv[0]);
    exit(1);
  }

  if ((err = snd_pcm_open (&playback_handle, argv[1], SND_PCM_STREAM_PLAYBACK, 0)) < 0) {
    fprintf (stderr, "cannot open audio device %s (%s)\n", 
	     argv[1],
	     snd_strerror (err));
    exit (1);
  }
		   
  if ((err = snd_pcm_hw_params_malloc (&hw_params)) < 0) {
    fprintf (stderr, "cannot allocate hardware parameter structure (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
				 
  if ((err = snd_pcm_hw_params_any (playback_handle, hw_params)) < 0) {
    fprintf (stderr, "cannot initialize hardware parameter structure (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
	
  if ((err = snd_pcm_hw_params_set_access (playback_handle, hw_params, SND_PCM_ACCESS_RW_INTERLEAVED)) < 0) {
    fprintf (stderr, "cannot set access type (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
	
  if ((err = snd_pcm_hw_params_set_format (playback_handle, hw_params, SND_PCM_FORMAT_S16_LE)) < 0) {
    fprintf (stderr, "cannot set sample format (%s)\n",
	     snd_strerror (err));
    exit (1);
  }


  if ((err = snd_pcm_hw_params_set_rate_near (playback_handle, hw_params, &rate, 0)) < 0) {
    fprintf (stderr, "cannot set sample rate (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
  printf("Rate set to %d\n", rate);
	
  if ((err = snd_pcm_hw_params_set_channels (playback_handle, hw_params, 2)) < 0) {
    fprintf (stderr, "cannot set channel count (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
	
  if ((err = snd_pcm_hw_params (playback_handle, hw_params)) < 0) {
    fprintf (stderr, "cannot set parameters (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
	
  snd_pcm_hw_params_free (hw_params);
	
  /*
  if ((err = snd_pcm_prepare (playback_handle)) < 0) {
    fprintf (stderr, "cannot prepare audio interface for use (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
  */
	
  if ((fin = fopen(argv[2], "r")) == NULL) {
      fprintf(stderr, "Can't open %s for reading\n", argv[2]);
      exit(1);
  }

  while ((nread = fread(buf, sizeof(int), 128, fin)) > 0) {
    //printf("writing\n");
    if ((err = snd_pcm_writei (playback_handle, buf, nread)) != nread) {
      fprintf (stderr, "write to audio interface failed (%s)\n",
	       snd_strerror (err));
      snd_pcm_prepare(playback_handle);
    }
  }

  snd_pcm_drain(playback_handle);	
  snd_pcm_close (playback_handle);
  exit (0);
}

      
```





Check that the microphone is enabled using `alsamixer`.
Record by `alsa_capture hw:0 tmp.s16`for example.
Playback by

```

	
sox -c 2 -r 44100 tmp.s16 tmp.wav
mplayer tmp.wav
	
      
```


or by using the next program

```

	
alsa_playback hw:0 tmp.s16
	
      
```




###  Capturing using callbacks 


See [A Tutorial on Using the ALSA Audio API](http://equalarea.com/paul/alsa-audio.html) 

###  Managing latency 


The program [/test/latency.c](http://www.alsa-project.org/alsa-doc/alsa-lib/_2test_2latency_8c-example.html) can be run with various parameters to test the latency of your system. _Warning: turn your volume way down low or the feedback might fry your speakers!_ For example,
on a low setting

```

	
latency -m 128 -M 128
	
      
```


gave a latency of only 0.93 msecs!


The "poor" latency test of

```

	
latency -m 8192 -M 8192 -t 1 -p
	
      
```


gave a latency of 92.9 msecs.


See [Low latency howto](http://www.alsa-project.org/main/index.php/Low_latency_howto) 


Two methods are available to control latency: one is through the ALSA configuration
files, the other is programmatically.
The following is [claimed to work](http://www.linuxquestions.org/questions/linux-software-2/alsa-latency-configuration-904689/) in the configuration file `/etc/asound.conf`:

```

	
pcm.card0 {
  type hw
  card 0
}

pcm.!default {
  type plug
  slave.pcm "dmixer"
}


pcm.dmixer {
  type dmix
  ipc_key 2048
  slave {
    pcm "hw:0,0"
    period_time 0
    period_size 2048
    buffer_size 65536
    buffer_time 0
    periods 128
    rate 48000
    channels 2
  }
  bindings {
    0 0
    1 1
  }
}
	
      
```


 _I haven't tested this yet_ .


Programmatically you need to set the internal buffer and period sizes using `snd_pcm_hw_params_set_buffer_size_near`and `snd_pcm_hw_params_set_period_size_near`. _I haven't got this to work yet_ .

###  Playback of captured sound 


Playback of captured sound involves two handles, possibly for different
cards. The direct method of just combining two of these in a loop

```cpp

	
while (1) {
    int nread;
    if ((nread = snd_pcm_readi (capture_handle, buf, BUF_SIZE)) != BUF_SIZE) {
      fprintf (stderr, "read from audio interface failed (%s)\n",
	       snd_strerror (nread));
      snd_pcm_prepare(capture_handle);
      continue;
    }
        
    printf("copying %d\n", nread);

    if ((err = snd_pcm_writei (playback_handle, buf, nread)) != nread) {
      if (err < 0) {
	fprintf (stderr, "write to audio interface failed (%s)\n",
		 snd_strerror (err));
      } else {
	fprintf (stderr, "write to audio interface failed after %d frames\n", err);
      }
      snd_pcm_prepare(playback_handle);
    }
} 
	
      
```


doesn't unfortunately work. On my computer it threw up a variety of
errors, including broken pipe, device not ready and device non-existent.


There are many issues that must be addressed in order to playback captured
sound directly. The first issue is that each soundcard has its own timing
clock. These must be synchronised. This is difficult to maintain for
consumer-grade cards as their clocks apparently are low quality and will
drift or be erratic. Nevertheless, ALSA will attempt to synchronise clocks
by the function `snd_pcm_link`which takes two card handles
as parameter.


The next issue is that finer control must be exercised over the buffers and how
often ALSA will fill these buffers. This is controlled by two parameters,
buffer size and period size (or buffer time and period time). The period size/time
controls how often interrupts occur to fill the buffer. Typically, the
period size (time) is set to half that of the buffer size (time).
Relevant functions are `snd_pcm_hw_params_set_buffer_size_near`and `snd_pcm_hw_params_set_period_size_near`.
Corresponding `get`functions can used to discover what values
were actually set.


In addition to hardware parameters, ALSA can also set software parameters.
The distinction between the two is not clear to me, but anyway, a "start
threshold" and "available minimum" have to set as software
parameters. I have managed to get working results by setting both of
these to the period size, using `snd_pcm_sw_params_set_start_threshold`and `snd_pcm_sw_params_set_avail_min`. Setting software
parameters is similar to setting hardware parameters: first a data
structure is initialised by `snd_pcm_sw_params_current`,
the software space is restricted by setter calls, and then the data
is set into the card by `snd_pcm_sw_params`.


ALSA needs to keep the output as full as possible. Otherwise it will generate
a "write error". I have no idea why, but it only seems to work if two
buffers are written to the playback device before attempts are made to read
and copy from the capture device. Sometimes one buffer will do, but no more
than two. To avoid extraneous unwanted noise at the beginning of playback,
two buffers of silence work well.


The resultant program is playback-capture.c:

```cpp

/**
 * Jan Newmarch
 */

#define PERIOD_SIZE 1024
#define BUF_SIZE (PERIOD_SIZE * 2)

#include <stdio.h>
#include <stdlib.h>
#include <alsa/asoundlib.h>

void print_pcm_state(snd_pcm_t *handle, char *name) {
  switch (snd_pcm_state(handle)) {
  case SND_PCM_STATE_OPEN:
    printf("state open %s\n", name);
    break;

  case SND_PCM_STATE_SETUP:
    printf("state setup %s\n", name);
    break;

  case SND_PCM_STATE_PREPARED:
    printf("state prepare %s\n", name);
    break;

  case SND_PCM_STATE_RUNNING:
    printf("state running %s\n", name);
    break;

  case SND_PCM_STATE_XRUN:
    printf("state xrun %s\n", name);
    break;

  default:
    printf("state other %s\n", name);
    break;

  }
}


int setparams(snd_pcm_t *handle, char *name) {
  snd_pcm_hw_params_t *hw_params;
  int err;


  if ((err = snd_pcm_hw_params_malloc (&hw_params)) < 0) {
    fprintf (stderr, "cannot allocate hardware parameter structure (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
				 
  if ((err = snd_pcm_hw_params_any (handle, hw_params)) < 0) {
    fprintf (stderr, "cannot initialize hardware parameter structure (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
	
  if ((err = snd_pcm_hw_params_set_access (handle, hw_params, SND_PCM_ACCESS_RW_INTERLEAVED)) < 0) {
    fprintf (stderr, "cannot set access type (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
	
  if ((err = snd_pcm_hw_params_set_format (handle, hw_params, SND_PCM_FORMAT_S16_LE)) < 0) {
    fprintf (stderr, "cannot set sample format (%s)\n",
	     snd_strerror (err));
    exit (1);
  }

  unsigned int rate = 48000;	
  if ((err = snd_pcm_hw_params_set_rate_near (handle, hw_params, &rate, 0)) < 0) {
    fprintf (stderr, "cannot set sample rate (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
  printf("Rate for %s is %d\n", name, rate);
	
  if ((err = snd_pcm_hw_params_set_channels (handle, hw_params, 2)) < 0) {
    fprintf (stderr, "cannot set channel count (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
	
  snd_pcm_uframes_t buffersize = BUF_SIZE;
  if ((err = snd_pcm_hw_params_set_buffer_size_near(handle, hw_params, &buffersize)) < 0) {
    printf("Unable to set buffer size %li: %s\n", BUF_SIZE, snd_strerror(err));
    exit (1);;
  }

  snd_pcm_uframes_t periodsize = PERIOD_SIZE;
  fprintf(stderr, "period size now %d\n", periodsize);
  if ((err = snd_pcm_hw_params_set_period_size_near(handle, hw_params, &periodsize, 0)) < 0) {
    printf("Unable to set period size %li: %s\n", periodsize, snd_strerror(err));
    exit (1);
  }

  if ((err = snd_pcm_hw_params (handle, hw_params)) < 0) {
    fprintf (stderr, "cannot set parameters (%s)\n",
	     snd_strerror (err));
    exit (1);
  }

  snd_pcm_uframes_t p_psize;
  snd_pcm_hw_params_get_period_size(hw_params, &p_psize, NULL);
  fprintf(stderr, "period size %d\n", p_psize);

  snd_pcm_hw_params_get_buffer_size(hw_params, &p_psize);
  fprintf(stderr, "buffer size %d\n", p_psize);

  snd_pcm_hw_params_free (hw_params);
	
  if ((err = snd_pcm_prepare (handle)) < 0) {
    fprintf (stderr, "cannot prepare audio interface for use (%s)\n",
	     snd_strerror (err));
    exit (1);
  }

  return 0;
}

int set_sw_params(snd_pcm_t *handle, char *name) {
  snd_pcm_sw_params_t *swparams;
  int err;

  snd_pcm_sw_params_alloca(&swparams);

  err = snd_pcm_sw_params_current(handle, swparams);
  if (err < 0) {
    fprintf(stderr, "Broken configuration for this PCM: no configurations available\n");
    exit(1);
  }
  
  err = snd_pcm_sw_params_set_start_threshold(handle, swparams, PERIOD_SIZE);
  if (err < 0) {
    printf("Unable to set start threshold: %s\n", snd_strerror(err));
    return err;
  }
  err = snd_pcm_sw_params_set_avail_min(handle, swparams, PERIOD_SIZE);
  if (err < 0) {
    printf("Unable to set avail min: %s\n", snd_strerror(err));
    return err;
  }

  if (snd_pcm_sw_params(handle, swparams) < 0) {
    fprintf(stderr, "unable to install sw params:\n");
    exit(1);
  }

  return 0;
}

/************** some code from latency.c *****************/
	      
main (int argc, char *argv[])
{
  int i;
  int err;
  int buf[BUF_SIZE];
  snd_pcm_t *playback_handle;
  snd_pcm_t *capture_handle;
  snd_pcm_hw_params_t *hw_params;
  FILE *fin;
  size_t nread;
  snd_pcm_format_t format = SND_PCM_FORMAT_S16_LE;
  if (argc != 3) {
    fprintf(stderr, "Usage: %s in-card out-card\n", argv[0]);
    exit(1);
  } 

  /**** Out card *******/
  if ((err = snd_pcm_open (&playback_handle, argv[2], SND_PCM_STREAM_PLAYBACK, 0)) < 0) {
    fprintf (stderr, "cannot open audio device %s (%s)\n", 
	     argv[2],
	     snd_strerror (err));
    exit (1);
  }

  setparams(playback_handle, "playback");
  set_sw_params(playback_handle, "playback");


  /*********** In card **********/

  if ((err = snd_pcm_open (&capture_handle, argv[1], SND_PCM_STREAM_CAPTURE, 0)) < 0) {
    fprintf (stderr, "cannot open audio device %s (%s)\n", 
	     argv[1],
	     snd_strerror (err));
    exit (1);
  }

  setparams(capture_handle, "capture");
  set_sw_params(capture_handle, "capture");
  
  if ((err = snd_pcm_link(capture_handle, playback_handle)) < 0) {
    printf("Streams link error: %s\n", snd_strerror(err));
    exit(0);
  }

  if ((err = snd_pcm_prepare (playback_handle)) < 0) {
    fprintf (stderr, "cannot prepare playback audio interface for use (%s)\n",
	     snd_strerror (err));
    exit (1);
  }
  
  /**************** stuff something into the playback buffer ****************/
  if (snd_pcm_format_set_silence(format, buf, 2*BUF_SIZE) < 0) {
    fprintf(stderr, "silence error\n");
    exit(1);
  }
  
  int n = 0;
  while (n++ < 2) {
    if (snd_pcm_writei (playback_handle, buf, BUF_SIZE) < 0) {
      fprintf(stderr, "write error\n");
      exit(1);
    }
  }
  
  /************* COPY ************/
  while (1) {
    int nread;
    if ((nread = snd_pcm_readi (capture_handle, buf, BUF_SIZE)) != BUF_SIZE) {
      if (nread < 0) {
	fprintf (stderr, "read from audio interface failed (%s)\n",
		 snd_strerror (nread));
      } else {
	fprintf (stderr, "read from audio interface failed after %d frames\n", nread);
      }	
      snd_pcm_prepare(capture_handle);
      continue;
    }
        
    if ((err = snd_pcm_writei (playback_handle, buf, nread)) != nread) {
      if (err < 0) {
	fprintf (stderr, "write to audio interface failed (%s)\n",
		 snd_strerror (err));
      } else {
	fprintf (stderr, "write to audio interface failed after %d frames\n", err);
      }
      snd_pcm_prepare(playback_handle);
    }
  }


  snd_pcm_drain(playback_handle);	
  snd_pcm_close (playback_handle);
  exit (0);
}

      
```



