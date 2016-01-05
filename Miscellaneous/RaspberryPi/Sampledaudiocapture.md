
##  Sampled audio capture 


The RPi does not have an audio-in or line-in port.
I connected my SoundBlaster USB card through a powered USB hub.
It shows up with `arecord -l`as

```
**** List of CAPTURE Hardware Devices ****
card 1: Pro [SB X-Fi Surround 5.1 Pro], device 0: USB Audio [USB Audio]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
```


so that to ALSA it is device `hw:1,0`.

###  ALSA 


The standard program `arecord`works if you get the options
correct:

```
arecord -D hw:1,0 -f S16_LE -c 2 -r 48000 tmp.s16
Recording WAVE 'tmp.s16' : Signed 16 bit Little Endian, Rate 48000 Hz, Stereo
```


The resulting file can be played back using

```
aplay -D hw:1,1 -c 2 -r 48000 -f S16_LE tmp.s16
```





In the chapter on [ALSA](../Sampled/Alsa) I gave the source for a program `alsa_capture.c`.
When run by

```
alsa_capture hw:1,0 tmp.s16
```


it records PCM data in stereo at 48,000hz.
