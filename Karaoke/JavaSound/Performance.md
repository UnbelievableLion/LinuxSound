
##  Performance 


The program `top`can give a good idea of how much CPU is used by
various processes. My current computer is a high-end Dell laptop with a
quad-core Intel i7-2760QM CPU running at 2.4GHz. According to [CPU Benchmarks](http://www.cpubenchmark.net/) the processor is in the "High End CPU Chart."
On this computer, tested with various KAR files, PulseAudio takes about 30%
of the CPU while Java takes about 60%. On occassions these figures exceeded.
There is not much left for additional functionality!


In addition, while playing a MIDI file, sometimes the Java process hangs,
resuming with upto 600% CPU usage (I don't know how `top`manages to record that)!. This makes it effectively unusable, and I am
not sure where the problem lies.
