#  Where does javaSound get its devices from? 

The first program in this chapter showed a list of mixer devices and their attributes.
      How does Java get this information? In this section we look at JDK 1.7 - OpenJDK will
      probably be similar.
      You will need the Java source from Oracle to track through this. Alternatively, move on...

The file
 `jre/lib/resources.jar`contains a list of resources used by the
      JRE runtime.  This is a zip file, and contains the file
 ` META-INF/services/javax.sound.sampled.spi.MixerProvider`.
      On my system the contents of this file are
```

	
# last mixer is default mixer
com.sun.media.sound.PortMixerProvider
com.sun.media.sound.DirectAudioDeviceProvider
	
      
```


The class
 `com.sun.media.sound.PortMixerProvider`is in
      the  file
 `java/media/src/share/native/com/sun/media/sound/PortMixerProvider.java`on my system. It extends
 `MixerProvider`and implements methods such as
 ` Mixer.Info[] getMixerInfo`. This class stores the device information.

The bulk of the work done done by this class is actually performed by native methods in the
      C file
 `java/media/src/share/native/com/sun/media/sound/PortMixerProvider.c`which implements the two methods
 `nGetNumDevices`and
 `nNewPortMixerInfo`used by the
 `PortMixerProvider`class.
      Unfortunately, there's ot much joy to be found in this C file, as it just makes calls
      to the C functions
 `PORT_GetPortMixerCount`and
 `PORT_GetPortMixerDescription`.

There are three files containing these functions
```

	
java/media/src/windows/native/com/sun/media/sound/PLATFORM_API_WinOS_Ports.c
java/media/src/solaris/native/com/sun/media/sound/PLATFORM_API_SolarisOS_Ports.c
java/media/src/solaris/native/com/sun/media/sound/PLATFORM_API_LinuxOS_ALSA_Ports.c
	
      
```
In the file
 `PLATFORM_API_LinuxOS_ALSA_Ports.c`you will see the
      function calls to ALSA as described in the
 [ALSA chapter] (../Alsa/)
.
      These calls fill in information about the ALSA devices for use by JavaSound.

