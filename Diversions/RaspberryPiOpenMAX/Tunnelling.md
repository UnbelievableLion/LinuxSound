
##  Tunnelling 


If you want to connect two or more OpenMAX components
then these two components have to be able to pass
information between them. This means that the port formats
must be the same between one component's output port
and the next component's input port, and there must be
a means of transferring from output buffers to input
buffers.


OpenMAX supplies two methods to do this:

+ Do it all yourself; or
+ Use tunnelling

Doing it yourself is always supported. In this case the client
has to work out compatable port formats, and co-ordinate
buffers. For example, when one component fills a buffer
the client could copy it to the next component's input
buffer. This is inefficient. Or the client could use
the first component's output buffer as the next component's
input buffer. But that would mean that the shared buffer
would not be free for the first component to refill
until the second component had received a buffer-empty
event. Messy.


The alternative is tunnelling where the client asks the
components to do all this for them. The OpenMAX components
support tunnelling, which makes life a lot easier.


Tunnelling is used to connect two ports. It can only be done
when the two components are in the Loaded state or when the
ports are disabled. The call `OMX_SetupTunnel`will then connect the two ports as in

```

	
    // establish tunnel between decoder output and resizer input
    OMX_SetupTunnel(decoder->imageDecoder->handle,
		    decoder->imageDecoder->outPort,
		    decoder->imageResizer->handle,
		    decoder->imageResizer->inPort);
	
      
```


A typical use of this is to disable the relevant ports
while they are in Idle state, and then to fill and empty
the input buffers of the first component. This will
trigger a `PortSettingsChanged`event on the first
component's output port. At this point, with formats
and things like image sizes determined, the two
ports can be connected by a tunnel.
There is no need to allocate buffers: the tunnel does that.
