
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
```cpp
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
```cpp
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
```cpp
decoder->ppRenderInputBufferHeader[0]->nAllocLen =
	decoder->pOutputBufferHeader->nAllocLen;
```


Apart from that, it is the usual games of playing with
state, enabling and disabling ports until it works
