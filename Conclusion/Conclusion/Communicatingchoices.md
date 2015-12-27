
##  Communicating choices 


When a controller chooses a song, the URL needs to be communicated to the
playing device. For commonality across Linux/Windows/Android clients,
a simple TCP connection is used.
The bandwidth is not high, so to avoid possible blocks caused by
the server crashing and clients holding TCP connections open, each client
opens a TCP connection,
just sends a single URL across a connection and then closes it.
