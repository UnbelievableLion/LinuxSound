
##  Song table 


The `SongTable`builds up a vector of `SongInformation`objects by traversing the file
tree.


If there are many songs (say, in the thousands)
this can lead to a slow startup time. To reduce this,
once a table is loaded, it is saved to disk as a persistent
object by writing it to an `ObjectOutputStream`.
The next time the program is started, an attempt is made to
read it back from this using an `ObjectInputStream`.
Note that we do _not_ use the [Java Persistence API](http://en.wikibooks.org/wiki/Java_Persistence/What_is_Java_persistence%3F) -
designed for J2EE, it is too heavyweight for our purpose here.


The `SongTable`also includes code to build
smaller song tables based on matches between patterns
and the title (or artist or number). It can search
for matches between a pattern and a song and build a new
table based on the matches. It contains a pointer to
the original table for restoration later.
This allows searches for patterns to use the same
data structure.


The code for `SongTable`is

```cpp


import java.util.Vector;
import java.io.FileInputStream;
import java.io.*;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.SimpleFileVisitor;
import java.nio.file.FileVisitResult;
import java.nio.file.FileSystems;
import java.nio.file.attribute.*;


class Visitor
    extends SimpleFileVisitor<Path> {

    private Vector<SongInformation> songs;

    public Visitor(Vector<SongInformation> songs) {
	this.songs = songs;
    }

    @Override
    public FileVisitResult visitFile(Path file,
                                   BasicFileAttributes attr) {
	if (attr.isRegularFile()) {
	    String fname = file.getFileName().toString();
	    //System.out.println("Regular file " + fname);
	    if (fname.endsWith(".zip") || 
		fname.endsWith(".mp3") || 
		fname.endsWith(".kar")) {
		String root = fname.substring(0, fname.length()-4);
		//System.err.println(" root " + root);
		String parts[] = root.split(" - ", 3);
		if (parts.length != 3)
		    return java.nio.file.FileVisitResult.CONTINUE;

		String index = parts[0];
		String artist = parts[1];
		String title = parts[2];

		SongInformation info = new SongInformation(file,
							   index,
							   title,
							   artist);
		songs.add(info);
	    }
	}

        return java.nio.file.FileVisitResult.CONTINUE;
    }
}

public class SongTable {

    private static final String SONG_INFO_ROOT = "/server/KARAOKE/KARAOKE/";

    private static Vector<SongInformation> allSongs;

    public Vector<SongInformation> songs = 
	new Vector<SongInformation>  ();

    public static long[] langCount = new long[0x23];

    public SongTable(Vector<SongInformation> songs) {
	this.songs = songs;
    }

    public SongTable(String[] args) throws java.io.IOException, 
					   java.io.FileNotFoundException {
	if (args.length >= 1) {
	    System.err.println("Loading from " + args[0]);
	    loadTableFromSource(args[0]);
	    saveTableToStore();
	} else {
	    loadTableFromStore();
	}
    }

    private boolean loadTableFromStore() {
	try {
	    /*
	    String userHome = System.getProperty("user.home");
	    Path storePath = FileSystems.getDefault().getPath(userHome, 
							      ".karaoke",
							      "SongStore");
	    
	    File storeFile = storePath.toFile();
	    */
	    File storeFile = new File("/server/KARAOKE/SongStore"); 
	    
	    FileInputStream in = new FileInputStream(storeFile); 
	    ObjectInputStream is = new ObjectInputStream(in);
	    songs = (Vector<SongInformation>) is.readObject();
	    in.close();
	} catch(Exception e) {
	    System.err.println("Can't load store file " + e.toString());
	    return false;
	}
	return true;
    }

    private void saveTableToStore() {
	try {
	    /*
	    String userHome = System.getProperty("user.home");
	    Path storePath = FileSystems.getDefault().getPath(userHome, 
							      ".karaoke",
							      "SongStore");
	    File storeFile = storePath.toFile();
	    */
	    File storeFile = new File("/server/KARAOKE/SongStore");
	    FileOutputStream out = new FileOutputStream(storeFile); 
	    ObjectOutputStream os = new ObjectOutputStream(out);
	    os.writeObject(songs); 
	    os.flush(); 
	    out.close();
	} catch(Exception e) {
	    System.err.println("Can't save store file " + e.toString());
	}
    }

    private void loadTableFromSource(String dir) throws java.io.IOException, 
			      java.io.FileNotFoundException {

	Path startingDir = FileSystems.getDefault().getPath(dir);
	Visitor pf = new Visitor(songs);
	Files.walkFileTree(startingDir, pf);
    }

    public java.util.Iterator<SongInformation> iterator() {
	return songs.iterator();
    }
 
    public SongTable titleMatches( String pattern) {
	Vector<SongInformation> matchSongs = 
	    new Vector<SongInformation>  ();

	for (SongInformation song: songs) {
	    if (song.titleMatch(pattern)) {
		matchSongs.add(song);
	    }
	}
	return new SongTable(matchSongs);
    }

     public SongTable artistMatches( String pattern) {
	Vector<SongInformation> matchSongs = 
	    new Vector<SongInformation>  ();

	for (SongInformation song: songs) {
	    if (song.artistMatch(pattern)) {
		matchSongs.add(song);
	    }
	}
	return new SongTable(matchSongs);
    }

    public SongTable numberMatches( String pattern) {
	Vector<SongInformation> matchSongs = 
	    new Vector<SongInformation>  ();

	for (SongInformation song: songs) {
	    if (song.numberMatch(pattern)) {
		matchSongs.add(song);
	    }
	}
	return new SongTable(matchSongs);
    }

    public String toString() {
	StringBuffer buf = new StringBuffer();
	for (SongInformation song: songs) {
	    buf.append(song.toString() + "\n");
	}
	return buf.toString();
    }
	
    public static void main(String[] args) {
	// for testing
	SongTable songs = null;
	try {
	    songs = new SongTable(new String[] {SONG_INFO_ROOT});
	} catch(Exception e) {
	    System.err.println(e.toString());
	    System.exit(1);
	}

	System.out.println(songs.artistMatches("Tom Jones").toString());

	System.exit(0);
    }
}

      
```
