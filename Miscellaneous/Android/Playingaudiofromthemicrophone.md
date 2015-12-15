#  Playing audio from the microphone 

Best so far: http://stackoverflow.com/questions/2413426/playing-an-arbitrary-tone-with-android
```

 `
    void playSound(){
        final AudioTrack audioTrack = new AudioTrack(AudioManager.STREAM_MUSIC,
                sampleRate, AudioFormat.CHANNEL_CONFIGURATION_MONO,
                AudioFormat.ENCODING_PCM_16BIT, generatedSnd.length,
                AudioTrack.MODE_STATIC);
        audioTrack.write(generatedSnd, 0, generatedSnd.length);
        audioTrack.play();
    }
`

```


Similar stuff at http://www.speakingcode.com/2012/01/01/playing-with-android-audiotrack-to-generate-sounds/
      Playing with Android AudioTrack to Generate Sounds, but no code

Code at http://masterex.github.com/archive/2012/05/28/android-audio-synthesis.html
      Android: Crafting a Metronome with Audio Synthesis

Replaying the audio recorded from the microphone to the output device makes use of two
      objects: an
 `AudioRecord`to capture data from the microphone and an
 `AudioTrack`to send it to the output device. The previous program for
      recording audio just needs to write the data to an
 `AudioTrack`object
      instead of to a file.

The code is PlayMicrophone.java:
```
 `
` `package` ` jan.newmarch.playmicrophone;

` `import` ` java.io.` `FileOutputStream` `;

` `import` ` android.app.` `Activity` `;
` `import` ` android.media.` `AudioFormat` `;
` `import` ` android.media.` `AudioManager` `;
` `import` ` android.media.` `AudioRecord` `;
` `import` ` android.media.` `AudioTrack` `;
` `import` ` android.media.` `MediaRecorder` `;
` `import` ` android.os.` `Bundle` `;
` `import` ` android.view.` `Menu` `;
` `import` ` android.view.` `View` `;
` `import` ` android.widget.` `Button` `;
` `import` ` android.widget.` `Toast` `;

