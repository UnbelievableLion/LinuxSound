#  Decoding a JPEG image 

OpenMAX on the RPi has a standard component
 `OMX.broadcom.image_decode`.
      The RPi documentation for it is
 [
	here ] (http://home.nouwen.name/RaspberryPi/documentation/ilcomponents/image_decode.html)
. It has two ports. The input port has (3) buffers to take a JPEG
      image, and one output port for the decoded image.
      The input buffers have a default size, and if the image is large you just
      cycle through them, filling and emptying each buffer in turn.

The program starts off fairly easily in
 `main`by reading the JPEG file into a byte-buffer of the right size.
      The call to
 `bcm_host_init`is required to
      initialise the Broadcom libraries. The JPEG image decoder
      is then created and asked to decode the image.
```sh_cpp

	
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
    s = setupOpenMaxJpegDecoder(pDecoder);
    assert(s == 0);
    s = decodeImage(pDecoder, sourceImage, imageSize);
    assert(s == 0);
    cleanup(pDecoder);
    free(sourceImage);
    return 0;
}
	
      
```


The call to
 `setupOpenMaxJpegDecoder`builds some
      data structures and calls to
 `prepareImageDecoder`to initialise the decoder and
 `startupImageDecoder`to move it into executing state, so that it can then decode
      the image.
```sh_cpp

	
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

    ret = startupImageDecoder(pDecoder[0]);
    if (ret != OMXJPEG_OK)
	return ret;

    return OMXJPEG_OK;
}
	
      
```


The call to
 `prepareImageDecoder`creates the
      component and establishes its input and output port numbers
      (which should be 320 and 321 respectively by the OpenMAX
      specification). These two ports are disabled, but they
      are enabled to have buffers.

The function
 `startupImageDecoder`is a heavy-duty
      function. It has to establish the format that it will
      accept from the input file by
```sh_cpp

	
    // set input image format
    OMX_IMAGE_PARAM_PORTFORMATTYPE imagePortFormat;
    memset(imagePortFormat, 0, sizeof(OMX_IMAGE_PARAM_PORTFORMATTYPE));
    imagePortFormat.nSize = sizeof(OMX_IMAGE_PARAM_PORTFORMATTYPE);
    imagePortFormat.nVersion.nVersion = OMX_VERSION;
    imagePortFormat.nPortIndex = decoder->imageDecoder->inPort;
    imagePortFormat.eCompressionFormat = OMX_IMAGE_CodingJPEG;
    OMX_SetParameter(decoder->imageDecoder->handle,
		     OMX_IndexParamImagePortFormat, imagePortFormat);
	
      
```


Then it queries for the buffer requirements, building an
 ` OMX_PARAM_PORTDEFINITIONTYPE portdef`structure and populating it with a get parameter call.
```sh_cpp

	
    // get buffer requirements
    OMX_PARAM_PORTDEFINITIONTYPE portdef;
    portdef.nSize = sizeof(OMX_PARAM_PORTDEFINITIONTYPE);
    portdef.nVersion.nVersion = OMX_VERSION;
    portdef.nPortIndex = decoder->imageDecoder->inPort;
    OMX_GetParameter(decoder->imageDecoder->handle,
		     OMX_IndexParamPortDefinition, portdef);
	
      
```


Then we can make a call to enable the input port,
      allocate the input buffers and wait for the port
      to become enabled
```sh_cpp

	
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
			       >ppInputBufferHeader[i],
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
	
      
```


Finally, we can move the component into executing state.
      But being paranoic about the behaviour of this API,
      we wait to ensure that it actually does make the state
      transition requested:
```sh_cpp

	
    // start executing the decoder 
    ret = OMX_SendCommand(decoder->imageDecoder-gt;handle,
			  OMX_CommandStateSet, OMX_StateExecuting, NULL);
    if (ret != 0) {
	fprintf(stderr, "Error starting image decoder %x\n", ret);
	return OMXJPEG_ERROR_EXECUTING;
    }
    ret = ilclient_wait_for_event(decoder-gt;imageDecoder-gt;component,
				  OMX_EventCmdComplete,
				  OMX_StateExecuting, 0, 0, 1, 0,
				  TIMEOUT_MS);
    if (ret != 0) {
	fprintf(stderr, "Did not receive executing stat %d\n", ret);
	// return OMXJPEG_ERROR_EXECUTING;
    }
	
      
```


The function
 `decodeImage`starts up normally enough.
      It loads the input buffers in a circular fashion
      from the JPEG image loaded
      into the
 `sourceImage`array.
      Each buffer is emptied by a call to
 ` OMX_EmptyThisBuffer`. When the entire image
      has been loaded, the final buffer has the
 ` OMX_BUFFERFLAG_EOS`flag set to indicate
      that the image is complete.

The snag with this component is that you don't know how large the decoded
      image will be until the decoder has done at least some work on it.
      So while the input buffers can be assigned statically up front,
      filled and emptied, we don't know what the size of the
      output buffer should be.
      Fortunately OpneMAX manages this
      by raising
      a
 `PortSettingsChanged`event
      when enough information is gained from the JPEG image
      to know the size of the decoded image.

If we were into concurrent programming, we would catch
      a
 `PortSettingsChanged`event in an
      event handling thread and work from there.
      The
 `ilclient`library tries to force a
      sequential mode of operation. So whenever a buffer
      is emptied, the application will go into a loop
      either waiting for a
 `PortSettingsChanged`event to occur and timing out after 5 milliseconds
      (I think)
      if it doesn't or exiting if the input buffer is empty.
      This code is a bit messy!
```sh_cpp

	
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
	
      
```


If a
 `PortSettingsChanged`event occurs,
      the application calls
 `portSettingsChanged`in the main thread. This queries the (single) output port
      for the width and height values now set, switches
      the component to enabled state, allocates a buffer
      and waits for it to move to enabled state.
      We can also collect information about the
      format of the decoded image as well as other
      features such as size.

Once the output buffer has been created, we can make a
      call to fill the buffer. We should only have to do this once,
      so a flag
 `bFilled`is used to control this.
```sh_cpp

	
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
		     OMX_IndexParamActiveStream, param);
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
	
      
```


Once the input buffers have been filled and emptied
      the output buffer has been sized, allocated and
      a call made to fill it, the application has nothing
      to do but wait until the output buffer is filled.
      OpenMAX should generate a
 `OMX_BUFFERFLAG_EOS`when this happens, so we just wait
```sh_cpp

	
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
	
      
```
Ooops! the EOS event doesn't seem to get generated in
      practice (contrary to the specification) but the program
      seems to work anyway :-(.

At this point we can do something like save the decoded
      image to a file, or do further processing.

The final code is
 [jpeg-decoder.c] (jpeg-decoder.c)

```sh_cpp

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

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS AS IS AND
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
#include jpeg.h

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
#if IR
    COMPONENT_DETAILS *imageResizer;
#endif
    OMX_BUFFERHEADERTYPE **ppInputBufferHeader;
    int             inputBufferHeaderCount;
    OMX_BUFFERHEADERTYPE *pOutputBufferHeader;
};

int             bufferIndex = 0;	// index to buffer array

void printState(OMX_HANDLETYPE handle) {
    OMX_STATETYPE state;
    OMX_ERRORTYPE err;

    err = OMX_GetState(handle, state);
    if (err != OMX_ErrorNone) {
        fprintf(stderr, Error on getting state\n);
        exit(1);
    }
    switch (state) {
    case OMX_StateLoaded: printf(StateLoaded\n); break;
    case OMX_StateIdle: printf(StateIdle\n); break;
    case OMX_StateExecuting: printf(StateExecuting\n); break;
    case OMX_StatePause: printf(StatePause\n); break;
    case OMX_StateWaitForResources: printf(StateWiat\n); break;
    default:  printf(State unknown\n); break;
    }
}


int
portSettingsChanged(OPENMAX_JPEG_DECODER * decoder)
{
    OMX_PARAM_PORTDEFINITIONTYPE portdef;

    // CLEANUP

    printf(Pport settings changed\n);
    // need to setup the input for the resizer with the output of the
    // decoder
    portdef.nSize = sizeof(OMX_PARAM_PORTDEFINITIONTYPE);
    portdef.nVersion.nVersion = OMX_VERSION;
    portdef.nPortIndex = decoder->imageDecoder->outPort;
    OMX_GetParameter(decoder->imageDecoder->handle,
		     OMX_IndexParamPortDefinition, portdef);

    unsigned int    uWidth =
	(unsigned int) portdef.format.image.nFrameWidth;
    unsigned int    uHeight =
	(unsigned int) portdef.format.image.nFrameHeight;

    // enable ports
    OMX_SendCommand(decoder->imageDecoder->handle,
		    OMX_CommandPortEnable,
		    decoder->imageDecoder->outPort, NULL);

    ilclient_wait_for_event(decoder->imageDecoder->component,
			    OMX_EventCmdComplete,
			    OMX_CommandPortEnable, 1,
			    decoder->imageDecoder->outPort, 1, 0,
			    TIMEOUT_MS);
    printf(Decoder output port enabled\n);

    OMX_IMAGE_PARAM_PORTFORMATTYPE iportdef;

    printf(Port settings changed\n);

    // show some logging so user knows its working
    printf
	(Width: %u Height: %u Output Color Format: 0x%x Buffer Size: %u\n,
	 (unsigned int) portdef.format.image.nFrameWidth,
	 (unsigned int) portdef.format.image.nFrameHeight,
	 (unsigned int) portdef.format.image.eColorFormat,
	 (unsigned int) portdef.nBufferSize);
    fflush(stdout);


    // enable output port of decoder
    OMX_SendCommand(decoder->imageDecoder->handle,
		    OMX_CommandPortEnable,
		    decoder->imageDecoder->outPort, NULL);


    int             ret = OMX_AllocateBuffer(decoder->imageDecoder->handle,
					     decoder->pOutputBufferHeader,
					     decoder->imageDecoder->
					     outPort,
					     NULL,
					     portdef.nBufferSize);
    printf(Output port buffer allocated\n);

    if (ret != OMX_ErrorNone) {
	perror(Eror allocating buffer);
	return OMXJPEG_ERROR_MEMORY;
    }


    ilclient_wait_for_event(decoder->imageDecoder->component,
			    OMX_EventCmdComplete,
			    OMX_CommandPortEnable, 1,
			    decoder->imageDecoder->outPort, 1, 0,
			    TIMEOUT_MS);
    printf(Decoder output port rnabled\n);

    return OMXJPEG_OK;
}

int
portSettingsChangedAgain(OPENMAX_JPEG_DECODER * decoder)
{
    printf(Port settings changed again\n);
    ilclient_disable_port(decoder->imageDecoder->component,
			  decoder->imageDecoder->outPort);

    OMX_PARAM_PORTDEFINITIONTYPE portdef;

    // need to setup the input for the resizer with the output of the
    // decoder
    portdef.nSize = sizeof(OMX_PARAM_PORTDEFINITIONTYPE);
    portdef.nVersion.nVersion = OMX_VERSION;
    portdef.nPortIndex = decoder->imageDecoder->outPort;
    OMX_GetParameter(decoder->imageDecoder->handle,
		     OMX_IndexParamPortDefinition, portdef);

    // enable output of decoder
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
prepareImageDecoder(OPENMAX_JPEG_DECODER * decoder)
{
    decoder->imageDecoder = malloc(sizeof(COMPONENT_DETAILS));
    if (decoder->imageDecoder == NULL) {
	perror(malloc image decoder);
	return OMXJPEG_ERROR_MEMORY;
    }

    int ret = ilclient_create_component(decoder->client,
					decoder->imageDecoder->component,
					image_decode,
					ILCLIENT_DISABLE_ALL_PORTS
					|
					ILCLIENT_ENABLE_INPUT_BUFFERS
					|
					ILCLIENT_ENABLE_OUTPUT_BUFFERS);
    
    if (ret != 0) {
	perror(image decode);
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
		     OMX_IndexParamImageInit, port);
    if (port.nPorts != 2) {
	return OMXJPEG_ERROR_WRONG_NO_PORTS;
    }
    decoder->imageDecoder->inPort = port.nStartPortNumber;
    decoder->imageDecoder->outPort = port.nStartPortNumber + 1;

   decoder->pOutputBufferHeader = NULL;

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
    memset(imagePortFormat, 0, sizeof(OMX_IMAGE_PARAM_PORTFORMATTYPE));
    imagePortFormat.nSize = sizeof(OMX_IMAGE_PARAM_PORTFORMATTYPE);
    imagePortFormat.nVersion.nVersion = OMX_VERSION;
    imagePortFormat.nPortIndex = decoder->imageDecoder->inPort;
    imagePortFormat.eCompressionFormat = OMX_IMAGE_CodingJPEG;
    OMX_SetParameter(decoder->imageDecoder->handle,
		     OMX_IndexParamImagePortFormat, imagePortFormat);

    // get buffer requirements
    OMX_PARAM_PORTDEFINITIONTYPE portdef;
    portdef.nSize = sizeof(OMX_PARAM_PORTDEFINITIONTYPE);
    portdef.nVersion.nVersion = OMX_VERSION;
    portdef.nPortIndex = decoder->imageDecoder->inPort;
    OMX_GetParameter(decoder->imageDecoder->handle,
		     OMX_IndexParamPortDefinition, portdef);

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
			       decoder->ppInputBufferHeader[i],
			       decoder->imageDecoder->inPort,
			       (void *) i,
			       portdef.nBufferSize) != OMX_ErrorNone) {
	    perror(Allocate decode buffer);
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
	fprintf(stderr, Did not get port enable %d\n, ret);
	return OMXJPEG_ERROR_EXECUTING;
    }
    // start executing the decoder 
    ret = OMX_SendCommand(decoder->imageDecoder->handle,
			  OMX_CommandStateSet, OMX_StateExecuting, NULL);
    if (ret != 0) {
	fprintf(stderr, Error starting image decoder %x\n, ret);
	return OMXJPEG_ERROR_EXECUTING;
    }
    ret = ilclient_wait_for_event(decoder->imageDecoder->component,
				  OMX_EventCmdComplete,
				  OMX_StateExecuting, 0, 0, 1, 0,
				  TIMEOUT_MS);
    if (ret != 0) {
	fprintf(stderr, Did not receive executing stat %d\n, ret);
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
	perror(malloc decoder);
	return OMXJPEG_ERROR_MEMORY;
    }
    memset(*pDecoder, 0, sizeof(OPENMAX_JPEG_DECODER));

    if ((pDecoder[0]->client = ilclient_init()) == NULL) {
	perror(ilclient_init);
	return OMXJPEG_ERROR_ILCLIENT_INIT;
    }

    if (OMX_Init() != OMX_ErrorNone) {
	ilclient_destroy(pDecoder[0]->client);
	perror(OMX_Init);
	return OMXJPEG_ERROR_OMX_INIT;
    }
    // prepare the image decoder
    int             ret = prepareImageDecoder(pDecoder[0]);
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
	printf(Read into buffer %d\n, pBufHeader->nFilledLen);

	// update the buffer pointer and set the input flags

	sourceOffset = sourceOffset + pBufHeader->nFilledLen;
	pBufHeader->nOffset = 0;
	pBufHeader->nFlags = 0;
	if (toread <= 0) {
	    pBufHeader->nFlags = OMX_BUFFERFLAG_EOS;
	}
	// empty the current buffer
	printf(Emptying buffer\n);
	int             ret =
	    OMX_EmptyThisBuffer(decoder->imageDecoder->handle,
				pBufHeader);

	if (ret != OMX_ErrorNone) {
	    perror(Empty input buffer);
	    fprintf(stderr, return code %x\n, ret);
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
		printf(Buffer is now size %d\n, pBufHeader->nFilledLen);
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
		     OMX_IndexParamActiveStream, param);
	    printf(Active stream %d\n, param.nU32);

	    printf(Trying to fill output buffer\n);
	    printState(decoder->imageDecoder->handle);
	    ret = OMX_FillThisBuffer(decoder->imageDecoder->handle,
				     decoder->pOutputBufferHeader);
	    
	    if (ret != OMX_ErrorNone) {
		perror(Filling output buffer);
		fprintf(stderr, Error code %x\n, ret);
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
	fprintf(stderr, No EOS event on image decoder %d\n, ret);
    } else  {
	fprintf(stderr, EOS event on image decoder %d\n, ret);
    }

    printf(Resized %d\n, decoder->pOutputBufferHeader->nFilledLen);
    FILE *fp = fopen(out, w);
    int n;
    for (n = 0; n < decoder->pOutputBufferHeader->nFilledLen; n++) {
	fputc(decoder->pOutputBufferHeader->pBuffer[n], fp);
    }
    fclose(fp);
    printf(File written\n);

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
	printf(Usage: %s <filename>\n, argv[0]);
	return -1;
    }
    FILE           *fp = fopen(argv[1], rb);
    if (!fp) {
	printf(File %s not found.\n, argv[1]);
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
    s = setupOpenMaxJpegDecoder(pDecoder);
    assert(s == 0);
    s = decodeImage(pDecoder, sourceImage, imageSize);
    assert(s == 0);
    cleanup(pDecoder);
    free(sourceImage);
    printf(Success\n);
    return 0;
}

      
```


