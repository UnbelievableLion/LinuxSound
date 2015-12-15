ALSA has some support for MIDI devices by a sequencer API.
	Clients can send MIDI events to the sequencer and it will
	play them according to the timing of the events.
	Other clients can then receive these sequenced events and,
	for example, synthesize them.