` `public` ` ` `class` ` ` `PlayMicrophoneActivity` ` extends ` `Activity` ` {
	` `private` ` ` `static` ` ` `final` ` ` `int` ` ` `RECORDER_BPP` ` = 16;
	` `private` ` ` `static` ` ` `final` ` ` `int` ` ` `RECORD_CHANNELS` ` = ` `AudioFormat` `.` `CHANNEL_IN_MONO` `;
	` `private` ` ` `static` ` ` `final` ` ` `int` ` ` `PLAY_CHANNELS` ` = ` `AudioFormat` `.` `CHANNEL_OUT_MONO` `;
	` `private` ` ` `static` ` ` `final` ` ` `int` ` ` `AUDIO_ENCODING` ` = ` `AudioFormat` `.` `ENCODING_PCM_16BIT` `;

	` `private` ` ` `AudioRecord` ` recorder = null;
	` `private` ` ` `AudioTrack` ` player = null;
	` `private` ` ` `int` ` bufferSize = 0;
	` `private` ` ` `Thread` ` recordingThread = null;
	` `private` ` ` `boolean` ` isRecording = false;
	` `private` ` ` `int` ` sampleRate;

	@` `Override` `
	` `protected` ` ` `void` ` onCreate(` `Bundle` ` savedInstanceState) {
		` `super` `.onCreate(savedInstanceState);
		setContentView(` `R` `.layout.activity_main);

		setButtonHandlers();
		enableButtons(false);

		sampleRate = ` `AudioTrack` `.getNativeOutputSampleRate(` `AudioManager` `.` `STREAM_MUSIC` `);
		` `int` ` bSize1 = ` `AudioRecord` `.getMinBufferSize(sampleRate,
				` `RECORD_CHANNELS` `, ` `AUDIO_ENCODING` `);
		` `int` ` bSize2 = ` `AudioTrack` `.getMinBufferSize(sampleRate,
				` `PLAY_CHANNELS` `, ` `AUDIO_ENCODING` `);
		bufferSize =  (bSize1 ` `>` ` bSize2) ? bSize1 : bSize2;
		` `Toast` ` toast = ` `Toast` `.makeText(getApplicationContext(), 
					` `"Sample rate: "` ` + sampleRate + 
						` `" min record buf size: "` ` + bSize1 +
							` `" min play buf size: "` ` + bSize2, 
					` `Toast` `.` `LENGTH_SHORT` `);
		toast.show();
		` `if` ` (bSize1 ` `<` ` 0 || bSize2 ` `<` ` 0) {
			fatal(` `"No microphone or no speaker"` `);
		}
	}
	
	` `private` ` ` `void` ` fatal(` `String` ` msg) {
` `		/*
		Toast toast = Toast.makeText(getApplicationContext(), 
				msg, 
				Toast.LENGTH_SHORT);
		toast.show();
		*/
` `		` `System` `.out.println(msg);
		finish();
	}

	` `private` ` ` `void` ` setButtonHandlers() {
		((` `Button` `) findViewById(` `R` `.id.btnStart)).setOnClickListener(btnClick);
		((` `Button` `) findViewById(` `R` `.id.btnStop)).setOnClickListener(btnClick);
	}

	` `private` ` ` `void` ` enableButton(` `int` ` id, ` `boolean` ` isEnable) {
		((` `Button` `) findViewById(id)).setEnabled(isEnable);
	}

	` `private` ` ` `void` ` enableButtons(` `boolean` ` isRecording) {
		enableButton(` `R` `.id.btnStart, !isRecording);
		enableButton(` `R` `.id.btnStop, isRecording);
	}

	` `private` ` ` `void` ` startRecording() {
		` `try` ` {
		
		recorder = ` `new` ` ` `AudioRecord` `(` `MediaRecorder` `.` `AudioSource` `.` `MIC` `,
				sampleRate, ` `RECORD_CHANNELS` `,
				` `AUDIO_ENCODING` `, bufferSize);
				
		player = ` `new` ` ` `AudioTrack` `(` `AudioManager` `.` `STREAM_MUSIC` `,
				sampleRate, ` `PLAY_CHANNELS` `,
				` `AUDIO_ENCODING` `, bufferSize,
				` `AudioTrack` `.` `MODE_STREAM` `);
		recorder.startRecording();
		player.play();
		} ` `catch` `(` `Exception` ` e) {
			fatal(` `"Can't create recorder or player"` `);
		}

		isRecording = true;

		recordingThread = ` `new` ` ` `Thread` `(` `new` ` ` `Runnable` `() {

			` `// @Override
` `			` `public` ` ` `void` ` run() {
				writeAudioDataToSpeaker();
			}
		}, ` `"AudioRecorder Thread"` `);

		recordingThread.start();
	}

	` `private` ` ` `void` ` writeAudioDataToSpeaker() {
		` `byte` ` data[] = ` `new` ` ` `byte` `[bufferSize];

		` `int` ` read = 0;

		` `while` ` (isRecording) {
			read = recorder.read(data, 0, bufferSize);

			` `if` ` (` `AudioRecord` `.` `ERROR_INVALID_OPERATION` ` != read) {
				player.write(data, 0, read);
			}
		}			
	}

	` `private` ` ` `void` ` stopRecording() {
		` `if` ` (null != recorder) {
			isRecording = false;

			recorder.stop();
			recorder.release();

			recorder = null;
			recordingThread = null;
			
			player.stop();
			player.release();
		}
	}

	` `private` ` ` `View` `.` `OnClickListener` ` btnClick = ` `new` ` ` `View` `.` `OnClickListener` `() {
		@` `Override` `
		` `public` ` ` `void` ` onClick(` `View` ` v) {
			` `switch` ` (v.getId()) {
			` `case` ` ` `R` `.id.btnStart: {
				enableButtons(true);
				startRecording();
				` `break` `;
			}
			` `case` ` ` `R` `.id.btnStop: {
				enableButtons(false);
				stopRecording();
				` `break` `;
			}
			}
			` `Toast` ` toast = ` `Toast` `.makeText(getApplicationContext(), 
					` `"Btn clicked handler called"` `, 
					` `Toast` `.` `LENGTH_SHORT` `);
			toast.show();
		}
	};

	@` `Override` `
	` `public` ` ` `boolean` ` onCreateOptionsMenu(` `Menu` ` menu) {
		` `// Inflate the menu; this adds items to the action bar if it is present.
` `		getMenuInflater().inflate(` `R` `.menu.activity_main, menu);
		` `return` ` true;
	}

}
`
```


This app requires RECORD_AUDIO permission. 
      In the AndroidManifest file this is
      given by
```

 `
	  ` `<` `uses-permission android:name="android.permission.RECORD_AUDIO"/` `>` `
	`

```


On my ASUS Transformer with 4.0, the input and output devices both require
      a minimum buffer of 8192 bytes with a sample rate of 44100hz.
      The latency is poor: 330 milliseconds and is similar to other reports.
      It is not usable for
      realtime record and playback. The new APIs in 4.1 may improve the situation.

