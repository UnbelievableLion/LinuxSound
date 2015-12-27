
##  Getting the list of lyrics 


The failing of the current interfaces in TiMidity with regard
to Karaoke is that while they can show the lyrics as they are played,
they don't show the lyric lines and progressively highlight them as they are
played. For that, you need the set of lyrics.


TiMidity in fact builds a list of lyrics, and makes them accessible.
It has a function `event2string()`which
takes an integer parameter from one upwards. For each value
it returns the string of a lyric or text event, finally
returning `NULL`on the end of the list.
The first character returned is a type parameter, the rest is
the string. Using GLib functions, we can build up an array
of lines for a `KAR`file by

```cpp

	
struct _lyric_t {
    gchar *lyric;
    long tick; // not used here
};
typedef struct _lyric_t lyric_t;

struct _lyric_lines_t {
    char *language;
    char *title;
    char *performer;
    GArray *lines; // array of GString *
};
typedef struct _lyric_lines_t lyric_lines_t;

GArray *lyrics;
lyric_lines_t lyric_lines;

static void build_lyric_lines() {
    int n;
    lyric_t *plyric;
    GString *line = g_string_new("");
    GArray *lines =  g_array_sized_new(FALSE, FALSE, sizeof(GString *), 64);

    lyric_lines.title = NULL;

    n = 1;
    char *evt_str;
    while ((evt_str = event2string(n++)) != NULL) {
        gchar *lyric = evt_str+1;

        if ((strlen(lyric) >= 2) && (lyric[0] == '@') && (lyric[1] == 'L')) {
            lyric_lines.language =  lyric + 2;
            continue;
        }

        if ((strlen(lyric) >= 2) && (lyric[0] == '@') && (lyric[1] == 'T')) {
            if (lyric_lines.title == NULL) {
                lyric_lines.title = lyric + 2;
            } else {
                lyric_lines.performer = lyric + 2;
            }
            continue;
        }

        if (lyric[0] == '@') {
            // some other stuff like @KMIDI KARAOKE FILE
            continue;
        }

        if ((lyric[0] == '/') || (lyric[0] == '\\')) {
            // start of a new line
            // add to lines
            g_array_append_val(lines, line);
            line = g_string_new(lyric + 1);
        }  else {
            line = g_string_append(line, lyric);
        }
    }
    lyric_lines.lines = lines;
    
    printf("Title is %s, performer is %s, language is %s\n", 
           lyric_lines.title, lyric_lines.performer, lyric_lines.language);
    for (n = 0; n < lines->len; n++) {
        printf("Line is %s\n", g_array_index(lines, GString *, n)->str);
    }
}
	
      
```





The function `build_lyric_lines()`should be called
from the `CTLE_LOADING_DONE`branch of `ctl_event()`.
