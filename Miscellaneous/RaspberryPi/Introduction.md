
##  Introduction 

###  Hardware 


The Raspberry Pi (RPi)  Model B  has 512Mb RAM, 2 USB ports and an Ethernet port.
      It has HDMI, and analogue audio and video outputs.
      From the [FAQ](http://www.raspberrypi.org/faqs) 


   > The SoC is a Broadcom BCM2835. This contains an ARM1176JZFS, with floating point, 
	running at 700Mhz, and a Videocore 4 GPU. The GPU is capable of BluRay quality 
	playback, using H.264 at 40MBits/s. It has a fast 3D core accessed using 
	the supplied OpenGL ES2.0 and OpenVG libraries.



Graphically it looks like


![alt text](http://www.raspberrypi.org/wp-content/uploads/2011/07/RaspiModelB.png)


and physically it looks like


![alt text](http://www.raspberrypi.org/wp-content/uploads/2011/07/7513051848_9a6ef2feb8_o.jpeg).


The RPi has audio out through the HDMI port and also through an analogue 3.5 mm
      audio out. There is no audio in. However, there are USB ports, and a USB sound
      card can be plugged which is recognised by the Linux distros.


The CPU is an ARM CPU. A simple overview of the differences between ARM and
      Intel instruction sets is given by [
	ARM vs x86 Processors: What's the Difference?
      ](http://www.brighthub.com/computing/hardware/articles/107133.aspx) 

###  Alternative Single Board Computers 


There are many single board computers. Wikipedia has a [
	List of single-board computers
      ](http://en.wikipedia.org/wiki/List_of_single_board_computers) . These are all potential alternatives to the RPi. Here is just a quick
      selection

+ __ [
	    Gumstix
	  ](http://en.wikipedia.org/wiki/Gumstix) __:
This is a single board computer that has been around for many years (I got one
	  in 2004). It isn't high powered, but isn't meant to be.
+ __ [
	    Arduino
	  ](http://en.wikipedia.org/wiki/Arduino) __:
The Arduino is designed as a micro-controller for electronic projects.
	  It uses an ARM Cortec-M3 CPU which has even lower specs than the RPi
+ __ [
	    UDOO
	  ](http://www.udoo.org/) __:
 [
	     UDOO
	  ](http://www.bit-tech.net/news/hardware/2013/04/16/udoo/1) attempts to marry the best of the RPi and Arduino with two CPUs
	  into a single board computer
+ __ [
	    ODroid
	  ](http://odroid.com) __:
The ODroid U2 is a higher powered system than the RPI, evaluated by [
	    Gigaom
	  ](http://gigaom.com/2013/02/11/following-raspberry-pi-the-89-odroid-u2-continues-small-cheap-computing-movement/) . It is about double the price.
+ __ [
	    BeagleBone
	  ](http://beagleboard.org/Products/BeagleBone%20Black) __:
The BeagleBone Black has a slightly better CPU (ARM Cortex-A8)
	  than the RPi, and is a bit more expensive
+ __Wandboard__:

+ __PandaBoard__:

+ __CubieBoard__:




###  Distros 


There are a number of Linux images available from the Raspberry Pi site,
      and others being developed elsewhere. I'm using the Debian-based image which
      essentially comes in two forms: with soft float using Debian and with hard float
      using  the FPU, called Raspbian. The hard float image is required for decent
      sound processing which is heavily floating point dependent.
      There is a good article benchmarking these against each other: [
	Raspbian Benchmarking – armel vs armhf
      ](http://www.memetic.org/raspbian-benchmarking-armel-vs-armhf/) .
      Another set of benchmarks is at [
	RPi Performance
      ](http://elinux.org/RaspberryPiPerformance) .
      Basically, these show that you should use the hard float version if you
      want good floating point performance, and this is required for audio
      processing.


ELinux.org maintains a list of [
	RPi Distributions
      ](http://elinux.org/RPi_Distributions) There are many standard Linux distros included here, such as Fedora,
      Debian, Arch, SUSE, Gentoo and others.
      The RPi has gained traction as a media centre based on the XBMC
      media centre, and this is represented by distros such as
      Raspbmc and OpenElec.


So how does it go with the various audio tools we have been discussing so far?
      It's a mixed bag.



