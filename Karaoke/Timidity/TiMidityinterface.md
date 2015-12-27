
##  TiMidity interface 


You will need to have the TiMidity source downloaded
from [SourceForge TiMidity++](http://sourceforge.net/projects/timidity/?source=dlp) .


In the earlier chapter on [MIDI and TiMidity](../../MIDI/Timidity/) we discussed two alternative ways of building applications
using TiMidity:

+ Build a front-end with TiMidity as a library back-end
+ Use standard TiMidity with a custom-built interface
as back-end to TiMidity




Both options are possible here, with one wrinkle: if we want to
capture MIDI events then we have to do so as a back-end to TiMidity, which
requires that we build a TiMidity interface.


To recap on this,
the different interface files for TiMidity are stored in the
directory `interface`and include files such as `dumb_c.c`for the dumb interface. They all revolve
around a data structure `ControlMode`defined in `timidity/controls.h`:

```cpp

	
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


.


For the simplest values of the functions in this structure,
see the code for the dumb interface in `interface/dumb_c.c`.


For dealing with lyrics, the main field to set is the
function `event()`. This will be passed a
pointer to a `CtlEvent`which is
defined in `timidity/controls.h`:

```cpp

	
typedef struct _CtlEvent {
    int type;           /* See above */
    ptr_size_t v1, v2, v3, v4;/* Event value */
} CtlEvent;
	
      
```





The type field distinguishes a large number of event types
such as `CTLE_NOW_LOADING`and `CTLE_PITCH_BEND`.
The type of interest to us is `CTLE_LYRIC`.
 `interface/dumb_c.c`
```cpp

	
static void ctl_event(CtlEvent *e)
{
    switch(e->type) {
      case CTLE_LYRIC:
        ctl_lyric((int)e->v1);
        break;
   }
}

static void ctl_lyric(int lyricid)
{
    char *lyric;

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
	
      
```



