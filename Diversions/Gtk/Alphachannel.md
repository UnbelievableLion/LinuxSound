
##  Alpha channel 


An overlay image may have some "transparent" parts in it. You don't want
such parts to be overlaid onto the underlying image. But such parts will
need to have a value in the array of pixels. Even zero is a value - black!
Some images will have another byte per pixel allocated as the
"alpha channel". This has a value to show how "transparent" the pixel is.
A value of 255 means not transparent at all, a value of zero means totally
transparent.


The simplest way of combining a "transparent" pixel with the underlying
pixel is simply to not do so: leave the underlying pixel untouched.
More complex algorithms are pointed to by the Wikipedia [Alpha compositing](http://en.wikipedia.org/wiki/Alpha_compositing) page.


Converting an image which doesn't have an alpha channel to one which
does can be done using the function `gdk_pixbuf_add_alpha`.
This can also be used to set the value of the alpha channel by
matching against a colour. For example, the following should set the
alpha value to 0 for any white pixels and to 255 for all others:

```cpp

pixbuf = gdk_pixbuf_add_alpha(pixbuf, TRUE, 255, 255, 255);
      
```


Unfortunately it seems to want to leave an "edge" of pixels which
should be marked as transparent.


With alpha marking in place, a simple test can be used in the overlay
function as to whether or not to perform the overlay:

```cpp

	
if (alpha < 128) {
    continue;
 }
	
      
```


It's not worth giving a complete program just for a couple
of changed lines. It is [gtk_play_video_overlay_alpha.c](gtk_play_video_overlay_alpha.c) .
