#  Starting Jack 

The Jack server is
 `jackd`. It has one required parameter which
      is the sound backend such as ALSA. The minimal command is
```

	
jackd -dalsa
	
      
```


if you are using a normal Linux distro such as Fedora or Ubuntu, this will
      quite likely fail if the PulseAudio system is running. This may need to be
      stopped, or at least paused while you run Jack. See the previous chapter
      for stopping PulseAudio, To pause it, I usually run this in a terminal window:
```

	
pasuspender cat
	
      
```
This will pause PulseAudio until
 `cat`terminates, which it will do when
      you enter ctrl-d.


 `jackd`will try to start using the Linux real-time scheduler. If you want
      to run without it, use the option
```

	
jackd --no-realtime -dalsa
	
      
```


If you want to run with the realtime scheduler, there are several ways:

+  Run the server from the root user
```

	    
sudo jackd -dalsa
	    
	  
```



+  Add a user to the
 `audio`and
 `jackuser`group by e.g.
```

	    
useradd -G audio newmarch
useradd -G jackuser newmarch
	    
	  
```
(You will need to logout and back in before this takes effect.)




Note that if you run the server as the root user, then you will not be able to
      connect to it from clients that are not in the
 `jackuser`group.


No apparent systemd or upstart scripts exist for Jack, but there are
      instructions about starting Jack at boot time from
 [
	Gentoo jack
      ] (http://en.gentoo-wiki.com/wiki/JACK#Starting_jack_manually)
:
```

	
#!/sbin/runscript
 # This programm will be used by init in order to launch jackd with the privileges
 # and id of the user defined into /etc/conf.d/jackd

 depend() {
	need alsasound
 }

 start() {
	if ! test -f "${JACKDHOME}/.jackdrc"; then
		eerror "You must start and configure jackd before launch it. Sorry."
		eerror "You can use qjackctl for that."
		return 1
	else JACKDOPTS=$(cat "${JACKDHOME}/.jackdrc"|sed -e 's\/usr/bin/jackd \\')
	fi

	if [ -e /var/run/jackd.pid ]; then
		 rm /var/run/jackd.pid
	fi

	ebegin "Starting JACK Daemon"
	env HOME="${JACKDHOME}" start-stop-daemon --start \
		--quiet --background \
		--make-pidfile --pidfile /var/run/jackd.pid \
		-c ${JACKDUSER} \
		-x /usr/bin/jackd -- ${JACKDOPTS} >${LOG}
	
	sleep 2
	if ! pgrep -u ${JACKDUSER} jackd > /dev/null; then
 		eerror "JACK daemon can't be started! Check logfile: ${LOG}"
 	fi
 	eend $?
 }

 stop() {
 	ebegin "Stopping JACK daemon -- please wait"
 	start-stop-daemon --stop --pidfile /var/run/jackd.pid &>/dev/null
 	eend $?
 }

 restart() {
 	svc_stop
 	while `pgrep -u ${JACKDUSER} jackd >/dev/null`; do
 		sleep 1
 	done
 	svc_start
 }
	
      
```
File: /etc/conf.d/jackd:
```




 # owner of jackd process (Must be an existing user.)
 JACKDUSER="dom"

 # .jackdrc location for that user (Must be existing, JACKDUSER can use
 # qjackctl in order to create it.) 
 JACKDHOME="/home/${JACKDUSER}" 

 # logfile (/dev/null for nowhere)
 LOG=/var/log/jackd.log



```
Create and save those 2 files. Don't forget to adjust JACKDUSER to the wanted user name (the same as yours I guess).

We need to make /etc/init.d/jackd executable:
```



# chmod +x /etc/init.d/jackd



```
Adding the script into the default run-level:
```


# rc-update add jackd default



```
Before restarting your system or starting this script, you must be sure that jackd is configured for 
$JACKUSER or jackd will fail. This is because the script will read /home/${USER}/.jackdrc.
If this file doesn't exist, the easiest way to create it is to run QJackCtl as explained above.

Note on Realtime: Due to a limitation in the implementation of start-stop-daemon, 
      it is not possible to start jackd in realtime mode as a non-root user by this method 
      if using pam_limits. start-stop-daemon does not implement support for pam_sessions, 
      meaning that changes to limits.conf have no effect in this context.

