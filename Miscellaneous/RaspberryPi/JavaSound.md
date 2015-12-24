
##  JavaSound 


I installed OpenJDK version 6, the default Java install at present.
      The program `DeviceInfo`was  given in the JavaSound Sampled chapter
      The output from this on the RPi is

```

	
Mixers:
   PulseAudio Mixer, version 0.02
    Mixer: org.classpath.icedtea.pulseaudio.PulseAudioMixer@1d05c81
      Source lines
        interface SourceDataLine supporting 42 audio formats, and buffers of 0 to 1000000 bytes
        interface Clip supporting 42 audio formats, and buffers of 0 to 1000000 bytes
      Target lines
        interface TargetDataLine supporting 42 audio formats, and buffers of 0 to 1000000 bytes
   ALSA [default], version 1.0.24
    Mixer: com.sun.media.sound.DirectAudioDevice@12558d6
      Source lines
        interface SourceDataLine supporting 84 audio formats, and buffers of at least 32 bytes
        interface Clip supporting 84 audio formats, and buffers of at least 32 bytes
      Target lines
   ALSA [plughw:0,0], version 1.0.24
    Mixer: com.sun.media.sound.DirectAudioDevice@eb7859
      Source lines
        interface SourceDataLine supporting 8 audio formats, and buffers of at least 32 bytes
        interface Clip supporting 8 audio formats, and buffers of at least 32 bytes
      Target lines
   Port ALSA [hw:0], version 1.0.24
    Mixer: com.sun.media.sound.PortMixer@fd54d6
      Source lines
      Target lines
        PCM target port
	
      
```


Althjough this is using the PulseAudio mixer, pulse audio isn't actually running
      (at this stage)!
      So it can only use the ALSA interface.


The program `PlayAudioFile`was  given in the JavaSound Sampled chapter.
      This can play .wav files okay. But it can't play Ogg-Vorbis or MP3 files and throws
      anUnsupportedAudioFileException.
