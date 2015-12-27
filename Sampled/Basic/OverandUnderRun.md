
## Over and Under Run


From [Introduction to Sound Programming with ALSA](http://www.linuxjournal.com/article/6735?page=0,1) 


   > 

> When a sound device is active, data is transferred continuously between
the hardware and application buffers. In the case of data capture (recording),
if the application does not read the data in the buffer rapidly enough,
the circular buffer is overwritten with new data. The resulting data
loss is known as overrun. During playback, if the application does not
pass data into the buffer quickly enough, it becomes starved for data,
resulting in an error called underrun.


