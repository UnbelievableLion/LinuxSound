
## {{ page.path }} Sample rate


Digitising an analogue signal means taking samples from that signal
at regular intervals, and representing those samples on a discrete
scale. The frequency of taking samples is the sample rate.
For example, audio on a CD is sampled at 44,100hz, that is,
44,100 times each second. On a DVD, samples may be taken
upto 192,000 times per second, with a sampling rate of
192kHz. Conversely, the standard telephone sampling rate
is 8kHz.


This figure from [Wikipedia: Pulse-code modulation](http://en.wikipedia.org/wiki/Pulse-code_modulation) illustrates sampling:


![alt text](http://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Pcm.svg/250px-Pcm.svg.png)


The sampling rate affects two major factors. Firstly, the
higher the sampling rate, the larger the size of the data.
All other things being equal, doubling the sample rate
will double the data requirements.
On the other hand the [Nyquist-Shannon theorem](http://en.wikipedia.org/wiki/Nyquist_theorem) places limits on the accuracy of sampling continous data:
an analogue signal can only be reconstructed from a digital
signal (i.e. be distortion-free) if the highest frequency
in the signal is less than one-half the sampling rate.


This is often where the arguments about the "quality" of
vinyl versus CDs end up, as in [Vinyl vs. CD myths refuse to die](http://www.eetimes.com/electronics-blogs/audio-designline-blog/4033509/Vinyl-vs-CD-myths-refuse-to-die) .
With a sampling rate of 44.1kHz, frequencies in the original
signal above 22.05kHz may not be reproduced accurately when
converted back to analogue for a loudspeaker or headphones.
Since the typical hearing range for humans is only upto 20,000hz
(and mine is now down to about 10,000hz) then this should not be
a significant problem. But some audiophiles claim to have amazingly
sensitive ears...
