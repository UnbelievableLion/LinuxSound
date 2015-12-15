#  Karaoke effects in ASS files 

A line in an ASS file essentially consists of a time to start
      display, a time to finish the display and the text itself.
      However, Karaoke users are accustomed to the text being 
      highlighted as it is played.

ASS supports two major highlight styles:

+  Words are highlighted one at a time


+  The text is highlighted by filling from the left


These effects are done by embedding "Karaoke overrides"
      into the text. These are in {} brackets with a duration
      time in hundredths of a second.

The details are

+ __
	  Word highlighting
	__:
 
An override of the form {\k
<
time
>
}
	  will highlight the following word for
time
hundredths of a second.
	  An example would be
```

	    
{\k100}Here {\k150}comes {\k50}the {\k150}sun
	    
	  
```


+ __
	  Fill highlighting
	__:
 
An override of the form {\kf
<
time
>
}
	  will progressively fill up the following word for
time
hundredths of a second.
	  An example would be
```

	    
{\kf100}Here {\kf150}comes {\kf50}the {\kf150}sun
	    
	  
```




The three styles appear as

+  Lines with no highlighting

![alt text](line.png)


+  Word highlighting

![alt text](word.png)


+  Fill highlighting

![alt text](fill.png)




