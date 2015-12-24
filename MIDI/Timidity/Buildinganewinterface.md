
##  Building a new interface 

###  Shared objects 


You can build your own interfaces and add them to TiMidity without
      changing or recompiling TiMidity. Such interfaces are built as
      dynamically loadable shared libraries, and are loaded when 
      TiMidity starts.


You have to be a little careful with compile and link flags
      to build these libraries 
      (see [
	Building shared objects in Linux
      ](http://stackoverflow.com/questions/7252550/loadable-bash-builtin) ). To build the shared object `if_my_interface.so`from `my_interface.c`I use

```

	
gcc  -fPIC $(CFLAGS) -c -o my_interface.o my_interface.c
gcc -shared -o if_my_interface.so my_interface.o
	
      
```


TiMidity will only load files that begin with `if_`.
      They can reside in any directory, with the default being
      something like `/usr/lib/timidity`or `/usr/local/lib/timidity`(see the "Supported dynamic load interfaces" directory
      from `timidity -h`).


The defaulty directory to load dynamic modules can be overridden
      by the option `-d`as in

```

	
timidity -d. -ik --trace 54154.mid
	
      
```

###  Entry point 


Each interface must have a unique function that can be called
      by the dynamic loader. Recall that interfaces are selected by the
      command line option `-i`, such as `timidity -iT ...`to choose the VT100 interface.
      Your interface must have a single ASCII letter identifier
      which isn't used by any other interface, say `m`for "my interface". The loader will then look for a function

```

	
ControlMode *interface_m_loader(void)
	
      
```


where the "m" in the function name is the identifier.
      This function is simple: it just returns the address of a
      structure of type `ControlMode`which is defined
      elsewhere in the interface's code:

```

	
ControlMode *interface_m_loader(void)
{
    return &ctl;
}
	
      
```

###  ControlMode 


The `ControlMode`structure is

```

	
typedef struct {
  char *id_name, id_character;
  char *id_short_name;
  int verbosity, trace_playing, opened;

  int32 flags;

  int  (*open)(int using_stdin, int using_stdout);
  void (*close)(void);
  int (*pass_playing_list)(int number_of_files, char *list_of_files[]);
  int  (*read)(int32 *valp);
  int  (*write)(char *buf, int32 size);
  int  (*cmsg)(int type, int verbosity_level, char *fmt, ...);
  void (*event)(CtlEvent *ev);  /* Control events */
} ControlMode;
	
      
```


which defines information about the interface and a set of functions
      which are called by TiMidity in response to events and actions
      within TiMidity. For example, for "my interface" this structure is

```

	
ControlMode ctl=
    {
	"my interface", 'm',
	"my iface",
	1,          /* verbosity */
	0,          /* trace playing */
	0,          /* opened */
	0,          /* flags */
	ctl_open,
	ctl_close,
	pass_playing_list,
	ctl_read,
	NULL,       /* write */
	cmsg,
	ctl_event
    };
	
      
```


Some of these fields are obvious, some are less so:

+ __ `open`__:
This is called to set which files are used for I/O...
+ __ `close`__:
... and to close them
+ __ `pass_playing_list`__:
This function is passed a list of files to play.
	  The most likely action is to walk through this
	  list, calling `play_midi_file`on each
+ __ `read`__:
Not sure yet
+ __ `write`__:
Not sure yet
+ __ `cmsg`__:
Called with information messages
+ __ `event`__:
This is the major function for handling MIDI control events.
	  Typically it will be a big switch for each type of control
	  event



###  Include files 


This is messy. A typical interface will need to know some of the
      constants and functions used by TiMidity. While these are organised
      logically for TiMidity, they are not organised conveniently for a
      new interface. So you have to keep pulling in extra includes, which point
      to other externals, which require more includes, etc. These may be in
      different directories such `timidity`and `utils`so you have to point to many different include directories.


Note that you will need the TiMidity source code to get these
      include files, downloaded from [
        SourceForge TiMidity++
      ](http://sourceforge.net/projects/timidity/?source=dlp) .

###  My simple interface 


This basically does the same as the "dumb" interface
      built into TiMidity. It is loaded from the current directory
      and invoked by

```

	
timidity -im -d. 54154.mid
	
      
```


The code is in one file, `my_interface.c`:

```

/*
  my_interface.c
*/

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif /* HAVE_CONFIG_H */
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#ifndef NO_STRING_H
#include <string.h>
#else
#include <strings.h>
#endif

#include "support.h"
#include "timidity.h"
#include "output.h"
#include "controls.h"
#include "instrum.h"
#include "playmidi.h"
#include "readmidi.h"

static int ctl_open(int using_stdin, int using_stdout);
static void ctl_close(void);
static int ctl_read(int32 *valp);
static int cmsg(int type, int verbosity_level, char *fmt, ...);
static void ctl_total_time(long tt);
static void ctl_file_name(char *name);
static void ctl_current_time(int ct);
static void ctl_lyric(int lyricid);
static void ctl_event(CtlEvent *e);
static int pass_playing_list(int number_of_files, char *list_of_files[]);


/**********************************/
/* export the interface functions */

#define ctl karaoke_control_mode

ControlMode ctl=
    {
	"my interface", 'm',
	"my iface",
	1,          /* verbosity */
	0,          /* trace playing */
	0,          /* opened */
	0,          /* flags */
	ctl_open,
	ctl_close,
	pass_playing_list,
	ctl_read,
	NULL,       /* write */
	cmsg,
	ctl_event
    };

static FILE *outfp;
int karaoke_error_count;
static char *current_file;
struct midi_file_info *current_file_info;

static int pass_playing_list(int number_of_files, char *list_of_files[]) {
    int n;

    for (n = 0; n < number_of_files; n++) {
	printf("Playing list %s\n", list_of_files[n]);
	
	current_file = list_of_files[n];
	/*
	  current_file_info = get_midi_file_info(current_file, 1);
	  if (current_file_info != NULL) {
	  printf("file info not NULL\n");
	  } else {
	  printf("File info is NULL\n");
	  }
	*/
	play_midi_file( list_of_files[n]);
    }
    return 0;
}

/*ARGSUSED*/
static int ctl_open(int using_stdin, int using_stdout)
{
    if(using_stdout)
	outfp=stderr;
    else
	outfp=stdout;
    ctl.opened=1;
    return 0;

    /*
    // dont know what this function does
    if (current_file != NULL) {
	current_file_info = get_midi_file_info(current_file, 1);
	printf("Opening info for %s\n", current_file);
    } else {
	printf("Current is NULL\n");
    }
    return 0;
    */
}

static void ctl_close(void)
{
    fflush(outfp);
    ctl.opened=0;
}

/*ARGSUSED*/
static int ctl_read(int32 *valp)
{
    return RC_NONE;
}

static int cmsg(int type, int verbosity_level, char *fmt, ...)
{
    va_list ap;

    if ((type==CMSG_TEXT || type==CMSG_INFO || type==CMSG_WARNING) &&
	ctl.verbosity<verbosity_level)
	return 0;
    va_start(ap, fmt);
    if(type == CMSG_WARNING || type == CMSG_ERROR || type == CMSG_FATAL)
	karaoke_error_count++;
    if (!ctl.opened)
	{
	    vfprintf(stderr, fmt, ap);
	    fputs(NLS, stderr);
	}
    else
	{
	    vfprintf(outfp, fmt, ap);
	    fputs(NLS, outfp);
	    fflush(outfp);
	}
    va_end(ap);
    return 0;
}

static void ctl_total_time(long tt)
{
    int mins, secs;
    if (ctl.trace_playing)
	{
	    secs=(int)(tt/play_mode->rate);
	    mins=secs/60;
	    secs-=mins*60;
	    cmsg(CMSG_INFO, VERB_NORMAL,
		 "Total playing time: %3d min %02d s", mins, secs);
	}
}

static void ctl_file_name(char *name)
{
    current_file = name;

    if (ctl.verbosity>=0 || ctl.trace_playing)
	cmsg(CMSG_INFO, VERB_NORMAL, "Playing %s", name);
}

static void ctl_current_time(int secs)
{
    int mins;
    static int prev_secs = -1;

#ifdef __W32__
    if(wrdt->id == 'w')
	return;
#endif /* __W32__ */
    if (ctl.trace_playing && secs != prev_secs)
	{
	    prev_secs = secs;
	    mins=secs/60;
	    secs-=mins*60;
	    //fprintf(outfp, "\r%3d:%02d", mins, secs);
	    //fflush(outfp);
	}
}

static void ctl_lyric(int lyricid)
{
    char *lyric;

    current_file_info = get_midi_file_info(current_file, 1);

    lyric = event2string(lyricid);
    if(lyric != NULL)
	{
	    if(lyric[0] == ME_KARAOKE_LYRIC)
		{
		    if(lyric[1] == '/' || lyric[1] == '\\')
			{
			    fprintf(outfp, "\n%s", lyric + 2);
			    fflush(outfp);
			}
		    else if(lyric[1] == '@')
			{
			    if(lyric[2] == 'L')
				fprintf(outfp, "\nLanguage: %s\n", lyric + 3);
			    else if(lyric[2] == 'T')
				fprintf(outfp, "Title: %s\n", lyric + 3);
			    else
				fprintf(outfp, "%s\n", lyric + 1);
			}
		    else
			{
			    fputs(lyric + 1, outfp);
			    fflush(outfp);
			}
		}
	    else
		{
		    if(lyric[0] == ME_CHORUS_TEXT || lyric[0] == ME_INSERT_TEXT)
			fprintf(outfp, "\r");
		    fputs(lyric + 1, outfp);
		    fflush(outfp);
		}
	}
}


static void ctl_event(CtlEvent *e)
{
    switch(e->type)
	{
	case CTLE_NOW_LOADING:
	    ctl_file_name((char *)e->v1);
	    break;
	case CTLE_LOADING_DONE:
	    // MIDI file is loaded, about to play
	    current_file_info = get_midi_file_info(current_file, 1);
	    if (current_file_info != NULL) {
		printf("file info not NULL\n");
	    } else {
		printf("File info is NULL\n");
	    }
	    break;
	case CTLE_PLAY_START:

	    ctl_total_time(e->v1);
	    break;
	case CTLE_CURRENT_TIME:
	    ctl_current_time((int)e->v1);
	    break;
#ifndef CFG_FOR_SF
	case CTLE_LYRIC:
	    ctl_lyric((int)e->v1);
	    break;
#endif
	}
}

/*
 * interface_<id>_loader();
 */
ControlMode *interface_k_loader(void)
{
    return &ctl;
}



      
```

###  Running my simple interface 


When I tried to run the interface using the standard package
      TiMidity v2.13.2-40.1 it crashed in a memory free call.
      The code is stripped, so tracking down why is not easy
      and I haven't bothered to do so yet - I'm not sure what
      libraries, versions of code, etc, the package distro was 
      compiled against.


I had built my own copy of TiMidity from source.
      This worked fine. Note that when you build TiMidity from
      source, you will need to specify that it can load dynamic
      modules, for example by

```

	
congfigure --enable-audio=alsa --enable-vt100 --enable-debug --enable-dynamic
	
      
```

###  Playing a background video to a MIDI file 


We can take the code from playing a video given earlier and put it
      as the "back end" of a TiMidity systems as a "video" interface.
      Essentially all that needs to be done is to change `ctl_open`from the simple interface to call
      the Gtk code to play the video, and change the identity
      of the interface.


The new "video" interface is `video_player_interface.c`

```

      /*
  video_player_interface.c
*/

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif /* HAVE_CONFIG_H */
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#ifndef NO_STRING_H
#include <string.h>
#else
#include <strings.h>
#endif

#include "support.h"
#include "timidity.h"
#include "output.h"
#include "controls.h"
#include "instrum.h"
#include "playmidi.h"
#include "readmidi.h"

static int ctl_open(int using_stdin, int using_stdout);
static void ctl_close(void);
static int ctl_read(int32 *valp);
static int cmsg(int type, int verbosity_level, char *fmt, ...);
static void ctl_total_time(long tt);
static void ctl_file_name(char *name);
static void ctl_current_time(int ct);
static void ctl_lyric(int lyricid);
static void ctl_event(CtlEvent *e);
static int pass_playing_list(int number_of_files, char *list_of_files[]);


/**********************************/
/* export the interface functions */

#define ctl karaoke_control_mode

ControlMode ctl=
    {
	"video player interface", 'v',
	"video player",
	1,          /* verbosity */
	0,          /* trace playing */
	0,          /* opened */
	0,          /* flags */
	ctl_open,
	ctl_close,
	pass_playing_list,
	ctl_read,
	NULL,       /* write */
	cmsg,
	ctl_event
    };

static FILE *outfp;
int video_player_error_count;
static char *current_file;
struct midi_file_info *current_file_info;

static int pass_playing_list(int number_of_files, char *list_of_files[]) {
    int n;

    for (n = 0; n < number_of_files; n++) {
	printf("Playing list %s\n", list_of_files[n]);
	
	current_file = list_of_files[n];
	/*
	  current_file_info = get_midi_file_info(current_file, 1);
	  if (current_file_info != NULL) {
	  printf("file info not NULL\n");
	  } else {
	  printf("File info is NULL\n");
	  }
	*/
	play_midi_file( list_of_files[n]);
    }
    return 0;
}

extern void *play_gtk(void *args);

/*ARGSUSED*/
static int ctl_open(int using_stdin, int using_stdout)
{
    if(using_stdout)
	outfp=stderr;
    else
	outfp=stdout;
    ctl.opened=1;

    init_ffmpeg();

    /* start Gtk in its own thread */
    pthread_t tid_gtk;
    init_gtk(0, NULL);
    //pthread_create(&tid_gtk, NULL, play_gtk, NULL);

    return 0;
}

static void ctl_close(void)
{
    fflush(outfp);
    ctl.opened=0;
}

/*ARGSUSED*/
static int ctl_read(int32 *valp)
{
    return RC_NONE;
}

static int cmsg(int type, int verbosity_level, char *fmt, ...)
{
    va_list ap;

    if ((type==CMSG_TEXT || type==CMSG_INFO || type==CMSG_WARNING) &&
	ctl.verbosity<verbosity_level)
	return 0;
    va_start(ap, fmt);
    if(type == CMSG_WARNING || type == CMSG_ERROR || type == CMSG_FATAL)
	video_player_error_count++;
    if (!ctl.opened)
	{
	    vfprintf(stderr, fmt, ap);
	    fputs(NLS, stderr);
	}
    else
	{
	    vfprintf(outfp, fmt, ap);
	    fputs(NLS, outfp);
	    fflush(outfp);
	}
    va_end(ap);
    return 0;
}

static void ctl_total_time(long tt)
{
    int mins, secs;
    if (ctl.trace_playing)
	{
	    secs=(int)(tt/play_mode->rate);
	    mins=secs/60;
	    secs-=mins*60;
	    cmsg(CMSG_INFO, VERB_NORMAL,
		 "Total playing time: %3d min %02d s", mins, secs);
	}
}

static void ctl_file_name(char *name)
{
    current_file = name;

    if (ctl.verbosity>=0 || ctl.trace_playing)
	cmsg(CMSG_INFO, VERB_NORMAL, "Playing %s", name);
}

static void ctl_current_time(int secs)
{
    int mins;
    static int prev_secs = -1;

#ifdef __W32__
    if(wrdt->id == 'w')
	return;
#endif /* __W32__ */
    if (ctl.trace_playing && secs != prev_secs)
	{
	    prev_secs = secs;
	    mins=secs/60;
	    secs-=mins*60;
	    //fprintf(outfp, "\r%3d:%02d", mins, secs);
	    //fflush(outfp);
	}
}

static void ctl_lyric(int lyricid)
{
    char *lyric;

    current_file_info = get_midi_file_info(current_file, 1);

    lyric = event2string(lyricid);
    if(lyric != NULL)
	{
	    if(lyric[0] == ME_KARAOKE_LYRIC)
		{
		    if(lyric[1] == '/' || lyric[1] == '\\')
			{
			    fprintf(outfp, "\n%s", lyric + 2);
			    fflush(outfp);
			}
		    else if(lyric[1] == '@')
			{
			    if(lyric[2] == 'L')
				fprintf(outfp, "\nLanguage: %s\n", lyric + 3);
			    else if(lyric[2] == 'T')
				fprintf(outfp, "Title: %s\n", lyric + 3);
			    else
				fprintf(outfp, "%s\n", lyric + 1);
			}
		    else
			{
			    fputs(lyric + 1, outfp);
			    fflush(outfp);
			}
		}
	    else
		{
		    if(lyric[0] == ME_CHORUS_TEXT || lyric[0] == ME_INSERT_TEXT)
			fprintf(outfp, "\r");
		    fputs(lyric + 1, outfp);
		    fflush(outfp);
		}
	}
}


static void ctl_event(CtlEvent *e)
{
    switch(e->type)
	{
	case CTLE_NOW_LOADING:
	    ctl_file_name((char *)e->v1);
	    break;
	case CTLE_LOADING_DONE:
	    // MIDI file is loaded, about to play
	    current_file_info = get_midi_file_info(current_file, 1);
	    if (current_file_info != NULL) {
		printf("file info not NULL\n");
	    } else {
		printf("File info is NULL\n");
	    }
	    break;
	case CTLE_PLAY_START:

	    ctl_total_time(e->v1);
	    break;
	case CTLE_CURRENT_TIME:
	    ctl_current_time((int)e->v1);
	    break;
#ifndef CFG_FOR_SF
	case CTLE_LYRIC:
	    ctl_lyric((int)e->v1);
	    break;
#endif
	}
}

/*
 * interface_<id>_loader();
 */
ControlMode *interface_v_loader(void)
{
    return &ctl;
}


      
```


The build command is

```

	
video_code.o: video_code.c
        gcc  -fPIC $(CFLAGS) -c -o video_code.o video_code.c $(LIBS3)

if_video_player.so: video_player_interface.c video_code.o
        gcc  -fPIC $(CFLAGS) -c -o video_player_interface.o video_player_interface.c
        gcc -shared -o if_video_player.so video_player_interface.o video_code.o $(LIBS3)
	
      
```


You may hit a hiccup with running this Gtk-based interface: Gtk version
      mismatch :-(. The current builds of TiMidity either do not have the Gtk
      interface compiled in, or have Gtk version 2. If Gtk is not compiled in,
      you should have no problem. Otherwise, if you have compiled this interface
      with Gtk version 3, you will get runtime errors about type mismatches,
      inability to load widgets and no visual display.


Check for Gtk in the executable by

```

	
nm timidity | grep gtk
	
      
```
