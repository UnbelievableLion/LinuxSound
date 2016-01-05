
##  Identifying devices 


Android doesn't have a means of listing the input and output devices.
Instead there are methods to query the state of various assumed or possible
devices. The page [Dealing with Audio Output Hardware](http://developer.android.com/training/managing-audio/audio-output.html) gives the code using `AudioManager`methods

```
if (isBluetoothA2dpOn()) {
    // Adjust output for Bluetooth.
} else if (isSpeakerphoneOn()) {
    // Adjust output for Speakerphone.
} else if (isWiredHeadsetOn()) {
    // Adjust output for headsets
} else { 
    // If audio plays and noone can hear it, is it still playing?
}
```



