
##  File organisation 


If MP3+G songs are ripped from CDG Karaoke disks, then
a natural organisation would be to store the files in
directories, each directory corresponding to one disk.
More structure may be given by grouping the directories
by common artist, or by style of music, etc.
We just assume a directory structure with music files
as leaf nodes. These files are kept on the HTTP server.


I currently have a large number of these files on my server.
Information about these needs to be supplied to the clients.
After a bit of experimentation a `Vector`of `SongInformation`is created and serialised
using Java's object serialisation methods. The serialised
file is also kept on the HTTP server. When a client
starts up, it gets this file from the HTTP server
and deserialises it.


Building this vector means walking the directory tree
on the HTTP server and recording information as it goes.
Java code to walk directory trees is fairly straightforward.
It is a little tedious if you want it to be O/S independent.
Java 1.7 introduced mechanisms to make this easier.
These belong to the New I/O (NIO) system. The first
class of importance is the [java.nio.file.Path](http://docs.oracle.com/javase/7/docs/api/java/nio/file/Path.html) which "[is] an object that may be used to locate a
file in a file system.
It will typically represent a system dependent file path."
A string representing a file location in, say, a Linux
or a Windows file system can be turned into a `Path`object by

```cpp
Path startingDir = FileSystems.getDefault().getPath(dirString);
```


Traversal of a file system from a given `path`is done by walking a file tree, calling a node "visitor"
at each point. The visitor is a subclass of `SimpleFileVisitor<Path>`and for leaf nodes only you would override the
method

```cpp
public FileVisitResult visitFile(Path file, BasicFileAttributes attr)
```

```cpp
Visitor pf = new Visitor();
Files.walkFileTree(startingDir, pf);
```


A full explanation of this is given in the Java Tutorials
on [Walking the File Tree](http://docs.oracle.com/javase/tutorial/essential/io/walk.html) .
We use this to load all song information
from disk into a vector of song
paths in `SongTable.java`.
