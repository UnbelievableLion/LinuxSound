
##  Recording audio 


There are two ways: using `MediaRecorder`or `AudioRecorder`.
The second gives you more control. An example using this is given as [Android audio recording, part 2](http://www.androiddevblog.net/android/android-audio-recording-part-2) by  Krishnaraj Varma.


This app requires RECORD_AUDIO permission.
In the AndroidManifest file this is
given by

```

	
	  <uses-permission android:name="android.permission.INTERNET"/>
	
      
```



