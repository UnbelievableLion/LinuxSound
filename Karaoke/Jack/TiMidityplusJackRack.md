
##  TiMidity plus Jack Rack 


In the chapter on [Karaoke TiMidity](../Timidity/) we used TiMidity with a Jack backend and an
Xaw interface to give a basic Karaoke system.
We can now improve on that by using Jack Rack
effects:

+ Run TiMidity with Jack output, an Xaw interface
and synchronising the lyrics to sound by
```
timidity -ia -B2,8 -Oj -EFverb=0 --trace --trace-text-meta
```

+ Run Jack rack with TAP reverberator and a volume
control installed
+ Connect ports using `qjackctl`

The resulting system looks like
TiMidity with Jack Rack![alt text](timidity+jackrack.png)