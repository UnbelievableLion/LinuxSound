
##  Comments on device choices 


if the default devices are chosen, the input and output devices are the PulseAudio
      default devices. Normally these would both be the computer's sound card.
      However, the default devices can be changed using for example, the PulseAudio
      volume control. These can set either the input device, the output device or both.
      The dialogue can also be used to set the input device for sampled media.


This raises a number of possible scenarios:

+ The default PulseAudio device selects the same device for input and output
+ The default PulseAudio device selects different devices for input and output
+ The default PulseAudio device is used for output while the ALSA device is
	  used for input, but the physical device is the same
+ The default PulseAudio device is used for output while the ALSA device is
	  used for input, and the physical devices are different




Using different devices raises the problem of "clock drift", where the devices
      have different clocks which are not synchronised. The worst case seems to be
      the second one, where over a three minute song on my system I could hear a noticeable
      lag in playing the sampled audio, while the KAR file played happily. It also introduced
      a noticeable latency in playing the sampled audio.
