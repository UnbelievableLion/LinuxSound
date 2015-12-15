#  PCM 

From
 [Wikipedia] ()


Pulse-code modulation (PCM) is a method used to digitally represent sampled analog signals. 
	  It is the standard form for digital audio in computers and various Blu-ray, 
	  DVD and Compact Disc formats, as well as other uses such as digital telephone systems. 
	  A PCM stream is a digital representation of an analog signal, in which the magnitude 
	  of the analog signal is sampled regularly at uniform intervals, with each sample being 
	  quantized to the nearest value within a range of digital steps.

PCM streams have two basic properties that determine their fidelity to the original 
	  analog signal: the sampling rate, which is the number of times per second that samples 
	  are taken; and the bit depth, which determines the number of possible digital values 
	  that each sample can take.



PCM data can be stored in files as "raw" data. In this case there is no header information
      to say what the sampling rate and bit depth are. Many tools such as
 `sox`use the file extension to determine these properties. From
 [ man soxformat] (http://sox.sourceforge.net/soxformat.html)
:

f32 and f64 indicate files encoded as 32 and
              64-bit  (IEEE  single  and  double precision) floating point PCM
              respectively; s8, s16, s24, and s32  indicate  8,  16,  24,  and
              32-bit  signed  integer  PCM respectively; u8, u16, u24, and u32
              indicate 8, 16, 24, and  32-bit  unsigned  integer  PCM  respectively

But it should be noted that the file extension is only an aid to understanding some of the
      PCM codec parameters and how it is stored in the file.

