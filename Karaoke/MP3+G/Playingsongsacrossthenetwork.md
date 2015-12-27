
##  Playing songs across the network 


I actually want to play songs from my server disk to a
Raspberry Pi or CubieBoard connected to my TV,
and control the play from a netbook sitting on my
lap. (Later I will try to get Android code running to
do the same.). This is a distributed system.


Mounting server files on a computer is simple: you can use
NFS, Samba, ... I am currently using `sshfs`as in

```

sshfs -o idmap=user -o rw -o allow_other newmarch@192.168.1.101:/home/httpd/html /server
      
```


For remote access/control I replace the `run`command
of the last section by a TCP client/server. On the client,
controlling the player, I have

```cpp

java SongTableSwing | client 192.168.1.7
      
```


while on the (Raspberry Pi/CubieBoard) server I run

```cpp

#!/bin/bash
set -x
VLC_OPTS="--play-and-exit -f"

server |
while read line
do
	if expr match "$line" ".*mp3"
	then
		vlc $VLC_OPTS "$line"
	elif expr match "$line" ".*zip"
	then
		rm -f /tmp/karaoke/*
		unzip -d /tmp/karaoke "$line"
		vlc $VLC_OPTS /tmp/karaoke/*.mp3
	fi
done
      
```


The client/server files are just standard TCP files.
The client reads a newline-terminated string
from standard input and writes it to the
server, and the server prints the same line to standard output.
Here is `client.c`:

```cpp

#include <stdio.h> 
#include <sys/types.h>
#include <sys/socket.h> 
#include <netinet/in.h> 
#include <stdlib.h>
#include <string.h>

#define SIZE 1024 
char buf[SIZE];
#define PORT 13000
int main(int argc, char *argv[]) { 
    int sockfd; 
    int nread; 
    struct sockaddr_in serv_addr; 
    if (argc != 2) { 
	fprintf(stderr, "usage: %s IPaddr\n", argv[0]); 
	exit(1); 
    } 


    while (fgets(buf, SIZE , stdin) != NULL) {
	/* create endpoint */ 
	if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0) { 
	    perror(NULL); exit(2); 
	} 
	/* connect to server */ 
	serv_addr.sin_family = AF_INET; 
	serv_addr.sin_addr.s_addr = inet_addr(argv[1]); 
	serv_addr.sin_port = htons(PORT);
 
	while (connect(sockfd, 
		       (struct sockaddr *) &serv_addr, 
		       sizeof(serv_addr)) < 0) {
	    /* allow for timesouts etc */
	    perror(NULL);
	    sleep(1);
	}
	
	printf("%s", buf);
	nread = strlen(buf);
	/* transfer data and quit */ 
	write(sockfd, buf, nread);
	close(sockfd); 
    }
} 

      
```


and here is `server.c`

```cpp

#include <stdio.h> 
#include <sys/types.h> 
#include <sys/socket.h> 
#include <netinet/in.h> 
#include <stdlib.h>
#include <signal.h>

#define SIZE 1024 
char buf[SIZE]; 
#define TIME_PORT 13000

int sockfd, client_sockfd; 

void intHandler(int dummy) {
    close(client_sockfd);
    close(sockfd);
    exit(1);
}

int main(int argc, char *argv[]) { 
    int sockfd, client_sockfd; 
    int nread, len; 
    struct sockaddr_in serv_addr, client_addr; 
    time_t t; 

    signal(SIGINT, intHandler);
    
    /* create endpoint */ 
    if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0) { 
	perror(NULL); exit(2); 
    } 
    /* bind address */ 
    serv_addr.sin_family = AF_INET; 
    serv_addr.sin_addr.s_addr = htonl(INADDR_ANY); 
    serv_addr.sin_port = htons(TIME_PORT); 
    if (bind(sockfd, 
	     (struct sockaddr *) &serv_addr, 
	     sizeof(serv_addr)) < 0) { 
	perror(NULL); exit(3); 
    } 
    /* specify queue */ 
    listen(sockfd, 5); 
    for (;;) { 
	len = sizeof(client_addr); 
	client_sockfd = accept(sockfd, 
			       (struct sockaddr *) &client_addr, 
			       &len); 
	if (client_sockfd == -1) { 
	    perror(NULL); continue; 
	} 
	while ((nread = read(client_sockfd, buf, SIZE-1)) > 0) {
	    buf[nread] = '\0';
	    fputs(buf, stdout);
	    fflush(stdout);
	}
	close(client_sockfd); 
    }
}

      
```
