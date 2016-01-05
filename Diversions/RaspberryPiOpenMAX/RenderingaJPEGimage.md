
##  Rendering a JPEG image 


In order to display am image we need to _render_ it
on some output device. There is no specific component to
render images. Broadcom has a `video_render`which will accept _both_ a video stream or a single image.
Now this component only has one input port, and that port is
a _video_ port. If we want to take an image from an output _image_ port, we would have to play some format
conversion games. Or, we can connect an image output port
to a video input port by using a tunnel, and let the
components sort it out themselves. This is much easier!


To render a JPEG image, we only need to use an `image_decode`and a `video_render`component. We need to set up the input port for the decoder
as in the last example. The video render component has no
output port so nothing needs to be done for that.
The two ports which are  connected by a tunnel do all necessary
setups and conversions themselves. So this is actually
simpler than the last program: load and empty input
buffers with the JPEG image, setup the tunnel
when port settings change, and ... that's
it! Note that we still defer setting up the tunnel
until the port settings have changed - otherwise
the buffer sizes would be wrong.


The program is [renderjpeg.c](renderjpeg.c) 

```cpp
/*
Copyright (c) 2012, Matt Ownby
                    Anthong Sale
Copyright (c) 2014, Jan Newmarch

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
};

int             bufferIndex = 0;	// index to buffer array

int
portSettingsChanged(OPENMAX_JPEG_DECODER * decoder)
{
    OMX_PARAM_PORTDEFINITIONTYPE portdef;
    int ret;

    printf("Port settings changed\n");

    // disable ports
    OMX_SendCommand(decoder->imageDecoder->handle,
		    OMX_CommandPortDisable,
		    decoder->imageDecoder->outPort, NULL);
    OMX_SendCommand(decoder->imageRender->handle,
		    OMX_CommandPortDisable,
		    decoder->imageRender->inPort, NULL);

    // state to idle
    OMX_SendCommand(decoder->imageDecoder->handle,
		    OMX_CommandStateSet, OMX_StateIdle, NULL);
     OMX_SendCommand(decoder->imageRender->handle,
		    OMX_CommandStateSet, OMX_StateIdle, NULL);

    // establish tunnel between decoder output and render input
    ret = OMX_SetupTunnel(decoder->imageDecoder->handle,
		    decoder->imageDecoder->outPort,
		    decoder->imageRender->handle,
		    decoder->imageRender->inPort);
    if (ret != OMX_ErrorNone) {
	fprintf(stderr, "Error setting up tunnel %X\n", ret);
	return OMXJPEG_ERROR_MEMORY;
    } else {
	printf("Tunnel set up ok\n");
    }

    // wait for ports to become disabled
    ilclient_wait_for_event(decoder->imageDecoder->component,
			    OMX_EventCmdComplete,
			    OMX_CommandPortDisable, 1,
			    decoder->imageDecoder->outPort, 1, 0,
			    TIMEOUT_MS);
    ilclient_wait_for_event(decoder->imageRender->component,
			    OMX_EventCmdComplete, OMX_CommandPortDisable, 1,
			    decoder->imageRender->inPort, 1, 0,
			    TIMEOUT_MS);
    printf("Port disable complete\n");

    // enable ports
    OMX_SendCommand(decoder->imageDecoder->handle,
		    OMX_CommandPortEnable,
		    decoder->imageDecoder->outPort, NULL);
    OMX_SendCommand(decoder->imageRender->handle,
		    OMX_CommandPortEnable,
		    decoder->imageRender->inPort, NULL);

    // wait for state change complete
    ilclient_wait_for_event(decoder->imageDecoder->component,
			    OMX_EventCmdComplete,
			    OMX_CommandStateSet, 1,
			    OMX_StateIdle, 1, 0, TIMEOUT_MS);
    printf("Decoder in idle state\n");

    ilclient_wait_for_event(decoder->imageRender->component,
			    OMX_EventCmdComplete,
			    OMX_CommandStateSet, 1,
			    OMX_StateIdle, 1, 0, TIMEOUT_MS);
    printf("Render in idle state\n");

    ilclient_wait_for_event(decoder->imageDecoder->component,
			    OMX_EventCmdComplete,
			    OMX_CommandPortEnable, 1,
			    decoder->imageDecoder->outPort, 1, 0,
			    TIMEOUT_MS);
    ilclient_wait_for_event(decoder->imageRender->component,
			    OMX_EventCmdComplete, OMX_CommandPortEnable, 1,
			    decoder->imageRender->inPort, 1, 0,
			    TIMEOUT_MS);
    printf("Ports re-enabled\n");

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

    int             ret = ilclient_create_component(decoder->client,
						    &decoder->
						    imageDecoder->
						    component,
						    "image_decode",
						    ILCLIENT_DISABLE_ALL_PORTS
						    |
						    ILCLIENT_ENABLE_INPUT_BUFFERS);

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
    int bTunnelCreated = 0;			// buffer

    bufferIndex = 0;

    OMX_BUFFERHEADERTYPE *pBufHeader;
    while (toread > 0) {
	// get next buffer from array
	pBufHeader =
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

	// update the buffer pointer and set the input flags

	sourceOffset = sourceOffset + pBufHeader->nFilledLen;
	pBufHeader->nOffset = 0;
	pBufHeader->nFlags = 0;
	if (toread <= 0) {
	    pBufHeader->nFlags = OMX_BUFFERFLAG_EOS;
	    printf("EOS added to stream\n");
	}
	printf("Input buffer called to empty %d\n",
	       pBufHeader->nFilledLen);

	// empty the current buffer
	int             ret =
	    OMX_EmptyThisBuffer(decoder->imageDecoder->handle,
				pBufHeader);

	if (ret != OMX_ErrorNone) {
	    fprintf(stderr, "Empty input buffer return code %x\n", ret);
	    return OMXJPEG_ERROR_MEMORY;
	}

	// wait for buffer to empty or port changed event
	int             done = 0;
	//while ((done == 0) || (decoder->pOutputBufferHeader == NULL)) {
	while (done == 0) {
	    // if (decoder->pOutputBufferHeader == NULL) {
	    if (! bTunnelCreated) {
		printf("Tunnel not yet created\n");
		ret =
		    ilclient_wait_for_event
		    (decoder->imageDecoder->component,
		     OMX_EventPortSettingsChanged,
		     decoder->imageDecoder->outPort, 0, 0, 1, 0, 5);

		if ((ret == 0) && ! bTunnelCreated) {
		    portSettingsChanged(decoder);
		    bTunnelCreated = 1;
		}
	    }

	    // check to see if buffer is now empty
	    if (pBufHeader->nFilledLen == 0) {
		done = 1;
		printf("Input buffer finished emptying\n");
	    } else {
		printf("Still %d in input buffer\n", 
		       pBufHeader->nFilledLen);
		// is there an event we can wait on instead of this?
		sleep(1);
	    } 
	}
    }

    // wait for end of stream events
    int             ret =
	ilclient_wait_for_event(decoder->imageDecoder->component,
				OMX_EventBufferFlag,
				decoder->imageDecoder->outPort, 1,
				OMX_BUFFERFLAG_EOS, 1,
				0, 2);
    if (ret != 0) {
	fprintf(stderr, "No EOS event on image decoder %d\n", ret);
    } else {
	printf("EOS event on decoder\n");
    }
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
    OMX_SendCommand(decoder->imageRender->handle, OMX_CommandFlush,
		    decoder->imageRender->inPort, NULL);
    ilclient_wait_for_event(decoder->imageRender->component,
			    OMX_EventCmdComplete, OMX_CommandFlush, 0,
			    decoder->imageRender->inPort, 1, 0,
			    TIMEOUT_MS);

    OMX_SendCommand(decoder->imageDecoder->handle, OMX_CommandPortDisable,
		    decoder->imageDecoder->inPort, NULL);

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

    OMX_SendCommand(decoder->imageDecoder->handle, OMX_CommandPortDisable,
		    decoder->imageDecoder->outPort, NULL);
    ilclient_wait_for_event(decoder->imageDecoder->component,
			    OMX_EventCmdComplete, OMX_CommandPortDisable,
			    0, decoder->imageDecoder->outPort, 0, 0,
			    TIMEOUT_MS);

    OMX_SendCommand(decoder->imageRender->handle, OMX_CommandPortDisable,
		    decoder->imageRender->inPort, NULL);
    ilclient_wait_for_event(decoder->imageRender->component,
			    OMX_EventCmdComplete, OMX_CommandPortDisable,
			    0, decoder->imageRender->inPort, 0, 0,
			    TIMEOUT_MS);

    OMX_SetupTunnel(decoder->imageDecoder->handle,
		    decoder->imageDecoder->outPort, NULL, 0);
    OMX_SetupTunnel(decoder->imageRender->handle,
		    decoder->imageRender->inPort, NULL, 0);

    ilclient_change_component_state(decoder->imageDecoder->component,
				    OMX_StateIdle);
    ilclient_change_component_state(decoder->imageRender->component,
				    OMX_StateIdle);

    ilclient_wait_for_event(decoder->imageDecoder->component,
			    OMX_EventCmdComplete, OMX_CommandStateSet, 0,
			    OMX_StateIdle, 0, 0, TIMEOUT_MS);
    ilclient_wait_for_event(decoder->imageRender->component,
			    OMX_EventCmdComplete, OMX_CommandStateSet, 0,
			    OMX_StateIdle, 0, 0, TIMEOUT_MS);

    ilclient_change_component_state(decoder->imageDecoder->component,
				    OMX_StateLoaded);
    ilclient_change_component_state(decoder->imageRender->component,
				    OMX_StateLoaded);

    ilclient_wait_for_event(decoder->imageDecoder->component,
			    OMX_EventCmdComplete, OMX_CommandStateSet, 0,
			    OMX_StateLoaded, 0, 0, TIMEOUT_MS);
    ilclient_wait_for_event(decoder->imageRender->component,
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
    printf("File size is %d\n", imageSize);
    bcm_host_init();
    s = setupOpenMaxJpegDecoder(&pDecoder);
    assert(s == 0);
    s = decodeImage(pDecoder, sourceImage, imageSize);
    assert(s == 0);

    // the image will be displayed until the program exits 
    sleep(100);
    cleanup(pDecoder);
    free(sourceImage);
    return 0;
}
```
