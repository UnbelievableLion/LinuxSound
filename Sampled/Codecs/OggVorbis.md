
##  Ogg Vorbis 


Ogg Vorbis is one of the "good guys". From [
	Vorbis.com
      ](http://www.vorbis.com/) "Ogg Vorbis is a completely open, patent-free, professional audio encoding and 
      streaming technology with all the benefits of Open Source"


The names are [ described](http://www.vorbis.com/faq/#what) as


   > 

> Ogg:
	  Ogg is the name of Xiph.org's container format for audio, video, and metadata.
	  This puts the stream data into _frames_ which are easier to manage in
	  files other things.


> Vorbis:
	  Vorbis is the name of a specific audio compression scheme that's designed to be 
	  contained in Ogg. Note that other formats are capable of being embedded in 
	  Ogg such as FLAC and Speex.




The extension .oga is preferred for Ogg audio files, although .ogg was previously used.


At times it is necessary to be closely aware of the distinction between Ogg and Vorbis.
      For example, OpenMAX IL has a number of standard audio components including one to decode
      various codecs. The LIM component with role "audio decoder ogg" 
      can decode Vorbis streams. 
      But even though the component includes the name "ogg", it _cannot_ decode
      Ogg files -
      they are the containers of Vorbis streams and it can _only_ decode the Vorbis stream. 
      To decode an Ogg file requires
      use of a different component, an "audio decoder with framing".
