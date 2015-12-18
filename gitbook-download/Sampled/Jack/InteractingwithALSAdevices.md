#  Interacting with ALSA devices 

Jack will eventually get its input from, and send its
      output to, devices. Currently, they are most likely
      to be ALSA devices. Consequently there must be a bridge
      between Jack processing and ALSA input and output.
      This will involve all the complexity of ALSA programming.

Fortunately there are Jack clients that do this.
      The Jack framework will talk to these as
      specified on starting the Jack server
```

	
jackd -dalsa
	
      
```
so you don't need to worry about that.

If you do want to worry, the examples directory
      contains ALSA examples. The program
 `alsa_in.c.ok`brings an ALSA input device into the Jack world
```sh_cpp


      
```


