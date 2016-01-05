
##  Starting, stopping and pausing PulseAudio 


If you have a current Linux system, PulseAudio is probably
running. Test by running this from the command line:

```
ps agx | grep pulse
```


If you see a line like "/usr/bin/pulseaudio --start --log-target=syslog"
then it is running already.


If it isn't running and you have it installed, then start it by

```
pulseaudio --start
```


Stopping PulseAudio isn't so easy - Carla Schroder [shows how](http://www.linuxplanet.com/linuxplanet/tutorials/7130/2) .
The basic problem is that PulseAudio is set to respawn itself
after it is killed. You have to turn that off by
editing /etc/pulse/client.conf,
changing autospawn = yes to autospawn = no,
and setting daemon-binary to /bin/true.
Then you can kill the processs, remove it from startup files, etc.


If you want to run another sound system (such as Jack) for a short
while, you may just want to pause PulseAudio. You do this by using `pasuspender`. This takes a command (after "--") and
will pause access by the PulseAudio server to the audio devices until
the subcommand has finished.
For example,

```
pasuspender -- jackd
```


will run the Jack server, with PulseAudio getting out of the way until
it has finished.
