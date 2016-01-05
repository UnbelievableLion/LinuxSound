
##  Compilation 


Just to add a wrinkle to OpenMAX's complexity, you have to be
careful to get all the flags correct in compiling programs -
or, guess what? - things don't work then either. I
suspect it is things like word-alignment that are critical,
but I've haven't checked
OpenMAX in detail. Here are what seems to work:

```
INCLUDES = -DSTANDALONE -D__STDC_CONSTANT_MACROS -D__STDC_LIMIT_MACROS -DTARGET_POSIX -D_LINUX -fPIC \
    -DPIC -D_REENTRANT -D_LARGEFILE64_SOURCE -D_FILE_OFFSET_BITS=64 -U_FORTIFY_SOURCE -Wall -g \
    -DHAVE_LIBOPENMAX=2 -DOMX -DOMX_SKIP64BIT -ftree-vectorize -pipe -DUSE_EXTERNAL_OMX -DHAVE_LIBBCM_HOST \
    -DUSE_EXTERNAL_LIBBCM_HOST -DUSE_VCHIQ_ARM -Wno-psabi -I/opt/vc/include/ -I/opt/vc/include/interface/vcos/pthreads \
    -I/opt/vc/include/interface/vmcs_host/linux -I./ -I/opt/vc/src/hello_pi/libs/ilclient -I/opt/vc/src/hello_pi/libs/vgfont

LDFLAGS = -Wl,--whole-archive -lilclient -L/opt/vc/lib/ -lopenmaxil -lbcm_host -lvcos -lvchiq_arm \
    -lpthread -lrt -L/opt/vc/src/hello_pi/libs/ilclient -L/opt/vc/src/hello_pi/libs/vgfont \
    -Wl,--no-whole-archive -rdynamic
```


You are welcome to try reducing the number of flags - good luck!
