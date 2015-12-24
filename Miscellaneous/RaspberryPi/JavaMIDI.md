
##  Java MIDI 


openJDK supports the Java MIDI devices. The program `DeviceInfo`reports

```

	
MIDI devices:
    Name: Gervill, Decription: Software MIDI Synthesizer, Vendor: OpenJDK
        Device is a synthesizer
        Open receivers:

        Default receiver: com.sun.media.sound.SoftReceiver@10655dd

        Open receivers now:
            com.sun.media.sound.SoftReceiver@10655dd

        Open transmitters:
        No default transmitter
    Name: Real Time Sequencer, Decription: Software sequencer, Vendor: Sun Microsystems
        Device is a sequencer
        Open receivers:

        Default receiver: com.sun.media.sound.RealTimeSequencer$SequencerReceiver@12f0999

        Open receivers now:
            com.sun.media.sound.RealTimeSequencer$SequencerReceiver@12f0999

        Open transmitters:

        Default transmitter: com.sun.media.sound.RealTimeSequencer$SequencerTransmitter@65a77f

        Open transmitters now:
            com.sun.media.sound.RealTimeSequencer$SequencerTransmitter@65a77f
Default system sequencer is Real Time Sequencer
Default system synthesizer is Gervill

	
      
```





Programs like DumpSequence work okay. But the SimpleMidiPlayer hits 80% CPU
      usage and is unusable.
      So any idea of a Karaoke player using Java on the RPi is simply not on :-(.
      There is a thread on the Raspberry Pi site discussing [
	problems with sound
      ](http://www.raspberrypi.org/phpBB3/viewtopic.php?f=38&t=11009) .
