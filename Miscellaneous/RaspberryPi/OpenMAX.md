
##  OpenMAX 


Audio and video can be played on the Raspberry Pi using the OpenMAX IL
      toolkit. This has been implemented by Broadcom for their GPU used by the
      RPi.  This is partly covered
      in the chapter [ OpenMAX and and OpenSL ](../../Sampled/OpenMAX/) .
      More examples will be explored in later editions of this book.

###  Displaying images 


As a step in using the RPi, I decided to try drawing JPEG
      images into the GPU using OpenMAX. As with all things related
      to OpenMAX this is far too hard - OpenMAX is one of the worst
      APIs I have ever had to deal with, and the version on the RPi
      brings its own set of problems.


The directory `/opt/vc/src/hello_pi/hello_jpeg`contains an example to read in a JPEG file and resize
      the image. This program works. But it uses the Broadcom
      convenience functions such as `ilclient_create_component`and I don't want to use those just in case they aen't available
      elsewhere.


I adapted their code, and it didn't work.
      Digging deep with the debugger showed a bizarre set of values:

+ The JPEG decoder has the OpenMAX label "image_decode"
+ This has an input port number 320 on which to receive
	  the original iamge and an output port number 321 to place
	  the decoded output
+ When I created a buffer for the input, the buffer showed
	  that port 320 was it's output port!
+ The Broadcom example showed that (correctly) it was the
	  input port

Duh!


The problem was the type `OMX_TICKS`. In a 64-bit
      environment it is a 64-bit integer, otherwise it is a struct
      of two 32-bit values. I used one version, the Broadcom code
      on the RPi is using the other.


By looking at the compile environment for the Broadcom example,
      it uses the defines

```

	
-DSTANDALONE -D__STDC_CONSTANT_MACROS -D__STDC_LIMIT_MACROS -DTARGET_POSIX\
-D_LINUX -fPIC -DPIC -D_REENTRANT -D_LARGEFILE64_SOURCE -D_FILE_OFFSET_BITS=64\
-U_FORTIFY_SOURCE -Wall -g -DHAVE_LIBOPENMAX=2 -DOMX -DOMX_SKIP64BIT\
-ftree-vectorize -pipe -DUSE_EXTERNAL_OMX -DHAVE_LIBBCM_HOST\
-DUSE_EXTERNAL_LIBBCM_HOST -DUSE_VCHIQ_ARM
	
      
```


The `OMX_SKIP64BIT`flag is needed to choose the right
      value for the RPi type. What else is needed for what, 
      I don't know yet :-(
