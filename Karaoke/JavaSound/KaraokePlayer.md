
##  KaraokePlayer 


The KaraokePlayer class extracts the filename of the Karaoke
      file and creates a MidiPlayer to handle the file:

```

      
      /*
 * KaraokePlayer.java
 *
 */

import javax.swing.*;

public class KaraokePlayer {


    public static void main(String[] args) throws Exception {
	if (args.length != 1) {
	    System.err.println("KaraokePlayer: usage: " +
			     "KaraokePlayer <midifile>");
	    System.exit(1);
	}
	String	strFilename = args[0];

	MidiPlayer midiPlayer = new MidiPlayer();
	midiPlayer.playMidiFile(strFilename);
    }
}




      
    
```
