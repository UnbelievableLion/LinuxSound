
##  Rendering a JPEG image without tunnelling 


Tunnelling gives an end-to-end means of decoding and rendering
      an image. If we wanted to do things in the middle - say, overlay
      some text - we would need to have access to the intermediate
      stages. In this section we repeat the previous section, but
      without using tunnelling.


We have to explicitly manage the communication between the
      decode and render components. For the decode component,
      we have to allocate a buffer.
      We don't want to copy data between decode and render
      buffers so the render component _uses_ the
      decoder's output buffers. Then as the decoder fills
      its output buffer, the render component empties that
      same buffer.


There are multiple hiccups along the way

+ Lots of information has to be copied from the
	  decode port to the render port.
	  We can't just use a `memcpy`because the decoder has a structure for an _image_ while the render has a
	  structure for a _video_ , and these
	  do not align.
```

	    
    // need to setup the input for the render with the output of the
    // decoder
    portdef.nSize = sizeof(OMX_PARAM_PORTDEFINITIONTYPE);
    portdef.nVersion.nVersion = OMX_VERSION;
    portdef.nPortIndex = decoder->imageDecoder->outPort;
    OMX_GetParameter(decoder->imageDecoder->handle,
		     OMX_IndexParamPortDefinition, &portdef);

    // Get default values of render
    rportdef.nSize = sizeof(OMX_PARAM_PORTDEFINITIONTYPE);
    rportdef.nVersion.nVersion = OMX_VERSION;
    rportdef.nPortIndex = decoder->imageRender->inPort;
    rportdef.nBufferSize = portdef.nBufferSize;

    ret = OMX_GetParameter(decoder->imageRender->handle,
			   OMX_IndexParamPortDefinition, &rportdef);

    // tell render input what the decoder output will be providing
    //Copy some
    rportdef.format.video.nFrameWidth = portdef.format.image.nFrameWidth;
    rportdef.format.video.nFrameHeight = portdef.format.image.nFrameHeight;
    rportdef.format.video.nStride = portdef.format.image.nStride;
    rportdef.format.video.nSliceHeight = portdef.format.image.nSliceHeight;

    ret = OMX_SetParameter(decoder->imageRender->handle,
			   OMX_IndexParamPortDefinition, &rportdef);
	    
	  
```

+ The decode component has one output buffer
	  while the render component has three input
	  buffers. We re-use one buffer and set the 
	  other two to `NULL`
```

	    
   ret = OMX_AllocateBuffer(decoder->imageDecoder->handle,
			     &decoder->pOutputBufferHeader,
			     decoder->imageDecoder->
			     outPort,
			     NULL,
			     portdef.nBufferSize);

    // and share it with the renderer
    // which has 3 default buffers, 2 minimum
    decoder->ppRenderInputBufferHeader =
	(OMX_BUFFERHEADERTYPE **) malloc(sizeof(void) *
					 decoder->renderInputBufferHeaderCount);

    ret = OMX_UseBuffer(decoder->imageRender->handle,
			&decoder->ppRenderInputBufferHeader[0],
			decoder->imageRender->inPort,
			NULL,
			rportdef.nBufferSize,
			decoder->pOutputBufferHeader->pBuffer);

    int n;
    for (n = 1; n < decoder->renderInputBufferHeaderCount; n++) {
	printState(decoder->imageRender->handle);
	ret = OMX_UseBuffer(decoder->imageRender->handle,
			    &
amp;decoder->ppRenderInputBufferHeader[n],
			    decoder->imageRender->inPort,
			    NULL,
			    0,
			    NULL);
    }
	    
	  
```

