#  libass 

Sub Station Alpha and its renderers appear to have been through a complex
      history. According to
 [
	The old and present: VSFilter
      ] (http://blog.aegisub.org/2010/02/old-and-present-vsfilter.html)
the ASS format was finalised about 2004, and the renderer
      VSFilter was made open source at this time.
      However, around 2007 development of VSFilter ceased
      and several forks were made. These introduced several
      extensions to the format, such as the
blur
tag
      by Aegisub. Some of these forks since merged, some were abandoned,
      and for some of these forks there is still code in the wild.


 [
	libass 
      ] (http://code.google.com/p/libass/)
is the main rendering library for Linux. An alternative,
      xy-vsfilter, claims to be faster, more reliable, etc but does
      not seem to have a Linux implementation.
      libass supports some of the later extensions - these seem to be
      the Aegisub 2008 extensions:
 [
	VSFilter hacks
      ] (http://blog.aegisub.org/2008/07/vsfilter-hacks.html)
.

