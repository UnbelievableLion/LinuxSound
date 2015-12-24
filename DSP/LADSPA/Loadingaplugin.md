
##  Loading a plugin 


An application can load a plugin by calling `loadLADSPAPluginLibrary`with one
      parameter which is the name of the plugin file.
      Note that there is no LADSPA library - LADPSA
      suuplies a header file `ladspa.h`and
      the distribution may include a file `load.c`which implements `loadLADSPAPluginLibrary`(it searches the directories in the `LADSPA_PATH`).


When a plugin is loaded by `dlopen`, 
      the function `_init`is called with no parameters. This may be used to setup
      the plugin and build, for example, the `LADSPA_Descriptor`.


A DLL must have an entry point that you can hook into.
      For LADSPA, each plugin must define a function `LADSPA_Descriptor * ladspa_descriptor(unsigned long Index)`.
      The values for indices 0, 1, ... are the `LADSPA_Descriptor`'s for each of the plugins
      included in the file.