+ Even though we feed the size of the shared buffer into `UseBuffer`call, the field `nAllocLen`does not get set correctly
	  (how do we know: because of an illegal parameter
	  error, and then using the debugger to guess at what
	  isn't right).
```

	    
    decoder->ppRenderInputBufferHeader[0]->nAllocLen =
	decoder->pOutputBufferHeader->nAllocLen;
	    
	  
```


Apart from that, it is the usual games of playing with
      state, enabling and disabling ports until it works

```

	/*
Copyright (c) 2012, Matt Ownby
                    Anthong Sale
Copyright (c) 2014: Jan Newmarch

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the copyright holder nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#include <stdio.h>
#include <assert.h>
#include "jpeg.h"

#define TIMEOUT_MS 2000

typedef struct _COMPONENT_DETAILS {
    COMPONENT_T    *component;
    OMX_HANDLETYPE  handle;
    int             inPort;
    int             outPort;
} COMPONENT_DETAILS;

struct _OPENMAX_JPEG_DECODER {
    ILCLIENT_T     *client;
    COMPONENT_DETAILS *imageDecoder;
    COMPONENT_DETAILS *imageRender;

    OMX_BUFFERHEADERTYPE **ppInputBufferHeader;
    int             inputBufferHeaderCount;
    OMX_BUFFERHEADERTYPE *pOutputBufferHeader;
    int             renderInputBufferHeaderCount;
    OMX_BUFFERHEADERTYPE **ppRenderInputBufferHeader;
};

int             bufferIndex = 0;	// index to buffer array

char *err2str(int err) {
    switch (err) {
    case OMX_ErrorInsufficientResources: return "OMX_ErrorInsufficientResources";
    case OMX_ErrorUndefined: return "OMX_ErrorUndefined";
    case OMX_ErrorInvalidComponentName: return "OMX_ErrorInvalidComponentName";
    case OMX_ErrorComponentNotFound: return "OMX_ErrorComponentNotFound";
    case OMX_ErrorInvalidComponent: return "OMX_ErrorInvalidComponent";
    case OMX_ErrorBadParameter: return "OMX_ErrorBadParameter";
    case OMX_ErrorNotImplemented: return "OMX_ErrorNotImplemented";
    case OMX_ErrorUnderflow: return "OMX_ErrorUnderflow";
    case OMX_ErrorOverflow: return "OMX_ErrorOverflow";
    case OMX_ErrorHardware: return "OMX_ErrorHardware";
    case OMX_ErrorInvalidState: return "OMX_ErrorInvalidState";
    case OMX_ErrorStreamCorrupt: return "OMX_ErrorStreamCorrupt";
    case OMX_ErrorPortsNotCompatible: return "OMX_ErrorPortsNotCompatible";
    case OMX_ErrorResourcesLost: return "OMX_ErrorResourcesLost";
    case OMX_ErrorNoMore: return "OMX_ErrorNoMore";
    case OMX_ErrorVersionMismatch: return "OMX_ErrorVersionMismatch";
    case OMX_ErrorNotReady: return "OMX_ErrorNotReady";
    case OMX_ErrorTimeout: return "OMX_ErrorTimeout";
    case OMX_ErrorSameState: return "OMX_ErrorSameState";
    case OMX_ErrorResourcesPreempted: return "OMX_ErrorResourcesPreempted";
    case OMX_ErrorPortUnresponsiveDuringAllocation: return "OMX_ErrorPortUnresponsiveDuringAllocation";
    case OMX_ErrorPortUnresponsiveDuringDeallocation: return "OMX_ErrorPortUnresponsiveDuringDeallocation";
    case OMX_ErrorPortUnresponsiveDuringStop: return "OMX_ErrorPortUnresponsiveDuringStop";
    case OMX_ErrorIncorrectStateTransition: return "OMX_ErrorIncorrectStateTransition";
    case OMX_ErrorIncorrectStateOperation: return "OMX_ErrorIncorrectStateOperation";
    case OMX_ErrorUnsupportedSetting: return "OMX_ErrorUnsupportedSetting";
    case OMX_ErrorUnsupportedIndex: return "OMX_ErrorUnsupportedIndex";
    case OMX_ErrorBadPortIndex: return "OMX_ErrorBadPortIndex";
    case OMX_ErrorPortUnpopulated: return "OMX_ErrorPortUnpopulated";
    case OMX_ErrorComponentSuspended: return "OMX_ErrorComponentSuspended";
    case OMX_ErrorDynamicResourcesUnavailable: return "OMX_ErrorDynamicResourcesUnavailable";
    case OMX_ErrorMbErrorsInFrame: return "OMX_ErrorMbErrorsInFrame";
    case OMX_ErrorFormatNotDetected: return "OMX_ErrorFormatNotDetected";
    case OMX_ErrorContentPipeOpenFailed: return "OMX_ErrorContentPipeOpenFailed";
    case OMX_ErrorContentPipeCreationFailed: return "OMX_ErrorContentPipeCreationFailed";
    case OMX_ErrorSeperateTablesUsed: return "OMX_ErrorSeperateTablesUsed";
    case OMX_ErrorTunnelingUnsupported: return "OMX_ErrorTunnelingUnsupported";
    default: return "unknown error";
    }
}

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

void printColorFormat(unsigned int colorFormat) {
    switch (colorFormat) {
    case    OMX_COLOR_FormatYUV411Planar: printf("   OMX_COLOR_FormatYUV411Planar\n"); break;
    case     OMX_COLOR_FormatYUV411PackedPlanar: printf("    OMX_COLOR_FormatYUV411PackedPlanar\n"); break;
    case     OMX_COLOR_FormatYUV420Planar: printf("    OMX_COLOR_FormatYUV420Planar,\n"); break;
    case     OMX_COLOR_FormatYUV420PackedPlanar: printf("    OMX_COLOR_FormatYUV420PackedPlanar\n"); break;
    case    OMX_COLOR_FormatYUV420SemiPlanar: printf("    OMX_COLOR_FormatYUV420SemiPlanar,\n"); break;
    case     OMX_COLOR_FormatYUV422Planar: printf("    OMX_COLOR_FormatYUV422Planar,\n"); break;
    case     OMX_COLOR_FormatYUV422PackedPlanar: printf("    OMX_COLOR_FormatYUV422PackedPlanar,\n"); break;
    case     OMX_COLOR_FormatYUV422SemiPlanar: printf("    OMX_COLOR_FormatYUV422SemiPlanar,\n"); break;
    }
}



int
portSettingsChanged(OPENMAX_JPEG_DECODER * decoder)
{
    OMX_PARAM_PORTDEFINITIONTYPE portdef,  rportdef;;
    int ret;

    // CLEANUP

    printf("Pport settings changed\n");
    // need to setup the input for the render with the output of the
    // decoder
    portdef.nSize = sizeof(OMX_PARAM_PORTDEFINITIONTYPE);
    portdef.nVersion.nVersion = OMX_VERSION;
    portdef.nPortIndex = decoder->imageDecoder->outPort;
    OMX_GetParameter(decoder->imageDecoder->handle,
		     OMX_IndexParamPortDefinition, &portdef);

    // Get default values of render
    rportdef.nSize = sizeof(OMX_PARAM_PORTDEFINITIONTYPE);
    rportdef.nVersion.nVersion = OMX_VERSION;
    rportdef.nPortIndex = decoder->imageRender->inPort;
    rportdef.nBufferSize = portdef.nBufferSize;

    ret = OMX_GetParameter(decoder->imageRender->handle,
			   OMX_IndexParamPortDefinition, &rportdef);
    if (ret != OMX_ErrorNone) {
	fprintf(stderr, "Error getting render port params %s\n", err2str(ret));
	return OMXJPEG_ERROR_MEMORY;
    }

    // tell render input what the decoder output will be providing
    //Copy some
    rportdef.format.video.nFrameWidth = portdef.format.image.nFrameWidth;
    rportdef.format.video.nFrameHeight = portdef.format.image.nFrameHeight;
    rportdef.format.video.nStride = portdef.format.image.nStride;
    rportdef.format.video.nSliceHeight = portdef.format.image.nSliceHeight;

    ret = OMX_SetParameter(decoder->imageRender->handle,
			   OMX_IndexParamPortDefinition, &rportdef);
    if (ret != OMX_ErrorNone) {
	fprintf(stderr, "Error setting render port params %s\n", err2str(ret));
	return OMXJPEG_ERROR_MEMORY;
    } else {
	printf("Render port params set up ok\n");
    }

    unsigned int    uWidth =
	(unsigned int) portdef.format.image.nFrameWidth;
    unsigned int    uHeight =
	(unsigned int) portdef.format.image.nFrameHeight;
   printf
	("Getting format Compression 0x%x Color Format: 0x%x\n",
	 (unsigned int) portdef.format.image.eCompressionFormat,
	 (unsigned int) portdef.format.image.eColorFormat);
    printColorFormat(portdef.format.image.eColorFormat);

    // enable ports
    OMX_SendCommand(decoder->imageDecoder->handle,
		    OMX_CommandPortEnable,
		    decoder->imageDecoder->outPort, NULL);

    // once the state changes, both ports should become enabled and the
    // render
    // output should generate a settings changed event
    ilclient_wait_for_event(decoder->imageDecoder->component,
			    OMX_EventCmdComplete,
			    OMX_CommandPortEnable, 1,
			    decoder->imageDecoder->outPort, 1, 0,
			    TIMEOUT_MS);
    printf("Decoder output port enabled\n");

    OMX_SendCommand(decoder->imageRender->handle,
		    OMX_CommandPortEnable,
		    decoder->imageRender->inPort, NULL);

    // once the state changes, both ports should become enabled and the
    // render
    // output should generate a settings changed event
    ilclient_wait_for_event(decoder->imageRender->component,
			    OMX_EventCmdComplete,
			    OMX_CommandPortEnable, 1,
			    decoder->imageRender->inPort, 1, 0,
			    TIMEOUT_MS);
    printf("Render input port enabled\n");

    ret = OMX_AllocateBuffer(decoder->imageDecoder->handle,
			     &decoder->pOutputBufferHeader,
			     decoder->imageDecoder->
			     outPort,
			     NULL,
			     portdef.nBufferSize);
    printf("Output port buffer allocated\n");

    if (ret != OMX_ErrorNone) {
	perror("Eror allocating buffer");
	return OMXJPEG_ERROR_MEMORY;
    }

    // and share it with the renderer
    // which has 3 default buffers, 2 minimum
    decoder->ppRenderInputBufferHeader =
	(OMX_BUFFERHEADERTYPE **) malloc(sizeof(void) *
					 decoder->renderInputBufferHeaderCount);
    printState(decoder->imageRender->handle);
			decoder->imageRender->inPort,
    ret = OMX_UseBuffer(decoder->imageRender->handle,
			&decoder->ppRenderInputBufferHeader[0],
			decoder->imageRender->inPort,
			NULL,
			rportdef.nBufferSize,
			decoder->pOutputBufferHeader->pBuffer);
    if (ret != OMX_ErrorNone) {
	fprintf(stderr, "Eror sharing buffer %s\n", err2str(ret));
	return OMXJPEG_ERROR_MEMORY;
    }
    decoder->ppRenderInputBufferHeader[0]->nAllocLen =
	decoder->pOutputBufferHeader->nAllocLen;

    int n;
    for (n = 1; n < decoder->renderInputBufferHeaderCount; n++) {
	printState(decoder->imageRender->handle);
	ret = OMX_UseBuffer(decoder->imageRender->handle,
			    &decoder->ppRenderInputBufferHeader[n],
			    decoder->imageRender->inPort,
			    NULL,
			    0,
			    NULL);
	if (ret != OMX_ErrorNone) {
	    fprintf(stderr, "Eror sharing null buffer %s\n", err2str(ret));
	    return OMXJPEG_ERROR_MEMORY;
	}
    }

    ilclient_wait_for_event(decoder->imageDecoder->component,
			    OMX_EventCmdComplete,
			    OMX_CommandPortEnable, 1,
			    decoder->imageDecoder->outPort, 1, 0,
			    TIMEOUT_MS);
    printf("Decoder output port rnabled\n");

    return OMXJPEG_OK;
}

int
portSettingsChangedAgain(OPENMAX_JPEG_DECODER * decoder)
{
    printf("Port settings changed again\n");
    ilclient_disable_port(decoder->imageDecoder->component,
			  decoder->imageDecoder->outPort);

    OMX_PARAM_PORTDEFINITIONTYPE portdef;

    // need to setup the input for the render with the output of the
    // decoder
    portdef.nSize = sizeof(OMX_PARAM_PORTDEFINITIONTYPE);
    portdef.nVersion.nVersion = OMX_VERSION;
    portdef.nPortIndex = decoder->imageDecoder->outPort;
    OMX_GetParameter(decoder->imageDecoder->handle,
		     OMX_IndexParamPortDefinition, &portdef);


    // enable output of decoder and input of render (ie enable tunnel)
    ilclient_enable_port(decoder->imageDecoder->component,
			 decoder->imageDecoder->outPort);

    // need to wait for this event
    ilclient_wait_for_event(decoder->imageDecoder->component,
			    OMX_EventPortSettingsChanged,
			    decoder->imageDecoder->outPort, 1,
			    0, 0, 0, TIMEOUT_MS);
    return OMXJPEG_OK;
}

int
prepareRender(OPENMAX_JPEG_DECODER * decoder)
{
    decoder->imageRender = malloc(sizeof(COMPONENT_DETAILS));
    if (decoder->imageRender == NULL) {
	perror("malloc image render");
	return OMXJPEG_ERROR_MEMORY;
    }

    int             ret = ilclient_create_component(decoder->client,
						    &decoder->
						    imageRender->
						    component,
						    "video_render",
						    ILCLIENT_DISABLE_ALL_PORTS
						    |
						    ILCLIENT_ENABLE_INPUT_BUFFERS
						    );
    if (ret != 0) {
	perror("image render");
	return OMXJPEG_ERROR_CREATING_COMP;
    }
    // grab the handle for later use
    decoder->imageRender->handle =
	ILC_GET_HANDLE(decoder->imageRender->component);

    // get and store the ports
    OMX_PORT_PARAM_TYPE port;
    port.nSize = sizeof(OMX_PORT_PARAM_TYPE);
    port.nVersion.nVersion = OMX_VERSION;

    OMX_GetParameter(ILC_GET_HANDLE(decoder->imageRender->component),
		     OMX_IndexParamVideoInit, &port);
    if (port.nPorts != 1) {
	return OMXJPEG_ERROR_WRONG_NO_PORTS;
    }
    decoder->imageRender->inPort = port.nStartPortNumber;

    /*
      decoder->imageRender->outPort = port.nStartPortNumber + 1;
    */

    // the default is 3 buffers, but we want to use only one

    // query output buffer requirements for render
    OMX_PARAM_PORTDEFINITIONTYPE portdef;
    portdef.nSize = sizeof(OMX_PARAM_PORTDEFINITIONTYPE);
    portdef.nVersion.nVersion = OMX_VERSION;
    portdef.nPortIndex = decoder->imageRender->inPort;
    OMX_GetParameter(decoder->imageRender->handle,
		     OMX_IndexParamPortDefinition, &portdef);
    decoder->renderInputBufferHeaderCount = portdef.nBufferCountActual;

    /* later settings params doesn't like this!
    portdef.nBufferCountActual = 1;
    ret =  OMX_SetParameter(decoder->imageRender->handle,
		     OMX_IndexParamPortDefinition, &portdef);
    if (ret != OMX_ErrorNone) {
	fprintf(stderr, "Eror setting render buffers to one %s\n", err2str(ret));
	return OMXJPEG_ERROR_MEMORY;
    }
    */

    decoder->pOutputBufferHeader = NULL;

    return OMXJPEG_OK;
}

int
prepareImageDecoder(OPENMAX_JPEG_DECODER * decoder)
{
    decoder->imageDecoder = malloc(sizeof(COMPONENT_DETAILS));
    if (decoder->imageDecoder == NULL) {
	perror("malloc image decoder");
	return OMXJPEG_ERROR_MEMORY;
    }

    int ret = ilclient_create_component(decoder->client,
					&decoder->
					imageDecoder->
					component,
					"image_decode",
					ILCLIENT_DISABLE_ALL_PORTS
					|
					ILCLIENT_ENABLE_INPUT_BUFFERS
					|
					ILCLIENT_ENABLE_OUTPUT_BUFFERS);

    if (ret != 0) {
	perror("image decode");
	return OMXJPEG_ERROR_CREATING_COMP;
    }
    // grab the handle for later use in OMX calls directly
    decoder->imageDecoder->handle =
	ILC_GET_HANDLE(decoder->imageDecoder->component);

    // get and store the ports
    OMX_PORT_PARAM_TYPE port;
    port.nSize = sizeof(OMX_PORT_PARAM_TYPE);
    port.nVersion.nVersion = OMX_VERSION;

    OMX_GetParameter(decoder->imageDecoder->handle,
		     OMX_IndexParamImageInit, &port);
    if (port.nPorts != 2) {
	return OMXJPEG_ERROR_WRONG_NO_PORTS;
    }
    decoder->imageDecoder->inPort = port.nStartPortNumber;
    decoder->imageDecoder->outPort = port.nStartPortNumber + 1;

   decoder->pOutputBufferHeader = NULL;

    return OMXJPEG_OK;
}

int
startupImageRender(OPENMAX_JPEG_DECODER * decoder)
{
    int ret;

    // We don't set any buffers - just change states

    // move to idle
    ilclient_change_component_state(decoder->imageRender->component,
				    OMX_StateIdle);
   ret = ilclient_wait_for_event(decoder->imageRender->component,
				  OMX_EventCmdComplete,
				  OMX_StateIdle, 0, 0, 1, 0,
				  TIMEOUT_MS);
    if (ret != 0) {
	fprintf(stderr, "Did not receive idle stat %d\n", ret);
	// return OMXJPEG_ERROR_EXECUTING;
    } else {
	printf("Render now in idle state\n");
    }

    // start executing the render 
    ret = OMX_SendCommand(decoder->imageRender->handle,
			  OMX_CommandStateSet, OMX_StateExecuting, NULL);
    if (ret != 0) {
	fprintf(stderr, "Error starting image render %x\n", ret);
	return OMXJPEG_ERROR_EXECUTING;
    }
    ret = ilclient_wait_for_event(decoder->imageRender->component,
				  OMX_EventCmdComplete,
				  OMX_StateExecuting, 0, 0, 1, 0,
				  TIMEOUT_MS);
    if (ret != 0) {
	fprintf(stderr, "Did not receive executing stat %d\n", ret);
	// return OMXJPEG_ERROR_EXECUTING;
    } else {
	printf("Render now in executing state\n");
    }


    return OMXJPEG_OK;
}

int
startupImageDecoder(OPENMAX_JPEG_DECODER * decoder)
{
    // move to idle
    ilclient_change_component_state(decoder->imageDecoder->component,
				    OMX_StateIdle);

    // set input image format
    OMX_IMAGE_PARAM_PORTFORMATTYPE imagePortFormat;
    memset(&imagePortFormat, 0, sizeof(OMX_IMAGE_PARAM_PORTFORMATTYPE));
    imagePortFormat.nSize = sizeof(OMX_IMAGE_PARAM_PORTFORMATTYPE);
    imagePortFormat.nVersion.nVersion = OMX_VERSION;
    imagePortFormat.nPortIndex = decoder->imageDecoder->inPort;
    imagePortFormat.eCompressionFormat = OMX_IMAGE_CodingJPEG;
    OMX_SetParameter(decoder->imageDecoder->handle,
		     OMX_IndexParamImagePortFormat, &imagePortFormat);

    // get buffer requirements
    OMX_PARAM_PORTDEFINITIONTYPE portdef;
    portdef.nSize = sizeof(OMX_PARAM_PORTDEFINITIONTYPE);
    portdef.nVersion.nVersion = OMX_VERSION;
    portdef.nPortIndex = decoder->imageDecoder->inPort;
    OMX_GetParameter(decoder->imageDecoder->handle,
		     OMX_IndexParamPortDefinition, &portdef);

    // enable the port and setup the buffers
    OMX_SendCommand(decoder->imageDecoder->handle,
		    OMX_CommandPortEnable,
		    decoder->imageDecoder->inPort, NULL);
    decoder->inputBufferHeaderCount = portdef.nBufferCountActual;
    // allocate pointer array
    decoder->ppInputBufferHeader =
	(OMX_BUFFERHEADERTYPE **) malloc(sizeof(void) *
					 decoder->inputBufferHeaderCount);
    // allocate each buffer
    int             i;
    for (i = 0; i < decoder->inputBufferHeaderCount; i++) {
	if (OMX_AllocateBuffer(decoder->imageDecoder->handle,
			       &decoder->ppInputBufferHeader[i],
			       decoder->imageDecoder->inPort,
			       (void *) i,
			       portdef.nBufferSize) != OMX_ErrorNone) {
	    perror("Allocate decode buffer");
	    return OMXJPEG_ERROR_MEMORY;
	}
    }
    // wait for port enable to complete - which it should once buffers are 
    // assigned
    int             ret =
	ilclient_wait_for_event(decoder->imageDecoder->component,
				OMX_EventCmdComplete,
				OMX_CommandPortEnable, 0,
				decoder->imageDecoder->inPort, 0,
				0, TIMEOUT_MS);
    if (ret != 0) {
	fprintf(stderr, "Did not get port enable %d\n", ret);
	return OMXJPEG_ERROR_EXECUTING;
    } else {
	printf("Ddecoder input port enabled after buffers allocated\n");
    }

    ret = ilclient_wait_for_event(decoder->imageDecoder->component,
				  OMX_EventCmdComplete,
				  OMX_StateIdle, 0, 0, 1, 0,
				  TIMEOUT_MS);
    if (ret != 0) {
	fprintf(stderr, "Did not receive executing stat %d\n", ret);
	// return OMXJPEG_ERROR_EXECUTING;
    } else {
	printf("Decoder now in idle state\n");
    }

    // start executing the decoder 
    ret = OMX_SendCommand(decoder->imageDecoder->handle,
			  OMX_CommandStateSet, OMX_StateExecuting, NULL);
    if (ret != 0) {
	fprintf(stderr, "Error starting image decoder %x\n", ret);
	return OMXJPEG_ERROR_EXECUTING;
    }
    ret = ilclient_wait_for_event(decoder->imageDecoder->component,
				  OMX_EventCmdComplete,
				  OMX_StateExecuting, 0, 0, 1, 0,
				  TIMEOUT_MS);
    if (ret != 0) {
	fprintf(stderr, "Did not receive executing stat %d\n", ret);
	// return OMXJPEG_ERROR_EXECUTING;
    }

    return OMXJPEG_OK;
}

// this function run the boilerplate to setup the openmax components;
int
setupOpenMaxJpegDecoder(OPENMAX_JPEG_DECODER ** pDecoder)
{
    *pDecoder = malloc(sizeof(OPENMAX_JPEG_DECODER));
    if (pDecoder[0] == NULL) {
	perror("malloc decoder");
	return OMXJPEG_ERROR_MEMORY;
    }
    memset(*pDecoder, 0, sizeof(OPENMAX_JPEG_DECODER));

    if ((pDecoder[0]->client = ilclient_init()) == NULL) {
	perror("ilclient_init");
	return OMXJPEG_ERROR_ILCLIENT_INIT;
    }

    if (OMX_Init() != OMX_ErrorNone) {
	ilclient_destroy(pDecoder[0]->client);
	perror("OMX_Init");
	return OMXJPEG_ERROR_OMX_INIT;
    }
    // prepare the image decoder
    int             ret = prepareImageDecoder(pDecoder[0]);
    if (ret != OMXJPEG_OK)
	return ret;

    ret = prepareRender(pDecoder[0]);
    if (ret != OMXJPEG_OK)
	return ret;

    ret = startupImageDecoder(pDecoder[0]);
    if (ret != OMXJPEG_OK)
	return ret;

    ret = startupImageRender(pDecoder[0]);
    if (ret != OMXJPEG_OK)
	return ret;

    return OMXJPEG_OK;
}

int
renderImage(OPENMAX_JPEG_DECODER * decoder) {
    int ret;

    printf("Rendering image\n");
    printState(decoder->imageDecoder->handle);

    // setup render buffer
    decoder->ppRenderInputBufferHeader[0]->nFilledLen =
	decoder->pOutputBufferHeader->nFilledLen;
    decoder->ppRenderInputBufferHeader[0]->nFlags = OMX_BUFFERFLAG_EOS;

    printf("Render buffer has %d\n",
	   decoder->ppRenderInputBufferHeader[0]->nFilledLen);
    ret = OMX_EmptyThisBuffer(decoder->imageRender->handle,
			     decoder->ppRenderInputBufferHeader[0]);
    if (ret != OMX_ErrorNone) {
	perror("Emptying render input buffer");
	fprintf(stderr, "Error code %s\n", err2str(ret));
	return OMXJPEG_ERROR_MEMORY;
    } else {
	printf("Called to empty render input buffer\n");
    }

    return OMXJPEG_OK;
}


// this function passed the jpeg image buffer in, and returns the decoded
// image
int
decodeImage(OPENMAX_JPEG_DECODER * decoder, char *sourceImage,
	    size_t imageSize)
{
    char           *sourceOffset = sourceImage;	// we store a seperate
						// buffer ot image so we
						// can offset it
    size_t          toread = 0;	// bytes left to read from buffer
    toread += imageSize;
    int             bFilled = 0;	// have we filled our output
					// buffer
    bufferIndex = 0;

    while (toread > 0) {
	// get next buffer from array
	OMX_BUFFERHEADERTYPE *pBufHeader =
	    decoder->ppInputBufferHeader[bufferIndex];

	// step index and reset to 0 if required
	bufferIndex++;
	if (bufferIndex >= decoder->inputBufferHeaderCount)
	    bufferIndex = 0;

	// work out the next chunk to load into the decoder
	if (toread > pBufHeader->nAllocLen)
	    pBufHeader->nFilledLen = pBufHeader->nAllocLen;
	else
	    pBufHeader->nFilledLen = toread;

	toread = toread - pBufHeader->nFilledLen;

	// pass the bytes to the buffer
	memcpy(pBufHeader->pBuffer, sourceOffset, pBufHeader->nFilledLen);
	printf("Read into buffer %d\n", pBufHeader->nFilledLen);

	// update the buffer pointer and set the input flags

	sourceOffset = sourceOffset + pBufHeader->nFilledLen;
	pBufHeader->nOffset = 0;
	pBufHeader->nFlags = 0;
	if (toread <= 0) {
	    pBufHeader->nFlags = OMX_BUFFERFLAG_EOS;
	    printf("Added EOS to last inout buffer\n");
	}
	// empty the current buffer
	printf("Emptying buffer\n");
	int             ret =
	    OMX_EmptyThisBuffer(decoder->imageDecoder->handle,
				pBufHeader);

	if (ret != OMX_ErrorNone) {
	    perror("Empty input buffer");
	    fprintf(stderr, "return code %x\n", ret);
	    return OMXJPEG_ERROR_MEMORY;
	}
	// wait for buffer to empty or port changed event
	int             done = 0;
	while ((done == 0) || (decoder->pOutputBufferHeader == NULL)) {
	    if (decoder->pOutputBufferHeader == NULL) {
		ret =
		    ilclient_wait_for_event
		    (decoder->imageDecoder->component,
		     OMX_EventPortSettingsChanged,
		     decoder->imageDecoder->outPort, 0, 0, 1, 0, 5);

		if (ret == 0) {
		    portSettingsChanged(decoder);
		}
	    } else {
		ret =
		    ilclient_remove_event(decoder->imageDecoder->component,
					  OMX_EventPortSettingsChanged,
					  decoder->imageDecoder->outPort,
					  0, 0, 1);
		if (ret == 0)
		    portSettingsChangedAgain(decoder);

	    }

	    // check to see if buffer is now empty
	    if (pBufHeader->nFilledLen == 0)
		done = 1;

	    if ((done == 0)
		|| (decoder->pOutputBufferHeader == NULL)) {
		printf("Buffer is now size %d\n", pBufHeader->nFilledLen);
		sleep(1);
	    }
	}

	// fill the buffer if we have created the buffer
	if (bFilled == 0) {
	    if ((decoder->pOutputBufferHeader == NULL)) {
		portSettingsChanged(decoder);
	    }
	    OMX_PARAM_U32TYPE param;
	    param.nSize = sizeof(OMX_PARAM_U32TYPE);
	    param.nVersion.nVersion = OMX_VERSION;
	    param.nPortIndex = decoder->imageDecoder->outPort;
	   
	    OMX_GetParameter(decoder->imageDecoder->handle,
		     OMX_IndexParamActiveStream, &param);
	    printf("Active stream %d\n", param.nU32);

	    printf("Trying to fill output buffer\n");
	    printState(decoder->imageDecoder->handle);
	    ret = OMX_FillThisBuffer(decoder->imageDecoder->handle,
				     decoder->pOutputBufferHeader);
	    
	    if (ret != OMX_ErrorNone) {
		perror("Filling output buffer");
		fprintf(stderr, "Error code %x\n", ret);
		return OMXJPEG_ERROR_MEMORY;
	    }

	    bFilled = 1;
	}
    }

    // wait for buffer to fill
    /*
     * while(pBufHeader->nFilledLen == 0) { sleep(5); } 
     */

    // wait for end of stream events
    int             ret =
	ilclient_wait_for_event(decoder->imageDecoder->component,
				OMX_EventBufferFlag,
				decoder->imageDecoder->outPort, 1,
				OMX_BUFFERFLAG_EOS, 1,
				0, 2);
    if (ret != 0) {
	fprintf(stderr, "No EOS event on image decoder %d\n", ret);
    } else  {
	fprintf(stderr, "EOS event on image decoder %d\n", ret);
    }

    printf("Resized %d\n", decoder->pOutputBufferHeader->nFilledLen);
    FILE *fp = fopen("out", "w");
    int n;
    for (n = 0; n < decoder->pOutputBufferHeader->nFilledLen; n++) {
	//fputc(decoder->pOutputBufferHeader->pBuffer[n], fp);
	fputc(decoder->ppRenderInputBufferHeader[0]->pBuffer[n], fp);
    }
    fclose(fp);
    printf("File written\n");

    renderImage(decoder);

    return OMXJPEG_OK;
}

// this function cleans up the decoder.
void
cleanup(OPENMAX_JPEG_DECODER * decoder)
{
    // flush everything through
    OMX_SendCommand(decoder->imageDecoder->handle,
		    OMX_CommandFlush, decoder->imageDecoder->outPort,
		    NULL);
    ilclient_wait_for_event(decoder->imageDecoder->component,
			    OMX_EventCmdComplete, OMX_CommandFlush, 0,
			    decoder->imageDecoder->outPort, 0, 0,
			    TIMEOUT_MS);

    OMX_SendCommand(decoder->imageDecoder->handle, OMX_CommandPortDisable,
		    decoder->imageDecoder->inPort, NULL);

    ilclient_wait_for_event(decoder->imageDecoder->component,
			    OMX_EventCmdComplete, OMX_CommandPortDisable,
			    0, decoder->imageDecoder->outPort, 0, 0,
			    TIMEOUT_MS);

    int             i = 0;
    for (i = 0; i < decoder->inputBufferHeaderCount; i++) {
	OMX_BUFFERHEADERTYPE *vpBufHeader =
	    decoder->ppInputBufferHeader[i];

	OMX_FreeBuffer(decoder->imageDecoder->handle,
		       decoder->imageDecoder->inPort, vpBufHeader);
    }

    ilclient_wait_for_event(decoder->imageDecoder->component,
			    OMX_EventCmdComplete, OMX_CommandPortDisable,
			    0, decoder->imageDecoder->inPort, 0, 0,
			    TIMEOUT_MS);

    OMX_FreeBuffer(decoder->imageDecoder->handle,
		   decoder->imageDecoder->outPort,
		   decoder->pOutputBufferHeader);

    ilclient_wait_for_event(decoder->imageDecoder->component,
			    OMX_EventCmdComplete, OMX_CommandPortDisable,
			    0, decoder->imageDecoder->outPort, 0, 0,
			    TIMEOUT_MS);

    ilclient_change_component_state(decoder->imageDecoder->component,
				    OMX_StateIdle);


    ilclient_change_component_state(decoder->imageDecoder->component,
				    OMX_StateLoaded);


    ilclient_wait_for_event(decoder->imageDecoder->component,
			    OMX_EventCmdComplete, OMX_CommandStateSet, 0,
			    OMX_StateLoaded, 0, 0, TIMEOUT_MS);

    OMX_Deinit();

    if (decoder->client != NULL) {
	ilclient_destroy(decoder->client);
    }
}

int
main(int argc, char *argv[])
{
    OPENMAX_JPEG_DECODER *pDecoder;
    char           *sourceImage;
    size_t          imageSize;
    int             s;
    if (argc < 2) {
	printf("Usage: %s <filename>\n", argv[0]);
	return -1;
    }
    FILE           *fp = fopen(argv[1], "rb");
    if (!fp) {
	printf("File %s not found.\n", argv[1]);
    }
    fseek(fp, 0L, SEEK_END);
    imageSize = ftell(fp);
    fseek(fp, 0L, SEEK_SET);
    sourceImage = malloc(imageSize);
    assert(sourceImage != NULL);
    s = fread(sourceImage, 1, imageSize, fp);
    assert(s == imageSize);
    fclose(fp);
    bcm_host_init();
    s = setupOpenMaxJpegDecoder(&pDecoder);
    assert(s == 0);
    s = decodeImage(pDecoder, sourceImage, imageSize);
    assert(s == 0);

    sleep(10);

    cleanup(pDecoder);
    free(sourceImage);
    printf("Success\n");
    return 0;
}

      
```


Copyright © Jan Newmarch, jan@newmarch.name





"Programming and Using Linux Sound - in depth"by [Jan Newmarch](https://jan.newmarch.name) is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/) .


Based on a work at [https://jan.newmarch.name/LinuxSound/](https://jan.newmarch.name/LinuxSound/) .


If you like this book, please contribute using Flattr


or donate using PayPal
![alt text](https://www.paypalobjects.com/WEBSCR-640-20110401-1/en_AU/i/scr/pixel.gif)