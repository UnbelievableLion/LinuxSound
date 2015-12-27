
##  The ilclient library 


The RPI has a library `ilclient`intended to make things easier.
This library is _not_ directly portable - it relies on
VideoCore VC threads.
This could presumably be replaced. The primary assistance that it appears
to give to me is:

+ OpenMAX is inherently multi-threaded, relying heavily on callbacks
called in various threads
+ The `ilclient`library manages those callbacks for you
in a generic manner
+ Instead of having to do asynchronous programming, the library gives
you a number of thread wait/synchronise calls, and you use
these to "sit out" the asynchronous calls in the main thread
+ The programming style is often: "make an asynchronous call and then
wait for it to complete."

That sounds awful, essentially turning concurrent programming into sequential
programming, but in fact it doesn't matter much: much of the
execution flow is just waiting in one thread or another,
and this just reduces the number of threads you have to think of...
It's also a protective style of programming: by call and wait at least
you have some chance of pinning down where your program has silently
ground to a halt.


For example, a port for a component
may be in disabled state. You can't allocate
buffers for it until a call has been made to enable it.
Then buffers can be allocated. After that (assuming no other
issues) the port should be able to transition to
enabled state. So wait for that to occur, to ensure that
it does. Typical code is

```cpp

	
    // enable output port of decoder
    OMX_SendCommand(decoder->imageDecoder->handle,
		    OMX_CommandPortEnable,
		    decoder->imageDecoder->outPort, NULL);

    // and allocate a buffer
    int             ret = OMX_AllocateBuffer(decoder->imageDecoder->handle,
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

    // wait for enable to complete
    ilclient_wait_for_event(decoder->imageDecoder->component,
			    OMX_EventCmdComplete,
			    OMX_CommandPortEnable, 1,
			    decoder->imageDecoder->outPort, 1, 0,
			    TIMEOUT_MS);
    printf("Decoder output port enabled\n");
	
      
```

###  ilclient errors 


Calls to the `ilclient`library will sometimes
throw error messages such as this

```

	
assertion failure:ilclient.c:747:ilclient_change_component_state():error == OMX_ErrorNone

Program received signal SIGABRT, Aborted.
0xb6e41bfc in raise () from /lib/arm-linux-gnueabihf/libc.so.6
	
      
```


This doesn't tell you where in your code the call was made, and gives
a totally useless error message.


Okay (you may think), run it
inside a debugger such as `gdb`and when it stops,
ask for a backtrace:

```

	
(gdb) where
#0  0xb6e41bfc in raise () from /lib/arm-linux-gnueabihf/libc.so.6
#1  0xb6e4597c in abort () from /lib/arm-linux-gnueabihf/libc.so.6
#2  0xb6f825a4 in ?? () from /opt/vc/lib/libvcos.so
#3  0xb6f825a4 in ?? () from /opt/vc/lib/libvcos.so
Backtrace stopped: previous frame identical to this frame (corrupt stack?)
(gdb) 
	
      
```


Ho hum, no luck there! You need to run the program inside the
debugger to figure out which `ilclient`call
broke, stepping past each `ilclient`call until one
of them breaks. In this case, it was a call to `ilclient_change_component_state`(about the fifth such call I had made).
Then run the program again, this time stepping _into_ the offending call. Then you can see the details of each
call made: in my case I was trying to change state with
insufficient resources set:

```

	
(gdb) 
365	    ilclient_change_component_state(decoder->imageRender->component,
(gdb) step
ilclient_change_component_state (comp=0x4b150, state=OMX_StateExecuting)
    at ilclient.c:746
746	   error = OMX_SendCommand(comp->comp, OMX_CommandStateSet, state, NULL);
(gdb) next
747	   vc_assert(error == OMX_ErrorNone);
(gdb) print error
$1 = OMX_ErrorInsufficientResources
	
      
```


That's very tedious. Welcome to OpenMAX programming.
