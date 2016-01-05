
##  Timidity design 


Timidty is designed as a standalone application.
When built, you get a single executable but do not get
a library of functions that can be called, unlike
FluidSynth for example.


What you _can_ do with Timidity is to add different interfaces.
For example, there are ncurses, XaW and dumb interfaces which can be
invoked at runtime by e.g.

```
timidity -in ...
timidity -ia ...
timidity -id ...
```


There are also others with more specialised uses such as WRD, emacs,
ALSA and remote interfaces.


For example, the Xaw interface looks like


![alt text](timidity-xaw.png)


The idea seems to be that if you want something extra, perhaps you should
build a custom interface and drive it from Timidity.


That doesn't always suit me, as I would prefer to be able to embed
Timidity into my own applications in a simple way.
The rest of this chapter looks at both ways:

+ Turn TiMidity into a library and include it in your own code
+ Build your own interface