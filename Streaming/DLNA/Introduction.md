
##  Introduction 


DLNA (Digital Living Network Alliance) is designed for sharing
digital media such as photos, audio and video in a home network.
It is built on top of the UPnP (Universal Plug 'n Play) protocol
suite. This in turn is built on some of the uglier of the internet
standards such as SOAP. UPnP itself compounds this poor choice of
base technologies by using what can only be described as an
appallingly badly engineered hack in order to handle media information:
with its most complex data type being a string, UPnP buries complete
XML documents inside these strings, so that one XML document contains
another XML document as embedded string.
Oh dear, better quality engineers could surely
have come up with better solutions than this!


UPnP is open in that it can describe many different home network devices
and formats of data. DLNA restricts this to only a few "approved"
types, and then makes the specification private, only available after
paying a fee.


Despite all this, an increasing number of devices are "DLNA enabled" such
as TVs, BluRay players, etc. It seems like DLNA is here to stay :-(.


Matthew Panton in [DLNA for media streamers--what does it all mean?](http://news.cnet.com/8301-17938_105-10007069-1.html) points out some further issues with DLNA.
mainly relating to supported file formats.
The truth of his comments are illustrated by my latest purchase of
a Sony BDP-S390 BluRay player. It supports LPCM (.wav) as required,
but out of the optional  	MP3, WMA9, AC-3, AAC, ATRAC3plus
it supports MP3, AAC/HE-AAC (.m4a) and WMA9 Standard (.wma).
And of course, Ogg is nowhere in any of the DLNA lists.
