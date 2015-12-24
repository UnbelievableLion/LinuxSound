
##  Using Cairo to draw on an image 


With the disappearance of pixmaps from Gtk 3.0, Cairo is now the
      only real way of assembling multiple components into an image.
      General Cairo information is at [
	Cairo documentation
      ](http://cairographics.org/documentation/) ,
      a tutorial is at [
	Cairo graphics tutorial
      ](http://zetcode.com/gfx/cairo/) and information about overlaying onto images is at [
	Images in Cairo
      ](http://zetcode.com/gfx/cairo/cairoimages/) .


Cairo takes sources and a destination. The sources can be changed,
      and frequently are: from an image source, to a colour source, etc.
      The destination is where the drawn stuff ends up.


Destinations can be in memory or at a variety of backends.
      We want in an in-memory destination so that we can extract
      a pixbuf from it, with all operations done on the client side.
      We create a destination as a _surface_ of type `cairo_surface_t`and set it into a _Cairo context_ of type `cairo_t`by

```

cairo_surface_t *surface = cairo_image_surface_create (CAIRO_FORMAT_ARGB32, 
						       width, height);
cairo_t *cr = cairo_create(surface);
      
```


The cairo context `cr`is then used to set sources, perform drawing, etc.
      At the end of this we will extract a pixmap from the `surface`.


The first step is to set the source to the pixbuf for each frame
      of the video and to `paint`this to the destination by

```

gdk_cairo_set_source_pixbuf(cr, pixbuf, 0, 0);
cairo_paint (cr);
      
```


We can overlay another image on top of this by changing the source
      to the overlay image and painting that:

```

gdk_cairo_set_source_pixbuf(cr, overlay_pixbuf, 300, 200);
cairo_paint (cr);
      
```


Note that Cairo will do any alpha blending that is required if
      the overlay has "transparent" pixels.


To draw the text, we need to reset the source to an RGB surface,
      set all the parameters for the text, and draw the text
      into the
      destination. This is done by

```

// white text
cairo_set_source_rgb(cr, 1.0, 1.0, 1.0); 
// this is a standard font for Cairo 
cairo_select_font_face (cr, "cairo:serif",
			CAIRO_FONT_SLANT_NORMAL, 
			CAIRO_FONT_WEIGHT_BOLD);
cairo_set_font_size (cr, 20);
cairo_move_to(cr, 10.0, 50.0);
cairo_show_text (cr, "hello");
      
```


Finally we want to extract the fnal image from the destination and set 
      it into the `GdkImage`for display. Here there is another
      difference between Gtk 2.0 and Gtk 3.0: Gtk 3.0 has a function `gdk_pixbuf_get_from_surface`which will return a `GdKPixbuf`; Gtk 2.0 has no such function.
      We only look at the Gtk 3.0 version for now

```

pixbuf = gdk_pixbuf_get_from_surface(surface,
				     0,
				     0,
				     width,
				     height);

gtk_image_set_from_pixbuf((GtkImage*) image, pixbuf); 
      
```


The complete program is `gtk_play_video_cairo.c`

```

	
#include <gtk/gtk.h>

#include <libavcodec/avcodec.h>
#include <libavformat/avformat.h>
#include <libswscale/swscale.h>

#define OVERLAY_IMAGE "jan-small.png"

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



static void pixmap_destroy_notify(guchar *pixels,
				  gpointer data) {
    printf("Destroy pixmap - not sure how\n");
}

static void *play_background(void *args) {
    /* based on code from
       http://www.cs.dartmouth.edu/~xy/cs23/gtk.html
       http://cdry.wordpress.com/2009/09/09/using-custom-io-callbacks-with-ffmpeg/
    */

    int i;
    AVPacket packet;
    int frameFinished;
    AVFrame *pFrame = NULL;

    int bytesDecoded;
    GdkPixbuf *pixbuf;
    GdkPixbuf *overlay_pixbuf;
    AVFrame *picture_RGB;
    char *buffer;

    GError *error = NULL;
    overlay_pixbuf = gdk_pixbuf_new_from_file(OVERLAY_IMAGE, &error);
    if (!overlay_pixbuf) {
	fprintf(stderr, "%s\n", error->message);
	g_error_free(error);
	exit(1);
    }

    // add an alpha layer for a white background
    overlay_pixbuf = gdk_pixbuf_add_alpha(overlay_pixbuf, TRUE, 255, 255, 255);

    int overlay_width = gdk_pixbuf_get_width(overlay_pixbuf);
    int overlay_height =  gdk_pixbuf_get_height(overlay_pixbuf);

    pFrame=avcodec_alloc_frame();

    i=0;
    picture_RGB = avcodec_alloc_frame();
    buffer = malloc (avpicture_get_size(PIX_FMT_RGB24, 720, 576));
    avpicture_fill((AVPicture *)picture_RGB, buffer, PIX_FMT_RGB24, 720, 576);

    while(av_read_frame(pFormatCtx, &packet)>=0) {
	if(packet.stream_index==videoStream) {
	    usleep(33670);  // 29.7 frames per second
	    // Decode video frame
	    avcodec_decode_video2(pCodecCtx, pFrame, &frameFinished,
				  &packet);

	    int width = pCodecCtx->width;
	    int height = pCodecCtx->height;
	    
	    sws_ctx = sws_getContext(width, height, pCodecCtx->pix_fmt, width, height, 
				     PIX_FMT_RGB24, SWS_BICUBIC, NULL, NULL, NULL);

	    if (frameFinished) {
		printf("Frame %d\n", i++);
		
		sws_scale(sws_ctx,  (uint8_t const * const *) pFrame->data, pFrame->linesize, 0, height, picture_RGB->data, picture_RGB->linesize);
		
		printf("old width %d new width %d\n",  pCodecCtx->width, picture_RGB->width);
		pixbuf = gdk_pixbuf_new_from_data(picture_RGB->data[0], GDK_COLORSPACE_RGB,
						  0, 8, width, height, 
						  picture_RGB->linesize[0], pixmap_destroy_notify,
						  NULL);

		// Create the destination surface
		cairo_surface_t *surface = cairo_image_surface_create (CAIRO_FORMAT_ARGB32, 
								       width, height);
		cairo_t *cr = cairo_create(surface);

		// draw the background image
		gdk_cairo_set_source_pixbuf(cr, pixbuf, 0, 0);
		cairo_paint (cr);

		// overlay an image on top
		// alpha blending will be done by Cairo
		gdk_cairo_set_source_pixbuf(cr, overlay_pixbuf, 300, 200);
		cairo_paint (cr);

		// draw some white text on top
		cairo_set_source_rgb(cr, 1.0, 1.0, 1.0);
		// this is a standard font for Cairo
		cairo_select_font_face (cr, "cairo:serif",
					CAIRO_FONT_SLANT_NORMAL, 
					CAIRO_FONT_WEIGHT_BOLD);
		cairo_set_font_size (cr, 20);
		cairo_move_to(cr, 10.0, 50.0);
		cairo_show_text (cr, "hello");

		/* start GTK thread lock for drawing */
		gdk_threads_enter();    

#if  GTK_MAJOR_VERSION == 2
		int pwidth, pheight, stride;
		unsigned char *data;

		data = cairo_image_surface_get_data (surface);
		pwidth = cairo_image_surface_get_width (surface);
		pheight = cairo_image_surface_get_height (surface);
		stride = cairo_image_surface_get_stride (surface);
		
		// this function doesn't work properly
		// code doesn't work
		pixmap = gdk_pixmap_create_from_data(NULL, data,
					      pwidth, pheight,
					      8, NULL, NULL);

		gtk_image_set_from_pixmap((GtkImage*) image, pixmap, NULL);

		gtk_widget_queue_draw(image);
#elif GTK_MAJOR_VERSION == 3
		pixbuf = gdk_pixbuf_get_from_surface(surface,
						     0,
						     0,
						     width,
						     height);

		gtk_image_set_from_pixbuf((GtkImage*) image, pixbuf); 

		//gtk_widget_queue_draw(image);
#endif	      
		/* reclaim memory */
		g_object_unref(pixbuf);
		//sws_freeContext(sws_ctx);
		cairo_surface_destroy(surface);
		cairo_destroy(cr);

		/* release GTK thread lock */
		gdk_threads_leave();
	    }
	}
	av_free_packet(&packet);
    }

    printf("Video over!\n");
    exit(0);
}

/* Called when the windows are realized
 */
static void realize_cb (GtkWidget *widget, gpointer data) {
    /* start the video playing in its own thread */
    pthread_t tid;
    pthread_create(&tid, NULL, play_background, NULL);
}

static gboolean delete_event( GtkWidget *widget,
                              GdkEvent  *event,
                              gpointer   data )
{
    /* If you return FALSE in the "delete-event" signal handler,
     * GTK will emit the "destroy" signal. Returning TRUE means
     * you don't want the window to be destroyed.
     * This is useful for popping up 'are you sure you want to quit?'
     * type dialogs. */

    g_print ("delete event occurred\n");

    /* Change TRUE to FALSE and the main window will be destroyed with
     * a "delete-event". */
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

    if(avformat_open_input(&pFormatCtx, "short.mpg", NULL, NULL)!=0)
	return -1; // Couldn't open file
  
    // Retrieve stream information
    if(avformat_find_stream_info(pFormatCtx, NULL)<0)
	return -1; // Couldn't find stream information
  
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
	return -1; // Didn't find a video stream

    for(i=0; i<pFormatCtx->nb_streams; i++)
	if(pFormatCtx->streams[i]->codec->codec_type==AVMEDIA_TYPE_AUDIO) {
	    printf("Found an audio stream too\n");
	    break;
	}

  
    // Get a pointer to the codec context for the video stream
    pCodecCtx=pFormatCtx->streams[videoStream]->codec;
  
    // Find the decoder for the video stream
    pCodec=avcodec_find_decoder(pCodecCtx->codec_id);
    if(pCodec==NULL) {
	fprintf(stderr, "Unsupported codec!\n");
	return -1; // Codec not found
    }
  
    // Open codec
    if(avcodec_open2(pCodecCtx, pCodec, &optionsDict)<0)
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
    gtk_init (&argc, &argv);
    
    /* create a new window */
    window = gtk_window_new (GTK_WINDOW_TOPLEVEL);
    
    /* When the window is given the "delete-event" signal (this is given
     * by the window manager, usually by the "close" option, or on the
     * titlebar), we ask it to call the delete_event () function
     * as defined above. The data passed to the callback
     * function is NULL and is ignored in the callback function. */
    g_signal_connect (window, "delete-event",
		      G_CALLBACK (delete_event), NULL);
    
    /* Here we connect the "destroy" event to a signal handler.  
     * This event occurs when we call gtk_widget_destroy() on the window,
     * or if we return FALSE in the "delete-event" callback. */
    g_signal_connect (window, "destroy",
		      G_CALLBACK (destroy), NULL);

    g_signal_connect (window, "realize", G_CALLBACK (realize_cb), NULL);
    
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
