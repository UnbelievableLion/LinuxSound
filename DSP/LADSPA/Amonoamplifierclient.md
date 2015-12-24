
##  A mono amplifier client 


The `applyplugin`program shows how clients can use
      LADSPA plugins in a general way. Unfortunately, the
      necessary generality makes it harder to see what is being
      done. In this section we just look at a simple client
      that uses the `amp_mono`plugin to halve the
      volume of a file.


From running `analyseplugin`on the `amp.so`file we can find that it contains
      a mono and stereo plugin. In the following program
      the `main`function loads the plugin file,
      gets a handle to the `ladspa_descriptor`structure and then looks through the descriptors until
      it finds the `amp_mono`plugin.


We know there are three ports: control, input and output,
      so we look through the list of ports to assign indices
      and connect the relevant arrays to the plugin descriptor.
      The control port only needs the address of a
      float value which is the amount of amplification that
      will occur.


The `run_plugin`function then just loops,
      reading samples from the imput file, applying the plugin
      and writing to the output file.
      I've used the [
	libsndfile](http://www.mega-nerd.com/libsndfile/) library to simplify reading and writing
      files in whatever format they are in.
      I've also used the `load.c`file from the
      LADSPA package to simplify loading the plugin library.


The program is `mono_amp.c`:

```


#include <stdlib.h>
#include <stdio.h>
#include <ladspa.h>
#include <dlfcn.h>
#include <sndfile.h>

#include "utils.h"

const LADSPA_Descriptor * psDescriptor;
LADSPA_Descriptor_Function pfDescriptorFunction;
LADSPA_Handle handle;

// choose the mono plugin from the amp file
char *pcPluginFilename = "amp.so";
char *pcPluginLabel = "amp_mono";

long lInputPortIndex = -1;
long lOutputPortIndex = -1;

SNDFILE* pInFile;
SNDFILE* pOutFile;

// for the amplifier, the sample rate doesn't really matter
#define SAMPLE_RATE 44100

// the buffer size isn't really important either
#define BUF_SIZE 2048
LADSPA_Data pInBuffer[BUF_SIZE];
LADSPA_Data pOutBuffer[BUF_SIZE];

// How much we are amplifying the sound by
LADSPA_Data control = 0.5f;

char *pInFilePath = "/home/local/antialize-wkhtmltopdf-7cb5810/scripts/static-build/linux-local/qts/demos/mobile/quickhit/plugins/LevelTemplate/sound/enableship.wav";
char *pOutFilePath = "tmp.wav";

void open_files() {
    // using libsndfile functions for easy read/write
    SF_INFO sfinfo;

    sfinfo.format = 0;
    pInFile = sf_open(pInFilePath, SFM_READ, &sfinfo);
    if (pInFile == NULL) {
	perror("can't open input file");
	exit(1);
    }

    pOutFile = sf_open(pOutFilePath, SFM_WRITE, &sfinfo);
    if (pOutFile == NULL) {
	perror("can't open output file");
	exit(1);
    }
}

sf_count_t fill_input_buffer() {
    return sf_read_float(pInFile, pInBuffer, BUF_SIZE);
}

void empty_output_buffer(sf_count_t numread) {
    sf_write_float(pOutFile, pOutBuffer, numread);
}

void run_plugin() {
    sf_count_t numread;

    open_files();

    // it's NULL for the amp plugin
    if (psDescriptor->activate != NULL)
	psDescriptor->activate(handle);

    while ((numread = fill_input_buffer()) > 0) {
	printf("Num read %d\n", numread);
	psDescriptor->run(handle, numread);
	empty_output_buffer(numread);
    }
}

int main(int argc, char *argv[]) {
    int lPluginIndex;

    void *pvPluginHandle = loadLADSPAPluginLibrary(pcPluginFilename);
    dlerror();

    pfDescriptorFunction 
	= (LADSPA_Descriptor_Function)dlsym(pvPluginHandle, "ladspa_descriptor");
    if (!pfDescriptorFunction) {
	const char * pcError = dlerror();
	if (pcError) 
	    fprintf(stderr,
		    "Unable to find ladspa_descriptor() function in plugin file "
		    "\"%s\": %s.\n"
		    "Are you sure this is a LADSPA plugin file?\n", 
		    pcPluginFilename,
		    pcError);
	return 1;
    }

    for (lPluginIndex = 0;; lPluginIndex++) {
	psDescriptor = pfDescriptorFunction(lPluginIndex);
	if (!psDescriptor)
	    break;
	if (pcPluginLabel != NULL) {
	    if (strcmp(pcPluginLabel, psDescriptor->Label) != 0)
		continue;
	}
	// got mono_amp

	handle = psDescriptor->instantiate(psDescriptor, SAMPLE_RATE);
	if (handle == NULL) {
	    fprintf(stderr, "Can't instantiate plugin %s\n", pcPluginLabel);
	    exit(1);
	}

	// get ports
	int lPortIndex;
	printf("Num ports %lu\n", psDescriptor->PortCount);
	for (lPortIndex = 0; 
	     lPortIndex < psDescriptor->PortCount; 
	     lPortIndex++) {
	    if (LADSPA_IS_PORT_INPUT
		(psDescriptor->PortDescriptors[lPortIndex])
		&& LADSPA_IS_PORT_AUDIO
		(psDescriptor->PortDescriptors[lPortIndex])) {
		printf("input %d\n", lPortIndex);
		lInputPortIndex = lPortIndex;

		psDescriptor->connect_port(handle,
					   lInputPortIndex, pInBuffer);
	    } else if (LADSPA_IS_PORT_OUTPUT
		       (psDescriptor->PortDescriptors[lPortIndex])
		       && LADSPA_IS_PORT_AUDIO
		       (psDescriptor->PortDescriptors[lPortIndex])) {
		printf("output %d\n", lPortIndex);
		lOutputPortIndex = lPortIndex;

		psDescriptor->connect_port(handle,
					   lOutputPortIndex, pOutBuffer);
	    }

	    if (LADSPA_IS_PORT_CONTROL
		(psDescriptor->PortDescriptors[lPortIndex])) {
		printf("control %d\n", lPortIndex);
		psDescriptor->connect_port(handle,			    
					   lPortIndex, &control);
	    }
	}
	// we've got what we wanted, get out of this loop
	break;
    }

    if ((psDescriptor == NULL) ||
	(lInputPortIndex == -1) ||
	(lOutputPortIndex == -1)) {
	fprintf(stderr, "Can't find plugin information\n");
	exit(1);
    }

    run_plugin();

    exit(0);
}

      
```


it is run just by calling `mono_amp`, 
      no arguments.
