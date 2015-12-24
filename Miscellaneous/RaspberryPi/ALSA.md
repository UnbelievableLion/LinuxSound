
##  ALSA 


The Raspberry Pi uses the ALSA driver snd_bcm2835, and this can manage
      HDMI output. The command `alsa-info`is not present, but as this is a shell
      script it can be copied from elsewhere  and will run on the RPi. 
      Some of the usual configuration files and
      commands on a larger distro are missing, but it shows on the soft float Debian distro

```

	
upload=true&script=true&cardinfo=
!!################################
!!ALSA Information Script v 0.4.61
!!################################

!!Script ran on: Sun Nov  4 02:33:41 UTC 2012


!!Linux Distribution
!!------------------

Debian GNU/Linux wheezy/sid \n \l PRETTY_NAME="Debian GNU/Linux wheezy/sid" NAME="Debian GNU/Linux" ID=debian


!!DMI Information
!!---------------

Manufacturer:      
Product Name:      
Product Version:   
Firmware Version:  


!!Kernel Information
!!------------------

Kernel release:    3.1.9+
Operating System:  GNU/Linux
Architecture:      armv6l
Processor:         unknown
SMP Enabled:       No


!!ALSA Version
!!------------

Driver version:     1.0.24
Library version:    1.0.25
Utilities version:  1.0.25


!!Loaded ALSA modules
!!-------------------

snd_bcm2835


!!Sound Servers on this system
!!----------------------------

No sound servers found.


!!Soundcards recognised by ALSA
!!-----------------------------

 0 [ALSA           ]: BRCM bcm2835 ALSbcm2835 ALSA - bcm2835 ALSA
                      bcm2835 ALSA


!!PCI Soundcards installed in the system
!!--------------------------------------



!!Advanced information - PCI Vendor/Device/Subsystem ID's
!!-------------------------------------------------------



!!Modprobe options (Sound related)
!!--------------------------------

snd_atiixp_modem: index=-2
snd_intel8x0m: index=-2
snd_via82xx_modem: index=-2
snd_pcsp: index=-2
snd_usb_audio: index=-2


!!Loaded sound module options
!!---------------------------

!!Module: snd_bcm2835
	* : 


!!ALSA Device nodes
!!-----------------

crw-rw---T+ 1 root audio 116,  0 Nov  3 22:17 /dev/snd/controlC0
crw-rw---T+ 1 root audio 116, 16 Nov  3 22:17 /dev/snd/pcmC0D0p
crw-rw---T+ 1 root audio 116,  1 Nov  3 22:17 /dev/snd/seq
crw-rw---T+ 1 root audio 116, 33 Nov  3 22:17 /dev/snd/timer

/dev/snd/by-path:
total 0
drwxr-xr-x 2 root root  60 Nov  3 22:17 .
drwxr-xr-x 3 root root 140 Nov  3 22:17 ..
lrwxrwxrwx 1 root root  12 Nov  3 22:17 platform-bcm2835_AUD0.0 -gt; ../controlC0


!!Aplay/Arecord output
!!--------------------

APLAY

**** List of PLAYBACK Hardware Devices ****
card 0: ALSA [bcm2835 ALSA], device 0: bcm2835 ALSA [bcm2835 ALSA]
  Subdevices: 8/8
  Subdevice #0: subdevice #0
  Subdevice #1: subdevice #1
  Subdevice #2: subdevice #2
  Subdevice #3: subdevice #3
  Subdevice #4: subdevice #4
  Subdevice #5: subdevice #5
  Subdevice #6: subdevice #6
  Subdevice #7: subdevice #7

ARECORD

**** List of CAPTURE Hardware Devices ****

!!Amixer output
!!-------------

!!-------Mixer controls for card 0 [ALSA]

Card hw:0 'ALSA'/'bcm2835 ALSA'
  Mixer name	: 'Broadcom Mixer'
  Components	: ''
  Controls      : 3
  Simple ctrls  : 1
Simple mixer control 'PCM',0
  Capabilities: pvolume pvolume-joined pswitch pswitch-joined penum
  Playback channels: Mono
  Limits: Playback -10239 - 400
  Mono: Playback -1725 [80%] [-17.25dB] [on]


!!Alsactl output
!!--------------

--startcollapse--
state.ALSA {
	control.1 {
		iface MIXER
		name 'PCM Playback Volume'
		value -1725
		comment {
			access 'read write'
			type INTEGER
			count 1
			range '-10239 - 400'
			dbmin -9999999
			dbmax 400
			dbvalue.0 -1725
		}
	}
	control.2 {
		iface MIXER
		name 'PCM Playback Switch'
		value true
		comment {
			access 'read write'
			type BOOLEAN
			count 1
		}
	}
	control.3 {
		iface MIXER
		name 'PCM Playback Route'
		value 2
		comment {
			access 'read write'
			type INTEGER
			count 1
			range '0 - 2'
		}
	}
}
--endcollapse--


!!All Loaded Modules
!!------------------

Module
snd_bcm2835
snd_pcm
snd_seq
snd_timer
snd_seq_device
snd
snd_page_alloc
evdev


!!ALSA/HDA dmesg
!!--------------

[   16.369584] EXT4-fs (mmcblk0p2): re-mounted. Opts: (null)
[   16.750460] ### snd_bcm2835_alsa_probe c05c88e0 ############### PROBING FOR bcm2835 ALSA device (0):(1) ###############
[   16.776071] Creating card...
--
[   16.834082] Registering card ....
[   16.853728] bcm2835 ALSA CARD CREATED!
[   16.883259] ### BCM2835 ALSA driver init OK ### 
[   23.608360] smsc95xx 1-1.1:1.0: eth0: link up, 100Mbps, full-duplex, lpa 0x45E1
	
      
```



