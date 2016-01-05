
##  Streaming audio 


The `MediaPlayer`will take the URL of an audio file - in some versions
of Android and for some file types. This is sad, particularly for me since
Android 2.2 won't stream Ogg files and  my media player can't be upgraded
from 2.2.


When an app can't stream a file from the web, we have to do silly tricks like
downloading it locally and then playing it. That code looks like

```cpp
package jan.newmarch.HttpPlayer;

import jan.newmarch.HttpPlayer.R;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.net.URL;

import android.media.AudioManager;
import android.media.MediaPlayer;
import android.net.Uri;
import android.os.Bundle;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.view.Menu;

public class HttpPlayerActivity extends Activity {

	private String uriStr = "http://192.168.1.9/music/test.ogg";
	private HttpPlayerActivity activity;
	private MediaPlayer player; 

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_http_player);

		activity = this;	
		try {
			// Try the URL directly (ok for Android 3.0 upwards)
			tryMediaPlayer(uriStr);
		} catch(Exception e) {
			// Try downloading the file and then playing it - needed for Android 2.2
			try {
				downloadToLocalFile(uriStr, "audiofile.ogg");
				File localFile = activity.getFileStreamPath("audiofile.ogg");
				tryMediaPlayer(localFile.getAbsolutePath());
			} catch(Exception e2) {
				System.out.println("File error " + e2.toString());
				AlertDialog.Builder builder = new AlertDialog.Builder(this);
				builder.setMessage(e.toString());
				builder.create();
				builder.show();
			}
		}
	}

	private void downloadToLocalFile(String uriStr, String filename) throws Exception {
		URL url = new URL(Uri.encode(uriStr, ":/"));
		BufferedInputStream reader = 
				new BufferedInputStream(url.openStream());
		FileOutputStream fOut = activity.openFileOutput(filename,
				Context.MODE_WORLD_READABLE);
		BufferedOutputStream writer = new BufferedOutputStream(fOut); 

		byte[] buff = new byte[1024]; 
		int nread;
		while ((nread = reader.read(buff, 0, 1024)) != -1) {
			writer.write(buff, 0, nread);
		}
		writer.close();
	}

	private void tryMediaPlayer(String uriStr) throws Exception {
		player = new MediaPlayer();
		player.setAudioStreamType(AudioManager.STREAM_MUSIC);
		player.setDataSource(uriStr);
		player.prepare();
		player.start();         
	}



	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.activity_http_player, menu);
		return true;
	}

}
```


This app requires access to the internet to get the resource.
In the AndroidManifest file this is
given by

```
<uses-permission android:name="android.permission.INTERNET"/>
```



