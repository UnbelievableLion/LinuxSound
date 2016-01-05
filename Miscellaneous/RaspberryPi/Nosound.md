
##  No sound 


I plugged mine into a 29 inch ViewSonic monitor using the HDMI connectors.
Initially I got no sound from either the 3.5mm analogue output or the HDMI monitor.
This is explained at [Why is my Audio (Sound) Output not working?](http://raspberrypi.stackexchange.com/questions/44/why-is-my-audio-sound-output-not-working) I edited the file `/boot/config.txt`and uncommented the line "hdmi_drive=2".
I also used the command

```
sudo amixer cset numid=3 <n>
```


where n is 0=auto, 1=headphones, 2=hdmi to toggle between outputs.


After that sound is fine.
