#  Writing Audio Applications With JACK 

See
 [
	Writing Audio Applications With JACK - A tutorial/journal
      ] (http://dis-dot-dat.net/index.cgi?item=/jacktuts/starting/)


The design of Jack is discussed at
 [
	The JACK Audio Connection Kit 
      ] (http://lac.linuxaudio.org/2003/zkm/slides/paul_davis-jack/title.html)
by its primary author Paul Davis.
      The goals are

+  Jack should allow streaming of low-latency, high-bandwidth data between independent applications.


+  Although not a requirement, Jack should support any streaming data type, not just audio.


+  In an active Jack setup, there will be one server and one or more Jack plugins. It will be possible to run multiple Jack servers, but each server will form an independent Jack setup. Jack will not define any interfaces between Jack servers.


+  Applications connected using Jack may have their own graphical interfaces. Jack will not make any specifications as to different GUI toolkits or libraries. As a consequence of this requirement, different parts of a running Jack setup may be spread across multiple processes.


+  Jack should provide full, sample accurate synchronation (ie. totally synchronous execution of all client plugins)


+  To represent audio data, Jack should use 32 bit IEEE floats, normalized to value range [-1,1].


+  Only noninterleaved audio streams will be supported.


+  One Jack client may consume or produce multiple data streams.


+  The Jack API should be specified in ANSI C. There are no restrictions on how servers and clients are to be implemented.


+  It should be possible to connect already running applications.


+  It should be possible to add or remove Jack clients while the server is running.




To pick the eyes out of this, the principal goals are

+  Jack should allow streaming of low-latency, high-bandwidth data between independent applications.


+  Jack should provide full, sample accurate synchronation (ie. totally synchronous execution of all client plugins)


The second is guaranteed by the Jack framework.
      The first is supplied by the Jack framework - as long
      as the applications are coded correctly.

Under the hood Jack uses fast Linux (Unix) pipelines to stream
      data from one aplication to another. Within each Jack application
      is a realtime loop which takes data off the input pipe
      and sends data to the output pipe. To avoid latency delays,
      there should essentially be no (or as little as possible) 
      processing between reading and writing data - the ideal
      would be to pass pointer data from input to output,
      or at most to just do a
 `memcpy`.

So how can processing be done? Copy the data read to another
      data structure and pass processing off to another thread,
      or copy data processed in another thread to the ouput pipe.
      Anything else will cause latency which may become noticeable.
      In particular, certain system calls are essentially banned:
 `malloc`can cause swapping;
 `sleep`is an obvious no-no;
 `read/write`etc can cause disk I/O;
 `pthread_cond_wait`will ... wait.

Jack applications are inherently multi-threaded.
      In  a Linux world this means Posix threads,
      and fortunately there is a book
 [
	PThreads Primer
      ] (http://www8.cs.umu.se/kurser/TDBC64/VT03/pthreads/pthread-primer.pdf)
by Bil Lewis and Daniel J Berg
      to tell you all about Posix threads!

There are mechanisms to set up a Jack application:

+  Open a  connection to a Jack server:
 `jack_client_open`


+  Examine the status of the connection and bail out if
	  needed


+  Install a process callback handler to manage I/O:
 `jack_set_process_callback`


+  Install a shutdown callback:
 `jack_on_shutdown`


+  Register input and output ports
	  with the Jack server:
 `jack_port_register`.
	  Note that each port only carries a mono channel,
	  so for stereo you will get two input ports, etc.
	  This does
not
as yet link them to the 
	  pipelines


+  Activate the ports i.e. tell Jack to start its processing
	  thread:
 `jack_activate`


+  Connect the ports to the pipelines:
 `jack_connect`


+  Sit there in some way - for a text client just sleep in
	  a loop. A GUI client might have a GUI processing loop




