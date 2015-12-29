# Programming and Using Linux Sound

Linux is a major operating system that can not only do what every other operating system can do, but can also do a lot more. But because of its size and complexity it can be hard to learn how to do any particular task. This is reinforced by its development model: anyone can develop new components, and indeed Linux relies on a huge army of paid and unpaid volunteers to do just that. But that can lead to confusion: if two methods are developed for one task, which one should be chosen? or more subtly, what are the distinguishing features of one solution that make it more appropriate for your problem?

The Linux sound system is a major example of this: there is a large variety of tools and approaches for almost every aspect of sound. This ranges from audio codecs, to audio players, to audio support both within and outside of the Linux kernel.

I've been using Linux since kernel 0.99. I'm not a kernel hacker, more of a user and a programmer at the application layer. But I've always got lost whenever I want to do something complex involving Linux sound. So I've decided out of sheer bravado to try to describe the range of solutions to Linux sound issues. Of course, I'm way out of my depth, but that makes it a challenge, not a hindrance!

I'm going to rely on the people who really know what they are doing. So rather than re-invent everything from scratch I'm going to borrow the words of experts whenever I can. But the responsibility will still be mine, so please forgive and correct all the errors that I will make...



<table border="1">
<tr>
<td> 
   <img alt="Jan Newmarch" src="https://jan.newmarch.name/jan-medium-2010.jpg"> 
</td>
<td> Jan Newmarch is Academic Course Manager (ICT) at 
<a href="http://boxhill.edu.au"> Box Hill Institute </a>
and Adjunct Professor <a href="http://canberra.edu.au"> Canberra University </a>. 
His home page is at <a href="https://jan.newmarch.name"> jan.newmarch.name </a>. 
Jan has been writing books and papers for many years on all sorts of aspects of ICT: distributed programming, user interfaces, audio,Java, Go,  GPUs, Raspberry Pi, X Window system, Wayland, ...
</td>
</tr>
</table>

<div>
<br/>
This version of the book is derived from HTML source at
<a href="https://jan.newmarch.name/LinuxSound/">
   jan.newmarch.name/LinuxSound
</a>
<br/><br/>

<table   style="text-align:center">
<tr>
<td width="33%">
If you like this book, please consider 
<br/>
contributing using PayPal:

<br/>

<a href="https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=jan%40newmarch%2ename&lc=AU&item_name=LinuxSound&currency_code=AUD&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted">

<img src="https://www.paypalobjects.com/WEBSCR-640-20110401-1/en_AU/i/btn/btn_donateCC_LG.gif">

</a>

<br/>
</td>
<td width="33%">
Or Flattr me:
<br/>
<a href="https://flattr.com/submit/auto?
  user_id=jannewmarch&url=http://jan.newmarch.name&
  title=Linux%20Sound&
  description=Programming%20and%20Using%20Linu%20 Sound&
  language=en_GB&tags=linux,sound,alsa,pulseaudio,JavaSound,MIDI&category=text">

<img src="https://api.flattr.com/button/flattr-badge-large.png" 
  alt="Flattr this book" />
</a>
</td>


</div>
<td width="33%">
Copyright © Jan Newmarch jan@newmarch.name 

<a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/3.0/"><img alt="Creative Commons License" style="border-width:0" src="http://i.creativecommons.org/l/by-nc-sa/3.0/88x31.png" /></a>

</td>
</tr>
</table>

This work is licensed under a Creative Commons [Attribution-NonCommercial-ShareAlike 3.0 Unported License](http://creativecommons.org/licenses/by-nc-sa/3.0/).
