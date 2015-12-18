#  Adding microphone input 

At this stage we have a single application which can play a MIDI file,
      play a background movie and display highlighted lyrics on top of
      the video. There is no microphone input to sing along.

Singing along can be handled either within this application or by an
      external process. if we want to include it in the current application
      then we will have to build a mixer for two audio streams. 
      Java does this in the JavaSound package, but in C we would need to
      do that ourselves. Now I think that can be done in ALSA, but at present
      their mixer code is gobbledygook to me.

Jack makes it easy to mix audio - from different
processes
.
      The earlier section showed how to do that.

My long term goal is to include scoring, etc. I need to split out the
      GUI code into a process that can also deal with microphone input.
      The Gtk interface in TiMidity is a "separate process" model,
      so I'll build on that - when I have Jack under control.


This section is a place-holder for now.


