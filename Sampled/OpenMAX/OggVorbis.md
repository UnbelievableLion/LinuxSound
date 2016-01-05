
##  Ogg Vorbis 


A typical use of an audio system is to play files containing audio data
to some output device. Ogg Vorbis is an open, patent free system that
defines the Vorbis codec to compress raw data into smaller streams,
and the Ogg container format to frame the data and make it easier
for applications to manage.


An "Ogg Vorbis" file is an Ogg container of Vorbis encoded data.
Playing such a file consists of reading the file, extracting the
Vorbis stream from the Ogg frames, decoding the compressed Vorbis
stream into, say, a PCM stream and then handing that to some renderer
that will play the PCM stream on an output device.

###  Decoding an Ogg Vorbis file to a PCM stream 


There are no standard OpenMAX IL components to decode Ogg
frame data. The `audio_decode`component _may_ decode a Vorbis stream, but to use that would first require
extracting the Vorbis stream from the Ogg frames.
We consider how to do that in a later section.


The LIM package has a non-standard component `OMX.limoi.ogg_dec`which plays the role `audio_decoder_with_framing.ogg`.
This can directly manage Ogg frames of Vorbis
data, and decode it into a PCM stream.


The OpenMAX IL specification shows in Figure 2.5 that in
an "in-context" framework where the component runs in
the same thread as the application, then the callback
must complete before a call to OMX_FillThis Buffer or to
OMX_EmptyThisBuffer returns. So the calback should not
make further calls to  OMX_FillThis Buffer or to
OMX_EmptyThisBuffer or it will just build up a long stack
of uncompleted calls. This won't happen if they run in
separate threads, so the calls coud be okay.


The Broadcom, LIM and Bellagio packages all use separate threads,
and all their examples make re-entrant calls. It's easier to write
the code that way. So we follow that, as we don't have any
example packages where such calls should not be made.


With those provisos in mind, the code is fairly straightforward:
when an input buffer is emptied, fill it and empty it again,
and when an output buffer is filled, empty it and fill it again.
The program is `ogg_decode.c`. it reads from an Ogg
Vorbis file and saves in a PCM file.

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


#ifdef LIM
    //char *componentName = "OMX.limoi.ffmpeg.decode.audio";
    char *componentName = "OMX.limoi.ogg_dec";
#endif

OMX_ERRORTYPE err;
OMX_HANDLETYPE handle;
OMX_VERSIONTYPE specVersion, compVersion;

int inFd = 0;
int outFd = 0;
unsigned int filesize;
static OMX_BOOL bEOS=OMX_FALSE;

OMX_U32 inBufferSize;
OMX_U32 outBufferSize;
int numInBuffers;
int numOutBuffers;

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

static void display_help() {
    fprintf(stderr, "Usage: ogg_decode input_file output_file");
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
	fprintf(stderr, "Event is %i\n", (int)eEvent);
	fprintf(stderr, "Param1 is %i\n", (int)Data1);
	fprintf(stderr, "Param2 is %i\n", (int)Data2);
    }

    return OMX_ErrorNone;
}

OMX_ERRORTYPE cEmptyBufferDone(
			       OMX_HANDLETYPE hComponent,
			       OMX_PTR pAppData,
			       OMX_BUFFERHEADERTYPE* pBuffer) {

    printf("Hi there, I am in the %s callback with buffer %p.\n", __func__, pBuffer);
    if (bEOS) {
	printf("Buffers emptied, exiting\n");
	wakeUp(OMX_StateLoaded);
	exit(0);
    }

    int data_read = read(inFd, pBuffer->pBuffer, inBufferSize);
    if (data_read <= 0) {
	bEOS = 1;
    }
    printf("  filled buffer with %d\n", data_read);
    pBuffer->nFilledLen = data_read;
    err = OMX_EmptyThisBuffer(handle, pBuffer);

    return OMX_ErrorNone;
}

OMX_ERRORTYPE cFillBufferDone(
			      OMX_HANDLETYPE hComponent,
			      OMX_PTR pAppData,
			      OMX_BUFFERHEADERTYPE* pBuffer) {

    fprintf(stderr, "Hi there, I am in the %s callback with buffer %pn", __func__, pBuffer);
    if (bEOS) {
	fprintf(stderr, "Buffers filled, exiting\n");
    }
    fprintf(stderr, " writing %d bytes\n",  pBuffer->nFilledLen);
    write(outFd, pBuffer->pBuffer, pBuffer->nFilledLen);
    pBuffer->nFilledLen = 0;
    err = OMX_FillThisBuffer(handle, pBuffer);
    
    return OMX_ErrorNone;
}


