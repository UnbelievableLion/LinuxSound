#  Displaying the video using Gtk 

We want to take the images produced by FFMpeg as
 `AVFrame`'s and display them in a
 `GtkImage`. We don't want to use code that
      reads from a file, because reading and writing files at 30 frames
      per second would be ludicrous. Instead we want some in-memory
      representation of the frames to load into the
 `GtkImage`.

Here is where we hit our first snag: the suitable in-memory
      representation changed in an incompatable way between Gtk 2.0 and
      Gtk 3.0.
      I'm only going to talk in the language of the X Window System
      since I don't know about other underlying systems such as
      Microsoft Windows.

See
 [
	Migrating from GTK+ 2.x to GTK+ 3
      ] (https://developer.gnome.org/gtk3/3.5/gtk-migrating-2-to-3.html)
for a description of some of the changes between these versions.
###  Pixmaps 

The X Window System architecture model is a client-server model which
      has clients (applications) talking to servers (devices with graphic
      displays and input devices). At the lowest level (Xlib) a client
      will send basic requests such as "draw a line from here to there"
      to the server. The server will draw the line using information on
      the server side such as current line thickness, colour, etc.

If you want to keep an array of pixels to represent an image, then
      this array is usually kept on the
X Window server
in a
pixmap
. Pixmaps can be created and modified by applications
      by sending messages across the wire from the client to the server.
      Even a simple modification such as changing the value of a single
      pixel involves a network roundtrip and this can obviously become
      very expensive if done often.

###  Pixbufs 

Pixbufs are
client
side equivalents of pixmaps.
      They can be manipulated by the client without round trips
      to the X server. This reduces time and network overheads in
      manipulating them. However, it means that information that would
      have been kept on the server now has to built and maintained on the
      client application side.

###  X, Wayland and Mir 

The X Window System is nearly 30 years old. During that time it has
      evolved to meet changes in hardware and in software requirements,
      while still maintaining backward compatability.

Significant changes have occurred in hardware during this 30 years:
      multi-core systems are now prevalent and GPUs have brought changes
      in processing video. And generally the amount of memory (cache and RAM)
      means that memory is no longer such an issue.

At the same time, the software side has evolved.
      It is now common to make use of a "compositing window manager" such
      as Compiz so that you can have effects such as Wobbly Windows. This
      is not good for the X Window model: requests from the application go
      to the X server but then a requested image has to be passed to the
      compositing window manager which will perform its effects and then
      send images back to the X server. This is big increase in network
      traffic, in which the X server is now just playing the role of
      display rather than compositor.

Application libraries have now evolved so that much of the work
      that was formerly done by the X server can now be done on the
      application side by libraries such as cairo, pixman, freetype, fontconfig
      and pango.

All of these changes have led to proposals for new backend
      servers which live cooperatively in this evolved world.
      This has been sparked by the development of
 [Wayland] (http://wayland.freedesktop.org/)
,
      but is a bit messed up by Ubuntu forking this to develop
 [Mir] (https://wiki.ubuntu.com/Mir/)
. 
      We won't buy into those arguments - just google for
      "mir and wayland"...

In a very simplistic sense, what it means here is that
      in future pixmaps are out while pixbufs are in.

###  Gtk 3.0 

With Gtk 3.0, pixmaps no longer exist. You only have pixbufs,
      in the data structure
 `GdkPixbuf`. To display the 
      FFMpeg decoded video we pick up after the image has been
      transcoded to the
 `picture_RGB`, translate it into
      a
 `GdkPixbuf`and create the
 `GtkImage`
```sh_cpp

	pixbuf = gdk_pixbuf_new_from_data(picture_RGB->data[0], GDK_COLORSPACE_RGB,
	                                  0, 8, width, height, 
	                                  picture_RGB->linesize[0], 
                                          pixmap_destroy_notify,
	                                  NULL);
	gtk_image_set_from_pixbuf((GtkImage*) image, pixbuf);
      
```


###  Gtk 2.0 

Gtk 2.0 still had pixmaps, in the structure
 `GdkPixmap`.
      In theory it should be possible to have code similar to the Gtk 3.0
      code using the function
 `GdkPixmap *gdk_pixmap_create_from_data(GdkDrawable *drawable,
	const gchar *data,
	gint width,
	gint height,
	gint depth,
	const GdkColor *fg,
	const GdkColor *bg)`which is documented in the GDK 2 Reference Manual at
 [
	Bitmaps and Pixmaps
      ] (https://developer.gnome.org/gdk/unstable/gdk-Bitmaps-and-Pixmaps.html#gdk-pixmap-create-from-data)
and then call
 `void gtk_image_set_from_pixmap(GtkImage *image,
	GdkPixmap *pixmap,
	GdkBitmap *mask)`documented in the Gtk 2.6 reference manual at
 [
	GtkImage
      ] (http://www.gtk.org/api/2.6/gtk/GtkImage.html#gtk-image-set-from-pixmap)
.

The only problem is that I couldn't get the function
 `gdk_pixmap_create_from_data`to work.
      No matter what argument I tried for the drawable,
      the call always barfed on either its type or its value.
      For example, a documented value is
 `NULL`but this always caused an assertion error
      ("should not be NULL").

So what does work? Well, all I could find was a bit of a mess of
      both pixmaps
and
pixbufs: create a pixbuf filled with
      video data, create a pixmap, write the pixbuf data into the pixmap,
      and then fill the image with the pixmap data:
```sh_cpp

	pixbuf = gdk_pixbuf_new_from_data(picture_RGB->data[0], GDK_COLORSPACE_RGB,
             	                          0, 8, width, height, 
	                                  picture_RGB->linesize[0], 
	                                  pixmap_destroy_notify,
	                                  NULL);
	pixmap = gdk_pixmap_new(window->window, width, height, -1);
	gdk_draw_pixbuf((GdkDrawable *) pixmap, NULL,
	                pixbuf, 
	                0, 0, 0, 0, wifth, height,
	                GDK_RGB_DITHER_NORMAL, 0, 0);

	gtk_image_set_from_pixmap((GtkImage*) image, pixmap, NULL);
      
```


###  Threads and Gtk 

The video will need to play in its own thread. Gtk will set up a 
      GUI processing loop in its thread. Since this is Linux, we will
      use Posix
 `pthreads`. The video thread will need to
      be started explicitly by
```sh_cpp

	pthread_t tid;
	pthread_create(, NULL, play_background, NULL);
      
```
where the function
 `play_background`calls the
      FFMpeg code to decode the video file.
      Note that the thread should not be started until the
      application has been realised, or it will attempt to draw
      into non-existent windows.

The Gtk thread will be started by the call to
```sh_cpp

	gtk_widget_show (window);
      
```


That's straightforward enough. But now we have to handle
      the video thread making calls into the GUI thread in order
      to draw the image. The best document I have found on this
      is
 [
	Is GTK+ thread safe? How do I write multi-threaded GTK+ applications?
      ] (https://developer.gnome.org/gtk-faq/stable/x481.html)
Basically it states that code which can affect the Gtk thread should
      be enclosed by a
 `gdk_threads_enter() ... gdk_threads_leave()`pair.

That's okay for Gtk 2.0. What about Gtk 3.0? Ooops!
      Those calls are now deprecated. So what are you supposed
      to do? So far (as at 3 July, 2013) all that seems to exist
      are developer dialogs such as
 [
	Re: deprecating gdk threads
      ] (https://mail.gnome.org/archives/gtk-devel-list/2012-August/msg00020.html)
which states "We have never done a great job of explaining when
      gdk_threads_enter/leave are required, it seems - as a consequence, a
      good number of the critical sections I've seen marked throughout my
      jhbuild checkout are unnecessary. If your application doesn't call
      gdk_threads_init or gdk_threads_set_lock_functions, there's no need to
      use enter/leave. Libraries are a different story, of course".
      But who should call
 `gdk_threads_init`? And what's this
      about libraries? I'll continue to use them until I know better.

###  The code 

Finally, the code to play a video in a Gtk application which
      works with both Gtk 2.0 and Gtk 3.0! It is
 `gtk_play_video.c`:
```sh_cpp

	
#include <gtk/gtk.h>
#include <gdk/gdkx.h>

#include <libavcodec/avcodec.h>
#include <libavformat/avformat.h>
#include <libswscale/swscale.h>

GtkWidget *image;
GtkWidget *window;

#if GTK_MAJOR_VERSION == 2
GdkPixmap *pixmap;
#endif

/* FFMpeg vbls */
AVFormatContext *pFormatCtx = NULL;
AVCodecContext *pCodecCtx = NULL;
int videoStream;
struct SwsContext *sws_ctx = NULL;
AVCodec *pCodec = NULL;

#define WIDTH 192
#define HEIGHT 144

static void pixmap_destroy_notify(guchar *pixels,
				  gpointer data) {
    printf(Destroy pixmap - not sure how\n);
}

static gpointer play_background(gpointer args) {
    /* based on code from
       http://www.cs.dartmouth.edu/~xy/cs23/gtk.html
       http://cdry.wordpress.com/2009/09/09/using-custom-io-callbacks-with-ffmpeg/
    */

    int i;
    AVPacket packet;
    int frameFinished;
    AVFrame *pFrame = NULL;

    /* initialize packet, set data to NULL, let the demuxer fill it */
    /* http://ffmpeg.org/doxygen/trunk/doc_2examples_2demuxing_8c-example.html#a80 */
    av_init_packet(packet);
    packet.data = NULL;
    packet.size = 0;

    int bytesDecoded;
    GdkPixbuf *pixbuf;
    AVFrame *picture_RGB;
    char *buffer;

    pFrame=avcodec_alloc_frame();

    i=0;
    picture_RGB = avcodec_alloc_frame();
    buffer = malloc (avpicture_get_size(PIX_FMT_RGB24, WIDTH, HEIGHT));
    avpicture_fill((AVPicture *)picture_RGB, buffer, PIX_FMT_RGB24, WIDTH, HEIGHT);

    while(av_read_frame(pFormatCtx, packet)>=0) {
	if(packet.stream_index==videoStream) {
	    usleep(33670);  // 29.7 frames per second
	    // Decode video frame
	    avcodec_decode_video2(pCodecCtx, pFrame, frameFinished,
				  packet);

	    int width = pCodecCtx->width;
	    int height = pCodecCtx->height;
	    
	    sws_ctx = sws_getContext(width, height, pCodecCtx->pix_fmt, width, height, 
				     PIX_FMT_RGB24, SWS_BICUBIC, NULL, NULL, NULL);

	    if (frameFinished) {
		printf(Frame %d\n, i++);
		
		sws_scale(sws_ctx,  (uint8_t const * const *) pFrame->data, pFrame->linesize, 0, height, picture_RGB->data, picture_RGB->linesize);
		
		printf(old width %d new width %d\n,  pCodecCtx->width, picture_RGB->width);
		pixbuf = gdk_pixbuf_new_from_data(picture_RGB->data[0], GDK_COLORSPACE_RGB,
						  0, 8, width, height, 
						  picture_RGB->linesize[0], pixmap_destroy_notify,
						  NULL);
				


		/* start GTK thread lock for drawing */
		gdk_threads_enter();    

#if  GTK_MAJOR_VERSION == 2
		/* this leaks memory somehow */
		pixmap = gdk_pixmap_new(window->window, WIDTH, HEIGHT, -1);
	
		gdk_draw_pixbuf((GdkDrawable *) pixmap, NULL,
				pixbuf, 
				0, 0, 0, 0, WIDTH, HEIGHT,
				GDK_RGB_DITHER_NORMAL, 0, 0);

		gtk_image_set_from_pixmap((GtkImage*) image, pixmap, NULL);

		//gtk_widget_queue_draw(image);
#elif GTK_MAJOR_VERSION == 3
		gtk_image_set_from_pixbuf((GtkImage*) image, pixbuf);
		
		//gtk_widget_queue_draw(image);
		
#endif	      
		//g_object_unref(pixbuf);
		//sws_freeContext(sws_ctx);
		/* release GTK thread lock */
		gdk_threads_leave();
	    }
	}
	av_free_packet(packet);
	g_thread_yield();
    }

    printf(Video over!\n);
    exit(0);
}

/* Called when the windows are realized
 */
static void realize_cb (GtkWidget *widget, gpointer data) {
    /* start the video playing in its own thread */
    GThread *tid;
    tid = g_thread_new(video,
		       play_background, 
		       NULL);
}

static gboolean delete_event( GtkWidget *widget,
                              GdkEvent  *event,
                              gpointer   data )
{
    /* If you return FALSE in the delete-event signal handler,
     * GTK will emit the destroy signal. Returning TRUE means
     * you dont want the window to be destroyed.
     * This is useful for popping up are you sure you want to quit?
     * type dialogs. */

    g_print (delete event occurred\n);

    /* Change TRUE to FALSE and the main window will be destroyed with
     * a delete-event. */
    return TRUE;
}

/* Another callback */
static void destroy( GtkWidget *widget,
                     gpointer   data )
{
    gtk_main_quit ();
}

int main(int argc, char** argv)
{
    // Is this necessary?
    XInitThreads();

    int i;


    /* FFMpeg stuff */

    AVFrame *pFrame = NULL;
    AVPacket packet;

    AVDictionary *optionsDict = NULL;

    av_register_all();

    if(avformat_open_input(pFormatCtx, /home/httpd/html/ComputersComputing/simpson.mpg, NULL, NULL)!=0)
	return -1; // Couldnt open file
  
    // Retrieve stream information
    if(avformat_find_stream_info(pFormatCtx, NULL)<0)
	return -1; // Couldnt find stream information
  
    // Dump information about file onto standard error
    av_dump_format(pFormatCtx, 0, argv[1], 0);
  
    // Find the first video stream
    videoStream=-1;
    for(i=0; i<pFormatCtx->nb_streams; i++)
	if(pFormatCtx->streams[i]->codec->codec_type==AVMEDIA_TYPE_VIDEO) {
	    videoStream=i;
	    break;
	}
    if(videoStream==-1)
	return -1; // Didnt find a video stream

    for(i=0; i<pFormatCtx->nb_streams; i++)
	if(pFormatCtx->streams[i]->codec->codec_type==AVMEDIA_TYPE_AUDIO) {
	    printf(Found an audio stream too\n);
	    break;
	}

  
    // Get a pointer to the codec context for the video stream
    pCodecCtx=pFormatCtx->streams[videoStream]->codec;
  
    // Find the decoder for the video stream
    pCodec=avcodec_find_decoder(pCodecCtx->codec_id);
    if(pCodec==NULL) {
	fprintf(stderr, Unsupported codec!\n);
	return -1; // Codec not found
    }
  
    // Open codec
    if(avcodec_open2(pCodecCtx, pCodec, optionsDict)<0)
	return -1; // Could not open codec

    sws_ctx =
	sws_getContext
	(
	 pCodecCtx->width,
	 pCodecCtx->height,
	 pCodecCtx->pix_fmt,
	 pCodecCtx->width,
	 pCodecCtx->height,
	 PIX_FMT_YUV420P,
	 SWS_BILINEAR,
	 NULL,
	 NULL,
	 NULL
	 );

    /* GTK stuff now */

     /* This is called in all GTK applications. Arguments are parsed
     * from the command line and are returned to the application. */
    gtk_init (argc, argv);
    
    /* create a new window */
    window = gtk_window_new (GTK_WINDOW_TOPLEVEL);
    
    /* When the window is given the delete-event signal (this is given
     * by the window manager, usually by the close option, or on the
     * titlebar), we ask it to call the delete_event () function
     * as defined above. The data passed to the callback
     * function is NULL and is ignored in the callback function. */
    g_signal_connect (window, delete-event,
		      G_CALLBACK (delete_event), NULL);
    
    /* Here we connect the destroy event to a signal handler.  
     * This event occurs when we call gtk_widget_destroy() on the window,
     * or if we return FALSE in the delete-event callback. */
    g_signal_connect (window, destroy,
		      G_CALLBACK (destroy), NULL);

    g_signal_connect (window, realize, G_CALLBACK (realize_cb), NULL);
    
    /* Sets the border width of the window. */
    gtk_container_set_border_width (GTK_CONTAINER (window), 10);

    image = gtk_image_new();
    gtk_widget_show (image);

    /* This packs the button into the window (a gtk container). */
    gtk_container_add (GTK_CONTAINER (window), image);
        
    /* and the window */
    gtk_widget_show (window);
    
    /* All GTK applications must have a gtk_main(). Control ends here
     * and waits for an event to occur (like a key press or
     * mouse event). */
    gtk_main ();
    
    return 0;
}


      
```


