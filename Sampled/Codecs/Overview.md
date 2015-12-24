
##  Overview 


Audio and video data needs to be represented in digital format to be
	used by a computer. Audio and video data contain an enormous amount of
	information, and so digital representations of this data can occupy
	huge amounts of space. Consequently, computer scientists have developed
	many different ways of representing this information, sometimes in
	ways that preserve all of the information (lossless) and sometimes
	in ways that lose information (lossy).


Each way of representing the information digitally is known as a _codec_ .
      The simplest way, described in the next section, is to represent it as "raw"
      pulse-code modulated data (PCM). Hardware devices such as sound cards can deal
      with PCM data directly, but PCM data can use a  lot of space.


Most codecs will attempt to reduce the memory requirements of PCM data by _encoding_ it to another form, called encoded data. It can then be _decoded_ back to PCM form when required. Depending on the codec
      algorithms, the re-generated PCM may have the same information content as
      the original PCM data
      (lossless) or may contain less information (lossless).


Encoded audio data may or may not contain information about the properties
      of the data. This information may be about the original PCM data such 
      as the number of channels (mono, stereo),
      the sampling rate, the number of bits in the sample, etc.
      Or it may be information about the encoding process itself, such as the
      size of framed data. The encoded data along with this additional information
      may be stored in a file, transmitted across the network, etc.
      if this is done, the encoded data plus the additional information is
      amalgamated into a _container_ .


It is important at times to know whether you are dealing with just the
      encoded data, or with a container that holds this data. For example,
      files on disk will normally be containers, holding additional information
      along with the encoded data. But audio data manipulation
      libaries will typically deal with the encoded data itself, after the
      additional data has been removed.
