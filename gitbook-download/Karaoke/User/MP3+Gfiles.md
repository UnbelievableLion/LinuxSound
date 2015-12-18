#  MP3+G files 

MP3+G files are CD+G files adapted for use on a normal
      PC. They consist of an MP3 file containing the audio
      and a CDG file containing the lyrics. Frequently they
      are zipp'ed together.

Many sites selling CD+G files also sell MP3+G files.
      Various web sites give instructions on how to create
      your own MP3+G files. There are not many free sites.

The program
 `cgdrip.py`from
 [
        cdgtools-0.3.2
      ] (http://www.kibosh.org/cdgtools/)
can rip CD+G files from an audio disk and convert
      them to a pair of MP3+G files.
      The instructions from the (Python) source code are
To start using cdgrip immediately, try the following from the 
        command-line (replacing the --device option by the path to your
        CD device):
```

          
 $ cdrdao read-cd --driver generic-mmc-raw --device /dev/cdroms/cdrom0 --read-subchan rw_raw mycd.toc
 $ python cdgrip.py --with-cddb --delete-bin-toc mycd.toc
          
        
```
You may need to use a different --driver option or --read-subchan mode
        to cdrdao depending on your CD device.


The MP3 and CDG files usually share the same root
      e.g. Track1.mp3 and Track1.cdg. When unzipped,
 `vlc`can play them by giving it the
      MP3 file
only
to play as in
```

        
vlc Track1.mp3
        
      
```
Other players such as mplayer do not recognise this
      combination and only play the audio.

