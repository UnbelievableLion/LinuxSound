
##  CD+G disks 


From Wikipedia "CD+G":


   > CD+G (also known as CD+Graphics) 
	is an extension of the compact disc standard that can 
	present low-resolution graphics alongside the audio data 
	on the disc when played on a compatible device. 
	CD+G discs are often used for karaoke machines, 
	which utilize this functionality to present on-screen 
	lyrics for the song contained on the disc.



Each song is composed of two files: an audio file
      and a video file containing the lyrics (and maybe
      some background scenes).


There are many disks that you can buy using this format.
      You can't play them on directly your computer.
      rythmbox will play the audio, but not the video.
      vlc and totem don't like them.


Ripping the files onto your computer for storage on your
      hard disk is not so straightforward. The audio disks do
      not have a file system in the normal sense. For example,
      you cannot mount them using the Unix `mount`command; they are not even in ISO format. Instead you need
      to use a program like `cdrdao`to rip the
      files to a binary file and then work on that,

```

          
 $ cdrdao read-cd --driver generic-mmc-raw --device /dev/cdroms/cdrom0 --read-subchan rw_raw mycd.toc
          
        
```


creates a data file and a table of contents file.


The format of the CDG files has not apparently been publically released,
      but is decribed by Jim Bumgardner (back in 1995!) at [
	CD+G Revealed: Playing back Karaoke tracks in Software
      ](http://jbum.com/cdg_revealed.html) 


Programs such as SoundJuicer will extract the audio
      tracks, but leave the video behind.
