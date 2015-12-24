
##  Song information 


The information about each song should include its path
      in the file system, the name of the artist(s), the title
      of the song and any other useful information. This information
      has to be pulled out of the the file path of the song.
      In my current setup, files look like

```

	
/server/KARAOKE/Sonken/SK-50154 - Crosby, Stills - Carry On.mp3
	
      
```


Each song has a reasonably unique identifier ("SK-50154"),
      a unique path and an artist and title. 
      Reasonably straight-forward pattern matching code can
      extract these parts:

```

Path file = ...
String fname = file.getFileName().toString();
if (fname.endsWith(".zip") || 
    fname.endsWith(".mp3")) {
    String root = fname.substring(0, fname.length()-4);
    String parts[] = root.split(" - ", 3);
    if (parts.length != 3)
        return;

	String index = parts[0];
	String artist = parts[1];
	String title = parts[2];

        SongInformation info = new SongInformation(file,
						   index,
						   title,
						   artist);
      
```


(The patterns produced by `cdrip.py`are not quite the same, but the code is easily changed.)


The `SongInformation`class captures this
      information and also includes methods for pattern matching
      of a string against the various fields. For example,
      to check if a title matches,

```

public boolean titleMatch(String pattern) {
    return title.matches("(?i).*" + pattern + ".*");
}
      
```


This gives a case-independent match using 
      Java regular expression support.
      See [
	Java Regex Tutorial
      ](http://www.vogella.com/articles/JavaRegularExpressions/article.html) by Lars Vogel for more details.


The complete `SongInformation`file is

```


import java.nio.file.Path;
import java.io.Serializable;

public class SongInformation implements Serializable {


    // Public fields of each song record

    public String path;

    public String index;

    /**
     * song title in Unicode
     */
    public String title;

    /**
     * artist in Unicode
     */
    public String artist;



    public SongInformation(Path path,
			   String index,
			   String title,
			   String artist) {
	this.path = path.toString();
	this.index = index;
	this.title = title;
	this.artist = artist;
    }

    public String toString() {
	return "(" + index + ") " + artist + ": " + title;
    }

    public boolean titleMatch(String pattern) {
	return title.matches("(?i).*" + pattern + ".*");
    }

    public boolean artistMatch(String pattern) {
	return artist.matches("(?i).*" + pattern + ".*");
    }

    public boolean numberMatch(String pattern) {
	return index.equals(pattern);
    }
}

      
```
