#  Format of decoded image

There are two principal colour formats used for images: YUV and RGB.
      It is
 [
	simple] (http://www.pcmag.com/encyclopedia/term/55166/yuv-rgb-conversion-formulas)
to translate from one to the other.
      But the Broadcom
 `image_decode`component won't do any
      translation: it will only give you YUV images. 
      This is according to the OpenMAX specifications for a JPEG
      decoder. If you want RGB, you have to do it yourself
      or use another Broadcom component,
      the
 `resize`component. This is not a standard
      OpenMAX component (see below).

