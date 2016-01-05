
##  User level tools 


LADSPA plugins live in a directory defaulting to `/usr/lib/ladspa`. This can be controlled
by the environment variable `LADSPA_PATH`.
This directory will contain a set of `.so`files as LADSPA plugins.


Each plugin contains information
about itself, and the set of plugins can be inspected by running the
command line tool `listplugins`. By installing
just LADPSA, the default plugins are

```
/usr/lib/ladspa/amp.so:
	Mono Amplifier (1048/amp_mono)
	Stereo Amplifier (1049/amp_stereo)
/usr/lib/ladspa/delay.so:
	Simple Delay Line (1043/delay_5s)
/usr/lib/ladspa/filter.so:
	Simple Low Pass Filter (1041/lpf)
	Simple High Pass Filter (1042/hpf)
/usr/lib/ladspa/sine.so:
	Sine Oscillator (Freq:audio, Amp:audio) (1044/sine_faaa)
	Sine Oscillator (Freq:audio, Amp:control) (1045/sine_faac)
	Sine Oscillator (Freq:control, Amp:audio) (1046/sine_fcaa)
	Sine Oscillator (Freq:control, Amp:control) (1047/sine_fcac)
/usr/lib/ladspa/noise.so:
	White Noise Source (1050/noise_white)
```


More detailed information about each plugin can be found from
the tool `analyseplugin`. For example for the `amp`plugin,

```
$analyseplugin amp

Plugin Name: "Mono Amplifier"
Plugin Label: "amp_mono"
Plugin Unique ID: 1048
Maker: "Richard Furse (LADSPA example plugins)"
Copyright: "None"
Must Run Real-Time: No
Has activate() Function: No
Has deactivate() Function: No
Has run_adding() Function: No
Environment: Normal or Hard Real-Time
Ports:	"Gain" input, control, 0 to ..., default 1, logarithmic
	"Input" input, audio
	"Output" output, audio

Plugin Name: "Stereo Amplifier"
Plugin Label: "amp_stereo"
Plugin Unique ID: 1049
Maker: "Richard Furse (LADSPA example plugins)"
Copyright: "None"
Must Run Real-Time: No
Has activate() Function: No
Has deactivate() Function: No
Has run_adding() Function: No
Environment: Normal or Hard Real-Time
Ports:	"Gain" input, control, 0 to ..., default 1, logarithmic
	"Input (Left)" input, audio
	"Output (Left)" output, audio
	"Input (Right)" input, audio
	"Output (Right)" output, audio
```


A simple test of each plugin can be performed using `applyplugin`. When run with no arguments
it gives a usage message:

```
$applyplugin 
Usage:	applyplugin [flags] <input Wave file> <output Wave file>
	<LADSPA plugin file name> <plugin label> <Control1> <Control2>...
	[<LADSPA plugin file name> <plugin label> <Control1> <Control2>...]...
Flags:	-s<seconds>  Add seconds of silence after end of input file.
```


This takes an input and an output WAV file as first and second parameters.
The next ones are the names of the `.so`file
and the plugin label chosen. This is followed by values of the
controls. For the `amp`plugin, the file name is `amp.so`, the stereo plugin is `amp_stereo`and there is only one control for gain as a value between zero
and one. To halve the volume of a file containing stereo WAV data,

```
applyplugin 54154.wav tmp.wav amp.so amp_stereo 0.5
```
