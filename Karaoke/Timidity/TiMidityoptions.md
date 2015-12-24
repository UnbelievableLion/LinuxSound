
##  TiMidity options 


If we choose to use TiMidity as front-end then we need to run it

```

	
timidity -d. -iv --trace  --trace-text-meta ...
	
      
```


for a "v" interface in the current directory.


The alternative is building a
      main program that calls TiMidity as a library. The command
      line parameters to TiMidity then have to be included as hard-coded
      parameters in the application. 
      One is easy: the `CtlMode`has a field `trace_playing`and setting that to one turns tracing on.
      Including Text events as Lyric events requires digging a bit deeper
      into TiMidity, but just requires (shortly after initialising
      the library)

```

	
extern int opt_trace_text_meta_event;
opt_trace_text_meta_event = 1;
	
      
```



