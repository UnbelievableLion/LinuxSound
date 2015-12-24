
##  OpenSL ES examples 


These examples are taken from the appendices of the OpenSL ES specification.
They have not been tested.

The programming model for OpenSL ES is that of _interfaces_ and _objects_ .
      The programming _language_ is C, so one of the common mechanisms for writing O/O style code
      in C is used (see e.g. [
	Object-Oriented Programming In C
      ](http://www.drdobbs.com/object-oriented-programming-in-c/184402190?pgno=1) ). Interfaces are represented by structures containing function pointers for
      methods. An object which implements the interface is of the interface type, with the
      methods as particular functions. Calling a method involves calling the
      appropriate function in the structure. The "this" object is always passed in as the
      first parameter of the function as in

```

	
(*object) -> method(object, ...)
	
      
```


Every object has to be "realised" before it can be used.


There does not seem to be any inheritance model, but then that isn't necessary here.


Note that every function returns a value that can be tested for sucess or fail.
      Objects that are created are passed as address parameters for filling.
      The application is responsible for freeing any memory allocated during this
      by calling `Destroy()`on the object.


An OpenSL (or OpenMAX AL) application is started by creating an "engine" using `slCreateEngine()`. This is the only global function in the library.
      From then on, objects are obtained from the engine or other objects by a call
      to `GetInterface()`or `CreateXYZ`on the engine or object. 
      For example,

```

	
(*engine) -> CreateOutputMix(engine, &output_mix...);
(*output_mix) -> GetInterface(output_mix, SL_IID_VOLUME, &volume, ...);
	
      
```

###  Play audio from a buffer 


The model for playing audio is not very complex, just verbose.
      It consists of

+ Initialise the system
+ Prepare a data source
+ Prepare an output sink
+ Set up a callback function to be called when the player needs more data
+ Create and start a playback engine
+ Clean up
####  Initialise the system 

```

	
    SLresult res;
    SLObjectItf sl;
    SLEngineOption EngineOption[] = {
	(SLuint32) SL_ENGINEOPTION_THREADSAFE,
	(SLuint32) SL_BOOLEAN_TRUE};
    res = slCreateEngine( &sl, 1, EngineOption, 0, NULL, NULL);
    CheckErr(res);
    /* Realizing the SL Engine in synchronous mode. */
    res = (*sl)->Realize(sl, SL_BOOLEAN_FALSE); CheckErr(res);
	
      
```

####  Prepare a data source 

```

	
    /* Local storage for Audio data */
    SLint16 pcmData[AUDIO_DATA_STORAGE_SIZE];
    /* put something nito pcmData ... not done here */

    /* Setup the data source structure for the buffer queue */
    bufferQueue.locatorType = SL_DATALOCATOR_BUFFERQUEUE;
    bufferQueue.numBuffers = 4; /* Four buffers in our buffer queue */
    /* Setup the format of the content in the buffer queue */
    pcm.formatType = SL_DATAFORMAT_PCM;
    pcm.numChannels = 2;
    pcm.samplesPerSec = SL_SAMPLINGRATE_44_1;
    pcm.bitsPerSample = SL_PCMSAMPLEFORMAT_FIXED_16;
    pcm.containerSize = 16;
    pcm.channelMask = SL_SPEAKER_FRONT_LEFT | SL_SPEAKER_FRONT_RIGHT;
    pcm.endianness = SL_BYTEORDER_LITTLEENDIAN;
    audioSource.pFormat	= (void *)&pcm;
    audioSource.pLocator    = (void *)&bufferQueue;
	
      
```

####  Prepare an output sink 

```

	
    for (i=0;i<MAX_NUMBER_INTERFACES;i++)
	{
	    required[i] = SL_BOOLEAN_FALSE;
	    iidArray[i] = SL_IID_NULL;
	}
    // Create Output Mix object to be used by player
    res = (*EngineItf)->CreateOutputMix(EngineItf, &OutputMix, 1,
					iidArray, required); CheckErr(res);
    // Realizing the Output Mix object in synchronous mode.
    res = (*OutputMix)->Realize(OutputMix, SL_BOOLEAN_FALSE);
    CheckErr(res);
	
      
```

####  Set up a callback function to be called when the player needs more data 


The callback in this case uses a data structure to hold all of the data and pointers
      to the start and current position of the data. This is for this application,
      and is not a part of OpenSL

```

	
/* Structure for passing information to callback function */
typedef struct CallbackCntxt_ {
    SLPlayItf playItf;
    SLint16* pDataBase;
    // Base adress of local audio data storage
    SLint16* pData;
    // Current adress of local audio data storage
    SLuint32 size;
} CallbackCntxt;
	
      
```


Then we can set up the output sink and callback data

```

	
    /* Setup the data sink structure */
    locator_outputmix.locatorType = SL_DATALOCATOR_OUTPUTMIX;
    locator_outputmix.outputMix = OutputMix;
    audioSink.pLocator = (void *)&locator_outputmix;
    audioSink.pFormat = NULL;
    /* Initialize the context for Buffer queue callbacks */
    cntxt.pDataBase = (void*)&pcmData;
    cntxt.pData = cntxt.pDataBase;
    cntxt.size = sizeof(pcmData);
	
      
```

####  Create and start a playback engine 

```

	
    /* Set arrays required[] and iidArray[] for SEEK interface
       (PlayItf is implicit) */
    required[0] =    SL_BOOLEAN_TRUE;
    iidArray[0] =    SL_IID_BUFFERQUEUE;
    /* Create the music player */
    res = (*EngineItf)->CreateAudioPlayer(EngineItf, &player,
					  &audioSource, &audioSink, 1, iidArray, required); CheckErr(res);
    /* Realizing the player in synchronous mode. */
    res = (*player)->Realize(player, SL_BOOLEAN_FALSE); CheckErr(res);
    /* Get seek and play interfaces */
    res = (*player)->GetInterface(player, SL_IID_PLAY, (void*)&playItf);
    CheckErr(res);
    res = (*player)->GetInterface(player, SL_IID_BUFFERQUEUE,
				  (void*)&bufferQueueItf); CheckErr(res);
    /* Setup to receive buffer queue event callbacks */
    res = (*bufferQueueItf)->RegisterCallback(bufferQueueItf,
					      BufferQueueCallback, NULL); CheckErr(res);
    /* Enqueue a few buffers to get the ball rolling */
    res = (*bufferQueueItf)->Enqueue(bufferQueueItf, cntxt.pData,
				     2 * AUDIO_DATA_BUFFER_SIZE); /* Size given in bytes. */
    CheckErr(res);
    cntxt.pData += AUDIO_DATA_BUFFER_SIZE;
    res = (*bufferQueueItf)->Enqueue(bufferQueueItf, cntxt.pData,
				     2 * AUDIO_DATA_BUFFER_SIZE); /* Size given in bytes. */
    CheckErr(res);
    cntxt.pData += AUDIO_DATA_BUFFER_SIZE;
    res = (*bufferQueueItf)->Enqueue(bufferQueueItf, cntxt.pData,
				     2 * AUDIO_DATA_BUFFER_SIZE); /* Size given in bytes. */
    CheckErr(res);
    cntxt.pData += AUDIO_DATA_BUFFER_SIZE;
    /* Play the PCM samples using a buffer queue */
    res = (*playItf)->SetPlayState( playItf, SL_PLAYSTATE_PLAYING );
    CheckErr(res);
    /* Wait until the PCM data is done playing, the buffer queue callback
       will continue to queue buffers until the entire PCM data has been
       played. This is indicated by waiting for the count member of the
       SLBufferQueueState to go to zero.
    */
    res = (*bufferQueueItf)->GetState(bufferQueueItf, &state);
    CheckErr(res);
    while(state.count)
	{
	    (*bufferQueueItf)->GetState(bufferQueueItf, &state);
	}

	
      
```

####  Clean up 

```

	
    /* Make sure player is stopped */
    res = (*playItf)->SetPlayState(playItf, SL_PLAYSTATE_STOPPED);
    CheckErr(res);
    /* Destroy the player */
    (*player)->Destroy(player);
    /* Destroy Output Mix object */
    (*OutputMix)->Destroy(OutputMix);
	
      
```

####  Full program 


The full code is

```

      
#include <stdio.h>
#include <stdlib.h>
#include "OpenSLES.h"
#define SLEEP(x) /* Client system sleep function to sleep x milliseconds
		    would replace SLEEP macro */
#define MAX_NUMBER_INTERFACES 3
#define MAX_NUMBER_OUTPUT_DEVICES 6
/* Local storage for Audio data in 16 bit words */
#define AUDIO_DATA_STORAGE_SIZE 4096
/* Audio data buffer size in 16 bit words. 8 data segments are used in
   this simple example */
#define AUDIO_DATA_BUFFER_SIZE 4096/8
/* Checks for error. If any errors exit the application! */
void CheckErr( SLresult res )
{
    if ( res != SL_RESULT_SUCCESS )
	{
	    // Debug printing to be placed here
	    exit(1);
	}
}
/* Structure for passing information to callback function */
typedef struct CallbackCntxt_ {
    SLPlayItf playItf;
    SLint16* pDataBase;
    // Base adress of local audio data storage
    SLint16* pData;
    // Current adress of local audio data storage
    SLuint32 size;
} CallbackCntxt;
/* Local storage for Audio data */
SLint16 pcmData[AUDIO_DATA_STORAGE_SIZE];
/* Callback for Buffer Queue events */
void BufferQueueCallback(
			 SLBufferQueueItf queueItf,
			 void *pContext)
{
    SLresult res;
    CallbackCntxt *pCntxt = (CallbackCntxt*)pContext;
    if(pCntxt->pData < (pCntxt->pDataBase + pCntxt->size))
	{
	    res = (*queueItf)->Enqueue(queueItf, (void*) pCntxt->pData,
				       2 * AUDIO_DATA_BUFFER_SIZE); /* Size given in bytes. */
	    CheckErr(res);
	    /* Increase data pointer by buffer size */
	    pCntxt->pData += AUDIO_DATA_BUFFER_SIZE;
	}
}
/* Play some music from a buffer queue */
void TestPlayMusicBufferQueue( SLObjectItf sl )
{
    SLEngineItf EngineItf;
    SLint32 numOutputs = 0;
    SLuint32 deviceID = 0;
    SLresult res;
    SLDataSource audioSource;
    SLDataLocator_BufferQueue bufferQueue;
    SLDataFormat_PCM pcm;
    SLDataSink audioSink;
    SLDataLocator_OutputMix locator_outputmix;
    SLObjectItf player;
    SLPlayItf playItf;
    SLBufferQueueItf bufferQueueItf;
    SLBufferQueueState state;
    SLObjectItf OutputMix;
    SLVolumeItf volumeItf;
    int i;
    SLboolean required[MAX_NUMBER_INTERFACES];
    SLInterfaceID iidArray[MAX_NUMBER_INTERFACES];
    /* Callback context for the buffer queue callback function */
    CallbackCntxt cntxt;
    /* Get the SL Engine Interface which is implicit */
    res = (*sl)->GetInterface(sl, SL_IID_ENGINE, (void*)&EngineItf);
    CheckErr(res);
    /* Initialize arrays required[] and iidArray[] */
    for (i=0;i<MAX_NUMBER_INTERFACES;i++)
	{
	    required[i] = SL_BOOLEAN_FALSE;
	    iidArray[i] = SL_IID_NULL;
	}
    // Set arrays required[] and iidArray[] for VOLUME interface
    required[0] = SL_BOOLEAN_TRUE;
    iidArray[0] = SL_IID_VOLUME;
    // Create Output Mix object to be used by player
    res = (*EngineItf)->CreateOutputMix(EngineItf, &OutputMix, 1,
					iidArray, required); CheckErr(res);
    // Realizing the Output Mix object in synchronous mode.
    res = (*OutputMix)->Realize(OutputMix, SL_BOOLEAN_FALSE);
    CheckErr(res);
    res = (*OutputMix)->GetInterface(OutputMix, SL_IID_VOLUME,
				     (void*)&volumeItf); CheckErr(res);
    /* Setup the data source structure for the buffer queue */
    bufferQueue.locatorType = SL_DATALOCATOR_BUFFERQUEUE;
    bufferQueue.numBuffers = 4; /* Four buffers in our buffer queue */
    /* Setup the format of the content in the buffer queue */
    pcm.formatType = SL_DATAFORMAT_PCM;
    pcm.numChannels = 2;
    pcm.samplesPerSec = SL_SAMPLINGRATE_44_1;
    pcm.bitsPerSample = SL_PCMSAMPLEFORMAT_FIXED_16;
    pcm.containerSize = 16;
    pcm.channelMask = SL_SPEAKER_FRONT_LEFT | SL_SPEAKER_FRONT_RIGHT;
    pcm.endianness = SL_BYTEORDER_LITTLEENDIAN;
    audioSource.pFormat	= (void *)&pcm;
    audioSource.pLocator    = (void *)&bufferQueue;
    /* Setup the data sink structure */
    locator_outputmix.locatorType = SL_DATALOCATOR_OUTPUTMIX;
    locator_outputmix.outputMix = OutputMix;
    audioSink.pLocator = (void *)&locator_outputmix;
    audioSink.pFormat = NULL;
    /* Initialize the context for Buffer queue callbacks */
    cntxt.pDataBase = (void*)&pcmData;
    cntxt.pData = cntxt.pDataBase;
    cntxt.size = sizeof(pcmData);
    /* Set arrays required[] and iidArray[] for SEEK interface
       (PlayItf is implicit) */
    required[0] =    SL_BOOLEAN_TRUE;
    iidArray[0] =    SL_IID_BUFFERQUEUE;
    /* Create the music player */
    res = (*EngineItf)->CreateAudioPlayer(EngineItf, &player,
					  &audioSource, &audioSink, 1, iidArray, required); CheckErr(res);
    /* Realizing the player in synchronous mode. */
    res = (*player)->Realize(player, SL_BOOLEAN_FALSE); CheckErr(res);
    /* Get seek and play interfaces */
    res = (*player)->GetInterface(player, SL_IID_PLAY, (void*)&playItf);
    CheckErr(res);
    res = (*player)->GetInterface(player, SL_IID_BUFFERQUEUE,
				  (void*)&bufferQueueItf); CheckErr(res);
    /* Setup to receive buffer queue event callbacks */
    res = (*bufferQueueItf)->RegisterCallback(bufferQueueItf,
					      BufferQueueCallback, NULL); CheckErr(res);
    /* Before we start set volume to -3dB (-300mB) */
    res = (*volumeItf)->SetVolumeLevel(volumeItf, -300); CheckErr(res);
    /* Enqueue a few buffers to get the ball rolling */
    res = (*bufferQueueItf)->Enqueue(bufferQueueItf, cntxt.pData,
				     2 * AUDIO_DATA_BUFFER_SIZE); /* Size given in bytes. */
    CheckErr(res);
    cntxt.pData += AUDIO_DATA_BUFFER_SIZE;
    res = (*bufferQueueItf)->Enqueue(bufferQueueItf, cntxt.pData,
				     2 * AUDIO_DATA_BUFFER_SIZE); /* Size given in bytes. */
    CheckErr(res);
    cntxt.pData += AUDIO_DATA_BUFFER_SIZE;
    res = (*bufferQueueItf)->Enqueue(bufferQueueItf, cntxt.pData,
				     2 * AUDIO_DATA_BUFFER_SIZE); /* Size given in bytes. */
    CheckErr(res);
    cntxt.pData += AUDIO_DATA_BUFFER_SIZE;
    /* Play the PCM samples using a buffer queue */
    res = (*playItf)->SetPlayState( playItf, SL_PLAYSTATE_PLAYING );
    CheckErr(res);
    /* Wait until the PCM data is done playing, the buffer queue callback
       will continue to queue buffers until the entire PCM data has been
       played. This is indicated by waiting for the count member of the
       SLBufferQueueState to go to zero.
    */
    res = (*bufferQueueItf)->GetState(bufferQueueItf, &state);
    CheckErr(res);
    while(state.count)
	{
	    (*bufferQueueItf)->GetState(bufferQueueItf, &state);
	    /* should sleep be called here? */
	}
    /* Make sure player is stopped */
    res = (*playItf)->SetPlayState(playItf, SL_PLAYSTATE_STOPPED);
    CheckErr(res);
    /* Destroy the player */
    (*player)->Destroy(player);
    /* Destroy Output Mix object */
    (*OutputMix)->Destroy(OutputMix);
}
int sl_main( void )
{
    SLresult res;
    SLObjectItf sl;
    SLEngineOption EngineOption[] = {
	(SLuint32) SL_ENGINEOPTION_THREADSAFE,
	(SLuint32) SL_BOOLEAN_TRUE};
    res = slCreateEngine( &sl, 1, EngineOption, 0, NULL, NULL);
    CheckErr(res);
    /* Realizing the SL Engine in synchronous mode. */
    res = (*sl)->Realize(sl, SL_BOOLEAN_FALSE); CheckErr(res);
    TestPlayMusicBufferQueue(sl);
    /* Shutdown OpenSL ES */
    (*sl)->Destroy(sl);
    exit(0);
}

      
  
```

###  Record audio 


The ability to record audio in OpenSL ES is an option for the implementation.
      Consequently, we cannot guarantee that there is any microphone or
      similar device. The main difference in this program from the previous one
      is that checks need to be performed first on the input devices:

```

	
    res = (*sl)->GetInterface(sl, SL_IID_AUDIOIODEVICECAPABILITIES,
			      (void*)&AudioIODeviceCapabilitiesItf); CheckErr(res);
    numInputs = MAX_NUMBER_INPUT_DEVICES;
    res = (*AudioIODeviceCapabilitiesItf)->GetAvailableAudioInputs(
								   AudioIODeviceCapabilitiesItf, &numInputs, InputDeviceIDs); CheckErr(res);
    /* Search for either earpiece microphone or headset microphone input
       device - with a preference for the latter */
    for (i=0;i < numInputs; i++)
	{
	    res = (*AudioIODeviceCapabilitiesItf)-
		>QueryAudioInputCapabilities(AudioIODeviceCapabilitiesItf,
					     InputDeviceIDs[i], &AudioInputDescriptor); CheckErr(res);
	    if((AudioInputDescriptor.deviceConnection ==
		SL_DEVCONNECTION_ATTACHED_WIRED)&&
	       (AudioInputDescriptor.deviceScope == SL_DEVSCOPE_USER)&&
	       (AudioInputDescriptor.deviceLocation ==
		SL_DEVLOCATION_HEADSET))
		{
		    mic_deviceID = InputDeviceIDs[i];
		    mic_available = SL_BOOLEAN_TRUE;
		    break;
		}
	    else if((AudioInputDescriptor.deviceConnection ==
		     SL_DEVCONNECTION_INTEGRATED)&&
		    (AudioInputDescriptor.deviceScope ==
		     SL_DEVSCOPE_USER)&&
		    (AudioInputDescriptor.deviceLocation ==
		     SL_DEVLOCATION_HANDSET))
		{
		    mic_deviceID = InputDeviceIDs[i];
		    mic_available = SL_BOOLEAN_TRUE;
		    break;
		}
	}
    /* If neither of the preferred input audio devices is available, no
       point in continuing */
    if (!mic_available) {
	/* Appropriate error message here */
	exit(1);
    }
	
      
```


The other major differences are that the engine is used to create
      an audio recorder rather than a player, and that the recorded
      sounds are saved to a file.

```

	
#include <stdio.h>
#include <stdlib.h>
#include "OpenSLES.h"
#define MAX_NUMBER_INTERFACES 5
#define MAX_NUMBER_INPUT_DEVICES 3
#define POSITION_UPDATE_PERIOD 1000 /* 1 sec */
/* Checks for error. If any errors exit the application! */
void CheckErr( SLresult res )
{
    if ( res != SL_RESULT_SUCCESS )
	{
	    // Debug printing to be placed here
	    exit(1);
	}
}
void RecordEventCallback(SLRecordItf caller,
			 void *pContext, 
			 SLuint32 recordevent)

{
    /* Callback code goes here */
}
/*
 * Test recording of audio from a microphone into a specified file
 */
void TestAudioRecording(SLObjectItf sl)
{
    SLObjectItf
	recorder;
    SLRecordItf
	recordItf;
    SLEngineItf
	EngineItf;
    SLAudioIODeviceCapabilitiesItf AudioIODeviceCapabilitiesItf;
    SLAudioInputDescriptor
	AudioInputDescriptor;
    SLresult
	res;
    SLDataSource audioSource;
    SLDataLocator_IODevice locator_mic;
    SLDeviceVolumeItf devicevolumeItf;
    SLDataSink audioSink;
    SLDataLocator_URI uri;
    SLDataFormat_MIME mime;
    int i;
    SLboolean required[MAX_NUMBER_INTERFACES];
    SLInterfaceID iidArray[MAX_NUMBER_INTERFACES];
    SLuint32 InputDeviceIDs[MAX_NUMBER_INPUT_DEVICES];
    SLint32
	numInputs = 0;
    SLboolean mic_available = SL_BOOLEAN_FALSE;
    SLuint32 mic_deviceID = 0;
    /* Get the SL Engine Interface which is implicit */
    res = (*sl)->GetInterface(sl, SL_IID_ENGINE, (void*)&EngineItf);
    CheckErr(res);
    /* Get the Audio IO DEVICE CAPABILITIES interface, which is also
       implicit */
    res = (*sl)->GetInterface(sl, SL_IID_AUDIOIODEVICECAPABILITIES,
			      (void*)&AudioIODeviceCapabilitiesItf); CheckErr(res);
    numInputs = MAX_NUMBER_INPUT_DEVICES;
    res = (*AudioIODeviceCapabilitiesItf)->GetAvailableAudioInputs(
								   AudioIODeviceCapabilitiesItf, &numInputs, InputDeviceIDs); CheckErr(res);
    /* Search for either earpiece microphone or headset microphone input
       device - with a preference for the latter */
    for (i=0;i<numInputs; i++)
	{
	    res = (*AudioIODeviceCapabilitiesItf)-
		>QueryAudioInputCapabilities(AudioIODeviceCapabilitiesItf,
					     InputDeviceIDs[i], &AudioInputDescriptor); CheckErr(res);
	    if((AudioInputDescriptor.deviceConnection ==
		SL_DEVCONNECTION_ATTACHED_WIRED)&&
	       (AudioInputDescriptor.deviceScope == SL_DEVSCOPE_USER)&&
	       (AudioInputDescriptor.deviceLocation ==
		SL_DEVLOCATION_HEADSET))
		{
		    mic_deviceID = InputDeviceIDs[i];
		    mic_available = SL_BOOLEAN_TRUE;
		    break;
		}
	    else if((AudioInputDescriptor.deviceConnection ==
		     SL_DEVCONNECTION_INTEGRATED)&&
		    (AudioInputDescriptor.deviceScope ==
		     SL_DEVSCOPE_USER)&&
		    (AudioInputDescriptor.deviceLocation ==
		     SL_DEVLOCATION_HANDSET))
		{
		    mic_deviceID = InputDeviceIDs[i];
		    mic_available = SL_BOOLEAN_TRUE;
		    break;
		}
	}
    /* If neither of the preferred input audio devices is available, no
       point in continuing */
    if (!mic_available) {
	/* Appropriate error message here */
	exit(1);
    }
    /* Initialize arrays required[] and iidArray[] */
    for (i=0;i<MAX_NUMBER_INTERFACES;i++)
	{
	    required[i] = SL_BOOLEAN_FALSE;
	    iidArray[i] = SL_IID_NULL;
	}
    /* Get the optional DEVICE VOLUME interface from the engine */
    res = (*sl)->GetInterface(sl, SL_IID_DEVICEVOLUME,
			      (void*)&devicevolumeItf); CheckErr(res);
    /* Set recording volume of the microphone to -3 dB */
    res = (*devicevolumeItf)->SetVolume(devicevolumeItf, mic_deviceID, -
					300); CheckErr(res);
    /* Setup the data source structure */
    locator_mic.locatorType	= SL_DATALOCATOR_IODEVICE;
    locator_mic.deviceType	= SL_IODEVICE_AUDIOINPUT;
    locator_mic.deviceID	= mic_deviceID;
    locator_mic.device	        = NULL;
    audioSource.pLocator 	= (void *)&locator_mic;
    audioSource.pFormat         = NULL;
    /* Setup the data sink structure */
    uri.locatorType	= SL_DATALOCATOR_URI;
    uri.URI	= (SLchar *) "file:///recordsample.wav";
    mime.formatType	= SL_DATAFORMAT_MIME;
    mime.mimeType	= (SLchar *) "audio/x-wav";
    mime.containerType	= SL_CONTAINERTYPE_WAV;
    audioSink.pLocator	= (void *)&uri;
    audioSink.pFormat	= (void *)&mime;
    /* Create audio recorder */
    res = (*EngineItf)->CreateAudioRecorder(EngineItf, &recorder,
					    &audioSource, &audioSink, 0, iidArray, required); CheckErr(res);
    /* Realizing the recorder in synchronous mode. */
    res = (*recorder)->Realize(recorder, SL_BOOLEAN_FALSE); CheckErr(res);
    /* Get the RECORD interface - it is an implicit interface */
    res = (*recorder)->GetInterface(recorder, SL_IID_RECORD,
				    (void*)&recordItf); CheckErr(res);
    /* Setup to receive position event callbacks */
    res = (*recordItf)->RegisterCallback(recordItf, RecordEventCallback,
					 NULL);
    CheckErr(res);
    /* Set notifications to occur after every second - may be useful in
       updating a recording progress bar */
    res = (*recordItf)->SetPositionUpdatePeriod( recordItf,
						 POSITION_UPDATE_PERIOD); CheckErr(res);
    res = (*recordItf)->SetCallbackEventsMask( recordItf,
					       SL_RECORDEVENT_HEADATNEWPOS); CheckErr(res);
    /* Set the duration of the recording - 30 seconds (30,000
       milliseconds) */
    res = (*recordItf)->SetDurationLimit(recordItf, 30000); CheckErr(res);
    /* Record the audio */
    res = (*recordItf)->SetRecordState(recordItf,SL_RECORDSTATE_RECORDING);
    /* Destroy the recorder object */
    (*recorder)->Destroy(recorder);
}
int sl_main( void )
{
    SLresult
	res;
    SLObjectItf sl;
    /* Create OpenSL ES engine in thread-safe mode */
    SLEngineOption EngineOption[] = {(SLuint32)
				     SL_ENGINEOPTION_THREADSAFE, (SLuint32) SL_BOOLEAN_TRUE};
    res = slCreateEngine( &sl, 1, EngineOption, 0, NULL, NULL);
    CheckErr(res);
    /* Realizing the SL Engine in synchronous mode. */
    res = (*sl)->Realize(sl, SL_BOOLEAN_FALSE); CheckErr(res);
    TestAudioRecording(sl);
    /* Shutdown OpenSL ES */
    (*sl)->Destroy(sl);
    exit(0);
}

	
    
```
