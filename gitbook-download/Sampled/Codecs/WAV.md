#  WAV 

WAV is a file format wrapper around audio data as a container.
      The audio data is often PCM.
      The file format is based on RIFF (Resource Interchange File Format ).
      While it is a Microsoft/IBM format, it does not seem to be encumbered by 
      patents.

A good description of the format is given by
 [
	Topherlee
      ] (http://www.topherlee.com/software/pcm-tut-wavformat.html)
.
      The WAV file header contains information about the PCM codec and also
      about how it is stored (e.g. little- or big-endian).

Because they usually contain uncompressed audio data, WAV files are often huge,
      around 50Mbytes for a 3 minute song.

