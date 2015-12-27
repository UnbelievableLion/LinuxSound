
##  Creating a component 


The `ilclient`library has a convenience function
to create a component, ` ilclient_create_component`.
This takes four parameters.
The first is an ` ILCLIENT_T`which an application gets by a
call to `ilclient_init()`.
The second is the address to store the component.


The third is a 'simple' form of the component's name.
Now this isn't the name used in the OpenMAX specification.
And it isn't the actual name of the component.
For an image decoder object these are `image_decoder`and `OMX.broadcom.image_decode`respectively.
The name used is formed by dropping `OMX.broadcom.`from the component's name,
to give `image_decode`.
The full list of Broadcom components is at [VMCS-X OpenMAX IL Components](http://home.nouwen.name/RaspberryPi/documentation/ilcomponents/index.html) and this lists the names used.


The fourth parameter is a bit-wise OR of several flags.
A major one is `ILCLIENT_DISABLE_ALL_PORTS`which - as might be expected - disables all ports of the
component, to make it easier to transition to idle state
later. Two other significant flags are `ILCLIENT_ENABLE_INPUT_BUFFERS`and `ILCLIENT_ENABLE_OUTPUT_BUFFERS`.
Now these don't actually enable any buffers for the ports,
create buffers, or apparently do anything really useful.
However, if you don't enable the appropriate buffers here
and later try to actually enable them using
an `OMX_CommandPortEnable`command,
then the library will throw a cryptic error
message  complaining about an illegal operation.
I suppose that is trying to ensure that you only
make valid calls for that component, but I wish the
error was not so un-helpful.


A typical component creation will look like

```cpp

	
 ilclient_create_component(decoder->client,
			&decoder->imageDecoder->component,
			"image_decode",
			ILCLIENT_DISABLE_ALL_PORTS
			|
			ILCLIENT_ENABLE_INPUT_BUFFERS
			|
			ILCLIENT_ENABLE_OUTPUT_BUFFERS)
	
      
```
