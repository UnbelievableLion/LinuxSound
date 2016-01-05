
##  OpenMAX IL 

###  Implementations 


There are three implementations that I have been able to access.

####  Raspberry Pi 


The Raspberry Pi has a Broadcom GPU (graphics processing unit) and
Broadcom support OpenMAX IL. The include files needed to build applications
are in `/opt/vc/include/IL`, `/opt/vc/include`and `/opt/vc/include/interface/vcos/pthreads `.
The libraries that need to be linked are in the `/opt/vc/lib`directory and are `openmaxil`and `bcm_host`.


The Broadcom libraries need additional code to be called as well as
standard OpenMAX IL functions. In addition, there are a number of
(legal) extensions to OpenMAX IL that are not found in the specification
or in other implementations. These are described in `/opt/vc/include/IL/OMX_Broadcom.h`.
For these reasons I define `RASPBERRY_PI`to allow
these to be dealt with.


The compile line for e.g. `listcomponents.c`is

```
cc -g -DRASPBERRY_PI -I /opt/vc/include/IL -I /opt/vc/include \
   -I /opt/vc/include/interface/vcos/pthreads \
   -o listcomponents listcomponents.c \
   -L /opt/vc/lib -l openmaxil -l bcm_host
```


The Broadcom implementation is closed source. It appears to be a [thin wrapper](http://www.raspberrypi.org/phpBB3/viewtopic.php?f=70&t=33101&p=287590#p287590) around their GPU API, and they [will not](http://www.raspberrypi.org/phpBB3/viewtopic.php?f=70&t=28313&p=276235#p276235) release any details of that API. This means that you cannot extend the set of
components, or the codecs supported, since there are no details of how to build new components.
While the set of components is reasonable, at present there is no support for codecs
other than PCM, and there is no support of non-GPU hardware such as USB soundcards.


 [OtherCrashOverride](http://www.raspberrypi.org/phpBB3/viewtopic.php?f=70&t=33101&p=287590#p287590) says he has managed to get the Broadcom components running under the LIM
implementation, but I haven't confirmed that yet.

####  Bellagio 


The Bellagio library does not require additional code or have any extensions.
There are a few minor bugs, so I define `BELLAGIO`to handle them.
I built from source, but didn't install, so the includes and libraries
are in a funny place. My compile line is

```
cc  -g -DBELLAGIO -I ../libomxil-bellagio-0.9.3/include/ \
    -o listcomponents listcomponents.c \
    -L ../libomxil-bellagio-0.9.3/src/.libs -l omxil-bellagio
```


and at run time

```
export LD_LIBRARY_PATH=../libomxil-bellagio-0.9.3/src/.libs/
./listcomponents
```


The Bellagio code is open source.

####  LIM 


Downloading the 1.1 version was a hassle  because the 1.1 download uses a Git repo that has
disappeared (as of Feb, 2013). Instead you have to run

```
git clone git://limoa.git.sourceforge.net/gitroot/limoa/limoi-components
  git clone git://limoa.git.sourceforge.net/gitroot/limoa/limoi-core
  git clone git://limoa.git.sourceforge.net/gitroot/limoa/limoi-plugins
  git clone git://limoa.git.sourceforge.net/gitroot/limoa/limutil
  git clone git://limoa.git.sourceforge.net/gitroot/limoa/manifest
```


"You have to copy the root.mk in build to a top level folder containing all
the code and rename it Makefile. The root.readme file has build instructions."
Thanks to [OtherCrashOverride](http://www.raspberrypi.org/phpBB3/viewtopic.php?f=70&t=33101&p=286516#p286516) for these instructions.


Building the library had some minor hiccups. I had to comment out a couple
of lines from one video file as it referred to non-existent structure fields,
and had to remove `-Werrors`from one `Makefile.am`as otherwise a warning about an unused variable would abort the compile.


The library build puts files in a new directory in my HOME. I have found some
minor bugs in the implementation so far. My compile line is

```
cc -g -DLIM -I ../../lim-omx-1.1/LIM/limoi-core/include/ \
   -o listcomponents listcomponents.c \
   -L /home/newmarch/osm-build/lib/ -l limoa -l limoi-core
```


and at runtime,

```
export LD_LIBRARY_PATH=/home/newmarch/osm-build/lib/
./listcomponents
```


The LIM code is open source.

####  Hardware supported versions 


A list of hardware supported versions is at [OpenMAX IL Conformant Products](http://www.khronos.org/conformance/adopters/conformant-products#openmaxil) .

###  OpenMAX IL concepts 


The OpenMAX IL API is quite distinct from that of OpenMAX AL.
The basic concept is of a _Component_ , which is an audio/video
(or other) processing unit of some type, such as a volume control, a mixer,
an output device. Each Component has zero or more input and
output _ports_ , and each port can have one or more _buffers_ that carry data.


OpenMAX IL is typically meant for use by an A/V framework of some kind,
such as OpenMAX AL. In addition to OpenMAX AL, there is curently
a GStreamer plugin that uses OpenMAX IL underneath.
But one can also build standalone applications where direct calls
are made into the OpenMAX IL API. Collectively, these are all
known as _IL clients_ .


The OpenMAX IL API is difficult to work with directly. Error messages are
frequently quite useless and threads will block without explanation
until everything is _exactly_ right - and silently blocking
doesn't give you any clues about what isn't right. In addition,
the examples I have to work with don't follow the specification
exactly correctly which can lead to much wasted time.


OpenMAX IL components use buffers to carry data. A component will
usually process data from an input buffer and place it on an
output buffer. This processing is not visible to the API,
and so allows vendors to implement components in hardware or software,
built on top of other A/V components, etc. OpenMAX IL gives
mechanisms for setting and getting parameters of components,
for calling standard functions on the components, or for
getting data in and out of components.


While some of the OpenMAX IL calls are synchronous,
those that require possibly substantial amounts of processing
are asynchronous, communicating the results through
callback functions. This leads naturally to a multi-threaded
processing model, although OpenMAX IL does not visibly use any
thread libraries and should be agnostic to how an IL client
uses threads. The Bellagio examples use pthreads
while the Broadcom examples for the Raspberry Pi use
Broadcom's [VideoCore O/S (vcos)](https://github.com/raspberrypi/userland/blob/master/interface/vcos/vcos_semaphore.h) threads.


There are two mechanisms for getting data into and out of components.
The first is where the IL client makes calls on the component.
All components are required to support this mechanism.
The second is where a _tunnel_ is set up between
two components for data to flow along a shared buffer.
A component is not required to support this mechanism.

###  OpenMAX IL components 


OpenMAX IL in 1.1.2 lists a number of standard components, including (for audio)
a decoder, an encoder, a mixer, a reader, a renderer, a writer,
a capturer and a processor.
An IL client gets such a component by calling `OMX_GetHandle()`,
passing in the name of the component. This is a problem: the components
do not have a standard name. The 1.1.2 specification says:


   > Since components are requested by name, a naming convention is defined. OpenMAX IL
component names are zero terminated strings with the following format:
“OMX.<vendor_name>.<vendor_specified_convention>”.
For example:


OMX.CompanyABC.MP3Decoder.productXYZ


No standardization among component names is dictated across different vendors.



The Bellagio library (you need the source package to see these files) lists in
its README only two audio components:

+ OMX audio volume control
+ OMX audio mixer component

and their names (from the example test files) are "OMX.st.volume.component" and
"OMX.st.audio.mixer" respectively. The company behind Bellagio is [STMicroelectronics](http://www.st.com/internet/com/home/home.jsp) which explains the "st".


The Broadcom OpenMAX IL implementation used on the Raspberry Pi is much better
documented. If you download the firmware-master file for the Raspberry Pi
it lists the IL components in the documentation/ilcomponents directory.
This lists the components audio_capture,
audio_decode,
audio_encode,
audio_lowpower,
audio_mixer,
audio_processor,
audio_render and
audio_splitter.


Many of the openMAX IL function calls in the Broadcom examples are
buried in Broadcom convenience functions
such as

```cpp
ilclient_create_component(st->client, &st->audio_render, 
                         "audio_render", 
                         ILCLIENT_ENABLE_INPUT_BUFFERS | ILCLIENT_DISABLE_ALL_PORTS);
```


which wraps around `OMX_GetHandle()`. But at least the `ilclient.h`states "Component names as provided are automatically prefixed with
'OMX.broadcom.' before passing to the IL core.". So we can conclude that the real names
are e.g. "OMX.broadcom.audio_render" etc.


There is a simple way of programmatically getting the supported components.
First initialise the OpenMAX system by `OMX_init()`and then make calls to `OMX_ComponentNameEnum()`.
For successive index values it returns a unique name each time,
until it finally returns an error value of `OMX_ErrorNoMore`.


Each component may support a number of _roles_ . These are given by `OMX_GetRolesOfComponent`. The 1.1 specification lists classes
of audio components and associated roles in section 8.6 "Standard Audio
Components". The LIM library matches these, while Bellagio and Broadcom
do not.


The program is listcomponents.c:

```cpp
#include <stdio.h>
#include <stdlib.h>

#include <OMX_Core.h>

#ifdef RASPBERRY_PI
#include <bcm_host.h>
#endif

OMX_ERRORTYPE err;

//extern OMX_COMPONENTREGISTERTYPE OMX_ComponentRegistered[];

void listroles(char *name) {
    int n;
    OMX_U32 numRoles;
    OMX_U8 *roles[32];

    /* get the number of roles by passing in a NULL roles param */
    err = OMX_GetRolesOfComponent(name, &numRoles, NULL);
    if (err != OMX_ErrorNone) {
	fprintf(stderr, "Getting roles failed\n", 0);
	exit(1);
    }
    printf("  Num roles is %d\n", numRoles);
    if (numRoles > 32) {
	printf("Too many roles to list\n");
	return;
    }

    /* now get the roles */
    for (n = 0; n < numRoles; n++) {
	roles[n] = malloc(OMX_MAX_STRINGNAME_SIZE);
    }
    err = OMX_GetRolesOfComponent(name, &numRoles, roles);
    if (err != OMX_ErrorNone) {
	fprintf(stderr, "Getting roles failed\n", 0);
	exit(1);
    }
    for (n = 0; n < numRoles; n++) {
	printf("    role: %s\n", roles[n]);
	free(roles[n]);
    }

    /* This is in version 1.2
    for (i = 0; OMX_ErrorNoMore != err; i++) {
	err = OMX_RoleOfComponentEnum(role, name, i);
	if (OMX_ErrorNone == err) {
	    printf("   Role of omponent is %s\n", role);
	}
    } 
    */   
}

int main(int argc, char** argv) {

    int i;
    unsigned char name[OMX_MAX_STRINGNAME_SIZE];

# ifdef RASPBERRY_PI
    bcm_host_init();
# endif

    err = OMX_Init();
    if (err != OMX_ErrorNone) {
	fprintf(stderr, "OMX_Init() failed\n", 0);
	exit(1);
    }

    err = OMX_ErrorNone;
    for (i = 0; OMX_ErrorNoMore != err; i++) {
	err = OMX_ComponentNameEnum(name, OMX_MAX_STRINGNAME_SIZE, i);
	if (OMX_ErrorNone == err) {
	    printf("Component is %s\n", name);
	    listroles(name);
	}
    }
    printf("No more components\n");

    /*
    i= 0 ;
    while (1) {
	printf("Component %s\n", OMX_ComponentRegistered[i++]);
    }
    */
    exit(0);
}
```


The output from the Bellagio library is

```
Component is OMX.st.clocksrc
  Num roles is 1
    role: clocksrc
Component is OMX.st.clocksrc
  Num roles is 1
    role: clocksrc
Component is OMX.st.video.scheduler
  Num roles is 1
    role: video.scheduler
Component is OMX.st.video.scheduler
  Num roles is 1
    role: video.scheduler
Component is OMX.st.volume.component
  Num roles is 1
    role: volume.component
Component is OMX.st.volume.component
  Num roles is 1
    role: volume.component
Component is OMX.st.audio.mixer
  Num roles is 1
    role: audio.mixer
Component is OMX.st.audio.mixer
  Num roles is 1
    role: audio.mixer
Component is OMX.st.clocksrc
  Num roles is 1
    role: clocksrc
Component is OMX.st.clocksrc
  Num roles is 1
    role: clocksrc
Component is OMX.st.video.scheduler
  Num roles is 1
    role: video.scheduler
Component is OMX.st.video.scheduler
  Num roles is 1
    role: video.scheduler
Component is OMX.st.volume.component
  Num roles is 1
    role: volume.component
Component is OMX.st.volume.component
  Num roles is 1
    role: volume.component
Component is OMX.st.audio.mixer
  Num roles is 1
    role: audio.mixer
Component is OMX.st.audio.mixer
  Num roles is 1
    role: audio.mixer
No more components
```


which is not quite correct: the OpenMAX IL specification says that each somponent
must appear once only, not repeated.


The Raspberry Pi reports a large number of components but does not define a
role for any of them:

```
Component is OMX.broadcom.audio_capture
  Num roles is 0
Component is OMX.broadcom.audio_decode
  Num roles is 0
Component is OMX.broadcom.audio_encode
  Num roles is 0
Component is OMX.broadcom.audio_render
  Num roles is 0
Component is OMX.broadcom.audio_mixer
  Num roles is 0
Component is OMX.broadcom.audio_splitter
  Num roles is 0
Component is OMX.broadcom.audio_processor
  Num roles is 0
Component is OMX.broadcom.camera
  Num roles is 0
Component is OMX.broadcom.clock
  Num roles is 0
Component is OMX.broadcom.coverage
  Num roles is 0
Component is OMX.broadcom.egl_render
  Num roles is 0
Component is OMX.broadcom.image_fx
  Num roles is 0
Component is OMX.broadcom.image_decode
  Num roles is 0
Component is OMX.broadcom.image_encode
  Num roles is 0
Component is OMX.broadcom.image_read
  Num roles is 0
Component is OMX.broadcom.image_write
  Num roles is 0
Component is OMX.broadcom.read_media
  Num roles is 0
Component is OMX.broadcom.resize
  Num roles is 0
Component is OMX.broadcom.source
  Num roles is 0
Component is OMX.broadcom.text_scheduler
  Num roles is 0
Component is OMX.broadcom.transition
  Num roles is 0
Component is OMX.broadcom.video_decode
  Num roles is 0
Component is OMX.broadcom.video_encode
  Num roles is 0
Component is OMX.broadcom.video_render
  Num roles is 0
Component is OMX.broadcom.video_scheduler
  Num roles is 0
Component is OMX.broadcom.video_splitter
  Num roles is 0
Component is OMX.broadcom.visualisation
  Num roles is 0
Component is OMX.broadcom.write_media
  Num roles is 0
Component is OMX.broadcom.write_still
  Num roles is 0
No more components
```


The output from LIM is

```
Component is OMX.limoi.alsa_sink
  Num roles is 1
    role: audio_renderer.pcm
Component is OMX.limoi.clock
  Num roles is 1
    role: clock.binary
Component is OMX.limoi.ffmpeg.decode.audio
  Num roles is 8
    role: audio_decoder.aac
    role: audio_decoder.adpcm
    role: audio_decoder.amr
    role: audio_decoder.mp3
    role: audio_decoder.ogg
    role: audio_decoder.pcm
    role: audio_decoder.ra
    role: audio_decoder.wma
Component is OMX.limoi.ffmpeg.decode.video
  Num roles is 7
    role: video_decoder.avc
    role: video_decoder.h263
    role: video_decoder.mjpeg
    role: video_decoder.mpeg2
    role: video_decoder.mpeg4
    role: video_decoder.rv
    role: video_decoder.wmv
Component is OMX.limoi.ffmpeg.demux
  Num roles is 1
    role: container_demuxer.all
Component is OMX.limoi.ffmpeg.encode.audio
  Num roles is 2
    role: audio_encoder.aac
    role: audio_encoder.mp3
Component is OMX.limoi.ffmpeg.encode.video
  Num roles is 2
    role: video_encoder.h263
    role: video_encoder.mpeg4
Component is OMX.limoi.ffmpeg.mux
  Num roles is 1
    role: container_muxer.all
Component is OMX.limoi.ogg_dec
  Num roles is 1
    role: audio_decoder_with_framing.ogg
Component is OMX.limoi.sdl.renderer.video
  Num roles is 1
    role: iv_renderer.yuv.overlay
Component is OMX.limoi.video_scheduler
  Num roles is 1
    role: video_scheduler.binary
No more components
```

###  Getting information about an IL component 


We will next look at how to get information about the OpenMAX IL
system and any component that we use.
All IL clients must initialise OpenMAX IL by calling `OMX_Init()`.
Nearly all functions return error values, and the style used by Bellagio is

```cpp
err = OMX_Init();
  if(err != OMX_ErrorNone) {
      fprintf(stderr, "OMX_Init() failed\n", 0);
      exit(1);
  }
```


This looks like a reasonable style to me, so I follow it in the sequel.


The next requirement is to get a _handle_ to a component.
This requires the vendor's name for the component,
which can be found using the `listcomponents.c`program above. The function `OMX_GetHandle`takes some parameters
including a set of _callback_ functions. These are needed to
track behaviour of the application, but are not needed for the example
in this section. This code shows how to get a handle to the Bellagio Volume component:

```cpp
OMX_HANDLETYPE handle;
  OMX_CALLBACKTYPE callbacks;
  OMX_ERRORTYPE err;

  err = OMX_GetHandle(&handle, "OMX.st.volume.component", NULL /*appPriv */, &callbacks);
  if(err != OMX_ErrorNone) {
      fprintf(stderr, "OMX_GetHandle failed\n", 0);
      exit(1);
  }
```


The component has ports and the ports have channels. Getting and setting
information about these is done by the functions `OMX_GetParameter()`, `OMX_SetParameter()`, `OMX_GetConfig()`and `OMX_GetConfig()`. The ...Parameter calls are made before the
component is "loaded", ...Config calls are made after it is loaded.


C is not an O/O language and this is an ordinary function call (well, actually
it's a macro). In an O/O language it would be a method of an object taking another
object as parameter as in `component.method(object)`.
In OpenMAX IL the Get/Set function takes the calling "object" as first parameter
- the component,
an indicator of what type of "object" the method's parameter is -
an index into possible "object"
types, and a structure for the parameter object.
The index values are related to structures in Table 4-2
"Audio Coding Types by Index" of the 1.1 specification.


The calls take a (pointer to a) structure for filling in or extracting values.
The structures are all normalised so that they share common fields such as the
size of the structure. In Bellagio examples, this is done by a macro `setHeader()`.
The structure passed in to get port information is usually a generic structure
of type `OMX_PORT_PARAM_TYPE`.
Some fields can be accessed directly; some need a typecast to a more specialised
type; and some buried down in unions and have to be extracted.


Ports are labelled by integer indices. There are different ports for different functions,
such as audio, image, video and other.
To get information about the starting value for audio ports, use:

```cpp
setHeader(&param, sizeof(OMX_PORT_PARAM_TYPE));
  err = OMX_GetParameter(handle, OMX_IndexParamAudioInit, &param);
  if(err != OMX_ErrorNone){
      fprintf(stderr, "Error in getting OMX_PORT_PARAM_TYPE parameter\n", 0);
    exit(1);
  }
  printf("Audio ports start on %d\n",
	 ((OMX_PORT_PARAM_TYPE)param).nStartPortNumber);
  printf("There are %d open ports\n",
	 ((OMX_PORT_PARAM_TYPE)param).nPorts);
```


The macro `setHeader`justs fills in header information such as version numbers,
and the size of the data structure.


Particular ports may now be queried about their capablilies.
We can query for the type of the port (audio or otherwise),
the direction (input or output) and information
about the MIME type supported.

```cpp
OMX_PARAM_PORTDEFINITIONTYPE sPortDef;

  setHeader(&sPortDef, sizeof(OMX_PARAM_PORTDEFINITIONTYPE));
  sPortDef.nPortIndex = 0;
  err = OMX_GetParameter(handle, OMX_IndexParamPortDefinition, &sPortDef);
  if(err != OMX_ErrorNone){
      fprintf(stderr, "Error in getting OMX_PORT_PARAM_TYPE parameter\n", 0);
    exit(1);
  }
  if (sPortDef.eDomain == OMX_PortDomainAudio) {
      printf("Is an audio port\n");
  } else {
      printf("Is other device port\n");
  }

  if (sPortDef.eDir == OMX_DirInput) {
      printf("Port is an input port\n");
  } else {
      printf("Port is an output port\n");
  }

  /* the Audio Port info is buried in a union format.audio within the struct */
  printf("Port min buffers %d,  mimetype %s, encoding %d\n",
	 sPortDef.nBufferCountMin,
	 sPortDef.format.audio.cMIMEType,
	 sPortDef.format.audio.eEncoding);
```


The Bellagio library returns "raw/audio" for the MIME type supported by
its volume control component.
This is not a valid MIME type as listed by [IANA MIME Media Types](http://www.iana.org/assignments/media-types) , though. The value returned from the encoding is zero,
corresponding to `OMX_AUDIO_CodingUnused`which also
does not seem to be correct.


If we try the same program on the Raspberry Pi component `audio_render`and on the LIM component `OMX.limoi.alsa_sink`we get NULL for the MIME type
but an encoding value of 2 which is `OMX_AUDIO_CodingPCM`.
PCM has a MIME type of `audio/L16`so NULL seems inappropriate.


An OpenMAX IL library allows a port to be queried for the data types it supports.
This is done by querying for a `OMX_AUDIO_PARAM_PORTFORMATTYPE`object using the index ` OMX_IndexParamAudioPortFormat`.
According to the specification, for each index from zero upwards
a call to `GetParameter()`should return an encoding such as `OMX_AUDIO_CodingPCM`or `OMX_AUDIO_CodingMp3`until
there are no more supported formats, on which it returns `OMX_ErrorNoMore`.


The Bellagio code returns a value of `OMX_AUDIO_CodingUnused`which is not correct. The LIM code does not set a value at all,
so you just get garbage. The Broadcom implementation works okay,
but as discussed below returns values that are not actually supported.
So there is limited value in this call...


This code tests this:

```cpp
void getSupportedAudioFormats(int indentLevel, int portNumber) {
    OMX_AUDIO_PARAM_PORTFORMATTYPE sAudioPortFormat;

    setHeader(&sAudioPortFormat, sizeof(OMX_AUDIO_PARAM_PORTFORMATTYPE));
    sAudioPortFormat.nIndex = 0;
    sAudioPortFormat.nPortIndex = portNumber;

    printf("Supported audio formats are:\n");
    for(;;) {
        err = OMX_GetParameter(handle, OMX_IndexParamAudioPortFormat, &sAudioPortFormat);
        if (err == OMX_ErrorNoMore) {
	    printf("No more formats supported\n");
	    return;
        }

	/* This shouldn't occur, but does with Broadcom library */
	if (sAudioPortFormat.eEncoding == OMX_AUDIO_CodingUnused) {
	     printf("No coding format returned\n");
	     return;
	}

	switch (sAudioPortFormat.eEncoding) {
	case OMX_AUDIO_CodingPCM:
	    printf("Supported encoding is PCM\n");
	    break; 
	case OMX_AUDIO_CodingVORBIS:
	    printf("Supported encoding is Ogg Vorbis\n");
	    break; 
	case OMX_AUDIO_CodingMP3:
	    printf("Supported encoding is MP3\n");
	    break;
#ifdef RASPBERRY_PI
	case OMX_AUDIO_CodingFLAC:
	    printf("Supported encoding is FLAC\n");
	    break; 
	case OMX_AUDIO_CodingDDP:
	    printf("Supported encoding is DDP\n");
	    break; 
	case OMX_AUDIO_CodingDTS:
	    printf("Supported encoding is DTS\n");
	    break; 
	case OMX_AUDIO_CodingWMAPRO:
	    printf("Supported encoding is WMAPRO\n");
	    break; 
#endif
	case OMX_AUDIO_CodingAAC:
	    printf("Supported encoding is AAC\n");
	    break; 
	case OMX_AUDIO_CodingWMA:
	    printf("Supported encoding is WMA\n");
	    break;
	case OMX_AUDIO_CodingRA:
	    printf("Supported encoding is RA\n");
	    break; 
	case OMX_AUDIO_CodingAMR:
	    printf("Supported encoding is AMR\n");
	    break; 
	case OMX_AUDIO_CodingEVRC:
	    printf("Supported encoding is EVRC\n");
	    break;
	case OMX_AUDIO_CodingG726:
	    printf("Supported encoding is G726\n");
	    break;
	case OMX_AUDIO_CodingMIDI:
	    printf("Supported encoding is MIDI\n");
	    break;
	case OMX_AUDIO_CodingATRAC3:
	    printf("Supported encoding is ATRAC3\n");
	    break;
	case OMX_AUDIO_CodingATRACX:
	    printf("Supported encoding is ATRACX\n");
	    break;
	case OMX_AUDIO_CodingATRACAAL:
	    printf("Supported encoding is ATRACAAL\n");
	    break;
	    /*
	case OMX_AUDIO_Coding:
	    printf("Supported encoding is \n");
	    break;
	    */
	default:
	    printf("Supported encoding is %d\n",
		  sAudioPortFormat.eEncoding);
	}
        sAudioPortFormat.nIndex++;
    }
}
```


Note that the code contains enum values such as `OMX_AUDIO_CodingATRAC3`which are specific to the Broadcom library. These are legal values according to an
OpenMAX IL extension mechanism, but of course are not portable values.


The Bellagio library incorrectly returns `OMX_AUDIO_CodingUnused`for every index value.


The Broadcom library can return lots of values. For example, for the `audio_decode`component it returns

```
Supported audio formats are:
      Supported encoding is MP3
      Supported encoding is PCM
      Supported encoding is AAC
      Supported encoding is WMA
      Supported encoding is Ogg Vorbis
      Supported encoding is RA
      Supported encoding is AMR
      Supported encoding is EVRC
      Supported encoding is G726
      Supported encoding is FLAC
      Supported encoding is DDP
      Supported encoding is DTS
      Supported encoding is WMAPRO
      Supported encoding is ATRAC3
      Supported encoding is ATRACX
      Supported encoding is ATRACAAL
      Supported encoding is MIDI
      No more formats supported
```


Regrettably, none of these are actually supported except for PCM.
According to [jamesh](http://www.raspberrypi.org/phpBB3/viewtopic.php?f=70&t=28313&p=272804#p272804) in "OMX_AllocateBuffer fails for audio decoder component":


   > The way it works is that the component passes back success for all the codecs it
can _potentially_ support. (i.e. all the codecs we've ever had going).
That is then constrained by what codecs are actually installed.
It would be better to run time detect which codecs are present,
but that code has never been written since its never been required.
It's also unlikely ever to be done as Broadcom no longer support
audio codecs in this way - they have moved off the Videocore to
the host CPU since they are now powerful enough to handle any audio decoding task



That's kind of sad, really.


Putting all the bits together gives the program info.c:

```cpp
/**
   Based on code
   Copyright (C) 2007-2009 STMicroelectronics
   Copyright (C) 2007-2009 Nokia Corporation and/or its subsidiary(-ies).
   under the LGPL
*/

#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>
#include <sys/stat.h>

#include <OMX_Core.h>
#include <OMX_Component.h>
#include <OMX_Types.h>
#include <OMX_Audio.h>

#ifdef RASPBERRY_PI
#include <bcm_host.h>
#endif

OMX_ERRORTYPE err;
OMX_HANDLETYPE handle;
OMX_VERSIONTYPE specVersion, compVersion;

OMX_CALLBACKTYPE callbacks;

#define indent {int n = 0; while (n++ < indentLevel*2) putchar(' ');}

static void setHeader(OMX_PTR header, OMX_U32 size) {
    /* header->nVersion */
    OMX_VERSIONTYPE* ver = (OMX_VERSIONTYPE*)(header + sizeof(OMX_U32));
    /* header->nSize */
    *((OMX_U32*)header) = size;

    /* for 1.2
       ver->s.nVersionMajor = OMX_VERSION_MAJOR;
       ver->s.nVersionMinor = OMX_VERSION_MINOR;
       ver->s.nRevision = OMX_VERSION_REVISION;
       ver->s.nStep = OMX_VERSION_STEP;
    */
    ver->s.nVersionMajor = specVersion.s.nVersionMajor;
    ver->s.nVersionMinor = specVersion.s.nVersionMinor;
    ver->s.nRevision = specVersion.s.nRevision;
    ver->s.nStep = specVersion.s.nStep;
}

void printState() {
    OMX_STATETYPE state;
    err = OMX_GetState(handle, &state);
    if (err != OMX_ErrorNone) {
	fprintf(stderr, "Error on getting state\n");
	exit(1);
    }
    switch (state) {
    case OMX_StateLoaded: fprintf(stderr, "StateLoaded\n"); break;
    case OMX_StateIdle: fprintf(stderr, "StateIdle\n"); break;
    case OMX_StateExecuting: fprintf(stderr, "StateExecuting\n"); break;
    case OMX_StatePause: fprintf(stderr, "StatePause\n"); break;
    case OMX_StateWaitForResources: fprintf(stderr, "StateWiat\n"); break;
    default:  fprintf(stderr, "State unknown\n"); break;
    }
}

OMX_ERRORTYPE setEncoding(int portNumber, OMX_AUDIO_CODINGTYPE encoding) {
    OMX_PARAM_PORTDEFINITIONTYPE sPortDef;

    setHeader(&sPortDef, sizeof(OMX_PARAM_PORTDEFINITIONTYPE));
    sPortDef.nPortIndex = portNumber;
    sPortDef.nPortIndex = portNumber;
    err = OMX_GetParameter(handle, OMX_IndexParamPortDefinition, &sPortDef);
    if(err != OMX_ErrorNone){
        fprintf(stderr, "Error in getting OMX_PORT_DEFINITION_TYPE parameter\n",
 0);
        exit(1);
    }

    sPortDef.format.audio.eEncoding = encoding;
    sPortDef.nBufferCountActual = sPortDef.nBufferCountMin;

    err = OMX_SetParameter(handle, OMX_IndexParamPortDefinition, &sPortDef);
    return err;
}

void getPCMInformation(int indentLevel, int portNumber) {
    /* assert: PCM is a supported mode */
    OMX_AUDIO_PARAM_PCMMODETYPE sPCMMode;

    /* set it into PCM format before asking for PCM info */
    if (setEncoding(portNumber, OMX_AUDIO_CodingPCM) != OMX_ErrorNone) {
	fprintf(stderr, "Error in setting coding to PCM\n");
	return;
    }
       
    setHeader(&sPCMMode, sizeof(OMX_AUDIO_PARAM_PCMMODETYPE));
    sPCMMode.nPortIndex = portNumber;
    err = OMX_GetParameter(handle, OMX_IndexParamAudioPcm, &sPCMMode);
    if(err != OMX_ErrorNone){
	indent printf("PCM mode unsupported\n");
    } else {
	indent printf("  PCM default sampling rate %d\n", sPCMMode.nSamplingRate);
	indent printf("  PCM default bits per sample %d\n", sPCMMode.nBitPerSample);
	indent printf("  PCM default number of channels %d\n", sPCMMode.nChannels);
    }      

    /*
    setHeader(&sAudioPortFormat, sizeof(OMX_AUDIO_PARAM_PORTFORMATTYPE));
    sAudioPortFormat.nIndex = 0;
    sAudioPortFormat.nPortIndex = portNumber;
    */

    
}
void getMP3Information(int indentLevel, int portNumber) {
    /* assert: MP3 is a supported mode */
    OMX_AUDIO_PARAM_MP3TYPE sMP3Mode;

    /* set it into MP3 format before asking for MP3 info */
    if (setEncoding(portNumber, OMX_AUDIO_CodingMP3) != OMX_ErrorNone) {
	fprintf(stderr, "Error in setting coding to MP3\n");
	return;
    }
    
    setHeader(&sMP3Mode, sizeof(OMX_AUDIO_PARAM_MP3TYPE));
    sMP3Mode.nPortIndex = portNumber;
    err = OMX_GetParameter(handle, OMX_IndexParamAudioMp3, &sMP3Mode);
    if(err != OMX_ErrorNone){
	indent printf("MP3 mode unsupported\n");
    } else {
	indent printf("  MP3 default sampling rate %d\n", sMP3Mode.nSampleRate);
	indent printf("  MP3 default bits per sample %d\n", sMP3Mode.nBitRate);
	indent printf("  MP3 default number of channels %d\n", sMP3Mode.nChannels);
    }   
}


void getSupportedAudioFormats(int indentLevel, int portNumber) {
    OMX_AUDIO_PARAM_PORTFORMATTYPE sAudioPortFormat;

    setHeader(&sAudioPortFormat, sizeof(OMX_AUDIO_PARAM_PORTFORMATTYPE));
    sAudioPortFormat.nIndex = 0;
    sAudioPortFormat.nPortIndex = portNumber;

#ifdef LIM
    printf("LIM doesn't set audio formats properly\n");
    return;
#endif

    indent printf("Supported audio formats are:\n");
    for(;;) {
        err = OMX_GetParameter(handle, OMX_IndexParamAudioPortFormat, &sAudioPortFormat);
        if (err == OMX_ErrorNoMore) {
	    indent printf("No more formats supported\n");
	    return;
        }

	/* This shouldn't occur, but does with Broadcom library */
	if (sAudioPortFormat.eEncoding == OMX_AUDIO_CodingUnused) {
	     indent printf("No coding format returned\n");
	     return;
	}

	switch (sAudioPortFormat.eEncoding) {
	case OMX_AUDIO_CodingPCM:
	    indent printf("Supported encoding is PCM\n");
	    getPCMInformation(indentLevel+1, portNumber);
	    break; 
	case OMX_AUDIO_CodingVORBIS:
	    indent printf("Supported encoding is Ogg Vorbis\n");
	    break; 
	case OMX_AUDIO_CodingMP3:
	    indent printf("Supported encoding is MP3\n");
	    getMP3Information(indentLevel+1, portNumber);
	    break;
#ifdef RASPBERRY_PI
	case OMX_AUDIO_CodingFLAC:
	    indent printf("Supported encoding is FLAC\n");
	    break; 
	case OMX_AUDIO_CodingDDP:
	    indent printf("Supported encoding is DDP\n");
	    break; 
	case OMX_AUDIO_CodingDTS:
	    indent printf("Supported encoding is DTS\n");
	    break; 
	case OMX_AUDIO_CodingWMAPRO:
	    indent printf("Supported encoding is WMAPRO\n");
	    break; 
	case OMX_AUDIO_CodingATRAC3:
	    indent printf("Supported encoding is ATRAC3\n");
	    break;
	case OMX_AUDIO_CodingATRACX:
	    indent printf("Supported encoding is ATRACX\n");
	    break;
	case OMX_AUDIO_CodingATRACAAL:
	    indent printf("Supported encoding is ATRACAAL\n");
	    break;
#endif
	case OMX_AUDIO_CodingAAC:
	    indent printf("Supported encoding is AAC\n");
	    break; 
	case OMX_AUDIO_CodingWMA:
	    indent printf("Supported encoding is WMA\n");
	    break;
	case OMX_AUDIO_CodingRA:
	    indent printf("Supported encoding is RA\n");
	    break; 
	case OMX_AUDIO_CodingAMR:
	    indent printf("Supported encoding is AMR\n");
	    break; 
	case OMX_AUDIO_CodingEVRC:
	    indent printf("Supported encoding is EVRC\n");
	    break;
	case OMX_AUDIO_CodingG726:
	    indent printf("Supported encoding is G726\n");
	    break;
	case OMX_AUDIO_CodingMIDI:
	    indent printf("Supported encoding is MIDI\n");
	    break;

	    /*
	case OMX_AUDIO_Coding:
	    indent printf("Supported encoding is \n");
	    break;
	    */
	default:
	    indent printf("Supported encoding is not PCM or MP3 or Vorbis, is 0x%X\n",
		  sAudioPortFormat.eEncoding);
	}
        sAudioPortFormat.nIndex++;
    }
}



void getAudioPortInformation(int indentLevel, int nPort, OMX_PARAM_PORTDEFINITIONTYPE sPortDef) {
    indent printf("Port %d requires %d buffers\n", nPort, sPortDef.nBufferCountMin); 
    indent printf("Port %d has min buffer size %d bytes\n", nPort, sPortDef.nBufferSize); 
    
    if (sPortDef.eDir == OMX_DirInput) {
	indent printf("Port %d is an input port\n", nPort);
    } else {
	indent printf("Port %d is an output port\n",  nPort);
    }
    switch (sPortDef.eDomain) {
    case OMX_PortDomainAudio:
	indent printf("Port %d is an audio port\n", nPort);
	indent printf("Port mimetype %s\n",
	       sPortDef.format.audio.cMIMEType);

	switch (sPortDef.format.audio.eEncoding) {
	case OMX_AUDIO_CodingPCM:
	    indent printf("Port encoding is PCM\n");
	    break; 
	case OMX_AUDIO_CodingVORBIS:
	    indent printf("Port encoding is Ogg Vorbis\n");
	    break; 
	case OMX_AUDIO_CodingMP3:
	    indent printf("Port encoding is MP3\n");
	    break; 
	default:
	    indent printf("Port encoding is not PCM or MP3 or Vorbis, is %d\n",
		   sPortDef.format.audio.eEncoding);
	}
	getSupportedAudioFormats(indentLevel+1, nPort);

	break;
	/* could put other port types here */
    default:
	indent printf("Port %d is not an audio port\n",  nPort);
    }    
}

void getAllAudioPortsInformation(int indentLevel) {
    OMX_PORT_PARAM_TYPE param;
    OMX_PARAM_PORTDEFINITIONTYPE sPortDef;

    int startPortNumber;
    int nPorts;
    int n;

    setHeader(&param, sizeof(OMX_PORT_PARAM_TYPE));

    err = OMX_GetParameter(handle, OMX_IndexParamAudioInit, &param);
    if(err != OMX_ErrorNone){
	fprintf(stderr, "Error in getting audio OMX_PORT_PARAM_TYPE parameter\n", 0);
	return;
    }
    indent printf("Audio ports:\n");
    indentLevel++;

    startPortNumber = param.nStartPortNumber;
    nPorts = param.nPorts;
    if (nPorts == 0) {
	indent printf("No ports of this type\n");
	return;
    }

    indent printf("Ports start on %d\n", startPortNumber);
    indent printf("There are %d open ports\n", nPorts);

    for (n = 0; n < nPorts; n++) {
	setHeader(&sPortDef, sizeof(OMX_PARAM_PORTDEFINITIONTYPE));
	sPortDef.nPortIndex = startPortNumber + n;
	err = OMX_GetParameter(handle, OMX_IndexParamPortDefinition, &sPortDef);
	if(err != OMX_ErrorNone){
	    fprintf(stderr, "Error in getting OMX_PORT_DEFINITION_TYPE parameter\n", 0);
	    exit(1);
	}
	getAudioPortInformation(indentLevel+1, startPortNumber + n, sPortDef);
    }
}

void getAllVideoPortsInformation(int indentLevel) {
    OMX_PORT_PARAM_TYPE param;
    int startPortNumber;
    int nPorts;
    int n;

    setHeader(&param, sizeof(OMX_PORT_PARAM_TYPE));

    err = OMX_GetParameter(handle, OMX_IndexParamVideoInit, &param);
    if(err != OMX_ErrorNone){
	fprintf(stderr, "Error in getting video OMX_PORT_PARAM_TYPE parameter\n", 0);
	return;
    }
    printf("Video ports:\n");
    indentLevel++;

    startPortNumber = param.nStartPortNumber;
    nPorts = param.nPorts;
    if (nPorts == 0) {
	indent printf("No ports of this type\n");
	return;
    }

    indent printf("Ports start on %d\n", startPortNumber);
    indent printf("There are %d open ports\n", nPorts);
}

void getAllImagePortsInformation(int indentLevel) {
    OMX_PORT_PARAM_TYPE param;
    int startPortNumber;
    int nPorts;
    int n;

    setHeader(&param, sizeof(OMX_PORT_PARAM_TYPE));

    err = OMX_GetParameter(handle, OMX_IndexParamVideoInit, &param);
    if(err != OMX_ErrorNone){
	fprintf(stderr, "Error in getting image OMX_PORT_PARAM_TYPE parameter\n", 0);
	return;
    }
    printf("Image ports:\n");
    indentLevel++;

    startPortNumber = param.nStartPortNumber;
    nPorts = param.nPorts;
    if (nPorts == 0) {
	indent printf("No ports of this type\n");
	return;
    }

    indent printf("Ports start on %d\n", startPortNumber);
    indent printf("There are %d open ports\n", nPorts);
}

void getAllOtherPortsInformation(int indentLevel) {
    OMX_PORT_PARAM_TYPE param;
    int startPortNumber;
    int nPorts;
    int n;

    setHeader(&param, sizeof(OMX_PORT_PARAM_TYPE));

    err = OMX_GetParameter(handle, OMX_IndexParamVideoInit, &param);
    if(err != OMX_ErrorNone){
	fprintf(stderr, "Error in getting other OMX_PORT_PARAM_TYPE parameter\n", 0);
	exit(1);
    }
    printf("Other ports:\n");
    indentLevel++;

    startPortNumber = param.nStartPortNumber;
    nPorts = param.nPorts;
    if (nPorts == 0) {
	indent printf("No ports of this type\n");
	return;
    }

    indent printf("Ports start on %d\n", startPortNumber);
    indent printf("There are %d open ports\n", nPorts);
}

int main(int argc, char** argv) {

    OMX_PORT_PARAM_TYPE param;
    OMX_PARAM_PORTDEFINITIONTYPE sPortDef;
    OMX_AUDIO_PORTDEFINITIONTYPE sAudioPortDef;
    OMX_AUDIO_PARAM_PORTFORMATTYPE sAudioPortFormat;
    OMX_AUDIO_PARAM_PCMMODETYPE sPCMMode;

#ifdef RASPBERRY_PI
    char *componentName = "OMX.broadcom.audio_mixer";
#endif
#ifdef LIM
    char *componentName = "OMX.limoi.alsa_sink";
#else
    char *componentName = "OMX.st.volume.component";
#endif
    unsigned char name[128]; /* spec says 128 is max name length */
    OMX_UUIDTYPE uid;
    int startPortNumber;
    int nPorts;
    int n;

    /* ovveride component name by command line argument */
    if (argc == 2) {
	componentName = argv[1];
    }

# ifdef RASPBERRY_PI
    bcm_host_init();
# endif

    err = OMX_Init();
    if(err != OMX_ErrorNone) {
	fprintf(stderr, "OMX_Init() failed\n", 0);
	exit(1);
    }
    /** Ask the core for a handle to the volume control component
     */
    err = OMX_GetHandle(&handle, componentName, NULL /*app private data */, &callbacks);
    if (err != OMX_ErrorNone) {
	fprintf(stderr, "OMX_GetHandle failed\n", 0);
	exit(1);
    }
    err = OMX_GetComponentVersion(handle, name, &compVersion, &specVersion, &uid);
    if (err != OMX_ErrorNone) {
	fprintf(stderr, "OMX_GetComponentVersion failed\n", 0);
	exit(1);
    }
    printf("Component name: %s version %d.%d, Spec version %d.%d\n",
	   name, compVersion.s.nVersionMajor,
	   compVersion.s.nVersionMinor,
	   specVersion.s.nVersionMajor,
	   specVersion.s.nVersionMinor);

    /** Get  ports information */
    getAllAudioPortsInformation(0);
    getAllVideoPortsInformation(0);
    getAllImagePortsInformation(0);
    getAllOtherPortsInformation(0);

    exit(0);
}
```


The Makefile for the Bellagio version is

```cpp
INCLUDES=-I ../libomxil-bellagio-0.9.3/include/
LIBS=-L ../libomxil-bellagio-0.9.3/src/.libs -l omxil-bellagio
CFLAGS = -g

info: info.c
        cc $(FLAGS) $(INCLUDES) -o info info.c $(LIBS)
```


The output using the Bellagio implementation is

```
Component name: OMX.st.volume.component version 1.1, Spec version 1.1
Audio ports:
  Ports start on 0
  There are 2 open ports
    Port 0 requires 2 buffers
    Port 0 is an input port
    Port 0 is an audio port
    Port mimetype raw/audio
    Port encoding is not PCM or MP3 or Vorbis, is 0
      Supported audio formats are:
      No coding format returned
    Port 1 requires 2 buffers
    Port 1 is an output port
    Port 1 is an audio port
    Port mimetype raw/audio
    Port encoding is not PCM or MP3 or Vorbis, is 0
      Supported audio formats are:
      No coding format returned
Video ports:
  No ports of this type
Image ports:
  No ports of this type
Other ports:
  No ports of this type
```


The Makefile for the Raspberry Pi is

```cpp
INCLUDES=-I /opt/vc/include/IL -I /opt/vc/include -I /opt/vc/include/interface/vcos/pthreads
CFLAGS=-g -DRASPBERRY_PI
LIBS=-L /opt/vc/lib -l openmaxil -l bcm_host

info: info.c
	cc $(CFLAGS) $(INCLUDES) -o info info.c $(LIBS)
```


The output on the Raspberry Pi for the audio_render component is

```
Audio ports:
  Ports start on 100
  There are 1 open ports
    Port 100 requires 1 buffers
    Port 100 is an input port
    Port 100 is an audio port
    Port mimetype (null)
    Port encoding is PCM
      Supported audio formats are:
      Supported encoding is PCM
          PCM default sampling rate 44100
          PCM default bits per sample 16
          PCM default number of channels 2
      Supported encoding is DDP
      No more formats supported
Video ports:
  No ports of this type
Image ports:
  No ports of this type
Other ports:
  No ports of this type
```


The Makefile for LIM is

```cpp
INCLUDES=-I ../../lim-omx-1.1/LIM/limoi-core/include/
#LIBS=-L ../../lim-omx-1.1/LIM/limoi-base/src/.libs -l limoi-base
LIBS = -L /home/newmarch/osm-build/lib/ -l limoa -l limoi-core
CFLAGS = -g -DLIM

info: info.c
	cc $(CFLAGS) $(INCLUDES) -o info info.c $(LIBS)
```


The output on LIM for the alsa_sink component is

```
Component name: OMX.limoi.alsa_sink version 0.0, Spec version 1.1
Audio ports:
  Ports start on 0
  There are 1 open ports
    Port 0 requires 2 buffers
    Port 0 is an input port
    Port 0 is an audio port
    Port mimetype (null)
    Port encoding is PCM
LIM doesn't set audio formats properly
Error in getting video OMX_PORT_PARAM_TYPE parameter
Error in getting image OMX_PORT_PARAM_TYPE parameter
Error in getting other OMX_PORT_PARAM_TYPE parameter
```


The LIM implementation throws errors when the component does not support
a mode (here an audio component does not support video, image or other).
This is against the 1.1 specification which says

```
"All standard components shall support the following parameters:
  o OMX_IndexParamPortDefinition
  o OMX_IndexParamCompBufferSupplier
  o OMX_IndexParamAudioInit
  o OMX_IndexParamImageInit
  o OMX_IndexParamVideoInit
  o OMX_IndexParamOtherInit"
```


I suppose you could argue that an `alsa_sink`component isn't
a standard one, so it is allowed. Well, okay...

###  Playing PCM audio files 


Playing audio to an output device requires use of an "audio_render"
device. This is one of the standard devices in the 1.1 specification,
and is included in the Broadcom Raspberry Pi library but not in the
Bellagio library.
LIM has a component "alsa_sink" which plays the same role.


The structure of a program to play audio is

+ initialise the library and audio render component
+ Continually fill input buffers and ask the component
to empty the buffers
+ Capture events from the component saying that a buffer
has been emptied in order to schedule re-filling
the buffer and requesting it to be emptied
+ Clean up on completion

Note that the Raspberry Pi audio render component will _only_ play PCM data
and that the LIM alsa_sink component only plays back at 44,100hz.

####  State 


Initialising the component is a multi-step process that depends on
the state of the component. Components are created in the `Loaded`state. They transition from one state to another
through an `OMX_SendCommand(handle, OMX_CommandStateSet, <next state>, <param>)`.
The next state from `Loaded`should be `Idle`and from there to `Executing`.  There are other states
which we need not be concerned about.


Requests to change state are asynchronous. The send command returns
immediately (well, within 5 milliseconds). When the actual change
of state occurs an event handler callback function is called.

####  Threads 


Some commands require a component to be in a particular state.
Requests to put a component into a state are asynchronous.
So a request can be made by a client but then the client might
have to wait until the state change has occurred. This is best done
by the client suspending operation of its thread until woken
up by the state change occurring in the event handler.





Linux/Unix has standardised on the Posix pthreads library for
managing multiple threads. For our purposes we use two parts
from this library: the ability to place a _mutex_ around critical sections, and the ability to suspend/wake up
threads based on _conditions_ .
Pthreads are covered in many places, with a short and good
tutorial by Blaise Barney at [POSIX Threads Programming](https://computing.llnl.gov/tutorials/pthreads/#Misc) .


The functions and data we use are

```cpp
pthread_mutex_t mutex;
OMX_STATETYPE currentState = OMX_StateLoaded;
pthread_cond_t stateCond;

void waitFor(OMX_STATETYPE state) {
    pthread_mutex_lock(&mutex);
    while (currentState != state)
	pthread_cond_wait(&stateCond, &mutex);
    fprintf(stderr, "Wait successfully completed\n");
    pthread_mutex_unlock(&mutex);
}

void wakeUp(OMX_STATETYPE newState) {
    pthread_mutex_lock(&mutex);
    currentState = newState;
    pthread_cond_signal(&stateCond);
    pthread_mutex_unlock(&mutex);
}
pthread_mutex_t empty_mutex;
int emptyState = 0;
OMX_BUFFERHEADERTYPE* pEmptyBuffer;
pthread_cond_t emptyStateCond;

void waitForEmpty() {
    pthread_mutex_lock(&empty_mutex);
    while (emptyState == 1)
	pthread_cond_wait(&emptyStateCond, &empty_mutex);
    emptyState = 1;
    pthread_mutex_unlock(&empty_mutex);
}

void wakeUpEmpty(OMX_BUFFERHEADERTYPE* pBuffer) {
    pthread_mutex_lock(&empty_mutex);
    emptyState = 0;
    pEmptyBuffer = pBuffer;
    pthread_cond_signal(&emptyStateCond);
    pthread_mutex_unlock(&empty_mutex);
}

void mutex_init() {
    int n = pthread_mutex_init(&mutex, NULL);
    if ( n != 0) {
	fprintf(stderr, "Can't init state mutex\n");
    }
    n = pthread_mutex_init(&empty_mutex, NULL);
    if ( n != 0) {
	fprintf(stderr, "Can't init empty mutex\n");
    }
}
```

####  Hungarian notation 


Hungarian notation was invented by Charles Simonyi to add
type or functional information to variable, structure and field
names. A form was heavily used in the Microsoft Windows SDK.
A simplified form is used in OpenMAX IL by prefixing variables,
fields, etc including the following:

+ 'n' prefixes a number of some kind
+ 'p' prefixes a pointer
+ 's' prefixes a structure or a string
+ 'c' prefixes a callback function

The value of such conventions is highly [debatable...](http://en.wikipedia.org/wiki/Hungarian_notation) 

####  Callbacks 


There are two types of callback functions relevant to this example:
event callbacks which occur on changes of state and some other events,
and empty buffer callbacks which occur when a component has emptied an input
buffer. These are registered by

```cpp
OMX_CALLBACKTYPE callbacks  = { .EventHandler = cEventHandler,
                                .EmptyBufferDone = cEmptyBufferDone,
};
err = OMX_GetHandle(&handle, componentName, NULL /*app private data */, &callbacks);
```

####  Component resources 


Each component has a number of ports that have to be configured.
The ports are some of the component's _resources_ .
Each port starts off as _enabled_ , but may be set to _disabled_ by `OMX_SendCommand(handle, OMX_CommandPortDisable, <port number>, NULL)`.


Enabled ports can have _buffers_ allocated for transfer of data
into and out of the component. This can be done in two ways: `OMX_AllocateBuffer`asks the component to perform the
allocation for the client, while with `OMX_UseBuffer`the client hands a buffer to the component. As there may be buffer
memory alignment issues, I prefer to let the component do the allocation.


Here is a tricky part. In order to allocate or use buffers on a component,
a request must be made to transition from `Loaded`state
to `Idle`. So a call to `OMX_SendCommand(handle, OMX_CommandStateSet, OMX_StateIdle, <param>)`.
must be made before buffers are allocated. _But_ the transition
to `Idle`will not take place
until each port is either disabled or all buffers
for it are allocated.


This last step cost me nearly a week of head scratching.
The `audio_render`component has two ports: an input audio
port and a time update port. While I had configured the audio port
correctly, I had not disabled the time port because I hadn't realised it had one.
Consequently the transition to `Idle`never took place... Code to handle this
is

```cpp
setHeader(&param, sizeof(OMX_PORT_PARAM_TYPE));
    err = OMX_GetParameter(handle, OMX_IndexParamOtherInit, &param);
    if(err != OMX_ErrorNone){
	fprintf(stderr, "Error in getting OMX_PORT_PARAM_TYPE parameter\n", 0);
	exit(1);
    }
    startPortNumber = ((OMX_PORT_PARAM_TYPE)param).nStartPortNumber;
    nPorts = ((OMX_PORT_PARAM_TYPE)param).nPorts;
    printf("Other has %d ports\n", nPorts);
    /* and disable it */
    err = OMX_SendCommand(handle, OMX_CommandPortDisable, startPortNumber, NULL);
    if (err != OMX_ErrorNone) {
	fprintf(stderr, "Error on setting port to disabled\n");
	exit(1);
    }
```


Setting parameters for the audio port is

```cpp
/** Get audio port information */
    setHeader(&param, sizeof(OMX_PORT_PARAM_TYPE));
    err = OMX_GetParameter(handle, OMX_IndexParamAudioInit, &param);
    if(err != OMX_ErrorNone){
	fprintf(stderr, "Error in getting OMX_PORT_PARAM_TYPE parameter\n", 0);
	exit(1);
    }
    startPortNumber = ((OMX_PORT_PARAM_TYPE)param).nStartPortNumber;
    nPorts = ((OMX_PORT_PARAM_TYPE)param).nPorts;
    if (nPorts > 1) {
	fprintf(stderr, "Render device has more than one port\n");
	exit(1);
    }

    setHeader(&sPortDef, sizeof(OMX_PARAM_PORTDEFINITIONTYPE));
    sPortDef.nPortIndex = startPortNumber;
    err = OMX_GetParameter(handle, OMX_IndexParamPortDefinition, &sPortDef);
    if(err != OMX_ErrorNone){
	fprintf(stderr, "Error in getting OMX_PORT_DEFINITION_TYPE parameter\n", 0);
	exit(1);
    }
    if (sPortDef.eDomain != OMX_PortDomainAudio) {
	fprintf(stderr, "Port %d is not an audio port\n", startPortNumber);
	exit(1);
    } 
      
    if (sPortDef.eDir != OMX_DirInput) {
	fprintf(stderr, "Port is not an input port\n");
	exit(1);
    }
    if (sPortDef.format.audio.eEncoding == OMX_AUDIO_CodingPCM) {
	printf("Port encoding is PCM\n"); 
    }    else {
	printf("Port has unknown encoding\n");
    }

    /* create minimum number of buffers for the port */
    nBuffers = sPortDef.nBufferCountActual = sPortDef.nBufferCountMin;
    printf("Number of bufers is %d\n", nBuffers);
    err = OMX_SetParameter(handle, OMX_IndexParamPortDefinition, &sPortDef);
    if(err != OMX_ErrorNone){
	fprintf(stderr, "Error in setting OMX_PORT_PARAM_TYPE parameter\n", 0);
	exit(1);
    }

    /* call to put state into idle before allocating buffers */
    err = OMX_SendCommand(handle, OMX_CommandStateSet, OMX_StateIdle, NULL);
    if (err != OMX_ErrorNone) {
	fprintf(stderr, "Error on setting state to idle\n");
	exit(1);
    }

    err = OMX_SendCommand(handle, OMX_CommandPortEnable, startPortNumber, NULL);
    if (err != OMX_ErrorNone) {
	fprintf(stderr, "Error on setting port to enabled\n");
	exit(1);
    }

    nBufferSize = sPortDef.nBufferSize;
    printf("%d buffers of size is %d\n", nBuffers, nBufferSize);

    inBuffers = malloc(nBuffers * sizeof(OMX_BUFFERHEADERTYPE *));
    if (inBuffers == NULL) {
	fprintf(stderr, "Can't allocate buffers\n");
	exit(1);
    }
    for (n = 0; n < nBuffers; n++) {
        err = OMX_AllocateBuffer(handle, inBuffers+n, startPortNumber, NULL,
                                 nBufferSize);
	if (err != OMX_ErrorNone) {
	    fprintf(stderr, "Error on AllocateBuffer in 1%i\n", err);
  	    exit(1);
	}

    }

    waitFor(OMX_StateIdle);    
    /* try setting the encoding to PCM mode */
    setHeader(&sPCMMode, sizeof(OMX_AUDIO_PARAM_PCMMODETYPE));
    sPCMMode.nPortIndex = startPortNumber;
    err = OMX_GetParameter(handle, OMX_IndexParamAudioPcm, &sPCMMode);
    if(err != OMX_ErrorNone){
	printf("PCM mode unsupported\n");
	exit(1);
    } else {
	printf("PCM mode supported\n");
	printf("PCM sampling rate %d\n", sPCMMode.nSamplingRate);
	printf("PCM nChannels %d\n", sPCMMode.nChannels);
    }
```

####  Setting the output device 


OpenMAX has a standard audio render component. But what device does it
render to? The inbuilt sound card? A USB sound card? That is not
a part of OpenMAX IL - there isn't even a way to list the audio
devices - only the audio components.


OpenMAX has an extension mechanism which can be used by an OpenMAX
implementor to answer questions like this. The Broadcom core implementation
has extension types `OMX_CONFIG_BRCMAUDIODESTINATIONTYPE`(and `OMX_CONFIG_BRCMAUDIOSOURCETYPE`) which can be used
to set the audio destination (source) device. Code to do this is

```cpp
void setOutputDevice(const char *name) {
   int32_t success = -1;
   OMX_CONFIG_BRCMAUDIODESTINATIONTYPE arDest;

   if (name && strlen(name) < sizeof(arDest.sName)) {
       setHeader(&arDest, sizeof(OMX_CONFIG_BRCMAUDIODESTINATIONTYPE));
       strcpy((char *)arDest.sName, name);
       
       err = OMX_SetParameter(handle, OMX_IndexConfigBrcmAudioDestination, &arDest);
       if (err != OMX_ErrorNone) {
	   fprintf(stderr, "Error on setting audio destination\n");
	   exit(1);
       }
   }
}
```


Here is where it descends into murkiness again: the header file
<IL/OMX_Broadcom.h> states that the default value of `sName`is "local" but doesn't give any other values.
The Raspberry Pi forums say that this refers to the 3.5mm analog
audio out, and that HDMI is chosen by using the value "hdmi".
No other values are documented, and it seems that the Broadcom OpenMAX IL
does not support any other audio devices: in particular, USB audio
devices are not supported by the current Broadcom OpenMAX IL
components for either input or output. So you can't use
OpenMAX IL for say audio capture on the Raspberry Pi since it
has no Broadcom supported audio input.

####  Main loop 


Playing the audio file once all the ports are set up consists of
filling buffers, waiting for them to empty and then re-filling them until
the data is finished. There are two possible styles:

+ fill the buffers once in the main loop and then continue to
fill and empty them in the empty buffer callbacks
+ in the main loop, fill and empty the buffers continually,
waiting between each fill for the buffer to empty

The Bellagio example use the first technique. However, the 1.2 specification says that
"...the IL client shall not
call IL core or component functions from within an IL callback context" so
this is not a good technique. The Raspberry Pi examples use the second technique,
but use a non-standard call to find the latency and delay for that time.
It is better to just set up more pthreads conditions and block on those.


This leads to a main loop of

```cpp
emptyState = 1;
    for (;;) {
	int data_read = read(fd, inBuffers[0]->pBuffer, nBufferSize);
	inBuffers[0]->nFilledLen = data_read;
	inBuffers[0]->nOffset = 0;
	filesize -= data_read;
	if (data_read <= 0) {
	    fprintf(stderr, "In the %s no more input data available\n", __func__);
	    inBuffers[0]->nFilledLen=0;
	    inBuffers[0]->nFlags = OMX_BUFFERFLAG_EOS;
	    bEOS=OMX_TRUE;
	    err = OMX_EmptyThisBuffer(handle, inBuffers[0]);
	    break;
	}
	if(!bEOS) {
	    fprintf(stderr, "Emptying again buffer %p %d bytes, %d to go\n", inBuffers[0], data_read, filesize);
	    err = OMX_EmptyThisBuffer(handle, inBuffers[0]);
	}else {
	    fprintf(stderr, "In %s Dropping Empty This buffer to Audio Dec\n", __func__);
	}
	waitForEmpty();
	printf("Waited for empty\n");
    }

    printf("Buffers emptied\n");
```

####  Complete program 


The complete program is

```cpp
/**
   Based on code
   Copyright (C) 2007-2009 STMicroelectronics
   Copyright (C) 2007-2009 Nokia Corporation and/or its subsidiary(-ies).
   under the LGPL
*/

#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>
#include <sys/stat.h>
#include <pthread.h>

#include <OMX_Core.h>
#include <OMX_Component.h>
#include <OMX_Types.h>
#include <OMX_Audio.h>

#ifdef RASPBERRY_PI
#include <bcm_host.h>
#include <IL/OMX_Broadcom.h>
#endif

OMX_ERRORTYPE err;
OMX_HANDLETYPE handle;
OMX_VERSIONTYPE specVersion, compVersion;

int fd = 0;
unsigned int filesize;
static OMX_BOOL bEOS=OMX_FALSE;

OMX_U32 nBufferSize;
int nBuffers;

pthread_mutex_t mutex;
OMX_STATETYPE currentState = OMX_StateLoaded;
pthread_cond_t stateCond;

void waitFor(OMX_STATETYPE state) {
    pthread_mutex_lock(&mutex);
    while (currentState != state)
	pthread_cond_wait(&stateCond, &mutex);
    pthread_mutex_unlock(&mutex);
}

void wakeUp(OMX_STATETYPE newState) {
    pthread_mutex_lock(&mutex);
    currentState = newState;
    pthread_cond_signal(&stateCond);
    pthread_mutex_unlock(&mutex);
}

pthread_mutex_t empty_mutex;
int emptyState = 0;
OMX_BUFFERHEADERTYPE* pEmptyBuffer;
pthread_cond_t emptyStateCond;

void waitForEmpty() {
    pthread_mutex_lock(&empty_mutex);
    while (emptyState == 1)
	pthread_cond_wait(&emptyStateCond, &empty_mutex);
    emptyState = 1;
    pthread_mutex_unlock(&empty_mutex);
}

void wakeUpEmpty(OMX_BUFFERHEADERTYPE* pBuffer) {
    pthread_mutex_lock(&empty_mutex);
    emptyState = 0;
    pEmptyBuffer = pBuffer;
    pthread_cond_signal(&emptyStateCond);
    pthread_mutex_unlock(&empty_mutex);
}

void mutex_init() {
    int n = pthread_mutex_init(&mutex, NULL);
    if ( n != 0) {
	fprintf(stderr, "Can't init state mutex\n");
    }
    n = pthread_mutex_init(&empty_mutex, NULL);
    if ( n != 0) {
	fprintf(stderr, "Can't init empty mutex\n");
    }
}

static void display_help() {
    fprintf(stderr, "Usage: render input_file");
}


/** Gets the file descriptor's size
 * @return the size of the file. If size cannot be computed
 * (i.e. stdin, zero is returned)
 */
static int getFileSize(int fd) {

    struct stat input_file_stat;
    int err;

    /* Obtain input file length */
    err = fstat(fd, &input_file_stat);
    if(err){
	fprintf(stderr, "fstat failed",0);
	exit(-1);
    }
    return input_file_stat.st_size;
}

OMX_ERRORTYPE cEventHandler(
			    OMX_HANDLETYPE hComponent,
			    OMX_PTR pAppData,
			    OMX_EVENTTYPE eEvent,
			    OMX_U32 Data1,
			    OMX_U32 Data2,
			    OMX_PTR pEventData) {

    fprintf(stderr, "Hi there, I am in the %s callback\n", __func__);
    if(eEvent == OMX_EventCmdComplete) {
	if (Data1 == OMX_CommandStateSet) {
	    fprintf(stderr, "Component State changed in ", 0);
	    switch ((int)Data2) {
	    case OMX_StateInvalid:
		fprintf(stderr, "OMX_StateInvalid\n", 0);
		break;
	    case OMX_StateLoaded:
		fprintf(stderr, "OMX_StateLoaded\n", 0);
		break;
	    case OMX_StateIdle:
		fprintf(stderr, "OMX_StateIdle\n",0);
		break;
	    case OMX_StateExecuting:
		fprintf(stderr, "OMX_StateExecuting\n",0);
		break;
	    case OMX_StatePause:
		fprintf(stderr, "OMX_StatePause\n",0);
		break;
	    case OMX_StateWaitForResources:
		fprintf(stderr, "OMX_StateWaitForResources\n",0);
		break;
	    }
	    wakeUp((int) Data2);
	} else  if (Data1 == OMX_CommandPortEnable){
     
	} else if (Data1 == OMX_CommandPortDisable){
     
	}
    } else if(eEvent == OMX_EventBufferFlag) {
	if((int)Data2 == OMX_BUFFERFLAG_EOS) {
     
	}
    } else {
	fprintf(stderr, "Param1 is %i\n", (int)Data1);
	fprintf(stderr, "Param2 is %i\n", (int)Data2);
    }

    return OMX_ErrorNone;
}

OMX_ERRORTYPE cEmptyBufferDone(
			       OMX_HANDLETYPE hComponent,
			       OMX_PTR pAppData,
			       OMX_BUFFERHEADERTYPE* pBuffer) {

    fprintf(stderr, "Hi there, I am in the %s callback.\n", __func__);
    if (bEOS) {
	fprintf(stderr, "Buffers emptied, exiting\n");
    }
    wakeUpEmpty(pBuffer);
    fprintf(stderr, "Exiting callback\n");

    return OMX_ErrorNone;
}

OMX_CALLBACKTYPE callbacks  = { .EventHandler = cEventHandler,
				.EmptyBufferDone = cEmptyBufferDone,
};

void printState() {
    OMX_STATETYPE state;
    err = OMX_GetState(handle, &state);
    if (err != OMX_ErrorNone) {
	fprintf(stderr, "Error on getting state\n");
	exit(1);
    }
    switch (state) {
    case OMX_StateLoaded: fprintf(stderr, "StateLoaded\n"); break;
    case OMX_StateIdle: fprintf(stderr, "StateIdle\n"); break;
    case OMX_StateExecuting: fprintf(stderr, "StateExecuting\n"); break;
    case OMX_StatePause: fprintf(stderr, "StatePause\n"); break;
    case OMX_StateWaitForResources: fprintf(stderr, "StateWiat\n"); break;
    default:  fprintf(stderr, "State unknown\n"); break;
    }
}


static void setHeader(OMX_PTR header, OMX_U32 size) {
    /* header->nVersion */
    OMX_VERSIONTYPE* ver = (OMX_VERSIONTYPE*)(header + sizeof(OMX_U32));
    /* header->nSize */
    *((OMX_U32*)header) = size;

    /* for 1.2
       ver->s.nVersionMajor = OMX_VERSION_MAJOR;
       ver->s.nVersionMinor = OMX_VERSION_MINOR;
       ver->s.nRevision = OMX_VERSION_REVISION;
       ver->s.nStep = OMX_VERSION_STEP;
    */
    ver->s.nVersionMajor = specVersion.s.nVersionMajor;
    ver->s.nVersionMinor = specVersion.s.nVersionMinor;
    ver->s.nRevision = specVersion.s.nRevision;
    ver->s.nStep = specVersion.s.nStep;
}

/**
 * Disable unwanted ports, or we can't transition to Idle state
 */
void disablePort(OMX_INDEXTYPE paramType) {
    OMX_PORT_PARAM_TYPE param;
    int nPorts;
    int startPortNumber;
    int n;

    setHeader(&param, sizeof(OMX_PORT_PARAM_TYPE));
    err = OMX_GetParameter(handle, paramType, &param);
    if(err != OMX_ErrorNone){
	fprintf(stderr, "Error in getting OMX_PORT_PARAM_TYPE parameter\n", 0);
	exit(1);
    }
    startPortNumber = ((OMX_PORT_PARAM_TYPE)param).nStartPortNumber;
    nPorts = ((OMX_PORT_PARAM_TYPE)param).nPorts;
    if (nPorts > 0) {
	fprintf(stderr, "Other has %d ports\n", nPorts);
	/* and disable it */
	for (n = 0; n < nPorts; n++) {
	    err = OMX_SendCommand(handle, OMX_CommandPortDisable, n + startPortNumber, NULL);
	    if (err != OMX_ErrorNone) {
		fprintf(stderr, "Error on setting port to disabled\n");
		exit(1);
	    }
	}
    }
}

#ifdef RASPBERRY_PI
/* For the RPi name can be "hdmi" or "local" */
void setOutputDevice(const char *name) {
   int32_t success = -1;
   OMX_CONFIG_BRCMAUDIODESTINATIONTYPE arDest;

   if (name && strlen(name) < sizeof(arDest.sName)) {
       setHeader(&arDest, sizeof(OMX_CONFIG_BRCMAUDIODESTINATIONTYPE));
       strcpy((char *)arDest.sName, name);
       
       err = OMX_SetParameter(handle, OMX_IndexConfigBrcmAudioDestination, &arDest);
       if (err != OMX_ErrorNone) {
	   fprintf(stderr, "Error on setting audio destination\n");
	   exit(1);
       }
   }
}
#endif

void setPCMMode(int startPortNumber) {
    OMX_AUDIO_PARAM_PCMMODETYPE sPCMMode;
 
    setHeader(&sPCMMode, sizeof(OMX_AUDIO_PARAM_PCMMODETYPE));
    sPCMMode.nPortIndex = startPortNumber;
    sPCMMode.nSamplingRate = 48000;
    sPCMMode.nChannels;

    err = OMX_SetParameter(handle, OMX_IndexParamAudioPcm, &sPCMMode);
    if(err != OMX_ErrorNone){
	fprintf(stderr, "PCM mode unsupported\n");
	return;
    } else {
	fprintf(stderr, "PCM mode supported\n");
	fprintf(stderr, "PCM sampling rate %d\n", sPCMMode.nSamplingRate);
	fprintf(stderr, "PCM nChannels %d\n", sPCMMode.nChannels);
    } 
}

int main(int argc, char** argv) {

    OMX_PORT_PARAM_TYPE param;
    OMX_PARAM_PORTDEFINITIONTYPE sPortDef;
    OMX_AUDIO_PORTDEFINITIONTYPE sAudioPortDef;
    OMX_AUDIO_PARAM_PORTFORMATTYPE sAudioPortFormat;
    OMX_AUDIO_PARAM_PCMMODETYPE sPCMMode;
    OMX_BUFFERHEADERTYPE **inBuffers;

#ifdef RASPBERRY_PI
    char *componentName = "OMX.broadcom.audio_render";
#endif
#ifdef LIM
    char *componentName = "OMX.limoi.alsa_sink";
#endif
    unsigned char name[OMX_MAX_STRINGNAME_SIZE];
    OMX_UUIDTYPE uid;
    int startPortNumber;
    int nPorts;
    int n;

# ifdef RASPBERRY_PI
    bcm_host_init();
# endif

    fprintf(stderr, "Thread id is %p\n", pthread_self());
    if(argc < 2){
	display_help();
	exit(1);
    }

    fd = open(argv[1], O_RDONLY);
    if(fd < 0){
	perror("Error opening input file\n");
	exit(1);
    }
    filesize = getFileSize(fd);


    err = OMX_Init();
    if(err != OMX_ErrorNone) {
	fprintf(stderr, "OMX_Init() failed\n", 0);
	exit(1);
    }
    /** Ask the core for a handle to the audio render component
     */
    err = OMX_GetHandle(&handle, componentName, NULL /*app private data */, &callbacks);
    if(err != OMX_ErrorNone) {
	fprintf(stderr, "OMX_GetHandle failed\n", 0);
	exit(1);
    }
    err = OMX_GetComponentVersion(handle, name, &compVersion, &specVersion, &uid);
    if(err != OMX_ErrorNone) {
	fprintf(stderr, "OMX_GetComponentVersion failed\n", 0);
	exit(1);
    }

    /** disable other ports */
    disablePort(OMX_IndexParamOtherInit);

    /** Get audio port information */
    setHeader(&param, sizeof(OMX_PORT_PARAM_TYPE));
    err = OMX_GetParameter(handle, OMX_IndexParamAudioInit, &param);
    if(err != OMX_ErrorNone){
	fprintf(stderr, "Error in getting OMX_PORT_PARAM_TYPE parameter\n", 0);
	exit(1);
    }
    startPortNumber = ((OMX_PORT_PARAM_TYPE)param).nStartPortNumber;
    nPorts = ((OMX_PORT_PARAM_TYPE)param).nPorts;
    if (nPorts > 1) {
	fprintf(stderr, "Render device has more than one port\n");
	exit(1);
    }

    /* Get and check port information */
    setHeader(&sPortDef, sizeof(OMX_PARAM_PORTDEFINITIONTYPE));
    sPortDef.nPortIndex = startPortNumber;
    err = OMX_GetParameter(handle, OMX_IndexParamPortDefinition, &sPortDef);
    if(err != OMX_ErrorNone){
	fprintf(stderr, "Error in getting OMX_PORT_DEFINITION_TYPE parameter\n", 0);
	exit(1);
    }
    if (sPortDef.eDomain != OMX_PortDomainAudio) {
	fprintf(stderr, "Port %d is not an audio port\n", startPortNumber);
	exit(1);
    } 
      
    if (sPortDef.eDir != OMX_DirInput) {
	fprintf(stderr, "Port is not an input port\n");
	exit(1);
    }
    if (sPortDef.format.audio.eEncoding == OMX_AUDIO_CodingPCM) {
	fprintf(stderr, "Port encoding is PCM\n"); 
    }    else {
	fprintf(stderr, "Port has unknown encoding\n");
    }

    /* Create minimum number of buffers for the port */
    nBuffers = sPortDef.nBufferCountActual = sPortDef.nBufferCountMin;
    fprintf(stderr, "Number of bufers is %d\n", nBuffers);
    err = OMX_SetParameter(handle, OMX_IndexParamPortDefinition, &sPortDef);
    if(err != OMX_ErrorNone){
	fprintf(stderr, "Error in setting OMX_PORT_PARAM_TYPE parameter\n", 0);
	exit(1);
    }
    if (sPortDef.bEnabled) {
	fprintf(stderr, "Port is enabled\n");
    } else {
	fprintf(stderr, "Port is not enabled\n");
    }

    /* call to put state into idle before allocating buffers */
    err = OMX_SendCommand(handle, OMX_CommandStateSet, OMX_StateIdle, NULL);
    if (err != OMX_ErrorNone) {
	fprintf(stderr, "Error on setting state to idle\n");
	exit(1);
    }
 
    err = OMX_SendCommand(handle, OMX_CommandPortEnable, startPortNumber, NULL);
    if (err != OMX_ErrorNone) {
	fprintf(stderr, "Error on setting port to enabled\n");
	exit(1);
    }

    /* Configure buffers for the port */
    nBufferSize = sPortDef.nBufferSize;
    fprintf(stderr, "%d buffers of size is %d\n", nBuffers, nBufferSize);

    inBuffers = malloc(nBuffers * sizeof(OMX_BUFFERHEADERTYPE *));
    if (inBuffers == NULL) {
	fprintf(stderr, "Can't allocate buffers\n");
	exit(1);
    }

    for (n = 0; n < nBuffers; n++) {
	err = OMX_AllocateBuffer(handle, inBuffers+n, startPortNumber, NULL,
				 nBufferSize);
	if (err != OMX_ErrorNone) {
	    fprintf(stderr, "Error on AllocateBuffer in 1%i\n", err);
	    exit(1);
	}
    }
    /* Make sure we've reached Idle state */
    waitFor(OMX_StateIdle);
    
    /* Now try to switch to Executing state */
    err = OMX_SendCommand(handle, OMX_CommandStateSet, OMX_StateExecuting, NULL);
    if(err != OMX_ErrorNone){
	exit(1);
    }

    /* One buffer is the minimum for Broadcom component, so use that */
    pEmptyBuffer = inBuffers[0];
    emptyState = 1;
    /* Fill and empty buffer */
    for (;;) {
	int data_read = read(fd, pEmptyBuffer->pBuffer, nBufferSize);
	pEmptyBuffer->nFilledLen = data_read;
	pEmptyBuffer->nOffset = 0;
	filesize -= data_read;
	if (data_read <= 0) {
	    fprintf(stderr, "In the %s no more input data available\n", __func__);
	    pEmptyBuffer->nFilledLen=0;
	    pEmptyBuffer->nFlags = OMX_BUFFERFLAG_EOS;
	    bEOS=OMX_TRUE;
	}
	fprintf(stderr, "Emptying again buffer %p %d bytes, %d to go\n", pEmptyBuffer, data_read, filesize);
	err = OMX_EmptyThisBuffer(handle, pEmptyBuffer);
	waitForEmpty();
	fprintf(stderr, "Waited for empty\n");
	if (bEOS) {
	    fprintf(stderr, "Exiting loop\n");
	    break;
	}
    }
    fprintf(stderr, "Buffers emptied\n");
    exit(0);
}
```
