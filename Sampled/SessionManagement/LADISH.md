
##  LADISH 


LADISH is designed as the successor to LASH and is available in the repositories.


LADISH can start, stop and configure sessions. In particular, it can setup
      different Jack configurations. This means that you do not start Jack and then
      start LADISH, but the other way around: start the GUI tool `gladish`,
      configure Jack and then start a session.
      The process is described in the [
	LADI Session Handler
      ](http://ladish.org/wiki/tutorial) Wiki - follow it, in particular connecting Jack to, say, ALSA.
      Otherwise you will get no sound!
      See also [
	The LADI Session Handler
      ](http://www.penguinproducer.com/Blog/2011/12/the-ladi-session-handler/) by the Penguin Producer.


Once set up, start a new Studio and then start applications from its
      Applications menu. To run `mplayer`you need to give the full
      command such as

```

	
	  mplayer -ao jack 54154.mp3
	
      
```


You can start `jack_mixer`from the Applications menu
      and then add two new sets of input ports, as in the Jack chapter.
      After reconnecting them, you end with a connection graph like


![alt text](ladish-session.png)





Connection graphs are stored as an XML file in `$HOME/.ladish`.
      For example, the above graph is stored as

```

	<?xml version="1.0"?>
<!--
ladish Studio configuration.
-->
<!-- Sun Sep 29 10:49:54 2013 -->
<studio>
  <jack>
    <conf>
      <parameter path="/engine/driver">alsa</parameter>
      <parameter path="/engine/client-timeout">500</parameter>
      <parameter path="/engine/port-max">64</parameter>
    </conf>
    <clients>
      <client name="system" uuid="5ef937c6-46f7-45cd-8441-8ff6e2aee4eb">
        <ports>
          <port name="capture_1" uuid="9432f206-44c3-45cb-8024-3ba7160962bc" />
          <port name="capture_2" uuid="3c9acf5c-c91d-4692-add2-e3defb7c508a" />
          <port name="playback_1" uuid="95c68011-dab9-401c-8904-b3d149e20570" />
          <port name="playback_2" uuid="5b8e9215-3ff4-4973-8c0b-1eb5ab7ccc9b" />
        </ports>
      </client>
      <client name="jack_mixer-3" uuid="4538833e-d7e7-47d0-8a43-67ee25d17898">
        <ports>
          <port name="midi in" uuid="17d04191-f59d-4d16-970c-55030162aae7" />
          <port name="MAIN L" uuid="9d986401-c303-4f35-89b7-a32e10120ce4" />
          <port name="MAIN R" uuid="fae94d01-00ef-449d-8e05-f95df84c5357" />
          <port name="Monitor L" uuid="1758d824-75cd-46b3-8e53-82c6be1ca200" />
          <port name="Monitor R" uuid="d14815e9-d3bc-457b-8e4f-29ad29ea36f7" />
          <port name="Mixer L" uuid="07d388ed-d00a-4ee0-92aa-3ae79200e11e" />
          <port name="Mixer R" uuid="d1eb3400-75ce-422d-b9b8-b7e670f95428" />
          <port name="Mixer Out L" uuid="fad2a77e-6146-4919-856f-b6f7befdb84d" />
          <port name="Mixer Out R" uuid="920c5d12-9f62-46aa-b191-52bfbb94065d" />
          <port name="mixer2 L" uuid="c2b96996-9cd1-41dd-a750-192bb5717438" />
          <port name="mixer2 R" uuid="3de52738-d7e8-4733-bf08-3ea2b6372a4c" />
          <port name="mixer2 Out L" uuid="4e08eba4-a0c1-4e76-9dff-c14f76d5328e" />
          <port name="mixer2 Out R" uuid="9d2f79a5-e2d0-484b-b094-98ef7a4f61a7" />
        </ports>
      </client>
      <client name="mplayer" uuid="66e0d45f-2e21-4fbf-ac34-5d3658ee018a">
        <ports>
          <port name="out_0" uuid="83152a6e-e6f6-4357-93ce-020ba58b7d00" />
          <port name="out_1" uuid="55a05594-174d-48a5-805b-96d2c9e77cf1" />
        </ports>
      </client>
    </clients>
  </jack>
  <clients>
    <client name="Hardware Capture" uuid="47c1cd18-7b21-4389-bec4-6e0658e1d6b1" naming="app">
      <ports>
        <port name="capture_1" uuid="9432f206-44c3-45cb-8024-3ba7160962bc" type="audio" direction="output" />
        <port name="capture_2" uuid="3c9acf5c-c91d-4692-add2-e3defb7c508a" type="audio" direction="output" />
      </ports>
      <dict>
        <key name="http://ladish.org/ns/canvas/x">1364.000000</key>
        <key name="http://ladish.org/ns/canvas/y">1083.000000</key>
      </dict>
    </client>
    <client name="Hardware Playback" uuid="b2a0bb06-28d8-4bfe-956e-eb24378f9629" naming="app">
      <ports>
        <port name="playback_1" uuid="95c68011-dab9-401c-8904-b3d149e20570" type="audio" direction="input" />
        <port name="playback_2" uuid="5b8e9215-3ff4-4973-8c0b-1eb5ab7ccc9b" type="audio" direction="input" />
      </ports>
      <dict>
        <key name="http://ladish.org/ns/canvas/x">1745.000000</key>
        <key name="http://ladish.org/ns/canvas/y">1112.000000</key>
      </dict>
    </client>
    <client name="jack_mixer-3" uuid="4b198f0f-5a77-4486-9f54-f7ec044d9bf2" naming="app" app="98729282-8b18-4bcf-b929-41bc53f2b4ed">
      <ports>
        <port name="midi in" uuid="17d04191-f59d-4d16-970c-55030162aae7" type="midi" direction="input" />
        <port name="MAIN L" uuid="9d986401-c303-4f35-89b7-a32e10120ce4" type="audio" direction="output" />
        <port name="MAIN R" uuid="fae94d01-00ef-449d-8e05-f95df84c5357" type="audio" direction="output" />
        <port name="Monitor L" uuid="1758d824-75cd-46b3-8e53-82c6be1ca200" type="audio" direction="output" />
        <port name="Monitor R" uuid="d14815e9-d3bc-457b-8e4f-29ad29ea36f7" type="audio" direction="output" />
        <port name="Mixer L" uuid="07d388ed-d00a-4ee0-92aa-3ae79200e11e" type="audio" direction="input" />
        <port name="Mixer R" uuid="d1eb3400-75ce-422d-b9b8-b7e670f95428" type="audio" direction="input" />
        <port name="Mixer Out L" uuid="fad2a77e-6146-4919-856f-b6f7befdb84d" type="audio" direction="output" />
        <port name="Mixer Out R" uuid="920c5d12-9f62-46aa-b191-52bfbb94065d" type="audio" direction="output" />
        <port name="mixer2 L" uuid="c2b96996-9cd1-41dd-a750-192bb5717438" type="audio" direction="input" />
        <port name="mixer2 R" uuid="3de52738-d7e8-4733-bf08-3ea2b6372a4c" type="audio" direction="input" />
        <port name="mixer2 Out L" uuid="4e08eba4-a0c1-4e76-9dff-c14f76d5328e" type="audio" direction="output" />
        <port name="mixer2 Out R" uuid="9d2f79a5-e2d0-484b-b094-98ef7a4f61a7" type="audio" direction="output" />
      </ports>
      <dict>
        <key name="http://ladish.org/ns/canvas/x">1560.000000</key>
        <key name="http://ladish.org/ns/canvas/y">1104.000000</key>
      </dict>
    </client>
    <client name="mplayer" uuid="2f15cfec-7f6d-41b4-80e8-e1ae80c3be9e" naming="app" app="7a9be17b-eb40-4be3-a9dc-82f36bbceeeb">
      <ports>
        <port name="out_0" uuid="83152a6e-e6f6-4357-93ce-020ba58b7d00" type="audio" direction="output" />
        <port name="out_1" uuid="55a05594-174d-48a5-805b-96d2c9e77cf1" type="audio" direction="output" />
      </ports>
      <dict>
        <key name="http://ladish.org/ns/canvas/x">1350.000000</key>
        <key name="http://ladish.org/ns/canvas/y">1229.000000</key>
      </dict>
    </client>
  </clients>
  <connections>
    <connection port1="9432f206-44c3-45cb-8024-3ba7160962bc" port2="07d388ed-d00a-4ee0-92aa-3ae79200e11e" />
    <connection port1="3c9acf5c-c91d-4692-add2-e3defb7c508a" port2="d1eb3400-75ce-422d-b9b8-b7e670f95428" />
    <connection port1="fad2a77e-6146-4919-856f-b6f7befdb84d" port2="95c68011-dab9-401c-8904-b3d149e20570" />
    <connection port1="920c5d12-9f62-46aa-b191-52bfbb94065d" port2="5b8e9215-3ff4-4973-8c0b-1eb5ab7ccc9b" />
    <connection port1="83152a6e-e6f6-4357-93ce-020ba58b7d00" port2="c2b96996-9cd1-41dd-a750-192bb5717438" />
    <connection port1="55a05594-174d-48a5-805b-96d2c9e77cf1" port2="3de52738-d7e8-4733-bf08-3ea2b6372a4c" />
  </connections>
  <applications>
    <application name="jack_mixer-3" uuid="98729282-8b18-4bcf-b929-41bc53f2b4ed" terminal="false" level="0" autorun="true">jack_mixer</application>
    <application name="mplayer" uuid="7a9be17b-eb40-4be3-a9dc-82f36bbceeeb" terminal="true" level="0" autorun="true">mplayer -ao jack %2Fhome%2Fhttpd%2Fhtml%2FLinuxSound%2FKaraoke%2FSubtitles%2Fsongs%2F54154.mp3</application>
  </applications>
</studio>

      
```


The full command to restart `mplayer`is stored in this file,
      as are all the connections made.


On stopping and restarting a session, `mplayer`is started
      with the same MP3 file, but has the default connections. 
      It ignores the connections of the LADISH session.
      Similarly, `jack_mixer`is restarted, but the 
      additional ports have to be recreated by hand - this is not a LADISH
      aware application so it runs at Level 0.
      However, once created, the LADISH reconnections are made okay.


A list of LADISH-aware applications is at [
	ladish: LADI Session Handler
      ](http://wiki.linuxaudio.org/apps/all/ladish) 


From the user's viewpoint, the difference between these session managers are

+ Jack applications can be started in any manner and will be picked up
	  by the Jack session manager.
	  However, any specific command-line parameters will be lost
+ Applications need to be started by the LADISH session manager in
	  order to be managed by it.
	  However, it can record command line parameters and restart the
	  application using them

From the developer's viewpoint (see later), the difference between these session managers are

+ Jack session aware applications can be started in any manner 
	  and will encode the command line required to restart them
	  in the program
+ 