OMX_CALLBACKTYPE callbacks  = { .EventHandler = cEventHandler,
				.EmptyBufferDone = cEmptyBufferDone,
				.FillBufferDone = cFillBufferDone
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

void setPCMMode(int portNumber) {
    OMX_AUDIO_PARAM_PCMMODETYPE pcm;
    int num_channels = 2;//1;
    int sample_rate = 0;//44100;
    int bit_depth = 0;//16;

    setHeader(&pcm, sizeof(OMX_AUDIO_PARAM_PCMMODETYPE));
    pcm.nPortIndex = portNumber;

    err = OMX_GetParameter(handle, OMX_IndexParamAudioPcm, &pcm);
    if (err != OMX_ErrorNone) {
	fprintf(stderr, "Error getting PCM mode on port %d\n", portNumber);
	exit(1);
    }

    err = OMX_SetParameter(handle, OMX_IndexParamAudioPcm, &pcm);
    if (err != OMX_ErrorNone) {
	fprintf(stderr, "Error setting PCM mode on port %d\n", portNumber);
	exit(1);
    }
}

void setEncoding(int portNumber, OMX_AUDIO_CODINGTYPE encoding) {
    OMX_AUDIO_PARAM_PORTFORMATTYPE sAudioPortFormat;


    setHeader(&sAudioPortFormat, sizeof(OMX_AUDIO_PARAM_PORTFORMATTYPE));
    sAudioPortFormat.nIndex = 0;
    sAudioPortFormat.nPortIndex = portNumber;

    err = OMX_GetParameter(handle, OMX_IndexParamAudioPortFormat, &sAudioPortFormat);
    if (err == OMX_ErrorNoMore) {
	printf("Can't get format\n");
	return;
    }
    sAudioPortFormat.eEncoding = encoding; //OMX_AUDIO_CodingPcm;
    err = OMX_SetParameter(handle, OMX_IndexParamAudioPortFormat, &sAudioPortFormat);
    if (err == OMX_ErrorNoMore) {
	printf("Can't set format\n");
	return;
    }
    printf("Set format on port %d to PCM\n", portNumber);
}

int setNumBuffers(int portNumber) {
    /* Get and check input port information */
    OMX_PARAM_PORTDEFINITIONTYPE sPortDef;
    int nBuffers;
    
    setHeader(&sPortDef, sizeof(OMX_PARAM_PORTDEFINITIONTYPE));
    sPortDef.nPortIndex = portNumber;
    err = OMX_GetParameter(handle, OMX_IndexParamPortDefinition, &sPortDef);
    if(err != OMX_ErrorNone){
	fprintf(stderr, "Error in getting OMX_PORT_DEFINITION_TYPE parameter\n", 0);
	exit(1);
    }

    /* Create minimum number of buffers for the port */
    nBuffers = sPortDef.nBufferCountActual = sPortDef.nBufferCountMin;
    fprintf(stderr, "Minimum number of buffers is %d\n", nBuffers);
    err = OMX_SetParameter(handle, OMX_IndexParamPortDefinition, &sPortDef);
    if(err != OMX_ErrorNone){
	fprintf(stderr, "Error in setting OMX_PORT_PARAM_TYPE parameter\n", 0);
	exit(1);
    }
    return nBuffers;
}

void createMinBuffers(int portNumber, OMX_U32 *pBufferSize, OMX_BUFFERHEADERTYPE ***pppBuffers) {
    OMX_PARAM_PORTDEFINITIONTYPE sPortDef;
    OMX_BUFFERHEADERTYPE **ppBuffers;
    int n;
    int nBuffers;

    setHeader(&sPortDef, sizeof(OMX_PARAM_PORTDEFINITIONTYPE));
    sPortDef.nPortIndex = portNumber;
    err = OMX_GetParameter(handle, OMX_IndexParamPortDefinition, &sPortDef);
    if(err != OMX_ErrorNone){
	fprintf(stderr, "Error in getting OMX_PORT_DEFINITION_TYPE parameter\n", 0);
	exit(1);
    }

    *pBufferSize = sPortDef.nBufferSize;
    nBuffers = sPortDef.nBufferCountMin;
    fprintf(stderr, "Port %d has %d buffers of size is %d\n", portNumber, nBuffers, *pBufferSize);

    ppBuffers = malloc(nBuffers * sizeof(OMX_BUFFERHEADERTYPE *));
    if (ppBuffers == NULL) {
	fprintf(stderr, "Can't allocate buffers\n");
	exit(1);
    }

    for (n = 0; n < nBuffers; n++) {
	err = OMX_AllocateBuffer(handle, ppBuffers+n, portNumber, NULL,
				 *pBufferSize);
	if (err != OMX_ErrorNone) {
	    fprintf(stderr, "Error on AllocateBuffer is %d\n", err);
	    exit(1);
	}
    }
    *pppBuffers = ppBuffers;
}

int main(int argc, char** argv) {

    OMX_PORT_PARAM_TYPE param;
    OMX_PARAM_PORTDEFINITIONTYPE sPortDef;
    OMX_AUDIO_PORTDEFINITIONTYPE sAudioPortDef;
    OMX_AUDIO_PARAM_PORTFORMATTYPE sAudioPortFormat;
    OMX_AUDIO_PARAM_PCMMODETYPE sPCMMode;
    OMX_BUFFERHEADERTYPE **inBuffers;
    OMX_BUFFERHEADERTYPE **outBuffers;
    OMX_AUDIO_PARAM_MP3TYPE sMP3Mode;


    unsigned char name[OMX_MAX_STRINGNAME_SIZE];
    OMX_UUIDTYPE uid;
    int startPortNumber;
    int nPorts;
    int n;

    fprintf(stderr, "Thread id is %p\n", pthread_self());
    if(argc < 2){
	display_help();
	exit(1);
    }

    inFd = open(argv[1], O_RDONLY);
    if(inFd < 0){
	perror("Error opening input file\n");
	exit(1);
    }
    filesize = getFileSize(inFd);

    outFd = open(argv[2], (O_WRONLY | O_CREAT), 0644);
    if(outFd < 0){
	perror("Error opening output file\n");
	exit(1);
    }

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

    /** no other ports to disable */

    /** Get audio port information */
    setHeader(&param, sizeof(OMX_PORT_PARAM_TYPE));
    err = OMX_GetParameter(handle, OMX_IndexParamAudioInit, &param);
    if(err != OMX_ErrorNone){
	fprintf(stderr, "Error in getting OMX_PORT_PARAM_TYPE parameter\n", 0);
	exit(1);
    }
    startPortNumber = ((OMX_PORT_PARAM_TYPE)param).nStartPortNumber;
    nPorts = ((OMX_PORT_PARAM_TYPE)param).nPorts;
    if (nPorts != 2) {
	fprintf(stderr, "Decode device has wrong number of ports: %d\n", nPorts);
	exit(1);
    }

    setEncoding(startPortNumber, OMX_AUDIO_CodingVORBIS);
    setEncoding(startPortNumber+1, OMX_AUDIO_CodingPCM);

    printState();;
    
    numInBuffers = setNumBuffers(startPortNumber);
    numOutBuffers = setNumBuffers(startPortNumber+1);

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
    err = OMX_SendCommand(handle, OMX_CommandPortEnable, startPortNumber+1, NULL);
    if (err != OMX_ErrorNone) {
	fprintf(stderr, "Error on setting port to enabled\n");
	exit(1);
    }

    createMinBuffers(startPortNumber, &inBufferSize, &inBuffers);
    createMinBuffers(startPortNumber+1, &outBufferSize, &outBuffers);


    /* Make sure we've reached Idle state */
    waitFor(OMX_StateIdle);
    fprintf(stderr, "Reached Idle state\n");
    //exit(0);

    /* Now try to switch to Executing state */
    err = OMX_SendCommand(handle, OMX_CommandStateSet, OMX_StateExecuting, NULL);
    if(err != OMX_ErrorNone){
	exit(1);
    }

    /* no buffers emptied yet */
    pEmptyBuffer = NULL;

    /* fill and empty the input buffers */
    
    for (n = 0; n < numInBuffers; n++) {
    //for (n = 0; n < 2; n++) {
	int data_read = read(inFd, inBuffers[n]->pBuffer, inBufferSize);
	inBuffers[n]->nFilledLen = data_read;
	printf("Read %d into buffer\n", data_read);
	if (data_read <= 0) {
	    printf("In the %s no more input data available\n", __func__);
	    inBuffers[n]->nFilledLen = 0;
	    inBuffers[n]->nFlags = OMX_BUFFERFLAG_EOS;
	    bEOS=OMX_TRUE;
	}
    }
    
    /* empty and fill the output buffers */
    //for (n = 0; n < numOutBuffers; n++) {
    for (n = 0; n < 2; n++) {
	outBuffers[n]->nFilledLen = 0;
	err = OMX_FillThisBuffer(handle, outBuffers[n]);
	if (err != OMX_ErrorNone) {
	    fprintf(stderr, "Error on filling buffer\n");
	    exit(1);
	}
    }

    for (n = 0; n < numInBuffers; n++) {
	//for (n = 0; n < 2; n++) {
	err = OMX_EmptyThisBuffer(handle, inBuffers[n]);
	if (err != OMX_ErrorNone) {
	    fprintf(stderr, "Error on emptying buffer\n");
	    exit(1);
	}
    }


    pEmptyBuffer = inBuffers[0];
    emptyState = 1;

    waitFor(OMX_StateLoaded);
    fprintf(stderr, "Buffers emptied\n");
    exit(0);
}
```

###  Playing an Ogg Vorbis file 


We shall use the LIM components and the LIM OpenMAX IL implementation
to demonstrate this.
There are no appropriate components in the Bellagio or Broadcom cores.


This problem requires the use and interaction
between _two_ components. In this case, it will be the `OMX.limoi.ogg_dec`and the `OMX.limoi.alsa_sink`components.
The `OMX.limoi.ogg_dec`component will take data from an
Ogg Vorbis stream, extract the Vorbis data and decode it to PCM.
The `OMX.limoi.alsa_sink`component can render this PCM
stream to an ALSA output device.


Using the `info`program, we can establish the following
characteristics of each component:

+ __ `OMX.limoi.ogg_dec`__: 
```
Component name: OMX.limoi.ogg_dec version 0.0, Spec version 1.1
Audio ports:
  Ports start on 0
  There are 2 open ports
    Port 0 requires 4 buffers
    Port 0 has min buffer size 4096 bytes
    Port 0 is an input port
    Port 0 is an audio port
    Port mimetype (null)
    Port encoding is Ogg Vorbis
LIM doesn't set audio formats properly
    Port 1 requires 4 buffers
    Port 1 has min buffer size 196608 bytes
    Port 1 is an output port
    Port 1 is an audio port
    Port mimetype (null)
    Port encoding is PCM
LIM doesn't set audio formats properly
Error in getting video OMX_PORT_PARAM_TYPE parameter
Error in getting image OMX_PORT_PARAM_TYPE parameter
Error in getting other OMX_PORT_PARAM_TYPE parameter
```

+ __ `OMX.limoi.alsa_sink`__: 
```
Component name: OMX.limoi.alsa_sink version 0.0, Spec version 1.1
Audio ports:
  Ports start on 0
  There are 1 open ports
    Port 0 requires 2 buffers
    Port 0 has min buffer size 32768 bytes
    Port 0 is an input port
    Port 0 is an audio port
    Port mimetype (null)
    Port encoding is PCM
LIM doesn't set audio formats properly
Error in getting video OMX_PORT_PARAM_TYPE parameter
Error in getting image OMX_PORT_PARAM_TYPE parameter
Error in getting other OMX_PORT_PARAM_TYPE parameter
```


The decoder has a minimum of four input and four output buffers.
The renderer only requires two input buffers, and of course
has no output buffers. We will need to take the output from
the decoder buffers and put them into the renderer's input
buffers. It isn't totally clear to me whether or not you are
required to use all of the buffers, but
you can add extra buffers. It would be easier coding
if we had the same number of buffers at each stage!


 _Should this be an aside?_ If you look at the LIM component
"OMX.limoi.ffmpeg.decode.video" it has a minimum of 64 buffers.
But if you look at the example LIM code `limoi-core/test/decode.c`you see the following:

```
port_def.nBufferCountActual = 2;
        port_def.nBufferCountMin = 2;
        port_def.nBufferSize = bytes;
        OMX_SetParameter(comp, OMX_IndexParamPortDefinition, &port_def);
```


Now this is _not_ correct! The 1.1 specification in section 3.1.2.12.1 says


   >  `nBufferCountMin`is a _read-only_ [emphasis added]
field that specifies the minimum number of
buffers that the port requires. The component shall define this non-zero default
value.





 `nBufferSize`is a _read-only_ [emphasis added]
field that specifies the minimum size in bytes for
buffers that are allocated for this port.



and this example resets these read-only fields.


So what I've done is to make the number of buffers configurable by a #define
and set this number in all of the components ports.


The callback logic I use is

+ Decode EmptyBuffer Done: refill the buffer from the input file
and empty it
+ Decode FillBufferDone: set the  corresponding alsa_sink input buffer
to point to the decoder output buffer data
and call EmptyThis Buffer on the alsa_sink
+ Alsa Sink EmptyBufferDone: fill the
corresponding output decode buffer

Thus the decoder output and renderer input buffers are linked by the IL client,
while the decoder input buffer is emptied by the decoder component independently.
In an earlier version I tried to link all three buffers,
but this always eventually deadlocked with a decoder input buffer not
emptying properly.


The code is [play_ogg.c](OpenMAX_IL/LIM/play_ogg.c) 

```cpp
/**
   Contains code
   Copyright (C) 2007-2009 STMicroelectronics
   Copyright (C) 2007-2009 Nokia Corporation and/or its subsidiary(-ies).
   under the LGPL

   and code Copyright (C) 2010 SWOAG Technology <www.swoag.com> under the LGPL
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

/* we will use 4 of each port's buffers */
#define NUM_BUFFERS_USED 4

#ifdef LIM
char *decodeComponentName = "OMX.limoi.ogg_dec";
char *renderComponentName = "OMX.limoi.alsa_sink";
#endif

OMX_HANDLETYPE decodeHandle;
OMX_HANDLETYPE renderHandle;
OMX_VERSIONTYPE specVersion, compVersion;

int inFd = 0;

static OMX_BOOL bEOS=OMX_FALSE;

OMX_U32 inDecodeBufferSize;
OMX_U32 outDecodeBufferSize;
int numInDecodeBuffers;
int numOutDecodeBuffers;

OMX_U32 inRenderBufferSize;
int numInRenderBuffers;

OMX_BUFFERHEADERTYPE *inDecodeBuffers[NUM_BUFFERS_USED];
OMX_BUFFERHEADERTYPE *outDecodeBuffers[NUM_BUFFERS_USED];
OMX_BUFFERHEADERTYPE *inRenderBuffers[NUM_BUFFERS_USED];

pthread_mutex_t mutex;
OMX_STATETYPE currentState = OMX_StateLoaded;
pthread_cond_t stateCond;

void waitFor(OMX_STATETYPE state) {
    pthread_mutex_lock(&mutex);
    while (currentState != state)
	pthread_cond_wait(&stateCond, &mutex);
    printf("Wait successfully completed\n");
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
    fprintf(stderr, "Usage: play_ogg input_file");
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

static void reconfig_component_port (OMX_HANDLETYPE comp, int port) {
    OMX_PARAM_PORTDEFINITIONTYPE port_def;

    port_def.nSize = sizeof(OMX_PARAM_PORTDEFINITIONTYPE);
    port_def.nPortIndex = port;
    if (OMX_ErrorNone != OMX_GetParameter
        (comp, OMX_IndexParamPortDefinition, &port_def))
    {
        fprintf(stderr, "unable to get port %d definition.\n", port);
        exit(-1);
    } else
    {
        port_def.nBufferCountActual = NUM_BUFFERS_USED;
        port_def.nBufferCountMin = NUM_BUFFERS_USED;

        OMX_SetParameter(comp, OMX_IndexParamPortDefinition, &port_def);
    }
}

OMX_ERRORTYPE cEventHandler(
			    OMX_HANDLETYPE hComponent,
			    OMX_PTR pAppData,
			    OMX_EVENTTYPE eEvent,
			    OMX_U32 Data1,
			    OMX_U32 Data2,
			    OMX_PTR pEventData) {
    OMX_ERRORTYPE err;

    printf("Hi there, I am in the %s callback\n", __func__);
    if(eEvent == OMX_EventCmdComplete) {
	if (Data1 == OMX_CommandStateSet) {
	    printf("Component State changed in ", 0);
	    switch ((int)Data2) {
	    case OMX_StateInvalid:
		printf("OMX_StateInvalid\n", 0);
		break;
	    case OMX_StateLoaded:
		printf("OMX_StateLoaded\n", 0);
		break;
	    case OMX_StateIdle:
		printf("OMX_StateIdle\n",0);
		break;
	    case OMX_StateExecuting:
		printf("OMX_StateExecuting\n",0);
		break;
	    case OMX_StatePause:
		printf("OMX_StatePause\n",0);
		break;
	    case OMX_StateWaitForResources:
		printf("OMX_StateWaitForResources\n",0);
		break;
	    }
	    wakeUp((int) Data2);
	} else  if (Data1 == OMX_CommandPortEnable){
	    printf("OMX State Port enabled\n");
	} else if (Data1 == OMX_CommandPortDisable){
	    printf("OMX State Port disabled\n");     
	}
    } else if(eEvent == OMX_EventBufferFlag) {
	if((int)Data2 == OMX_BUFFERFLAG_EOS) {
     
	}
    } else if(eEvent == OMX_EventError) {
	printf("Event is Error\n");
    } else  if(eEvent == OMX_EventMark) {
	printf("Event is Buffer Mark\n");
    } else  if(eEvent == OMX_EventPortSettingsChanged) {
	/* See 1.1 spec, section 8.9.3.1 Playback Use Case */
	OMX_PARAM_PORTDEFINITIONTYPE sPortDef;

	setHeader(&sPortDef, sizeof(OMX_PARAM_PORTDEFINITIONTYPE));
	sPortDef.nPortIndex = Data1;

	err = OMX_GetConfig(hComponent, OMX_IndexParamPortDefinition, &sPortDef);
	if(err != OMX_ErrorNone){
	    fprintf(stderr, "Error in getting OMX_PORT_DEFINITION_TYPE parameter\n", 0);
	    exit(1);
	}
	printf("Event is Port Settings Changed on port %d in component %p\n",
	       Data1, hComponent);
	printf("Port has %d buffers of size is %d\n",  sPortDef.nBufferCountMin, sPortDef.nBufferSize);
    } else {
	printf("Event is %i\n", (int)eEvent);
	printf("Param1 is %i\n", (int)Data1);
	printf("Param2 is %i\n", (int)Data2);
    }

    return OMX_ErrorNone;
}

OMX_ERRORTYPE cDecodeEmptyBufferDone(
			       OMX_HANDLETYPE hComponent,
			       OMX_PTR pAppData,
			       OMX_BUFFERHEADERTYPE* pBuffer) {
    int n;
    OMX_ERRORTYPE err;

    printf("Hi there, I am in the %s callback, buffer %p.\n", __func__, pBuffer);
    if (bEOS) {
	printf("Buffers emptied, exiting\n");
	wakeUp(OMX_StateLoaded);
	exit(0);
    }
    printf("  left in buffer %d\n", pBuffer->nFilledLen);

    /* put data into the buffer, and then empty it */
    int data_read = read(inFd, pBuffer->pBuffer, inDecodeBufferSize);
    if (data_read <= 0) {
	bEOS = 1;
    }
    printf("  filled buffer %p with %d\n", pBuffer, data_read);
    pBuffer->nFilledLen = data_read;

    err = OMX_EmptyThisBuffer(decodeHandle, pBuffer);
    if (err != OMX_ErrorNone) {
	fprintf(stderr, "Error on emptying decode buffer\n");
	exit(1);
    }

    return OMX_ErrorNone;
}

OMX_ERRORTYPE cDecodeFillBufferDone(
			      OMX_HANDLETYPE hComponent,
			      OMX_PTR pAppData,
			      OMX_BUFFERHEADERTYPE* pBuffer) {
    OMX_BUFFERHEADERTYPE* pRenderBuffer;
    int n;
    OMX_ERRORTYPE err;

    printf("Hi there, I am in the %s callback, buffer %p with %d bytes.\n", 
	   __func__, pBuffer, pBuffer->nFilledLen);
    if (bEOS) {
	printf("Buffers filled, exiting\n");
    }

    /* find matching render buffer */
    for (n = 0; n < NUM_BUFFERS_USED; n++) {
	if (pBuffer == outDecodeBuffers[n]) {
	    pRenderBuffer = inRenderBuffers[n];
	    break;
	}
    }

    pRenderBuffer->nFilledLen = pBuffer->nFilledLen;
    /* We don't attempt to refill the decode output buffer until we
       have emptied the render input buffer. So we can just use the
       decode output buffer for the render input buffer.
       Avoids us copying the data across buffers.
    */
    pRenderBuffer->pBuffer = pBuffer->pBuffer;

    err = OMX_EmptyThisBuffer(renderHandle, pRenderBuffer);
    if (err != OMX_ErrorNone) {
	fprintf(stderr, "Error on emptying buffer\n");
	exit(1);
    }

    return OMX_ErrorNone;
}


OMX_CALLBACKTYPE decodeCallbacks  = { .EventHandler = cEventHandler,
				.EmptyBufferDone = cDecodeEmptyBufferDone,
				.FillBufferDone = cDecodeFillBufferDone
};


OMX_ERRORTYPE cRenderEmptyBufferDone(
			       OMX_HANDLETYPE hComponent,
			       OMX_PTR pAppData,
			       OMX_BUFFERHEADERTYPE* pBuffer) {
    OMX_BUFFERHEADERTYPE *inDecodeBuffer;
    OMX_BUFFERHEADERTYPE *outDecodeBuffer;
    int n;
    OMX_ERRORTYPE err;
 
    printf("Hi there, I am in the %s callback, buffer %p.\n", __func__, pBuffer);

    /* find matching buffer indices */
    for (n = 0; n < NUM_BUFFERS_USED; n++) {
	if (pBuffer == inRenderBuffers[n]) {
	    outDecodeBuffer = outDecodeBuffers[n];
	    break;
	}
    }

    /* and fill the corresponding output buffer */
    outDecodeBuffer->nFilledLen = 0;
    err = OMX_FillThisBuffer(decodeHandle, outDecodeBuffer);
    if (err != OMX_ErrorNone) {
	fprintf(stderr, "Error on filling buffer\n");
	exit(1);
    }
       
    return OMX_ErrorNone;
}


OMX_CALLBACKTYPE renderCallbacks  = { .EventHandler = cEventHandler,
				.EmptyBufferDone = cRenderEmptyBufferDone,
				.FillBufferDone = NULL
};

void printState(OMX_HANDLETYPE handle) {
    OMX_STATETYPE state;
    OMX_ERRORTYPE err;

    err = OMX_GetState(handle, &state);
    if (err != OMX_ErrorNone) {
	fprintf(stderr, "Error on getting state\n");
	exit(1);
    }
    switch (state) {
    case OMX_StateLoaded: printf("StateLoaded\n"); break;
    case OMX_StateIdle: printf("StateIdle\n"); break;
    case OMX_StateExecuting: printf("StateExecuting\n"); break;
    case OMX_StatePause: printf("StatePause\n"); break;
    case OMX_StateWaitForResources: printf("StateWiat\n"); break;
    default:  printf("State unknown\n"); break;
    }
}

void setEncoding(OMX_HANDLETYPE handle, int portNumber, OMX_AUDIO_CODINGTYPE encoding) {
    OMX_AUDIO_PARAM_PORTFORMATTYPE sAudioPortFormat;
    OMX_ERRORTYPE err;


    setHeader(&sAudioPortFormat, sizeof(OMX_AUDIO_PARAM_PORTFORMATTYPE));
    sAudioPortFormat.nIndex = 0;
    sAudioPortFormat.nPortIndex = portNumber;

    err = OMX_GetParameter(handle, OMX_IndexParamAudioPortFormat, &sAudioPortFormat);
    if (err == OMX_ErrorNoMore) {
	printf("Can't get format\n");
	return;
    }
    sAudioPortFormat.eEncoding = encoding;
    err = OMX_SetParameter(handle, OMX_IndexParamAudioPortFormat, &sAudioPortFormat);
    if (err == OMX_ErrorNoMore) {
	printf("Can't set format\n");
	return;
    }
    printf("Set format on port %d\n", portNumber);
}

/*
   *pBuffer is set to non-zero if a particular buffer size is required by the client
 */
void createBuffers(OMX_HANDLETYPE handle, int portNumber, 
		      OMX_U32 *pBufferSize, OMX_BUFFERHEADERTYPE **ppBuffers) {
    OMX_PARAM_PORTDEFINITIONTYPE sPortDef;
    int n;
    int nBuffers;
    OMX_ERRORTYPE err;

    setHeader(&sPortDef, sizeof(OMX_PARAM_PORTDEFINITIONTYPE));
    sPortDef.nPortIndex = portNumber;
    err = OMX_GetParameter(handle, OMX_IndexParamPortDefinition, &sPortDef);
    if(err != OMX_ErrorNone){
	fprintf(stderr, "Error in getting OMX_PORT_DEFINITION_TYPE parameter\n", 0);
	exit(1);
    }

    /* if no size pre-allocated, use the minimum */
    if (*pBufferSize == 0) {
	*pBufferSize = sPortDef.nBufferSize;
    } else {
	sPortDef.nBufferSize = *pBufferSize;
    }

    nBuffers = NUM_BUFFERS_USED;
    printf("Port %d has %d buffers of size is %d\n", portNumber, nBuffers, *pBufferSize);

    for (n = 0; n < nBuffers; n++) {
	err = OMX_AllocateBuffer(handle, ppBuffers+n, portNumber, NULL,
				 *pBufferSize);
	if (err != OMX_ErrorNone) {
	    fprintf(stderr, "Error on AllocateBuffer is %d\n", err);
	    exit(1);
	}
    }
}

int main(int argc, char** argv) {

    OMX_PORT_PARAM_TYPE param;
    OMX_PARAM_PORTDEFINITIONTYPE sPortDef;
    OMX_AUDIO_PORTDEFINITIONTYPE sAudioPortDef;
    OMX_AUDIO_PARAM_PORTFORMATTYPE sAudioPortFormat;
    OMX_AUDIO_PARAM_PCMMODETYPE sPCMMode;
    OMX_ERRORTYPE err;

    OMX_AUDIO_PARAM_MP3TYPE sMP3Mode;


    unsigned char name[OMX_MAX_STRINGNAME_SIZE];
    OMX_UUIDTYPE uid;
    int startDecodePortNumber;
    int nDecodePorts;
    int startRenderPortNumber;
    int nRenderPorts;
    int n;

    printf("Thread id is %p\n", pthread_self());
    if(argc < 1){
	display_help();
	exit(1);
    }

    inFd = open(argv[1], O_RDONLY);
    if(inFd < 0){
	fprintf(stderr, "Error opening input file \"%s\"\n", argv[1]);
	exit(1);
    }

    err = OMX_Init();
    if(err != OMX_ErrorNone) {
	fprintf(stderr, "OMX_Init() failed\n", 0);
	exit(1);
    }
 
   /** Ask the core for a handle to the decode component
     */
    err = OMX_GetHandle(&decodeHandle, decodeComponentName, 
			NULL /*app private data */, &decodeCallbacks);
    if(err != OMX_ErrorNone) {
	fprintf(stderr, "OMX_GetHandle failed\n", 0);
	exit(1);
    }
    err = OMX_GetComponentVersion(decodeHandle, name, &compVersion, &specVersion, &uid);
    if(err != OMX_ErrorNone) {
	fprintf(stderr, "OMX_GetComponentVersion failed\n", 0);
	exit(1);
    }

    /** Ask the core for a handle to the render component
     */
    err = OMX_GetHandle(&renderHandle, renderComponentName, 
			NULL /*app private data */, &renderCallbacks);
    if(err != OMX_ErrorNone) {
	fprintf(stderr, "OMX_GetHandle failed\n", 0);
	exit(1);
    }

    /** no other ports to disable */

    /** Get audio port information */
    /* Decode component */
    setHeader(&param, sizeof(OMX_PORT_PARAM_TYPE));
    err = OMX_GetParameter(decodeHandle, OMX_IndexParamAudioInit, &param);
    if(err != OMX_ErrorNone){
	fprintf(stderr, "Error in getting OMX_PORT_PARAM_TYPE parameter\n", 0);
	exit(1);
    }
    startDecodePortNumber = ((OMX_PORT_PARAM_TYPE)param).nStartPortNumber;
    nDecodePorts = ((OMX_PORT_PARAM_TYPE)param).nPorts;
    if (nDecodePorts != 2) {
	fprintf(stderr, "Decode device has wrong number of ports: %d\n", nDecodePorts);
	exit(1);
    }

    setEncoding(decodeHandle, startDecodePortNumber, OMX_AUDIO_CodingVORBIS);
    setEncoding(decodeHandle, startDecodePortNumber+1, OMX_AUDIO_CodingPCM);

    printState(decodeHandle);;

    reconfig_component_port(decodeHandle, startDecodePortNumber);
    reconfig_component_port(decodeHandle, startDecodePortNumber+1);

    /* call to put decoder state into idle before allocating buffers */
    err = OMX_SendCommand(decodeHandle, OMX_CommandStateSet, OMX_StateIdle, NULL);
    if (err != OMX_ErrorNone) {
	fprintf(stderr, "Error on setting state to idle\n");
	exit(1);
    }
 
    /* ensure decoder ports are enabled */
    err = OMX_SendCommand(decodeHandle, OMX_CommandPortEnable, startDecodePortNumber, NULL);
    if (err != OMX_ErrorNone) {
	fprintf(stderr, "Error on setting port to enabled\n");
	exit(1);
    }
    err = OMX_SendCommand(decodeHandle, OMX_CommandPortEnable, startDecodePortNumber+1, NULL);
    if (err != OMX_ErrorNone) {
	fprintf(stderr, "Error on setting port to enabled\n");
	exit(1);
    }

    /* use default buffer sizes */
    inDecodeBufferSize = outDecodeBufferSize = 0;
    createBuffers(decodeHandle, startDecodePortNumber, &inDecodeBufferSize, inDecodeBuffers);
    createBuffers(decodeHandle, startDecodePortNumber+1, &outDecodeBufferSize, outDecodeBuffers);


    /* Make sure we've reached Idle state */
    waitFor(OMX_StateIdle);
    printf("Reached Idle state\n");

    /* Now try to switch to Executing state */
    err = OMX_SendCommand(decodeHandle, OMX_CommandStateSet, OMX_StateExecuting, NULL);
    if(err != OMX_ErrorNone){
	fprintf(stderr, "Error changing to Executing state\n");
	exit(1);
    }
    /* end decode setting */


    /* Render component */
    setHeader(&param, sizeof(OMX_PORT_PARAM_TYPE));
    err = OMX_GetParameter(renderHandle, OMX_IndexParamAudioInit, &param);
    if(err != OMX_ErrorNone){
	fprintf(stderr, "Error in getting OMX_PORT_PARAM_TYPE parameter\n", 0);
	exit(1);
    }
    startRenderPortNumber = ((OMX_PORT_PARAM_TYPE)param).nStartPortNumber;
    nRenderPorts = ((OMX_PORT_PARAM_TYPE)param).nPorts;
    if (nRenderPorts != 1) {
	fprintf(stderr, "Render device has wrong number of ports: %d\n", nRenderPorts);
	exit(1);
    }

    setEncoding(renderHandle, startRenderPortNumber, OMX_AUDIO_CodingPCM);

    printState(renderHandle);
    
     /* call to put state into idle before allocating buffers */
    err = OMX_SendCommand(renderHandle, OMX_CommandStateSet, OMX_StateIdle, NULL);
    if (err != OMX_ErrorNone) {
	fprintf(stderr, "Error on setting state to idle\n");
	exit(1);
    }

    /* ensure port is enabled */ 
    err = OMX_SendCommand(renderHandle, OMX_CommandPortEnable, startRenderPortNumber, NULL);
    if (err != OMX_ErrorNone) {
	fprintf(stderr, "Error on setting port to enabled\n");
	exit(1);
    }

    reconfig_component_port(renderHandle, startRenderPortNumber);

    /* set render buffer size to decoder out buffer size */
    inRenderBufferSize = outDecodeBufferSize;
    createBuffers(renderHandle, startRenderPortNumber, &inRenderBufferSize, inRenderBuffers);


    /* Make sure we've reached Idle state */
    waitFor(OMX_StateIdle);
    printf("Reached Idle state\n");

    /* Now try to switch renderer to Executing state */
    err = OMX_SendCommand(renderHandle, OMX_CommandStateSet, OMX_StateExecuting, NULL);
    if(err != OMX_ErrorNone){
	fprintf(stderr, "Error changing render to executing state\n");
	exit(1);
    }
    /* end render setting */


    /* debugging: print buffer pointers */
    for (n = 0; n < NUM_BUFFERS_USED; n++)
	printf("In decode buffer %d is %p\n", n, inDecodeBuffers[n]);
    for (n = 0; n < NUM_BUFFERS_USED; n++)
	printf("Out decode buffer %d is %p\n", n, outDecodeBuffers[n]);
    for (n = 0; n < NUM_BUFFERS_USED; n++)
	printf("In render buffer %d is %p\n", n, inRenderBuffers[n]);


    /* no buffers emptied yet */
    pEmptyBuffer = NULL;

    /* load  the decoder input buffers */
    for (n = 0; n < NUM_BUFFERS_USED; n++) {
	int data_read = read(inFd, inDecodeBuffers[n]->pBuffer, inDecodeBufferSize);
	inDecodeBuffers[n]->nFilledLen = data_read;
	printf("Read %d into buffer %p\n", data_read, inDecodeBuffers[n]);
	if (data_read <= 0) {
	    printf("In the %s no more input data available\n", __func__);
	    inDecodeBuffers[n]->nFilledLen = 0;
	    inDecodeBuffers[n]->nFlags = OMX_BUFFERFLAG_EOS;
	    bEOS=OMX_TRUE;
	}
    }
    
    /* fill the decoder output buffers */
    for (n = 0; n < NUM_BUFFERS_USED; n++) {
	outDecodeBuffers[n]->nFilledLen = 0;
	err = OMX_FillThisBuffer(decodeHandle, outDecodeBuffers[n]);
	if (err != OMX_ErrorNone) {
	    fprintf(stderr, "Error on filling buffer\n");
	    exit(1);
	}
    }

    /* empty the decoder input bufers */
    for (n = 0; n < NUM_BUFFERS_USED; n++) {
	err = OMX_EmptyThisBuffer(decodeHandle, inDecodeBuffers[n]);
	if (err != OMX_ErrorNone) {
	    fprintf(stderr, "Error on emptying buffer\n");
	    exit(1);
	}
    }

    pEmptyBuffer = inDecodeBuffers[0];
    emptyState = 1;

    waitFor(OMX_StateLoaded);
    printf("Buffers emptied\n");
    exit(0);
}
```
