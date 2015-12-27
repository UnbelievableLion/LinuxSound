
##  The type LADSPA_Descriptor 


Coomunication between an application and a LADSPA plugin
takes place through a data structure of type `LADSPA_Descriptor`. This has fields that
contain all of the information that is shown by `listplugins`and `analyseplugins`.
In addition, it contains fields that control memory layout,
whether or not it supports hard realtime, etc.

+ __ ` unsigned long UniqueID `__: Each plugin must have a unique ID within the LADSPA
system.
+ __ ` const char * Label  `__: This is the label used to refer to the plugin within the
LADSPA system
+ __ ` const char * Name  `__: This is the "user friendly" name of the plugin.
For example, the `amp`file (shown later)
contains two plugins,
the mono amplifier has ID 1048,  label "amp_mono" and
name "Mono Amplifier", while the stereo amplifier has
ID 1049, label "amp_stereo" and name "Stereo Amplifier"
+ __ ` const char * Maker, * Copyright `__: Obvious
+ __ ` unsigned long PortCount `__: This indicates the number of ports (input AND output) present on
the plugin
+ __ ` const LADSPA_PortDescriptor * PortDescriptors  `__: This member indicates an array of port descriptors. Valid indices
vary from 0 to PortCount-1
+ __ ` const char * const * PortNames `__: This member indicates an array of null-terminated strings
describing ports. For example, the mono amplifer has two
input ports and one output port labelled
"Gain", "Input" and "Output". The Input port has
PortDescriptor `(LADSPA_PORT_INPUT | LADSPA_PORT_AUDIO)`while the Output port has
PortDescriptor `(LADSPA_PORT_OUTPUT | LADSPA_PORT_AUDIO)`
+ __ ` LADSPA_PortRangeHint * PortRangeHints  `__: This is an array of type `LADSPA_PortRangeHint`,
one element for each port. This allows the plugin to
pass information such as whether it has a value that
is bounded above or below, and if so what is that bound,
as to whether it should be treated as a Boolean value,
and so on. These hints could be used by, say, a GUI to
give a visual control display for the plugin.

Additionally, it contains fields that are function
pointers, which are called by the LADSPA runtime to
initialise the plugin, handle data and clean up.
These fields are

+ __ `instantiate`__: This takes the sample rate as parameter.
It is responsible for general instantiation of the plugin,
setting local parameters, allocating memory, etc.
It returns a pointer to a plugin-specific data
structure containing all of the information
relating to that plugin. This pointer will be passed
as the first parameter to the other functions
so that they can retrieve information for this plugin.
+ __ `connect_port`__: This takes three parameters, the second and third being
the port number and the address on which data will be
readable/writable respectively. The plugin is expected
to read/write data from the LADSPA runtime using this
address only for each port. it will be called before `run`or `run_adding`.
+ __ `activate/deactivate`__: These may be called to re-initialise the plugin state.
They may be `NULL`.
+ __ `run`__: This function is where all of the plugin'a real work is done.
Its second parameter is the number of samples that are
ready to read/write.
+ __ `cleanup`__: Obvious

Other function fields are normally set to `NULL`.
