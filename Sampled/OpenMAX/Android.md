
##  Android 


You write Android apps in Java. But like most Java systems,
      code written in C or C++ can be included as "native" methods.
      The native code is linked by a framework called JNI
      (Java Native Interface). For the Android, Google have
      standardised a number of libraries in the NDK (Native
      Development Kit). This includes both OpenSL ES and OpenMAX AL.
      Informaton about these is included in the [
	Android NDK
      ](http://developer.android.com/tools/sdk/ndk/index.html) .


Documents in the NDK such as android-ndk-r8d/docs/opensles/index.html
      give good overviews of using these, although using the JNI
      to build applications is not for the faint of heart. In addition,
      the documentation inlcudes comments like
      "In particular, use
      of OpenSL ES does not guarantee a lower audio latency, higher scheduling
      priority, etc. than what the platform generally provides".
      From Android 4.2 on, lower latency will be possible using OpenSL ES. 
      See the Performance section in
      opensles/index.html


See android-ndk-r8d/samples/native-audio for an example using
      Java + JNI + OpenSL ES.
