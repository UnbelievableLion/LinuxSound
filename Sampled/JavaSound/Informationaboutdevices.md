
##  Information about devices 


Each device is represented by a `Mixer`object.
Ask the `AudioSystem`for a list of these.
Each mixer has a set of target (output) lines and source
(input lines). Query each mixer about these separately.
The program is DeviceInfo.java:

```cpp

      


import javax.sound.sampled.*;

public class DeviceInfo {

    public static void main(String[] args) throws Exception {

	Mixer.Info[] minfoSet = AudioSystem.getMixerInfo();
	System.out.println("Mixers:");
	for (Mixer.Info minfo: minfoSet) {
	    System.out.println("   " + minfo.toString());

	    Mixer m = AudioSystem.getMixer(minfo);
	    System.out.println("    Mixer: " + m.toString());
	    System.out.println("      Source lines");
	    Line.Info[] slines = m.getSourceLineInfo();
	    for (Line.Info s: slines) {
		System.out.println("        " + s.toString());
	    }

	    Line.Info[] tlines = m.getTargetLineInfo();
	    System.out.println("      Target lines");
	    for (Line.Info t: tlines) {
		System.out.println("        " + t.toString());
	    }
	}
    }
}
      
    
```


A part of the output on my system is

```

	
Mixers:
   PulseAudio Mixer, version 0.02
      Source lines
        interface SourceDataLine supporting 42 audio formats, and buffers of 0 to 1000000 bytes
        interface Clip supporting 42 audio formats, and buffers of 0 to 1000000 bytes
      Target lines
        interface TargetDataLine supporting 42 audio formats, and buffers of 0 to 1000000 bytes
   default [default], version 1.0.24
      Source lines
        interface SourceDataLine supporting 512 audio formats, and buffers of at least 32 bytes
        interface Clip supporting 512 audio formats, and buffers of at least 32 bytes
      Target lines
        interface TargetDataLine supporting 512 audio formats, and buffers of at least 32 bytes
   PCH [plughw:0,0], version 1.0.24
      Source lines
        interface SourceDataLine supporting 24 audio formats, and buffers of at least 32 bytes
        interface Clip supporting 24 audio formats, and buffers of at least 32 bytes
      Target lines
        interface TargetDataLine supporting 24 audio formats, and buffers of at least 32 bytes
   NVidia [plughw:1,3], version 1.0.24
      Source lines
        interface SourceDataLine supporting 96 audio formats, and buffers of at least 32 bytes
        interface Clip supporting 96 audio formats, and buffers of at least 32 bytes
      Target lines
   NVidia [plughw:1,7], version 1.0.24
      Source lines
        interface SourceDataLine supporting 96 audio formats, and buffers of at least 32 bytes
        interface Clip supporting 96 audio formats, and buffers of at least 32 bytes
      Target lines
   NVidia [plughw:1,8], version 1.0.24
      Source lines
        interface SourceDataLine supporting 96 audio formats, and buffers of at least 32 bytes
        interface Clip supporting 96 audio formats, and buffers of at least 32 bytes
      Target lines
	
      
```


This shows both PulseAudio and ALSA mixers.
Further queries could show what the supported formats are, for example.
