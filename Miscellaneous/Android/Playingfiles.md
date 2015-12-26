
##  Playing files 


An app can get media from various sources

+ Packaged with the app
+ From the MediaStore
+ From an external source such as an SD card
+ Streamed from the network

I'm not so much interested in the first two. They are discussed in books such as
      "Pro Android Media Developing Graphics, Music, Video,
      and Rich Media Apps for Smartphones
      and Tablets" by Shawn Van Every from APress.





An SD card on my ASUS Transformer is mounted into `/Removable/SD`.
      I put audio files into a subdirectory `Music`. Files from here can
      be played using an Android `MediaPlayer`. There is a state machine
      model for setting up the media player to play files: here it consists of
      setting a data source and then calling `prepare()`and `start()`.
      The only wrinkle in this is actually finding the path to the data file: in the
      Android, the `File`class doesn't like a path with embedded '/'.
      So you have to walk the file path one directory at a time till you get to the
      file itself. Note that the ASUS Transformer has an internal SD card, and the
      "recommended" way of getExternalStorageDirectory returns the internal card
      and _not_ the external one!


I'm not going to go through any of how to set up an environment such as Eclipse
      or how to build projects. Once done, an app can be "exported" to an SD card
      and installed from the file browser. A player for a single file
      on the SD disk looks like

```cpp

      
      package jan.newmarch.DiskPlayer;

import java.io.File;

import android.media.AudioManager;
import android.media.MediaPlayer;
import android.os.Bundle;
import android.app.Activity;
import android.app.AlertDialog;
import android.view.Menu;

public class DiskPlayerActivity extends Activity {

    private String filePath = "/Removable/SD/Music/audio_01.ogg";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
	super.onCreate(savedInstanceState);
	setContentView(R.layout.activity_disk_player);
	try {
	    String[] array=filePath.split("/");
	    File f = null;
	    for(int t = 0; t < array.length - 1; t++)
		{
		    f = new File(f, array[t]);
		}
	    File songFile=new File(f, array[array.length-1]);
		
	    MediaPlayer player = new MediaPlayer();
	    player.setAudioStreamType(AudioManager.STREAM_MUSIC);
	    player.setDataSource(songFile.getAbsolutePath());
	    player.prepare()	;
	    player.start();
	} catch (Exception e) {
	    AlertDialog.Builder builder = new AlertDialog.Builder(this);
	    builder.setMessage(e.toString());
	    builder.create();
	    builder.show();
	}
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
	// Inflate the menu; this adds items to the action bar if it is present.
	getMenuInflater().inflate(R.menu.activity_disk_player, menu);
	return true;
    }

}

      
    
```


This app requires access to read the SD card. In the AndroidManifest file this is
      given by

```

	
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>
	
      
```



