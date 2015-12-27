
##  Background video with TiMidity as front-end 


The interface needs to be built as a shared library by

```

	
if_video.so: video_code.c
        gcc  -fPIC $(CFLAGS) -c -o video_code.o video_code.c $(LIBS)
        gcc -shared -o if_video.so video_code.o $(LIBS)
	
      
```





TiMidity is then run with options

```

	
timidity -d. -iv --trace  --trace-text-meta 
	
      
```


As before, it crashes TiMidity from the Ubuntu distro
but works fine with TiMidity built from source in
the current Linux environment.
