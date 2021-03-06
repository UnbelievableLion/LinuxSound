
##  Examples 

```cpp
/*
 *
 * ao_example.c
 *
 *     Written by Stan Seibert - July 2001
 *
 * Legal Terms:
 *
 *     This source file is released into the public domain.  It is
 *     distributed without any warranty; without even the implied
 *     warranty * of merchantability or fitness for a particular
 *     purpose.
 *
 * Function:
 *
 *     This program opens the default driver and plays a 440 Hz tone for
 *     one second.
 *
 * Compilation command line (for Linux systems):
 *
 *     gcc -lao -ldl -lm -o ao_example ao_example.c
 *
 */

#include <stdio.h>
#include <ao/ao.h>
#include <math.h>

#define BUF_SIZE 4096

int main(int argc, char **argv)
{
	ao_device *device;
	ao_sample_format format;
	int default_driver;
	char *buffer;
	int buf_size;
	int sample;
	float freq = 440.0;
	int i;

	/* -- Initialize -- */

	fprintf(stderr, "libao example program\n");

	ao_initialize();

	/* -- Setup for default driver -- */

	default_driver = ao_default_driver_id();

        memset(&format, 0, sizeof(format));
	format.bits = 16;
	format.channels = 2;
	format.rate = 44100;
	format.byte_format = AO_FMT_LITTLE;

	/* -- Open driver -- */
	device = ao_open_live(default_driver, &format, NULL /* no options */);
	if (device == NULL) {
		fprintf(stderr, "Error opening device.\n");
		return 1;
	}

	/* -- Play some stuff -- */
	buf_size = format.bits/8 * format.channels * format.rate;
	buffer = calloc(buf_size,
			sizeof(char));

	for (i = 0; i < format.rate; i++) {
		sample = (int)(0.75 * 32768.0 *
			sin(2 * M_PI * freq * ((float) i/format.rate)));

		/* Put the same stuff in left and right channel */
		buffer[4*i] = buffer[4*i+2] = sample & 0xff;
		buffer[4*i+1] = buffer[4*i+3] = (sample >> 8) & 0xff;
	}
	ao_play(device, buffer, buf_size);

	/* -- Close and shutdown -- */
	ao_close(device);

	ao_shutdown();

  return (0);
}
```

***


Copyright © Jan Newmarch, jan@newmarch.name


<a href="http://creativecommons.org/licenses/by-sa/4.0/" rel="license">
<img alt="Creative Commons License" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" style="border-width:0"/>
</a>


"Programming and Using Linux Sound - in depth"by [Jan Newmarch](https://jan.newmarch.name) is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/) .


Based on a work at [https://jan.newmarch.name/LinuxSound/](https://jan.newmarch.name/LinuxSound/) .


If you like this book, please contribute using PayPal


<a href="https://www.paypal.com/cgi-bin/webscr?cmd=_donations&amp;business=jan%40newmarch%2ename&amp;lc=AU&amp;item_name=LinuxSound&amp;currency_code=AUD&amp;bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted">
<img src="https://www.paypalobjects.com/WEBSCR-640-20110401-1/en_AU/i/btn/btn_donateCC_LG.gif"/>
</a>


Or Flattr me:


<a href="https://flattr.com/submit/auto?user_id=jannewmarch&amp;url=http://jan.newmarch.name&amp;title=Linux%20Sound&amp;description=Programming%20and%20Using%20Linu%20Sound&amp;language=en_GB&amp;tags=linux,sound,alsa,pulseaudio,JavaSound,MIDI&amp;category=text">
<img alt="Flattr this book" src="https://api.flattr.com/button/flattr-badge-large.png"/>
</a>
