
##  Asynchronous API 


The simple API is ... simple. By contrast, the asynchronous API is
large and complex. There are also very few examples of using this
API.


Nearly all interaction with this API is asynchronous.
A call is made to the PulseAudio server and when the response
is ready, a library invokes a callback function that you
will have passed to it when making the library call.
This avoids the need for user code to either block or make
polling calls.


The essential structure is

+ Create a PulseAudio mainloop (synchronous - pa_mainloop_new)
+ Get the mainloop API object, a table of mainloop functions
(synchronous - pa_mainloop_get_api)
+ Get a context object to talk to the PulseAudio server
(synchronous - pa_context_new)
+ Establish a connection to the PulseAudio server.
This is asynchronous -  pa_context_connect
+ Register a callback for context state changes from the server
-  pa_context_set_state_callback
+ Commence the event processing loop - (pa_mainloop_run
+ Within the context state callback, determine what state
has changed e.g. the connection has been established
+ Within this callback, set up, for example,
record or playback streams
+ Establish further callbacks for these streams
+ Within the stream callbacks, do more processing,
such as saving a recording stream to file

Steps (1) - (7) will be common to most applications.
The context state callback wil be called in response to changes
in the server. These are state changes such as `PA_CONTEXT_CONNECTIN`, `PA_CONTEXT_SETTING_NAME`and so on. The change of relevance to most applications will be `PA_CONTEXT_READY`. This signifies that the application
can make requests of the server in its steady state.


In step (8) the application will set its own behaviour.
This is done by setting up further callback functions for various
operations, such as listing devices or playing audio.

###  List of devices 


The function `pa_context_get_sink_info_list`will set up a callback function to list source devices by

```
pa_context_get_sink_info_list(c, sinklist_cb, NULL)
```


where `c`is the context, `sinklist_cb`is the application's callback
and `NULL`is user data passed to the callback.


The callback is called as

```
void sinklist_cb(pa_context *c, const pa_sink_info *i, int eol, void *userdata)
```


The parameter `eol`can take three values: negative means a failure
of some kind; zero means a valid entry for `pa_sink_info`; positive means that there are no more
valid entries in the list.


The structure `pa_sink_info`is defined as

```
struct {
  const char *  name;
  uint32_t 	index;
  const char * 	description;
  pa_sample_spec 	sample_spec;
  pa_channel_map 	channel_map;
  uint32_t 	owner_module;
  pa_cvolume 	volume;
  int 	mute;
  uint32_t 	monitor_source;
  const char * 	monitor_source_name;
  pa_usec_t 	latency;
  const char * 	driver;
  pa_sink_flags_t 	flags;
  pa_proplist * 	proplist;
  pa_usec_t 	configured_latency;
  pa_volume_t 	base_volume;
  pa_sink_state_t 	state;
  uint32_t 	n_volume_steps;
  uint32_t 	card;
  uint32_t 	n_ports;
  pa_sink_port_info ** 	ports;
  pa_sink_port_info * 	active_port;
  uint8_t 	n_formats;
  pa_format_info ** 	formats;
} pa_sink_info
```


Further information about this structure is maintained in the
Doxygen entry [pa_sink_info Struct Reference](http://freedesktop.org/software/pulseaudio/doxygen/structpa__sink__info.html) 


For information, the major fields are the `name`and the `description`. The `index`is an opaque index into
some data structure and is used in many PulseAudio functions.
The `proplist`is a map of general information that may contain interesting information.
This can be retrieved by iterating through the map.


There is a similar callback and data structures for input devices.


A program to list input and output devices current when the application connects
to the server is [palist_devices.c:](palist_devices.c) 

```cpp
/**
 * palist_devices.c 
 * Jan Newmarch
 */

#include <stdio.h>
#include <string.h>
#include <pulse/pulseaudio.h>

#define _(x) x

// quit when this reaches 2
int no_more_sources_or_sinks = 0;

int ret;

pa_context *context;

void show_error(char *s) {
    fprintf(stderr, "%s\n", s);
}

void print_properties(pa_proplist *props) {
    void *state = NULL;

    printf("  Properties are: \n");
    while (1) {
	char *key;
	if ((key = pa_proplist_iterate(props, &state)) == NULL) {
	    return;
	}
	char *value = pa_proplist_gets(props, key);
	printf("   key: %s, value: %s\n", key, value);
    }
}


/**
 * print information about a sink
 */
void sinklist_cb(pa_context *c, const pa_sink_info *i, int eol, void *userdata) {

    // If eol is set to a positive number, you're at the end of the list
    if (eol > 0) {
	printf("**No more sinks\n");
	no_more_sources_or_sinks++;
	if (no_more_sources_or_sinks == 2)
	    exit(0);
	return;
    }

    printf("Sink: name %s, description %s\n", i->name, i->description);
    print_properties(i->proplist);
}

/**
 * print information about a source
 */
void sourcelist_cb(pa_context *c, const pa_source_info *i, int eol, void *userdata) {
    if (eol > 0) {
	printf("**No more sources\n");
	no_more_sources_or_sinks++;
	if (no_more_sources_or_sinks == 2)
	    exit(0);
	return;
    }

    printf("Source: name %s, description %s\n", i->name, i->description);
    print_properties(i->proplist);
}


void context_state_cb(pa_context *c, void *userdata) {

    switch (pa_context_get_state(c)) {
    case PA_CONTEXT_UNCONNECTED:
    case PA_CONTEXT_CONNECTING:
    case PA_CONTEXT_AUTHORIZING:
    case PA_CONTEXT_SETTING_NAME:
	break;

    case PA_CONTEXT_READY: {
	pa_operation *o;

	// set up a callback to tell us about source devices
	if (!(o = pa_context_get_source_info_list(c,
					    sourcelist_cb,
					    NULL
						  ))) {
	    show_error(_("pa_context_subscribe() failed"));
	    return;
	}
	pa_operation_unref(o);

	// set up a callback to tell us about sink devices
	if (!(o = pa_context_get_sink_info_list(c,
					    sinklist_cb,
					    NULL
						  ))) {
	    show_error(_("pa_context_subscribe() failed"));
	    return;
	}
	pa_operation_unref(o);

	break;
    }

    case PA_CONTEXT_FAILED:
    case PA_CONTEXT_TERMINATED:
    default:
	return;
    }
}

int main(int argc, char *argv[]) {

    // Define our pulse audio loop and connection variables
    pa_mainloop *pa_ml;
    pa_mainloop_api *pa_mlapi;

    // Create a mainloop API and connection to the default server
    pa_ml = pa_mainloop_new();
    pa_mlapi = pa_mainloop_get_api(pa_ml);
    context = pa_context_new(pa_mlapi, "Device list");

    // This function connects to the pulse server
    pa_context_connect(context, NULL, 0, NULL);

    // This function defines a callback so the server will tell us its state.
    pa_context_set_state_callback(context, context_state_cb, NULL);

    if (pa_mainloop_run(pa_ml, &ret) < 0) {
	printf("pa_mainloop_run() failed.");
	exit(1);
    }
}
```


On my laptop this gives (elided)

```
Source: name alsa_output.pci-0000_01_00.1.hdmi-stereo.monitor, description Monitor of HDMI Audio stub Digital Stereo (HDMI)
  Properties are: 
   key: device.description, value: Monitor of HDMI Audio stub Digital Stereo (HDMI)
   key: device.class, value: monitor
   key: alsa.card, value: 1
   key: alsa.card_name, value: HDA NVidia
   key: alsa.long_card_name, value: HDA NVidia at 0xe5080000 irq 17
   key: alsa.driver_name, value: snd_hda_intel
   key: device.bus_path, value: pci-0000:01:00.1
   key: sysfs.path, value: /devices/pci0000:00/0000:00:01.0/0000:01:00.1/sound/card1
   key: device.bus, value: pci
   key: device.vendor.id, value: 10de
   key: device.vendor.name, value: nVidia Corporation
   key: device.product.id, value: 0e08
   key: device.product.name, value: HDMI Audio stub
   key: device.string, value: 1
   key: module-udev-detect.discovered, value: 1
   key: device.icon_name, value: audio-card-pci
Source: name alsa_output.pci-0000_00_1b.0.analog-stereo.monitor, description Monitor of Internal Audio Analog Stereo
  Properties are: 
   ...
Source: name alsa_input.pci-0000_00_1b.0.analog-stereo, description Internal Audio Analog Stereo
  Properties are: 
  ...
Source: name alsa_output.usb-Creative_Technology_Ltd_SB_X-Fi_Surround_5.1_Pro_000003d0-00-Pro.analog-stereo.monitor, description Monitor of SB X-Fi Surround 5.1 Pro Analog Stereo
  Properties are: 
  ...
Source: name alsa_input.usb-Creative_Technology_Ltd_SB_X-Fi_Surround_5.1_Pro_000003d0-00-Pro.analog-stereo, description SB X-Fi Surround 5.1 Pro Analog Stereo
  Properties are: 
  ...
**No more sources
Sink: name alsa_output.pci-0000_01_00.1.hdmi-stereo, description HDMI Audio stub Digital Stereo (HDMI)
  Properties are: 
   key: alsa.resolution_bits, value: 16
   key: device.api, value: alsa
   key: device.class, value: sound
   key: alsa.class, value: generic
   key: alsa.subclass, value: generic-mix
   key: alsa.name, value: HDMI 0
   key: alsa.id, value: HDMI 0
   key: alsa.subdevice, value: 0
   key: alsa.subdevice_name, value: subdevice #0
   key: alsa.device, value: 3
   key: alsa.card, value: 1
   key: alsa.card_name, value: HDA NVidia
   key: alsa.long_card_name, value: HDA NVidia at 0xe5080000 irq 17
   key: alsa.driver_name, value: snd_hda_intel
   key: device.bus_path, value: pci-0000:01:00.1
   key: sysfs.path, value: /devices/pci0000:00/0000:00:01.0/0000:01:00.1/sound/card1
   key: device.bus, value: pci
   key: device.vendor.id, value: 10de
   key: device.vendor.name, value: nVidia Corporation
   key: device.product.id, value: 0e08
   key: device.product.name, value: HDMI Audio stub
   key: device.string, value: hdmi:1
   key: device.buffering.buffer_size, value: 352768
   key: device.buffering.fragment_size, value: 176384
   key: device.access_mode, value: mmap+timer
   key: device.profile.name, value: hdmi-stereo
   key: device.profile.description, value: Digital Stereo (HDMI)
   key: device.description, value: HDMI Audio stub Digital Stereo (HDMI)
   key: alsa.mixer_name, value: Nvidia GPU 1c HDMI/DP
   key: alsa.components, value: HDA:10de001c,10281494,00100100
   key: module-udev-detect.discovered, value: 1
   key: device.icon_name, value: audio-card-pci
Sink: name alsa_output.pci-0000_00_1b.0.analog-stereo, description Internal Audio Analog Stereo
  Properties are: 
  ...
Sink: name alsa_output.usb-Creative_Technology_Ltd_SB_X-Fi_Surround_5.1_Pro_000003d0-00-Pro.analog-stereo, description SB X-Fi Surround 5.1 Pro Analog Stereo
  Properties are: 
  ...
**No more sinks
```


An alternative program with the same effect is [PulseAudio: An Async Example To Get Device Lists](http://www.ypass.net/blog/2009/10/pulseaudio-an-async-example-to-get-device-lists) by Igor Brezac and Eric Connell.
It doesn't follow quite as complex a route as the above,
as it only queries the server for its devices.
However, it uses its own state machine to track where in the
callback process it is!

###  Monitoring ongoing changes: new sources and sinks 


The last program listed the source and sink devices registered
with PulseAudio at the time a connection to the server was established.
However, when a new device is connected or an existing device is
disconnected, PulseAudio registers a changes in the context and this
can also be monitored by callbacks.


The key to doing this is to _subscribe_ to context changes by `pa_context_subscribe`. This takes a context, a mask of
subscription events and user data. Possible values of the mask are
described at [Subscription event mask](http://freedesktop.org/software/pulseaudio/doxygen/def_8h.html#ad4e7f11f879e8c77ae5289145ecf6947) and include `PA_SUBSCRIPTION_MASK_SINK`for changes in sinks
and `PA_SUBSCRIPTION_MASK_SINK_INPUT`for sink input events.


Setting the callback function to monitor these changes
is a bit odd.
The function `pa_context_subscribe`takes a callback function
of type `pa_context_success_cb`but this doesn't contain
information about what caused the callback.
Instead, it is better to first call `pa_context_set_subscribe_callback`which takes a
callback function of type ` 	pa_context_subscribe_cb_t`which _does_ get passed such information and then use `NULL`for the callback in `pa_context_subscribe`!


Within a ` 	pa_context_subscribe_cb_t`subscription callback, the cause of the callback can be
examined and appropriate code called. If a new subscription to a sink
is found, then information about the sink can be found by ` pa_context_get_sink_info_by_index`which takes
another callback! after chasing through all these callbacks, you can
eventually get information about new devices.


Note that the callback function used by `pa_context_get_sink_info_list`and the callback
function used by `pa_context_get_sink_info_by_index`are the same - the callback is called once per sink device
regardless of whether it is a singleton or one of a list
of devices.


A program to list devices on connection and also to list changes
as devices are connected or disconnected is [palist_devices_ongoing.c:](palist_devices_ongoing.c) 

```cpp
/**
 * palist_clients.c 
 * Jan Newmarch
 */

/***
    This file is based on pacat.c and pavuctl.c,  part of PulseAudio.

    pacat.c:
    Copyright 2004-2006 Lennart Poettering
    Copyright 2006 Pierre Ossman <ossman@cendio.se> for Cendio AB

    PulseAudio is free software; you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published
    by the Free Software Foundation; either version 2.1 of the License,
    or (at your option) any later version.

    PulseAudio is distributed in the hope that it will be useful, but
    WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
    General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with PulseAudio; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
    USA.
***/


#include <stdio.h>
#include <string.h>
#include <pulse/pulseaudio.h>

#define _(x) x

int ret;

pa_context *context;

void show_error(char *s) {
    fprintf(stderr, "%s\n", s);
}

void print_properties(pa_proplist *props) {
    void *state = NULL;

    printf("  Properties are: \n");
    while (1) {
	char *key;
	if ((key = pa_proplist_iterate(props, &state)) == NULL) {
	    return;
	}
	char *value = pa_proplist_gets(props, key);
	printf("   key: %s, value: %s\n", key, value);
    }
}

/**
 * print information about a sink
 */
void sink_cb(pa_context *c, const pa_sink_info *i, int eol, void *userdata) {

    // If eol is set to a positive number, you're at the end of the list
    if (eol > 0) {
	return;
    }

    printf("Sink: name %s, description %s\n", i->name, i->description);
    // print_properties(i->proplist);
}

/**
 * print information about a source
 */
void source_cb(pa_context *c, const pa_source_info *i, int eol, void *userdata) {
    if (eol > 0) {
	return;
    }

    printf("Source: name %s, description %s\n", i->name, i->description);
    // print_properties(i->proplist);
}

void subscribe_cb(pa_context *c, pa_subscription_event_type_t t, uint32_t index, void *userdata) {

    switch (t & PA_SUBSCRIPTION_EVENT_FACILITY_MASK) {
	
    case PA_SUBSCRIPTION_EVENT_SINK:
	if ((t & PA_SUBSCRIPTION_EVENT_TYPE_MASK) == PA_SUBSCRIPTION_EVENT_REMOVE)
	    printf("Removing sink index %d\n", index);
	else {
	    pa_operation *o;
	    if (!(o = pa_context_get_sink_info_by_index(c, index, sink_cb, NULL))) {
		show_error(_("pa_context_get_sink_info_by_index() failed"));
		return;
	    }
	    pa_operation_unref(o);
	}
	break;

    case PA_SUBSCRIPTION_EVENT_SOURCE:
	if ((t & PA_SUBSCRIPTION_EVENT_TYPE_MASK) == PA_SUBSCRIPTION_EVENT_REMOVE)
	    printf("Removing source index %d\n", index);
	else {
	    pa_operation *o;
	    if (!(o = pa_context_get_source_info_by_index(c, index, source_cb, NULL))) {
		show_error(_("pa_context_get_source_info_by_index() failed"));
		return;
	    }
	    pa_operation_unref(o);
	}
	break;
    }
}

void context_state_cb(pa_context *c, void *userdata) {

    switch (pa_context_get_state(c)) {
    case PA_CONTEXT_UNCONNECTED:
    case PA_CONTEXT_CONNECTING:
    case PA_CONTEXT_AUTHORIZING:
    case PA_CONTEXT_SETTING_NAME:
	break;

    case PA_CONTEXT_READY: {
	pa_operation *o;

	if (!(o = pa_context_get_source_info_list(c,
						  source_cb,
						  NULL
						  ))) {
	    show_error(_("pa_context_subscribe() failed"));
	    return;
	}
	pa_operation_unref(o);

	if (!(o = pa_context_get_sink_info_list(c,
						sink_cb,
						NULL
						))) {
	    show_error(_("pa_context_subscribe() failed"));
	    return;
	}
	pa_operation_unref(o);

	pa_context_set_subscribe_callback(c, subscribe_cb, NULL);

	if (!(o = pa_context_subscribe(c, (pa_subscription_mask_t)
				       (PA_SUBSCRIPTION_MASK_SINK|
					PA_SUBSCRIPTION_MASK_SOURCE), NULL, NULL))) {
	    show_error(_("pa_context_subscribe() failed"));
	    return;
	}
	pa_operation_unref(o);

	break;
    }

    case PA_CONTEXT_FAILED:
    case PA_CONTEXT_TERMINATED:
    default:
	return;
    }
}

int main(int argc, char *argv[]) {

    // Define our pulse audio loop and connection variables
    pa_mainloop *pa_ml;
    pa_mainloop_api *pa_mlapi;
    pa_operation *pa_op;
    pa_time_event *time_event;

    // Create a mainloop API and connection to the default server
    pa_ml = pa_mainloop_new();
    pa_mlapi = pa_mainloop_get_api(pa_ml);
    context = pa_context_new(pa_mlapi, "Device list");

    // This function connects to the pulse server
    pa_context_connect(context, NULL, 0, NULL);

    // This function defines a callback so the server will tell us its state.
    pa_context_set_state_callback(context, context_state_cb, NULL);

    
    if (pa_mainloop_run(pa_ml, &ret) < 0) {
	printf("pa_mainloop_run() failed.");
	exit(1);
    }
}
```

###  Record a stream 


If you download the source for PulseAudio
from [FreeDesktop.org](http://www.freedesktop.org/wiki/Software/PulseAudio/Download) you will find a program `pacat.c`in the `utils`directory. This program uses some of the "private" API and will not
compile using the "public" libraries. It also has
all the bells and whistles that you would expect from a production program.
I've taken
this and stripped out the complexities so that you can find your
way into this API.
The file is [parec.c:](parec.c) 

```cpp
/**
 * parec.c 
 * Jan Newmarch
 */

/***
  This file is based on pacat.c,  part of PulseAudio.

  pacat.c:
  Copyright 2004-2006 Lennart Poettering
  Copyright 2006 Pierre Ossman <ossman@cendio.se> for Cendio AB

  PulseAudio is free software; you can redistribute it and/or modify
  it under the terms of the GNU Lesser General Public License as published
  by the Free Software Foundation; either version 2.1 of the License,
  or (at your option) any later version.

  PulseAudio is distributed in the hope that it will be useful, but
  WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
  General Public License for more details.

  You should have received a copy of the GNU Lesser General Public License
  along with PulseAudio; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
  USA.
***/


#include <stdio.h>
#include <string.h>
#include <pulse/pulseaudio.h>

#define CLEAR_LINE "\n"
#define _(x) x

// From pulsecore/macro.h
#define pa_memzero(x,l) (memset((x), 0, (l)))
#define pa_zero(x) (pa_memzero(&(x), sizeof(x)))

int fdout;
char *fname = "tmp.s16";

int verbose = 1;
int ret;

pa_context *context;

static pa_sample_spec sample_spec = {
  .format = PA_SAMPLE_S16LE,
  .rate = 44100,
  .channels = 2
};

static pa_stream *stream = NULL;

/* This is my builtin card. Use paman to find yours
   or set it to NULL to get the default device
*/
static char *device = "alsa_input.pci-0000_00_1b.0.analog-stereo";

static pa_stream_flags_t flags = 0;

void stream_state_callback(pa_stream *s, void *userdata) {
  assert(s);

  switch (pa_stream_get_state(s)) {
  case PA_STREAM_CREATING:
    // The stream has been created, so 
    // let's open a file to record to
    printf("Creating stream\n");
    fdout = creat(fname,  0711);
    break;

  case PA_STREAM_TERMINATED:
    close(fdout);
    break;

  case PA_STREAM_READY:

    // Just for info: no functionality in this branch
    if (verbose) {
      const pa_buffer_attr *a;
      char cmt[PA_CHANNEL_MAP_SNPRINT_MAX], sst[PA_SAMPLE_SPEC_SNPRINT_MAX];

      printf("Stream successfully created.");

      if (!(a = pa_stream_get_buffer_attr(s)))
	printf("pa_stream_get_buffer_attr() failed: %s", pa_strerror(pa_context_errno(pa_stream_get_context(s))));
      else {
	printf("Buffer metrics: maxlength=%u, fragsize=%u", a->maxlength, a->fragsize);
                    
      }

      printf("Connected to device %s (%u, %ssuspended).",
	     pa_stream_get_device_name(s),
	     pa_stream_get_device_index(s),
	     pa_stream_is_suspended(s) ? "" : "not ");
    }

    break;

  case PA_STREAM_FAILED:
  default:
    printf("Stream error: %s", pa_strerror(pa_context_errno(pa_stream_get_context(s))));
    exit(1);
  }
}

/*********** Stream callbacks **************/

/* This is called whenever new data is available */
static void stream_read_callback(pa_stream *s, size_t length, void *userdata) {

  assert(s);
  assert(length > 0);

  // Copy the data from the server out to a file
  fprintf(stderr, "Can read %d\n", length);


  while (pa_stream_readable_size(s) > 0) {
    const void *data;
    size_t length;
    
    // peek actually creates and fills the data vbl
    if (pa_stream_peek(s, &data, &length) < 0) {
      fprintf(stderr, "Read failed\n");
      exit(1);
      return;
    }
    fprintf(stderr, "Writing %d\n", length);
    write(fdout, data, length);

    // swallow the data peeked at before
    pa_stream_drop(s);
  }
}


// This callback gets called when our context changes state.  We really only
// care about when it's ready or if it has failed
void state_cb(pa_context *c, void *userdata) {
  pa_context_state_t state;
  int *pa_ready = userdata;

  printf("State changed\n");
  state = pa_context_get_state(c);
  switch  (state) {
    // There are just here for reference
  case PA_CONTEXT_UNCONNECTED:
  case PA_CONTEXT_CONNECTING:
  case PA_CONTEXT_AUTHORIZING:
  case PA_CONTEXT_SETTING_NAME:
  default:
    break;
  case PA_CONTEXT_FAILED:
  case PA_CONTEXT_TERMINATED:
    *pa_ready = 2;
    break;
  case PA_CONTEXT_READY: {
    pa_buffer_attr buffer_attr;

    if (verbose)
      printf("Connection established.%s\n", CLEAR_LINE);

    if (!(stream = pa_stream_new(c, "JanCapture", &sample_spec, NULL))) {
      printf("pa_stream_new() failed: %s", pa_strerror(pa_context_errno(c)));
      exit(1);
    }

    // Watch for changes in the stream state to create the output file
    pa_stream_set_state_callback(stream, stream_state_callback, NULL);
    
    // Watch for changes in the stream's read state to write to the output file
    pa_stream_set_read_callback(stream, stream_read_callback, NULL);

    // Set properties of the record buffer
    pa_zero(buffer_attr);
    buffer_attr.maxlength = (uint32_t) -1;
    buffer_attr.prebuf = (uint32_t) -1;
    buffer_attr.fragsize = buffer_attr.tlength = (uint32_t) -1;
    buffer_attr.minreq = (uint32_t) -1;
      
    // and start recording
    if (pa_stream_connect_record(stream, device, &buffer_attr, flags) < 0) {
      printf("pa_stream_connect_record() failed: %s", pa_strerror(pa_context_errno(c)));
      exit(1);
    }
  }

    break;
  }
}

int main(int argc, char *argv[]) {

  // Define our pulse audio loop and connection variables
  pa_mainloop *pa_ml;
  pa_mainloop_api *pa_mlapi;
  pa_operation *pa_op;
  pa_time_event *time_event;

  // Create a mainloop API and connection to the default server
  pa_ml = pa_mainloop_new();
  pa_mlapi = pa_mainloop_get_api(pa_ml);
  context = pa_context_new(pa_mlapi, "test");

  // This function connects to the pulse server
  pa_context_connect(context, NULL, 0, NULL);

  // This function defines a callback so the server will tell us its state.
  pa_context_set_state_callback(context, state_cb, NULL);

  if (pa_mainloop_run(pa_ml, &ret) < 0) {
    printf("pa_mainloop_run() failed.");
    exit(1);
  }
}
```

###  Play a file 


Recording  an input stream is done within a stream read callback by the
call `pa_stream_peek`.
Similarly, playing an output stream is done by a stream write callback
by the call `pa_stream_write`.


In the following program
the callback is set within the PA_CONTEXT_READY branch of the context
state change callback. The stream write callback is passed the number
of bytes the consuming stream is prepared to receive, so read that number
of bytes from the file and write them to the stream.


Care has to be taken at the end of file. There may be unplayed material in
PulseAudio's output buffers. This needs to be drained before the program
can exit. This is done by the function `pa_stream_drain`.
On end of file, first set the stream write callback to null so that the
output stream doesn't keep calling for more input, and then drain the stream.
A stream drain complete callback will be called on completion of this, so the
program can then exit (or do something else).


In this program we include many more callbacks than in earlier ones, to show
the range of features that can be monitored.


The program is [pacat2.c:](pacat2.c) 

```cpp
/**
 * pacat2.c 
 * Jan Newmarch
 */


/***
  This file is based on pacat.c,  part of PulseAudio.

  pacat.c:
  Copyright 2004-2006 Lennart Poettering
  Copyright 2006 Pierre Ossman <ossman@cendio.se> for Cendio AB

  PulseAudio is free software; you can redistribute it and/or modify
  it under the terms of the GNU Lesser General Public License as published
  by the Free Software Foundation; either version 2.1 of the License,
  or (at your option) any later version.

  PulseAudio is distributed in the hope that it will be useful, but
  WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
  General Public License for more details.

  You should have received a copy of the GNU Lesser General Public License
  along with PulseAudio; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
  USA.
***/


#include <stdio.h>
#include <string.h>
#include <pulse/pulseaudio.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <errno.h>
#include <unistd.h>

// ???
#define CLEAR_LINE "\n"

// From pulsecore/macro.h JN
#define pa_memzero(x,l) (memset((x), 0, (l)))
#define pa_zero(x) (pa_memzero(&(x), sizeof(x)))

int verbose = 1;
int ret;

static pa_volume_t volume = PA_VOLUME_NORM;
static int volume_is_set = 0;

static int fdin;

static pa_sample_spec sample_spec = {
  .format = PA_SAMPLE_S16LE,
  .rate = 44100,
  .channels = 2
};

static pa_stream *stream = NULL;
static pa_channel_map channel_map;
static pa_proplist *proplist = NULL;

// Define our pulse audio loop and connection variables
static pa_mainloop *mainloop;
static pa_mainloop_api *mainloop_api;
static pa_operation *pa_op;
static pa_context *context = NULL;

static void *buffer = NULL;
static size_t buffer_length = 0, buffer_index = 0;

static pa_io_event* stdio_event = NULL;

// Get device name from e.g. paman
//static char *device = "alsa_output.pci-0000_00_1b.0.analog-stereo";
// Use default device
static char *device = NULL;

static pa_stream_flags_t flags = 0;

static size_t latency = 0, process_time = 0;
static int32_t latency_msec = 1, process_time_msec = 0;

static int raw = 1;


/* Connection draining complete */
static void context_drain_complete(pa_context*c, void *userdata) {
  pa_context_disconnect(c);
}

static void stream_drain_complete(pa_stream*s, int success, void *userdata) {
  pa_operation *o = NULL;

  if (!success) {
    printf("Failed to drain stream: %s", pa_strerror(pa_context_errno(context)));
    exit(1);
  }

  if (verbose)
    printf("Playback stream drained.");

  pa_stream_disconnect(stream);
  pa_stream_unref(stream);
  stream = NULL;

  if (!(o = pa_context_drain(context, context_drain_complete, NULL)))
    pa_context_disconnect(context);
  else {
    pa_operation_unref(o);
    if (verbose)
      printf("Draining connection to server.");
  }
}


/* Start draining */
static void start_drain(void) {
  printf("Draining\n");
  if (stream) {
    pa_operation *o;

    pa_stream_set_write_callback(stream, NULL, NULL);

    if (!(o = pa_stream_drain(stream, stream_drain_complete, NULL))) {
      //printf("pa_stream_drain(): %s", pa_strerror(pa_context_errno(context)));
      exit(1);
      return;
    }

    pa_operation_unref(o);
  } else
    exit(0);
}

/* Write some data to the stream */
static void do_stream_write(size_t length) {
  size_t l;
  assert(length);

  printf("do stream write: Writing %d to stream\n", length);
  
  if (!buffer || !buffer_length) {
    buffer = pa_xmalloc(length);
    buffer_length = length;
    buffer_index = 0;
    //printf("  return without writing\n");
    //return;

  }

  while (buffer_length > 0) {
    l = read(fdin, buffer + buffer_index, buffer_length);
    if (l <= 0) {
      start_drain();
      return;
    }
    if (pa_stream_write(stream, (uint8_t*) buffer + buffer_index, l, NULL, 0, PA_SEEK_RELATIVE) < 0) {
      printf("pa_stream_write() failed: %s", pa_strerror(pa_context_errno(context)));
      exit(1);
      return;
    }
    buffer_length -= l;
    buffer_index += l;

    if (!buffer_length) {
      pa_xfree(buffer);
      buffer = NULL;
      buffer_index = buffer_length = 0;
    }
  }
}


void stream_state_callback(pa_stream *s, void *userdata) {
  assert(s);

  switch (pa_stream_get_state(s)) {
  case PA_STREAM_CREATING:
    break;
  case PA_STREAM_TERMINATED:
    break;

  case PA_STREAM_READY:

    if (verbose) {
      const pa_buffer_attr *a;
      char cmt[PA_CHANNEL_MAP_SNPRINT_MAX], sst[PA_SAMPLE_SPEC_SNPRINT_MAX];

      printf("Stream successfully created.\n");

      if (!(a = pa_stream_get_buffer_attr(s)))
	printf("pa_stream_get_buffer_attr() failed: %s\n", pa_strerror(pa_context_errno(pa_stream_get_context(s))));
      else {
	printf("Buffer metrics: maxlength=%u, fragsize=%u\n", a->maxlength, a->fragsize);
                    
      }
      /*
	printf("Using sample spec '%s', channel map '%s'.",
	pa_sample_spec_snprint(sst, sizeof(sst), pa_stream_get_sample_spec(s)),
	pa_channel_map_snprint(cmt, sizeof(cmt), pa_stream_get_channel_map(s)));
      */

      printf("Connected to device %s (%u, %ssuspended).\n",
	     pa_stream_get_device_name(s),
	     pa_stream_get_device_index(s),
	     pa_stream_is_suspended(s) ? "" : "not ");
    }

    break;

  case PA_STREAM_FAILED:
  default:
    printf("Stream error: %s", pa_strerror(pa_context_errno(pa_stream_get_context(s))));
    exit(1); //quit(1);
  }
}


/*********** Stream callbacks **************/


static void stream_success(pa_stream *s, int succes, void *userdata) {
  printf("Succeded\n");
}


static void stream_suspended_callback(pa_stream *s, void *userdata) {
  assert(s);

  if (verbose) {
    if (pa_stream_is_suspended(s))
      fprintf(stderr, "Stream device suspended.%s \n", CLEAR_LINE);
    else
      fprintf(stderr, "Stream device resumed.%s \n", CLEAR_LINE);
  }
}

static void stream_underflow_callback(pa_stream *s, void *userdata) {
  assert(s);

  if (verbose)
    fprintf(stderr, "Stream underrun.%s \n",  CLEAR_LINE);
}

static void stream_overflow_callback(pa_stream *s, void *userdata) {
  assert(s);

  if (verbose)
    fprintf(stderr, "Stream overrun.%s \n", CLEAR_LINE);
}

static void stream_started_callback(pa_stream *s, void *userdata) {
  assert(s);

  if (verbose)
    fprintf(stderr, "Stream started.%s \n", CLEAR_LINE);
}

static void stream_moved_callback(pa_stream *s, void *userdata) {
  assert(s);

  if (verbose)
    fprintf(stderr, "Stream moved to device %s (%u, %ssuspended).%s \n", pa_stream_get_device_name(s), pa_stream_get_device_index(s), pa_stream_is_suspended(s) ? "" : "not ",  CLEAR_LINE);
}

static void stream_buffer_attr_callback(pa_stream *s, void *userdata) {
  assert(s);

  if (verbose)
    fprintf(stderr, "Stream buffer attributes changed.%s \n",  CLEAR_LINE);
}

static void stream_event_callback(pa_stream *s, const char *name, pa_proplist *pl, void *userdata) {
  char *t;

  assert(s);
  assert(name);
  assert(pl);

  t = pa_proplist_to_string_sep(pl, ", ");
  fprintf(stderr, "Got event '%s', properties '%s'\n", name, t);
  pa_xfree(t);
}


/* This is called whenever new data may be written to the stream */
static void stream_write_callback(pa_stream *s, size_t length, void *userdata) {
  //assert(s);
  //assert(length > 0);

  printf("Stream write callback: Ready to write %d bytes\n", length);
  
  printf("  do stream write from stream write callback\n");
  do_stream_write(length);

 }


// This callback gets called when our context changes state.  We really only
// care about when it's ready or if it has failed
void state_cb(pa_context *c, void *userdata) {
  pa_context_state_t state;
  int *pa_ready = userdata;

  printf("State changed\n");
  state = pa_context_get_state(c);
  switch  (state) {
    // There are just here for reference
  case PA_CONTEXT_UNCONNECTED:
  case PA_CONTEXT_CONNECTING:
  case PA_CONTEXT_AUTHORIZING:
  case PA_CONTEXT_SETTING_NAME:
  default:
    break;
  case PA_CONTEXT_FAILED:
  case PA_CONTEXT_TERMINATED:
    *pa_ready = 2;
    break;
  case PA_CONTEXT_READY: {
    pa_buffer_attr buffer_attr;

    if (verbose)
      printf("Connection established.%s\n", CLEAR_LINE);

    if (!(stream = pa_stream_new(c, "JanPlayback", &sample_spec, NULL))) {
      printf("pa_stream_new() failed: %s", pa_strerror(pa_context_errno(c)));
      exit(1); // goto fail;
    }

    pa_stream_set_state_callback(stream, stream_state_callback, NULL);
    
    pa_stream_set_write_callback(stream, stream_write_callback, NULL);
    
    //pa_stream_set_read_callback(stream, stream_read_callback, NULL);
    
    pa_stream_set_suspended_callback(stream, stream_suspended_callback, NULL);
    pa_stream_set_moved_callback(stream, stream_moved_callback, NULL);
    pa_stream_set_underflow_callback(stream, stream_underflow_callback, NULL);
    pa_stream_set_overflow_callback(stream, stream_overflow_callback, NULL);
    
    pa_stream_set_started_callback(stream, stream_started_callback, NULL);
    
    pa_stream_set_event_callback(stream, stream_event_callback, NULL);
    pa_stream_set_buffer_attr_callback(stream, stream_buffer_attr_callback, NULL);
    
    

    pa_zero(buffer_attr);
    buffer_attr.maxlength = (uint32_t) -1;
    buffer_attr.prebuf = (uint32_t) -1;
    
    pa_cvolume cv;
      



    if (pa_stream_connect_playback(stream, NULL, &buffer_attr, flags,
				   NULL, 
				   NULL) < 0) {
      printf("pa_stream_connect_playback() failed: %s", pa_strerror(pa_context_errno(c)));
      exit(1); //goto fail;
    } else {
      printf("Set playback callback\n");
    }

    pa_stream_trigger(stream, stream_success, NULL);
  }

    break;
  }
}


int main(int argc, char *argv[]) {


  struct stat st;
  off_t size;
  ssize_t nread;

  // We'll need these state variables to keep track of our requests
  int state = 0;
  int pa_ready = 0;

  if (argc != 2) {
    fprintf(stderr, "Usage: %s file\n", argv[0]);
    exit(1);
  }
  // slurp the whole file into buffer
  if ((fdin = open(argv[1],  O_RDONLY)) == -1) {
    perror("open");
    exit(1);
  }

  // Create a mainloop API and connection to the default server
  mainloop = pa_mainloop_new();
  mainloop_api = pa_mainloop_get_api(mainloop);
  context = pa_context_new(mainloop_api, "test");

  // This function connects to the pulse server
  pa_context_connect(context, NULL, 0, NULL);
  printf("Connecting\n");

  // This function defines a callback so the server will tell us it's state.
  // Our callback will wait for the state to be ready.  The callback will
  // modify the variable to 1 so we know when we have a connection and it's
  // ready.
  // If there's an error, the callback will set pa_ready to 2
  pa_context_set_state_callback(context, state_cb, &pa_ready);


  if (pa_mainloop_run(mainloop, &ret) < 0) {
    printf("pa_mainloop_run() failed.");
    exit(1); // goto quit
  }



}
```


With the latency set to the default, the number of bytes that can be written on each
callback is 65470 bytes. This gives a minimum latency of 65470/44100 secs, or about
1500 msecs.
With the latency and process time both set to 1msec,
the buffer size is about 1440 bytes, for a latency
of 32 msecs.

###  Play a file using I/O callbacks 


Writing a file to an output stream is simple:
read from a file into a buffer, and keep emptying the buffer by
writing to the stream.  Reading from a file is straightforward:
use the standard Unix `read`function. You request a read of a
number of bytes, and the `read`function returns the number of bytes
actually read.
This was discussed in the last section.


The program in the PulseAudio distribution uses a more complex system.
It uses I/O-ready callbacks to pass some handling to an I/O callback.
This makes use of two functions:

+  ` pa_stream_writable_size`tells how many bytes can be
written to the stream
+  `pa_stream_write`writes a number of bytes to a stream

The logic becomes: fill a buffer by reading from the file, and at the
same time write as many bytes as possible from the buffer to the stream,
upto the limit
of the buffer size or however many bytes the stream can take, whichever
is smaller.


In PulseAudio this is done asynchronously,
using callback functions. The two relevant functions are

+ 

The function `pa_stream_set_write_callback()`registers a
callback that will be called whenever the stream is ready to be
written to. Registering the callback looks like

```
pa_stream_set_write_callback(stream, stream_write_callback, NULL)
```


The callback is passed the stream to write to (s) and the number
of bytes that can be written (length):

```
void stream_write_callback(pa_stream *s, size_t length, void *userdata)
```

+ 

A callback to read from files is registered by one of the functions
kept in the `mainloop_api`table. The registering function
is `io_new`and is passed a Unix file descriptor for the file
and the callback function. Reigstering the callback looks like

```
mainloop_api->io_new(mainloop_api,
		      fdin,
		      PA_IO_EVENT_INPUT,
		      stdin_callback, NULL))
```


The callback is passed the file descriptor (fd) to read from:

```
void stdin_callback(pa_mainloop_api *mainloop_api, pa_io_event *stdio_event, 
                    int fd, pa_io_event_flags_t f, void *userdata)
```


(Note: the PulseAudio code does a `dup2`from the source file's
descriptor to `STDIN_FILENO`- which matches the name of the
function. I can't see the point of that, and their code uses `fd`anyway.)


When should these callbacks be registered? The stream write callback can
be registered at any time after the stream has been created which is done by `pa_stream_new`. For the stdin callback, I could only get it
to work properly by registering it once the stream was ready i.e.
in the ` PA_STREAM_READY`branch of the stream state callback
function.


So after all that, what is the logic of the program?

+ In the stdin callback:
+ if the buffer has stuff in it, then just return - no point in adding
any more
+ if the buffer is empty, then query the stream to see how much can be written
to it
+ if the stream says no more, then just read something into the buffer and return
+ if the stream can be written to, then read from the file into the buffer
and write it to the stream
+ In the stream write callback:
+ if the buffer is non-empty, write its contents to the stream

The program to play from a file presently looks like [pacat.c:](pacat.c) 

```cpp
/***
  This file is based on pacat.c,  part of PulseAudio.

  pacat.c:
  Copyright 2004-2006 Lennart Poettering
  Copyright 2006 Pierre Ossman <ossman@cendio.se> for Cendio AB

  PulseAudio is free software; you can redistribute it and/or modify
  it under the terms of the GNU Lesser General Public License as published
  by the Free Software Foundation; either version 2.1 of the License,
  or (at your option) any later version.

  PulseAudio is distributed in the hope that it will be useful, but
  WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
  General Public License for more details.

  You should have received a copy of the GNU Lesser General Public License
  along with PulseAudio; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
  USA.
***/



#include <stdio.h>
#include <string.h>
#include <pulse/pulseaudio.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <errno.h>
#include <unistd.h>

#define CLEAR_LINE "\n"

// From pulsecore/macro.h JN
#define pa_memzero(x,l) (memset((x), 0, (l)))
#define pa_zero(x) (pa_memzero(&(x), sizeof(x)))

int verbose = 1;
int ret;

static pa_volume_t volume = PA_VOLUME_NORM;
static int volume_is_set = 0;

static int fdin;

static pa_sample_spec sample_spec = {
  .format = PA_SAMPLE_S16LE,
  .rate = 44100,
  .channels = 2
};

static pa_stream *stream = NULL;
static pa_channel_map channel_map;
static pa_proplist *proplist = NULL;

// Define our pulse audio loop and connection variables
static pa_mainloop *mainloop;
static pa_mainloop_api *mainloop_api;
static pa_operation *pa_op;
static pa_context *context = NULL;

static void *buffer = NULL;
static size_t buffer_length = 0, buffer_index = 0;

static pa_io_event* stdio_event = NULL;


static char *device = "alsa_output.pci-0000_00_1b.0.analog-stereo";

static pa_stream_flags_t flags = 0;

static size_t latency = 0, process_time = 0;
static int32_t latency_msec = 0, process_time_msec = 0;

static int raw = 1;



/* Write some data to the stream */
static void do_stream_write(size_t length) {
  size_t l;
  assert(length);

  printf("do stream write: Writing %d to stream\n", length);
  
  if (!buffer || !buffer_length) {
    printf("  return without writing\n");
    return;
  }

  l = length;
  if (l > buffer_length)
    l = buffer_length;
  printf("  writing %d\n", l);
  if (pa_stream_write(stream, (uint8_t*) buffer + buffer_index, l, NULL, 0, PA_SEEK_RELATIVE) < 0) {
    printf("pa_stream_write() failed: %s", pa_strerror(pa_context_errno(context)));
    exit(1);
    return;
  }

  buffer_length -= l;
  buffer_index += l;

  if (!buffer_length) {
    pa_xfree(buffer);
    buffer = NULL;
    buffer_index = buffer_length = 0;
  }
  
}

/* Connection draining complete */
static void context_drain_complete(pa_context*c, void *userdata) {
  pa_context_disconnect(c);
}

static void stream_drain_complete(pa_stream*s, int success, void *userdata) {
  pa_operation *o = NULL;

  if (!success) {
    printf("Failed to drain stream: %s", pa_strerror(pa_context_errno(context)));
    exit(1);
  }

  if (verbose)
    printf("Playback stream drained.");

  pa_stream_disconnect(stream);
  pa_stream_unref(stream);
  stream = NULL;

  if (!(o = pa_context_drain(context, context_drain_complete, NULL)))
    pa_context_disconnect(context);
  else {
    pa_operation_unref(o);
    if (verbose)
      printf("Draining connection to server.");
  }
}


/* Start draining */
static void start_drain(void) {
  printf("Draining\n");
  if (stream) {
    pa_operation *o;

    pa_stream_set_write_callback(stream, NULL, NULL);

    if (!(o = pa_stream_drain(stream, stream_drain_complete, NULL))) {
      //printf("pa_stream_drain(): %s", pa_strerror(pa_context_errno(context)));
      exit(1);
      return;
    }

    pa_operation_unref(o);
  } else
    exit(0);
}


/* New data on STDIN **/
static void stdin_callback(pa_mainloop_api *mainloop_api, pa_io_event *stdio_event, int fd, pa_io_event_flags_t f, void *userdata) {
  size_t l, w = 0;
  ssize_t r;

  printf("In stdin callback\n");
  //pa_assert(a == mainloop_api);
  // pa_assert(e);
  // pa_assert(stdio_event == e);

  if (buffer) {
    mainloop_api->io_enable(stdio_event, PA_IO_EVENT_NULL);
    printf("  Buffer isn't null\n");
    return;
  }

  if (!stream || pa_stream_get_state(stream) != PA_STREAM_READY || !(l = w = pa_stream_writable_size(stream)))
    l = 4096;

  buffer = pa_xmalloc(l);

  if ((r = read(fd, buffer, l)) <= 0) {
    if (r == 0) {
      if (verbose)
	printf("Got EOF.\n");

      start_drain();

    } else {
      printf("read() failed: %s\n", strerror(errno));
      exit(1);
    }

    mainloop_api->io_free(stdio_event);
    stdio_event = NULL;
    return;
  }
  printf("  Read %d\n", r);

  buffer_length = (uint32_t) r;
  buffer_index = 0;

  if (w) {
    printf("  do stream write from stdin callback\n");    
    do_stream_write(w);
  }
}



void stream_state_callback(pa_stream *s, void *userdata) {
  assert(s);

  switch (pa_stream_get_state(s)) {
  case PA_STREAM_CREATING:
    break;
  case PA_STREAM_TERMINATED:
    break;

  case PA_STREAM_READY:

    if (verbose) {
      const pa_buffer_attr *a;
      char cmt[PA_CHANNEL_MAP_SNPRINT_MAX], sst[PA_SAMPLE_SPEC_SNPRINT_MAX];

      printf("Stream successfully created.\n");

      if (!(a = pa_stream_get_buffer_attr(s)))
	printf("pa_stream_get_buffer_attr() failed: %s\n", pa_strerror(pa_context_errno(pa_stream_get_context(s))));
      else {
	printf("Buffer metrics: maxlength=%u, fragsize=%u\n", a->maxlength, a->fragsize);
                    
      }
      /*
	printf("Using sample spec '%s', channel map '%s'.",
	pa_sample_spec_snprint(sst, sizeof(sst), pa_stream_get_sample_spec(s)),
	pa_channel_map_snprint(cmt, sizeof(cmt), pa_stream_get_channel_map(s)));
      */

      printf("Connected to device %s (%u, %ssuspended).\n",
	     pa_stream_get_device_name(s),
	     pa_stream_get_device_index(s),
	     pa_stream_is_suspended(s) ? "" : "not ");
    }

    // TRY HERE???
    
    if (!(stdio_event = mainloop_api->io_new(mainloop_api,
					     fdin, // STDIN_FILENO,
					     PA_IO_EVENT_INPUT,
					     stdin_callback, NULL))) {
      printf("io_new() failed.");
      exit(1);
    }
    
    break;

  case PA_STREAM_FAILED:
  default:
    printf("Stream error: %s", pa_strerror(pa_context_errno(pa_stream_get_context(s))));
    exit(1); //quit(1);
  }
}


/*********** Stream callbacks **************/


static void stream_read_callback(pa_stream *s, size_t length, void *userdata) {
  printf("Raedy to read\n");
}


static void stream_success(pa_stream *s, int succes, void *userdata) {
  printf("Succeded\n");
}


static void stream_suspended_callback(pa_stream *s, void *userdata) {
  assert(s);

  if (verbose) {
    if (pa_stream_is_suspended(s))
      fprintf(stderr, "Stream device suspended.%s \n", CLEAR_LINE);
    else
      fprintf(stderr, "Stream device resumed.%s \n", CLEAR_LINE);
  }
}

static void stream_underflow_callback(pa_stream *s, void *userdata) {
  assert(s);

  if (verbose)
    fprintf(stderr, "Stream underrun.%s \n",  CLEAR_LINE);
}

static void stream_overflow_callback(pa_stream *s, void *userdata) {
  assert(s);

  if (verbose)
    fprintf(stderr, "Stream overrun.%s \n", CLEAR_LINE);
}

static void stream_started_callback(pa_stream *s, void *userdata) {
  assert(s);

  if (verbose)
    fprintf(stderr, "Stream started.%s \n", CLEAR_LINE);
}

static void stream_moved_callback(pa_stream *s, void *userdata) {
  assert(s);

  if (verbose)
    fprintf(stderr, "Stream moved to device %s (%u, %ssuspended).%s \n", pa_stream_get_device_name(s), pa_stream_get_device_index(s), pa_stream_is_suspended(s) ? "" : "not ",  CLEAR_LINE);
}

static void stream_buffer_attr_callback(pa_stream *s, void *userdata) {
  assert(s);

  if (verbose)
    fprintf(stderr, "Stream buffer attributes changed.%s \n",  CLEAR_LINE);
}

static void stream_event_callback(pa_stream *s, const char *name, pa_proplist *pl, void *userdata) {
  char *t;

  assert(s);
  assert(name);
  assert(pl);

  t = pa_proplist_to_string_sep(pl, ", ");
  fprintf(stderr, "Got event '%s', properties '%s'\n", name, t);
  pa_xfree(t);
}


/* This is called whenever new data may be written to the stream */
static void stream_write_callback(pa_stream *s, size_t length, void *userdata) {
  //assert(s);
  //assert(length > 0);

  printf("Stream write callback: Ready to write %d bytes\n", length);
  
  if (raw) {
    // assert(!sndfile);

    if (stdio_event)
      mainloop_api->io_enable(stdio_event, PA_IO_EVENT_INPUT);

    if (!buffer)
      return;
    printf("  do stream write from stream write callback\n");
    do_stream_write(length);

  } 
}

// This callback gets called when our context changes state.  We really only
// care about when it's ready or if it has failed
void state_cb(pa_context *c, void *userdata) {
  pa_context_state_t state;
  int *pa_ready = userdata;

  printf("State changed\n");
  state = pa_context_get_state(c);
  switch  (state) {
    // There are just here for reference
  case PA_CONTEXT_UNCONNECTED:
  case PA_CONTEXT_CONNECTING:
  case PA_CONTEXT_AUTHORIZING:
  case PA_CONTEXT_SETTING_NAME:
  default:
    break;
  case PA_CONTEXT_FAILED:
  case PA_CONTEXT_TERMINATED:
    *pa_ready = 2;
    break;
  case PA_CONTEXT_READY: {
    pa_buffer_attr buffer_attr;

    if (verbose)
      printf("Connection established.%s\n", CLEAR_LINE);

    if (!(stream = pa_stream_new(c, "JanPlayback", &sample_spec, NULL))) {
      printf("pa_stream_new() failed: %s", pa_strerror(pa_context_errno(c)));
      exit(1); // goto fail;
    }

    pa_stream_set_state_callback(stream, stream_state_callback, NULL);
    
    pa_stream_set_write_callback(stream, stream_write_callback, NULL);
    
    pa_stream_set_read_callback(stream, stream_read_callback, NULL);
    
    pa_stream_set_suspended_callback(stream, stream_suspended_callback, NULL);
    pa_stream_set_moved_callback(stream, stream_moved_callback, NULL);
    pa_stream_set_underflow_callback(stream, stream_underflow_callback, NULL);
    pa_stream_set_overflow_callback(stream, stream_overflow_callback, NULL);
    
    pa_stream_set_started_callback(stream, stream_started_callback, NULL);
    
    pa_stream_set_event_callback(stream, stream_event_callback, NULL);
    pa_stream_set_buffer_attr_callback(stream, stream_buffer_attr_callback, NULL);
    
    

    pa_zero(buffer_attr);
    buffer_attr.maxlength = (uint32_t) -1;
    buffer_attr.prebuf = (uint32_t) -1;
    
    buffer_attr.fragsize = buffer_attr.tlength = (uint32_t) -1;
    buffer_attr.minreq = (uint32_t) -1;
    
    pa_cvolume cv;
 
    if (pa_stream_connect_playback(stream, NULL, &buffer_attr, flags,
				   NULL, 
				   NULL) < 0) {
      printf("pa_stream_connect_playback() failed: %s", pa_strerror(pa_context_errno(c)));
      exit(1); //goto fail;
    } else {
      printf("Set playback callback\n");
    }

    pa_stream_trigger(stream, stream_success, NULL);
  }

    break;
  }
}


int main(int argc, char *argv[]) {


  struct stat st;
  off_t size;
  ssize_t nread;

  // We'll need these state variables to keep track of our requests
  int state = 0;
  int pa_ready = 0;

  if (argc != 2) {
    fprintf(stderr, "Usage: %s file\n", argv[0]);
    exit(1);
  }
  // slurp the whole file into buffer
  if ((fdin = open(argv[1],  O_RDONLY)) == -1) {
    perror("open");
    exit(1);
  }

  // Create a mainloop API and connection to the default server
  mainloop = pa_mainloop_new();
  mainloop_api = pa_mainloop_get_api(mainloop);
  context = pa_context_new(mainloop_api, "test");

  // This function connects to the pulse server
  pa_context_connect(context, NULL, 0, NULL);
  printf("Connecting\n");

  // This function defines a callback so the server will tell us it's state.
  // Our callback will wait for the state to be ready.  The callback will
  // modify the variable to 1 so we know when we have a connection and it's
  // ready.
  // If there's an error, the callback will set pa_ready to 2
  pa_context_set_state_callback(context, state_cb, &pa_ready);


  if (pa_mainloop_run(mainloop, &ret) < 0) {
    printf("pa_mainloop_run() failed.");
    exit(1); // goto quit
  }
}
```

###  Controlling latency 


Managing latency is described at [Software/PulseAudio/Documentation/Developer/Clients/LatencyControl](http://www.freedesktop.org/wiki/Software/PulseAudio/Documentation/Developer/Clients/LactencyControl) . In brief:





   > In your code you then have to do the following when calling pa_stream_connect_playback()
resp. pa_stream_connect_record():
> + Pass PA_STREAM_ADJUST_LATENCY in the flags parameter.
Only if this flag is set PA will reconfigure the low-level
device's buffer size and adjust it to the latency you specify.
> + Pass a pa_buffer_attr struct in the buffer_attr parameter.
In the fields of this struct make sure to initialize every
single field to (uint32_t) -1, with the exception of tlength (for playback)
resp. fragsize (for recording). Initialize those to the latency
you want to achieve. Use pa_usec_to_bytes(&ss, ...) to convert
the latency from a time unit to bytes.



The extra code is:




```cpp
// Set properties of the record buffer
    pa_zero(buffer_attr);
    buffer_attr.maxlength = (uint32_t) -1;
    buffer_attr.prebuf = (uint32_t) -1;

    if (latency_msec > 0) {
      buffer_attr.fragsize = buffer_attr.tlength = pa_usec_to_bytes(latency_msec * PA_USEC_PER_MSEC, &sample_spec);
      flags |= PA_STREAM_ADJUST_LATENCY;
    } else if (latency > 0) {
      buffer_attr.fragsize = buffer_attr.tlength = (uint32_t) latency;
      flags |= PA_STREAM_ADJUST_LATENCY;
    } else
      buffer_attr.fragsize = buffer_attr.tlength = (uint32_t) -1;

    if (process_time_msec > 0) {
      buffer_attr.minreq = pa_usec_to_bytes(process_time_msec * PA_USEC_PER_MSEC, &sample_spec);
    } else if (process_time > 0)
      buffer_attr.minreq = (uint32_t) process_time;
    else
      buffer_attr.minreq = (uint32_t) -1;
```


PulseAudio also has mechanisms to estimate the latency of the devices.
It uses information from timing events.
A timer event callback has to be declared, as in




```
pa_context_rttime_new(context, pa_rtclock_now() + TIME_EVENT_USEC, time_event_callback, NULL))
```


The timer event callback is a "single shot" calback.  It installs a stream update timer callback
and sets up another timer callback:

```
void time_event_callback(pa_mainloop_api *m, 
				pa_time_event *e, const struct timeval *t, 
				void *userdata) {
    if (stream && pa_stream_get_state(stream) == PA_STREAM_READY) {
        pa_operation *o;
        if (!(o = pa_stream_update_timing_info(stream, stream_update_timing_callback, NULL)))
	  1; //pa_log(_("pa_stream_update_timing_info() failed: %s"), pa_strerror(pa_context_errno(context)));
        else
            pa_operation_unref(o);
    }

    pa_context_rttime_restart(context, e, pa_rtclock_now() + TIME_EVENT_USEC);
```


The stream update timer callback can then estimate the latency:

```
void stream_update_timing_callback(pa_stream *s, int success, void *userdata) {
    pa_usec_t l, usec;
    int negative = 0;

    // pa_assert(s);

    fprintf(stderr, "Update timing\n");

    if (!success ||
        pa_stream_get_time(s, &usec) < 0 ||
        pa_stream_get_latency(s, &l, &negative) < 0) {
        fprintf(stderr, "Failed to get latency\n");
        return;
    }

    fprintf(stderr, _("Time: %0.3f sec; Latency: %0.0f usec."),
            (float) usec / 1000000,
            (float) l * (negative?-1.0f:1.0f));
    fprintf(stderr, "        \r");
}
```


With latency left to PulseAudio by setting  fragsize and tlength to -1,
I got:

```
Time: 0.850 sec; Latency: 850365 usec.
Time: 0.900 sec; Latency: 900446 usec.
Time: 0.951 sec; Latency: 950548 usec.
Time: 1.001 sec; Latency: 1000940 usec.
Time: 1.051 sec; Latency: 50801 usec.
Time: 1.101 sec; Latency: 100934 usec.
Time: 1.151 sec; Latency: 151007 usec.
Time: 1.201 sec; Latency: 201019 usec.
Time: 1.251 sec; Latency: 251150 usec.
Time: 1.301 sec; Latency: 301160 usec.
Time: 1.351 sec; Latency: 351218 usec.
Time: 1.401 sec; Latency: 401329 usec.
Time: 1.451 sec; Latency: 451400 usec.
Time: 1.501 sec; Latency: 501465 usec.
Time: 1.551 sec; Latency: 551587 usec.
Time: 1.602 sec; Latency: 601594 usec.
```


With them set to 1 msec, I got:

```
Time: 1.599 sec; Latency: 939 usec.
Time: 1.649 sec; Latency: 1105 usec.
Time: 1.699 sec; Latency: -158 usec.
Time: 1.750 sec; Latency: 1020 usec.
Time: 1.800 sec; Latency: 397 usec.
Time: 1.850 sec; Latency: -52 usec.
Time: 1.900 sec; Latency: 1827 usec.
Time: 1.950 sec; Latency: 529 usec.
Time: 2.000 sec; Latency: -90 usec.
Time: 2.050 sec; Latency: 997 usec.
Time: 2.100 sec; Latency: 436 usec.
Time: 2.150 sec; Latency: 866 usec.
Time: 2.200 sec; Latency: 406 usec.
Time: 2.251 sec; Latency: 1461 usec.
Time: 2.301 sec; Latency: 107 usec.
Time: 2.351 sec; Latency: 1257 usec.
```


The program to do all this is [parec-latency.c:](parec-latency.c) 

```cpp
/* parec-latency.c */


#include <stdio.h>
#include <string.h>
#include <pulse/pulseaudio.h>

#define CLEAR_LINE "\n"
#define _(x) x

#define TIME_EVENT_USEC 50000

// From pulsecore/macro.h
#define pa_memzero(x,l) (memset((x), 0, (l)))
#define pa_zero(x) (pa_memzero(&(x), sizeof(x)))

int fdout;
char *fname = "tmp.pcm";

int verbose = 1;
int ret;

pa_context *context;

static pa_sample_spec sample_spec = {
  .format = PA_SAMPLE_S16LE,
  .rate = 44100,
  .channels = 2
};

static pa_stream *stream = NULL;

/* This is my builtin card. Use paman to find yours
   or set it to NULL to get the default device
*/
static char *device = "alsa_input.pci-0000_00_1b.0.analog-stereo";

static pa_stream_flags_t flags = 0;

static size_t latency = 0, process_time = 0;
static int32_t latency_msec = 0, process_time_msec = 0;

void stream_state_callback(pa_stream *s, void *userdata) {
  assert(s);

  switch (pa_stream_get_state(s)) {
  case PA_STREAM_CREATING:
    // The stream has been created, so 
    // let's open a file to record to
    printf("Creating stream\n");
    fdout = creat(fname,  0711);
    break;

  case PA_STREAM_TERMINATED:
    close(fdout);
    break;

  case PA_STREAM_READY:

    // Just for info: no functionality in this branch
    if (verbose) {
      const pa_buffer_attr *a;
      char cmt[PA_CHANNEL_MAP_SNPRINT_MAX], sst[PA_SAMPLE_SPEC_SNPRINT_MAX];

      printf("Stream successfully created.");

      if (!(a = pa_stream_get_buffer_attr(s)))
	printf("pa_stream_get_buffer_attr() failed: %s", pa_strerror(pa_context_errno(pa_stream_get_context(s))));
      else {
	printf("Buffer metrics: maxlength=%u, fragsize=%u", a->maxlength, a->fragsize);
                    
      }

      printf("Connected to device %s (%u, %ssuspended).",
	     pa_stream_get_device_name(s),
	     pa_stream_get_device_index(s),
	     pa_stream_is_suspended(s) ? "" : "not ");
    }

    break;

  case PA_STREAM_FAILED:
  default:
    printf("Stream error: %s", pa_strerror(pa_context_errno(pa_stream_get_context(s))));
    exit(1);
  }
}


/* Show the current latency */
static void stream_update_timing_callback(pa_stream *s, int success, void *userdata) {
    pa_usec_t l, usec;
    int negative = 0;

    // pa_assert(s);

    fprintf(stderr, "Update timing\n");

    if (!success ||
        pa_stream_get_time(s, &usec) < 0 ||
        pa_stream_get_latency(s, &l, &negative) < 0) {
        // pa_log(_("Failed to get latency"));
        //pa_log(_("Failed to get latency: %s"), pa_strerror(pa_context_errno(context)));
        // quit(1);
        return;
    }

    fprintf(stderr, _("Time: %0.3f sec; Latency: %0.0f usec.\n"),
            (float) usec / 1000000,
            (float) l * (negative?-1.0f:1.0f));
    //fprintf(stderr, "        \r");
}

static void time_event_callback(pa_mainloop_api *m, 
				pa_time_event *e, const struct timeval *t, 
				void *userdata) {
    if (stream && pa_stream_get_state(stream) == PA_STREAM_READY) {
        pa_operation *o;
        if (!(o = pa_stream_update_timing_info(stream, stream_update_timing_callback, NULL)))
	  1; //pa_log(_("pa_stream_update_timing_info() failed: %s"), pa_strerror(pa_context_errno(context)));
        else
            pa_operation_unref(o);
    }

    pa_context_rttime_restart(context, e, pa_rtclock_now() + TIME_EVENT_USEC);
}


void get_latency(pa_stream *s) {
  pa_usec_t latency;
  int neg;
  pa_timing_info *timing_info;

  timing_info = pa_stream_get_timing_info(s);
  
  if (pa_stream_get_latency(s, &latency, &neg) != 0) {
    fprintf(stderr, __FILE__": pa_stream_get_latency() failed\n");
    return;
  }
  
  fprintf(stderr, "%0.0f usec    \r", (float)latency);
}


/*********** Stream callbacks **************/

/* This is called whenever new data is available */
static void stream_read_callback(pa_stream *s, size_t length, void *userdata) {

  assert(s);
  assert(length > 0);

  // Copy the data from the server out to a file
  //fprintf(stderr, "Can read %d\n", length);


  while (pa_stream_readable_size(s) > 0) {
    const void *data;
    size_t length;
    
    //get_latency(s);

    // peek actually creates and fills the data vbl
    if (pa_stream_peek(s, &data, &length) < 0) {
      fprintf(stderr, "Read failed\n");
      exit(1);
      return;
    }
    fprintf(stderr, "Writing %d\n", length);
    write(fdout, data, length);

    // swallow the data peeked at before
    pa_stream_drop(s);
  }
}


// This callback gets called when our context changes state.  We really only
// care about when it's ready or if it has failed
void state_cb(pa_context *c, void *userdata) {
  pa_context_state_t state;
  int *pa_ready = userdata;

  printf("State changed\n");
  state = pa_context_get_state(c);
  switch  (state) {
    // There are just here for reference
  case PA_CONTEXT_UNCONNECTED:
  case PA_CONTEXT_CONNECTING:
  case PA_CONTEXT_AUTHORIZING:
  case PA_CONTEXT_SETTING_NAME:
  default:
    break;
  case PA_CONTEXT_FAILED:
  case PA_CONTEXT_TERMINATED:
    *pa_ready = 2;
    break;
  case PA_CONTEXT_READY: {
    pa_buffer_attr buffer_attr;

    if (verbose)
      printf("Connection established.%s\n", CLEAR_LINE);

    if (!(stream = pa_stream_new(c, "JanCapture", &sample_spec, NULL))) {
      printf("pa_stream_new() failed: %s", pa_strerror(pa_context_errno(c)));
      exit(1);
    }

    // Watch for changes in the stream state to create the output file
    pa_stream_set_state_callback(stream, stream_state_callback, NULL);
    
    // Watch for changes in the stream's read state to write to the output file
    pa_stream_set_read_callback(stream, stream_read_callback, NULL);

    // timing info
    pa_stream_update_timing_info(stream, stream_update_timing_callback, NULL);

    // Set properties of the record buffer
    pa_zero(buffer_attr);
    buffer_attr.maxlength = (uint32_t) -1;
    buffer_attr.prebuf = (uint32_t) -1;

    if (latency_msec > 0) {
      buffer_attr.fragsize = buffer_attr.tlength = pa_usec_to_bytes(latency_msec * PA_USEC_PER_MSEC, &sample_spec);
      flags |= PA_STREAM_ADJUST_LATENCY;
    } else if (latency > 0) {
      buffer_attr.fragsize = buffer_attr.tlength = (uint32_t) latency;
      flags |= PA_STREAM_ADJUST_LATENCY;
    } else
      buffer_attr.fragsize = buffer_attr.tlength = (uint32_t) -1;

    if (process_time_msec > 0) {
      buffer_attr.minreq = pa_usec_to_bytes(process_time_msec * PA_USEC_PER_MSEC, &sample_spec);
    } else if (process_time > 0)
      buffer_attr.minreq = (uint32_t) process_time;
    else
      buffer_attr.minreq = (uint32_t) -1;

    flags |= PA_STREAM_INTERPOLATE_TIMING;

    get_latency(stream);

    // and start recording
    if (pa_stream_connect_record(stream, device, &buffer_attr, flags) < 0) {
      printf("pa_stream_connect_record() failed: %s", pa_strerror(pa_context_errno(c)));
      exit(1);
    }
  }

    break;
  }
}

int main(int argc, char *argv[]) {

  // Define our pulse audio loop and connection variables
  pa_mainloop *pa_ml;
  pa_mainloop_api *pa_mlapi;
  pa_operation *pa_op;
  pa_time_event *time_event;

  // Create a mainloop API and connection to the default server
  pa_ml = pa_mainloop_new();
  pa_mlapi = pa_mainloop_get_api(pa_ml);
  context = pa_context_new(pa_mlapi, "test");

  // This function connects to the pulse server
  pa_context_connect(context, NULL, 0, NULL);

  // This function defines a callback so the server will tell us its state.
  pa_context_set_state_callback(context, state_cb, NULL);

  if (!(time_event = pa_context_rttime_new(context, pa_rtclock_now() + TIME_EVENT_USEC, time_event_callback, NULL))) {
    //pa_log(_("pa_context_rttime_new() failed."));
    //goto quit;
  }
  

  if (pa_mainloop_run(pa_ml, &ret) < 0) {
    printf("pa_mainloop_run() failed.");
    exit(1);
  }
}
```

###  Play microphone to speaker 


Combining what we have so far, we get [pa-mic-2-speaker.c:](pa-mic-2-speaker.c) 

```cpp
/*
 * Copy from microphone to speaker
 * pa-mic-2-speaker.c
 */


#include <stdio.h>
#include <string.h>
#include <pulse/pulseaudio.h>

#define CLEAR_LINE "\n"
#define BUFF_LEN 4096

// From pulsecore/macro.h
#define pa_memzero(x,l) (memset((x), 0, (l)))
#define pa_zero(x) (pa_memzero(&(x), sizeof(x)))

static void *buffer = NULL;
static size_t buffer_length = 0, buffer_index = 0;


int verbose = 1;
int ret;

static pa_sample_spec sample_spec = {
  .format = PA_SAMPLE_S16LE,
  .rate = 44100,
  .channels = 2
};

static pa_stream *istream = NULL,
                 *ostream = NULL;

// This is my builtin card. Use paman to find yours
//static char *device = "alsa_input.pci-0000_00_1b.0.analog-stereo";
static char *idevice = NULL;
static char *odevice = NULL;

static pa_stream_flags_t flags = 0;

static size_t latency = 0, process_time = 0;
static int32_t latency_msec = 1, process_time_msec = 0;

void stream_state_callback(pa_stream *s, void *userdata) {
  assert(s);

  switch (pa_stream_get_state(s)) {
  case PA_STREAM_CREATING:
    // The stream has been created, so 
    // let's open a file to record to
    printf("Creating stream\n");
    // fdout = creat(fname,  0711);
    buffer = pa_xmalloc(BUFF_LEN);
    buffer_length = BUFF_LEN;
    buffer_index = 0;
    break;

  case PA_STREAM_TERMINATED:
    // close(fdout);
    break;

  case PA_STREAM_READY:

    // Just for info: no functionality in this branch
    if (verbose) {
      const pa_buffer_attr *a;
      char cmt[PA_CHANNEL_MAP_SNPRINT_MAX], sst[PA_SAMPLE_SPEC_SNPRINT_MAX];

      printf("Stream successfully created.");

      if (!(a = pa_stream_get_buffer_attr(s)))
	printf("pa_stream_get_buffer_attr() failed: %s", pa_strerror(pa_context_errno(pa_stream_get_context(s))));
      else {
	printf("Buffer metrics: maxlength=%u, fragsize=%u", a->maxlength, a->fragsize);
                    
      }

      printf("Connected to device %s (%u, %ssuspended).",
	     pa_stream_get_device_name(s),
	     pa_stream_get_device_index(s),
	     pa_stream_is_suspended(s) ? "" : "not ");
    }

    break;

  case PA_STREAM_FAILED:
  default:
    printf("Stream error: %s", pa_strerror(pa_context_errno(pa_stream_get_context(s))));
    exit(1);
  }
}


/*********** Stream callbacks **************/

/* This is called whenever new data is available */
static void stream_read_callback(pa_stream *s, size_t length, void *userdata) {

  assert(s);
  assert(length > 0);

  // Copy the data from the server out to a file
  fprintf(stderr, "Can read %d\n", length);

  while (pa_stream_readable_size(s) > 0) {
    const void *data;
    size_t length, lout;
    
    // peek actually creates and fills the data vbl
    if (pa_stream_peek(s, &data, &length) < 0) {
      fprintf(stderr, "Read failed\n");
      exit(1);
      return;
    }

    fprintf(stderr, "read %d\n", length);
    lout =  pa_stream_writable_size(ostream);
    fprintf(stderr, "Writable: %d\n", lout);
    if (lout == 0) {
      fprintf(stderr, "can't write, zero writable\n");
      return;
    }
    if (lout < length) {
      fprintf(stderr, "Truncating read\n");
      length = lout;
  }
    
  if (pa_stream_write(ostream, (uint8_t*) data, length, NULL, 0, PA_SEEK_RELATIVE) < 0) {
    fprintf(stderr, "pa_stream_write() failed\n");
    exit(1);
    return;
  }
    

    // STICK OUR CODE HERE TO WRITE OUT
    //fprintf(stderr, "Writing %d\n", length);
    //write(fdout, data, length);

    // swallow the data peeked at before
    pa_stream_drop(s);
  }
}



/* This is called whenever new data may be written to the stream */
// We don't actually write anything this time
static void stream_write_callback(pa_stream *s, size_t length, void *userdata) {
  //assert(s);
  //assert(length > 0);

  printf("Stream write callback: Ready to write %d bytes\n", length);
 }


// This callback gets called when our context changes state.  We really only
// care about when it's ready or if it has failed
void state_cb(pa_context *c, void *userdata) {
  pa_context_state_t state;
  int *pa_ready = userdata;

  printf("State changed\n");
  state = pa_context_get_state(c);
  switch  (state) {
    // There are just here for reference
  case PA_CONTEXT_UNCONNECTED:
  case PA_CONTEXT_CONNECTING:
  case PA_CONTEXT_AUTHORIZING:
  case PA_CONTEXT_SETTING_NAME:
  default:
    break;
  case PA_CONTEXT_FAILED:
  case PA_CONTEXT_TERMINATED:
    *pa_ready = 2;
    break;
  case PA_CONTEXT_READY: {
    pa_buffer_attr buffer_attr;

    if (verbose)
      printf("Connection established.%s\n", CLEAR_LINE);

    if (!(istream = pa_stream_new(c, "JanCapture", &sample_spec, NULL))) {
      printf("pa_stream_new() failed: %s", pa_strerror(pa_context_errno(c)));
      exit(1);
    }

    if (!(ostream = pa_stream_new(c, "JanPlayback", &sample_spec, NULL))) {
      printf("pa_stream_new() failed: %s", pa_strerror(pa_context_errno(c)));
      exit(1);
    }

    // Watch for changes in the stream state to create the output file
    pa_stream_set_state_callback(istream, stream_state_callback, NULL);
    
    // Watch for changes in the stream's read state to write to the output file
    pa_stream_set_read_callback(istream, stream_read_callback, NULL);

    pa_stream_set_write_callback(ostream, stream_write_callback, NULL);
    


    // Set properties of the record buffer
    pa_zero(buffer_attr);
    buffer_attr.maxlength = (uint32_t) -1;
    buffer_attr.prebuf = (uint32_t) -1;

    if (latency_msec > 0) {
      buffer_attr.fragsize = buffer_attr.tlength = pa_usec_to_bytes(latency_msec * PA_USEC_PER_MSEC, &sample_spec);
      flags |= PA_STREAM_ADJUST_LATENCY;
    } else if (latency > 0) {
      buffer_attr.fragsize = buffer_attr.tlength = (uint32_t) latency;
      flags |= PA_STREAM_ADJUST_LATENCY;
    } else
      buffer_attr.fragsize = buffer_attr.tlength = (uint32_t) -1;

    if (process_time_msec > 0) {
      buffer_attr.minreq = pa_usec_to_bytes(process_time_msec * PA_USEC_PER_MSEC, &sample_spec);
    } else if (process_time > 0)
      buffer_attr.minreq = (uint32_t) process_time;
    else
      buffer_attr.minreq = (uint32_t) -1;

    // and start recording
    if (pa_stream_connect_record(istream, idevice, &buffer_attr, flags) < 0) {
      printf("pa_stream_connect_record() failed: %s", pa_strerror(pa_context_errno(c)));
      exit(1);
    }

    
    if (pa_stream_connect_playback(ostream, odevice, &buffer_attr, flags,
				   NULL, 
				   NULL) < 0) {
      printf("pa_stream_connect_playback() failed: %s", pa_strerror(pa_context_errno(c)));
      exit(1); //goto fail;
    } else {
      printf("Set playback callback\n");
    }
    
  }

    break;
  }
}

int main(int argc, char *argv[]) {

  // Define our pulse audio loop and connection variables
  pa_mainloop *pa_ml;
  pa_mainloop_api *pa_mlapi;
  pa_operation *pa_op;
  pa_context *pa_ctx;

  // Create a mainloop API and connection to the default server
  pa_ml = pa_mainloop_new();
  pa_mlapi = pa_mainloop_get_api(pa_ml);
  pa_ctx = pa_context_new(pa_mlapi, "test");

  // This function connects to the pulse server
  pa_context_connect(pa_ctx, NULL, 0, NULL);

  // This function defines a callback so the server will tell us its state.
  pa_context_set_state_callback(pa_ctx, state_cb, NULL);

  if (pa_mainloop_run(pa_ml, &ret) < 0) {
    printf("pa_mainloop_run() failed.");
    exit(1);
  }
}
```


When the latency is set to 1 msec for everything, the actual latency is
about 16-28 msec. I couldn't detect it.

###  Setting the volume on devices 


Each device can have its input or output volume controlled by
PulseAudio. The principal calls for sinks are `pa_context_set_sink_volume_by_name`and ` pa_context_set_sink_volume_by_index`with similar
calls for sources.


These calls make use of a structure `pa_cvolume`.
This stucture can be manipulated using calls such as

+  ` pa_cvolume_init`
+  `pa_cvolume_set`
+  `pa_cvolume_mute`

In the following program we set the volume on a particular device
by reading integer values from stdin and using these to set the
value. Such a loop should probably best take place in a separate thread
to the PulseAudio framework. Rather than introducing application
threading here, we make use of an alternative set of PulseAudio
calls which set up a separate thread for the PulseAudio main loop.
These calls are

+  ` pa_threaded_mainloop`instead of ` pa_mainloop`
+  ` pa_threaded_mainloop_get_api`instead of ` pa_mainloop_get_api`
+  `pa_threaded_mainloop_start`instead of `pa_mainloop_start`

The threaded calls allow us to start PulseAudio in its own thread,
and leave the current thread for reading volume values. This gives
the relatively simple program [pavolume.c:](pavolume.c) 

```cpp
/**
 * pavolume.c 
 * Jan Newmarch
 */

#include <stdio.h>
#include <string.h>
#include <pulse/pulseaudio.h>

#define _(x) x

char *device = "alsa_output.pci-0000_00_1b.0.analog-stereo";

int ret;

pa_context *context;

void show_error(char *s) {
    fprintf(stderr, "%s\n", s);
}


void volume_cb(pa_context *c, int success, void *userdata) {
    if (success) 
	printf("Volume set\n");
    else
	printf("Volume not set\n");
}
		       
void context_state_cb(pa_context *c, void *userdata) {

    switch (pa_context_get_state(c)) {
    case PA_CONTEXT_UNCONNECTED:
    case PA_CONTEXT_CONNECTING:
    case PA_CONTEXT_AUTHORIZING:
    case PA_CONTEXT_SETTING_NAME:
	break;

    case PA_CONTEXT_READY: {
	pa_operation *o;

	break;
    }

    case PA_CONTEXT_FAILED:
    case PA_CONTEXT_TERMINATED:
    default:
	return;
    }
}

int main(int argc, char *argv[]) {
    long volume = 0;
    char buf[128];
    struct pa_cvolume v;

    // Define our pulse audio loop and connection variables
    pa_threaded_mainloop *pa_ml;
    pa_mainloop_api *pa_mlapi;

    // Create a mainloop API and connection to the default server
    //pa_ml = pa_mainloop_new();
    pa_ml = pa_threaded_mainloop_new();
    pa_mlapi = pa_threaded_mainloop_get_api(pa_ml);
    context = pa_context_new(pa_mlapi, "Voulme control");

    // This function connects to the pulse server
    pa_context_connect(context, NULL, 0, NULL);

    // This function defines a callback so the server will tell us its state.
    pa_context_set_state_callback(context, context_state_cb, NULL);

    pa_threaded_mainloop_start(pa_ml);
    printf("Enter volume for device %s\n");
    
    pa_cvolume_init(&v);
    while (1) {
        puts("Enter an integer 0-65536\n");
        fgets(buf, 128, stdin);
        volume = atoi(buf);
	pa_cvolume_set(&v, 2, volume);
	pa_context_set_sink_volume_by_name(context,
					   device,
					   &v,
					   volume_cb,
					   NULL
					   );
    }
}
```

###  Listing clients 


PulseAudio is a server that talks to devices at the bottom layer and to clients
at the top layer. The clients are producers and consumers of audio.
One of the roles of PulseAudio is to mix signals from different source clients
to shared output devices. In order to do this, PulseAudio keeps track
of registrations by clients, and can make these available to _other_ clients by suitbale callbacks.


The program palist_clients.c is very similar to the program
palist_devices.c. The principal difference is that when the
context changes state to `PA_CONTEXT_READY`the application subscribes to `PA_SUBSCRIPTION_MASK_CLIENT`instead of `(PA_SUBSCRIPTION_MASK_SINK|PA_SUBSCRIPTION_MASK_SOURCE)`and the subscription callback asks for `pa_context_get_client_info`instead of `pa_context_get_source_info`.


The program [palist_clients.c](palist_clients.c) is

```cpp
/**
 * palist_clients.c 
 * Jan Newmarch
 */

#include <stdio.h>
#include <string.h>
#include <pulse/pulseaudio.h>

#define CLEAR_LINE "\n"
#define _(x) x

// From pulsecore/macro.h
//#define pa_memzero(x,l) (memset((x), 0, (l)))
//#define pa_zero(x) (pa_memzero(&(x), sizeof(x)))

int ret;

pa_context *context;

void show_error(char *s) {
    /* stub */
}

void print_properties(pa_proplist *props) {
    void *state = NULL;

    printf("  Properties are: \n");
    while (1) {
	char *key;
	if ((key = pa_proplist_iterate(props, &state)) == NULL) {
	    return;
	}
	char *value = pa_proplist_gets(props, key);
	printf("   key %s, value %s\n", key, value);
    }
}

void add_client_cb(pa_context *context, const pa_client_info *i, int eol, void *userdata) {

    if (eol < 0) {
        if (pa_context_errno(context) == PA_ERR_NOENTITY)
            return;

        show_error(_("Client callback failure"));
        return;
    }

    if (eol > 0) {
        return;
    }

    printf("Found a new client index %d name %s eol %d\n", i->index, i->name, eol);
    print_properties(i->proplist);
}

void remove_client_cb(pa_context *context, const pa_client_info *i, int eol, void *userdata) {

    if (eol < 0) {
        if (pa_context_errno(context) == PA_ERR_NOENTITY)
            return;

        show_error(_("Client callback failure"));
        return;
    }

    if (eol > 0) {
        return;
    }

    printf("Removing a client index %d name %s\n", i->index, i->name);
    print_properties(i->proplist);
}

void subscribe_cb(pa_context *c, pa_subscription_event_type_t t, uint32_t index, void *userdata) {

    switch (t & PA_SUBSCRIPTION_EVENT_FACILITY_MASK) {

    case PA_SUBSCRIPTION_EVENT_CLIENT:
	if ((t & PA_SUBSCRIPTION_EVENT_TYPE_MASK) == PA_SUBSCRIPTION_EVENT_REMOVE) {
	    printf("Remove event at index %d\n", index);
	    pa_operation *o;
	    if (!(o = pa_context_get_client_info(c, index, remove_client_cb, NULL))) {
		show_error(_("pa_context_get_client_info() failed"));
		return;
	    }
	    pa_operation_unref(o);

	} else {
	    pa_operation *o;
	    if (!(o = pa_context_get_client_info(c, index, add_client_cb, NULL))) {
		show_error(_("pa_context_get_client_info() failed"));
		return;
	    }
	    pa_operation_unref(o);
	}
	break;
    }
}

void context_state_cb(pa_context *c, void *userdata) {

    switch (pa_context_get_state(c)) {
    case PA_CONTEXT_UNCONNECTED:
    case PA_CONTEXT_CONNECTING:
    case PA_CONTEXT_AUTHORIZING:
    case PA_CONTEXT_SETTING_NAME:
	break;

    case PA_CONTEXT_READY: {
	pa_operation *o;

	pa_context_set_subscribe_callback(c, subscribe_cb, NULL);

	if (!(o = pa_context_subscribe(c, (pa_subscription_mask_t)
				       (PA_SUBSCRIPTION_MASK_CLIENT), NULL, NULL))) {
	    show_error(_("pa_context_subscribe() failed"));
	    return;
	}
	pa_operation_unref(o);

	if (!(o = pa_context_get_client_info_list(context,
						  add_client_cb,
						  NULL
	) )) {
	    show_error(_("pa_context_subscribe() failed"));
	    return;
	}
	pa_operation_unref(o);
	

	break;
    }

    case PA_CONTEXT_FAILED:
	return;

    case PA_CONTEXT_TERMINATED:
    default:
	return;
    }
}




void stream_state_callback(pa_stream *s, void *userdata) {
    assert(s);

    switch (pa_stream_get_state(s)) {
    case PA_STREAM_CREATING:
	break;

    case PA_STREAM_TERMINATED:
	break;

    case PA_STREAM_READY:

	break;

    case PA_STREAM_FAILED:
    default:
	printf("Stream error: %s", pa_strerror(pa_context_errno(pa_stream_get_context(s))));
	exit(1);
    }
}

int main(int argc, char *argv[]) {

    // Define our pulse audio loop and connection variables
    pa_mainloop *pa_ml;
    pa_mainloop_api *pa_mlapi;
    pa_operation *pa_op;
    pa_time_event *time_event;

    // Create a mainloop API and connection to the default server
    pa_ml = pa_mainloop_new();
    pa_mlapi = pa_mainloop_get_api(pa_ml);
    context = pa_context_new(pa_mlapi, "test");

    // This function connects to the pulse server
    pa_context_connect(context, NULL, 0, NULL);

    // This function defines a callback so the server will tell us its state.
    //pa_context_set_state_callback(context, state_cb, NULL);
    pa_context_set_state_callback(context, context_state_cb, NULL);

    
    if (pa_mainloop_run(pa_ml, &ret) < 0) {
	printf("pa_mainloop_run() failed.");
	exit(1);
    }
}
```


The output on my system is (elided)

```
Found a new client index 0 name ConsoleKit Session /org/freedesktop/ConsoleKit/Session2 eol 0
  Properties are: 
   key application.name, value ConsoleKit Session /org/freedesktop/ConsoleKit/Session2
   key console-kit.session, value /org/freedesktop/ConsoleKit/Session2
Found a new client index 4 name XSMP Session on gnome-session as 1057eba7239ba1ec3d136359809598590100000018790044 eol 0
  Properties are: 
   key application.name, value XSMP Session on gnome-session as 1057eba7239ba1ec3d136359809598590100000018790044
   key xsmp.vendor, value gnome-session
   key xsmp.client.id, value 1057eba7239ba1ec3d136359809598590100000018790044
Found a new client index 5 name GNOME Volume Control Media Keys eol 0
  Properties are: 
   ...
Found a new client index 7 name GNOME Volume Control Applet eol 0
  Properties are: 
   ...
Found a new client index 53 name Metacity eol 0
  Properties are: 
  ...
Found a new client index 54 name Firefox eol 0
  Properties are: 
    ...
Found a new client index 248 name PulseAudio Volume Control eol 0
  Properties are: 
    ...
Found a new client index 341 name test eol 0
  Properties are: 
    ...
```

###  Listing client sources and sinks 


Clients can act as sources: programs such as `mplayer`and `vlc`do just that, sending streams to PulseAudio.
Other clients can act as sinks. The clients themselves are monitored
by the previous program. To monitor their _activity_ you set the mask on `pa_subscribe_callback`to `(PA_SUBSCRIPTION_MASK_CLIENT | PA_SUBSCRIPTION_MASK_SINK_INPUT | 					PA_SUBSCRIPTION_MASK_SOURCE_OUTPUT)`.
Within the subscription
callback you make calls to `pa_context_get_sink_input_info`within the ` PA_SUBSCRIPTION_EVENT_SINK_INPUT`branch
and similarly for the source output.


The sink input callback is passed the structure `pa_sink_input_info`. This contains the familiar `name`and `index`fields but also
has an integer field `client`. This links the sink input
back to the index of the client responsible for the sink.
In the following program we list all the clients as well, so that
these links can followed visually. Programatically, PulseAudio makes you
keep much information (such as what clients have what indices)
yourself: this is ignored here.


The program to list clients and monitor changes in their input and
output streams is [pamonitor_clients.c:](pamonitor_clients.c) 

```cpp
/**
 * pamonitor_clients.c 
 * Jan Newmarch
 */



#include <stdio.h>
#include <string.h>
#include <pulse/pulseaudio.h>

#define CLEAR_LINE "\n"
#define _(x) x

// From pulsecore/macro.h
#define pa_memzero(x,l) (memset((x), 0, (l)))
#define pa_zero(x) (pa_memzero(&(x), sizeof(x)))

int ret;

pa_context *context;

void show_error(char *s) {
    /* stub */
}

void add_client_cb(pa_context *context, const pa_client_info *i, int eol, void *userdata) {

    if (eol < 0) {
        if (pa_context_errno(context) == PA_ERR_NOENTITY)
            return;

        show_error(_("Client callback failure"));
        return;
    }

    if (eol > 0) {
        return;
    }

    printf("Found a new client index %d name %s eol %d\n", i->index, i->name, eol);
}

void remove_client_cb(pa_context *context, const pa_client_info *i, int eol, void *userdata) {

    if (eol < 0) {
        if (pa_context_errno(context) == PA_ERR_NOENTITY)
            return;

        show_error(_("Client callback failure"));
        return;
    }

    if (eol > 0) {
        return;
    }

    printf("Removing a client index %d name %s\n", i->index, i->name);
}

void sink_input_cb(pa_context *c, const pa_sink_input_info *i, int eol, void *userdata) {
    if (eol < 0) {
        if (pa_context_errno(context) == PA_ERR_NOENTITY)
            return;

        show_error(_("Sink input callback failure"));
        return;
    }

    if (eol > 0) {
        return;
    }
    printf("Sink input found index %d name %s for client %d\n", i->index, i->name, i->client);
}

void source_output_cb(pa_context *c, const pa_source_output_info *i, int eol, void *userdata) {
    if (eol < 0) {
        if (pa_context_errno(context) == PA_ERR_NOENTITY)
            return;

        show_error(_("Source output callback failure"));
        return;
    }

    if (eol > 0) {
        return;
    }
    printf("Source output found index %d name %s for client %d\n", i->index, i->name, i->client);
}


void subscribe_cb(pa_context *c, pa_subscription_event_type_t t, uint32_t index, void *userdata) {

    switch (t & PA_SUBSCRIPTION_EVENT_FACILITY_MASK) {

    case PA_SUBSCRIPTION_EVENT_CLIENT:
	if ((t & PA_SUBSCRIPTION_EVENT_TYPE_MASK) == PA_SUBSCRIPTION_EVENT_REMOVE) {
	    printf("Remove event at index %d\n", index);
	    pa_operation *o;
	    if (!(o = pa_context_get_client_info(c, index, remove_client_cb, NULL))) {
		show_error(_("pa_context_get_client_info() failed"));
		return;
	    }
	    pa_operation_unref(o);

	} else {
	    pa_operation *o;
	    if (!(o = pa_context_get_client_info(c, index, add_client_cb, NULL))) {
		show_error(_("pa_context_get_client_info() failed"));
		return;
	    }
	    pa_operation_unref(o);
	}
	break;

    case PA_SUBSCRIPTION_EVENT_SINK_INPUT:
	if ((t & PA_SUBSCRIPTION_EVENT_TYPE_MASK) == PA_SUBSCRIPTION_EVENT_REMOVE)
	    printf("Removing sink input %d\n", index);
	else {
	    pa_operation *o;
	    if (!(o = pa_context_get_sink_input_info(context, index, sink_input_cb, NULL))) {
		show_error(_("pa_context_get_sink_input_info() failed"));
		return;
	    }
	    pa_operation_unref(o);
	}
	break;

    case PA_SUBSCRIPTION_EVENT_SOURCE_OUTPUT:
	if ((t & PA_SUBSCRIPTION_EVENT_TYPE_MASK) == PA_SUBSCRIPTION_EVENT_REMOVE)
	    printf("Removing source output %d\n", index);
	else {
	    pa_operation *o;
	    if (!(o = pa_context_get_source_output_info(context, index, source_output_cb, NULL))) {
		show_error(_("pa_context_get_sink_input_info() failed"));
		return;
	    }
	    pa_operation_unref(o);
	}
	break;
    }
}

void context_state_cb(pa_context *c, void *userdata) {

    switch (pa_context_get_state(c)) {
    case PA_CONTEXT_UNCONNECTED:
    case PA_CONTEXT_CONNECTING:
    case PA_CONTEXT_AUTHORIZING:
    case PA_CONTEXT_SETTING_NAME:
	break;

    case PA_CONTEXT_READY: {
	pa_operation *o;

	pa_context_set_subscribe_callback(c, subscribe_cb, NULL);

	if (!(o = pa_context_subscribe(c, (pa_subscription_mask_t)
				       (PA_SUBSCRIPTION_MASK_CLIENT | 
					PA_SUBSCRIPTION_MASK_SINK_INPUT | 
					PA_SUBSCRIPTION_MASK_SOURCE_OUTPUT), NULL, NULL))) {
	    show_error(_("pa_context_subscribe() failed"));
	    return;
	}
	pa_operation_unref(o);

	if (!(o = pa_context_get_client_info_list(context,
						  add_client_cb,
						  NULL
	) )) {
	    show_error(_("pa_context_subscribe() failed"));
	    return;
	}
	pa_operation_unref(o);
	
	break;
    }

    case PA_CONTEXT_FAILED:
	return;

    case PA_CONTEXT_TERMINATED:
    default:
	// Gtk::Main::quit();
	return;
    }
}




void stream_state_callback(pa_stream *s, void *userdata) {
    assert(s);

    switch (pa_stream_get_state(s)) {
    case PA_STREAM_CREATING:
	break;

    case PA_STREAM_TERMINATED:
	break;

    case PA_STREAM_READY:
	break;

    case PA_STREAM_FAILED:
    default:
	printf("Stream error: %s", pa_strerror(pa_context_errno(pa_stream_get_context(s))));
	exit(1);
    }
}

int main(int argc, char *argv[]) {

    // Define our pulse audio loop and connection variables
    pa_mainloop *pa_ml;
    pa_mainloop_api *pa_mlapi;
    pa_operation *pa_op;
    pa_time_event *time_event;

    // Create a mainloop API and connection to the default server
    pa_ml = pa_mainloop_new();
    pa_mlapi = pa_mainloop_get_api(pa_ml);
    context = pa_context_new(pa_mlapi, "test");

    // This function connects to the pulse server
    pa_context_connect(context, NULL, 0, NULL);

    // This function defines a callback so the server will tell us its state.
    //pa_context_set_state_callback(context, state_cb, NULL);
    pa_context_set_state_callback(context, context_state_cb, NULL);

    
    if (pa_mainloop_run(pa_ml, &ret) < 0) {
	printf("pa_mainloop_run() failed.");
	exit(1);
    }
}
```


The output on my system is

```
Found a new client index 0 name ConsoleKit Session /org/freedesktop/ConsoleKit/Session2 eol 0
Found a new client index 4 name XSMP Session on gnome-session as 1057eba7239ba1ec3d136359809598590100000018790044 eol 0
Found a new client index 5 name GNOME Volume Control Media Keys eol 0
Found a new client index 7 name GNOME Volume Control Applet eol 0
Found a new client index 53 name Metacity eol 0
Found a new client index 54 name Firefox eol 0
Found a new client index 248 name PulseAudio Volume Control eol 0
Found a new client index 342 name test eol 0
```

###  Controlling the volume of a sink client 


One of the significant features of PulseAudio is that not only can it
mix streams to a device, but it can also control the volume of each stream.
This is in addition to the volume control of each device.
In `pavucontrol`you can see this under the Playback
tab, where the volume of playback clients can be adjusted.


Programatically this is done by calling `pa_context_set_sink_input_volume`with parameters
the index of the sink input and the volume.
In the following program we follow what we did in the
pavolume_client.c program where we set PulseAudio to run
in a separate thread and input values for the volume in the
main thread. A slight difference is that we have to wait for a client
to start up a sink input, which we do by sleeping until the
sink input callback assigns a non-zero value to the `sink_index`variable. Crude, yes. In a program such
as `pavucontrol`the GUI runs in separate threads
anyway and we do not need to resort to such simple tricks.


The program is [pavolume_sink.c](pavolume_sink.c) .
If you play a file using
e.g. `mplayer`then its volume can be adjusted
by this program.

```cpp
/**
 * pavolume_sink.c 
 * Jan Newmarch
 */

#include <stdio.h>
#include <string.h>
#include <pulse/pulseaudio.h>

#define CLEAR_LINE "\n"
#define _(x) x

int ret;

// sink we will control volume on when it is non-zero
int sink_index = 0;
int sink_num_channels;

pa_context *context;

void show_error(char *s) {
    /* stub */
}

void sink_input_cb(pa_context *c, const pa_sink_input_info *i, int eol, void *userdata) {
    if (eol < 0) {
        if (pa_context_errno(context) == PA_ERR_NOENTITY)
            return;

        show_error(_("Sink input callback failure"));
        return;
    }

    if (eol > 0) {
        return;
    }
    printf("Sink input found index %d name %s for client %d\n", i->index, i->name, i->client);
    sink_num_channels = i->channel_map.channels;
    sink_index = i->index;
}

void volume_cb(pa_context *c, int success, void *userdata) {
    if (success) 
	printf("Volume set\n");
    else
	printf("Volume not set\n");
}

void subscribe_cb(pa_context *c, pa_subscription_event_type_t t, uint32_t index, void *userdata) {

    switch (t & PA_SUBSCRIPTION_EVENT_FACILITY_MASK) {

    case PA_SUBSCRIPTION_EVENT_SINK_INPUT:
	if ((t & PA_SUBSCRIPTION_EVENT_TYPE_MASK) == PA_SUBSCRIPTION_EVENT_REMOVE)
	    printf("Removing sink input %d\n", index);
	else {
	    pa_operation *o;
	    if (!(o = pa_context_get_sink_input_info(context, index, sink_input_cb, NULL))) {
		show_error(_("pa_context_get_sink_input_info() failed"));
		return;
	    }
	    pa_operation_unref(o);
	}
	break;
    }
}

void context_state_cb(pa_context *c, void *userdata) {

    switch (pa_context_get_state(c)) {
    case PA_CONTEXT_UNCONNECTED:
    case PA_CONTEXT_CONNECTING:
    case PA_CONTEXT_AUTHORIZING:
    case PA_CONTEXT_SETTING_NAME:
	break;

    case PA_CONTEXT_READY: {
	pa_operation *o;

	pa_context_set_subscribe_callback(c, subscribe_cb, NULL);

	if (!(o = pa_context_subscribe(c, (pa_subscription_mask_t)
				       (PA_SUBSCRIPTION_MASK_SINK_INPUT), NULL, NULL))) {
	    show_error(_("pa_context_subscribe() failed"));
	    return;
	}
	break;
    }

    case PA_CONTEXT_FAILED:
	return;

    case PA_CONTEXT_TERMINATED:
    default:
	// Gtk::Main::quit();
	return;
    }
}

void stream_state_callback(pa_stream *s, void *userdata) {
    assert(s);

    switch (pa_stream_get_state(s)) {
    case PA_STREAM_CREATING:
	break;

    case PA_STREAM_TERMINATED:
	break;

    case PA_STREAM_READY:
	break;

    case PA_STREAM_FAILED:
    default:
	printf("Stream error: %s", pa_strerror(pa_context_errno(pa_stream_get_context(s))));
	exit(1);
    }
}

int main(int argc, char *argv[]) {

    // Define our pulse audio loop and connection variables
    pa_threaded_mainloop *pa_ml;
    pa_mainloop_api *pa_mlapi;
    pa_operation *pa_op;
    pa_time_event *time_event;
    long volume = 0;
    char buf[128];
    struct pa_cvolume v;

    // Create a mainloop API and connection to the default server
    pa_ml = pa_threaded_mainloop_new();
    pa_mlapi = pa_threaded_mainloop_get_api(pa_ml);
    context = pa_context_new(pa_mlapi, "test");

    // This function connects to the pulse server
    pa_context_connect(context, NULL, 0, NULL);

    // This function defines a callback so the server will tell us its state.
    //pa_context_set_state_callback(context, state_cb, NULL);
    pa_context_set_state_callback(context, context_state_cb, NULL);

    
    pa_threaded_mainloop_start(pa_ml);

    /* wait till there is a sink */
    while (sink_index == 0) {
	sleep(1);
    }

    printf("Enter volume for sink %d\n", sink_index);
    pa_cvolume_init(&v);
    while (1) {
        puts("Enter an integer 0-65536");
        fgets(buf, 128, stdin);
        volume = atoi(buf);
	pa_cvolume_set(&v, sink_num_channels, volume);
	pa_context_set_sink_input_volume(context,
					   sink_index,
					   &v,
					   volume_cb,
					   NULL
					   );
    }
}
```
