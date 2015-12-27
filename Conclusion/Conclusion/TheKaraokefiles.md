
##  The Karaoke files 


The Karaoke files are all stored on a server.
They could be accessible from Samba, NFS, SSHFS, etc, etc.
The only thing I can guarantee across Linux, Windows and Android
is HTTP, so I just make the files available through an Apache
server.


The files are stored in subdirectories according to their source.
For example, the files I ripped from the Sonken disk are in
subdirectory `KARAOKE/Sonken`.
These files can be accessed through a simple HTTP GET request,
given the URL for the file.
