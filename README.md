# Programming and Using Linux Sound

Linux is a major operating system that can not only do what every other operating system can do, but can also do a lot more. But because of its size and complexity it can be hard to learn how to do any particular task. This is reinforced by its development model: anyone can develop new components, and indeed Linux relies on a huge army of paid and unpaid volunteers to do just that. But that can lead to confusion: if two methods are developed for one task, which one should be chosen? or more subtly, what are the distinguishing features of one solution that make it more appropriate for your problem?

The Linux sound system is a major example of this: there is a large variety of tools and approaches for almost every aspect of sound. This ranges from audio codecs, to audio players, to audio support both within and outside of the Linux kernel.

I've been using Linux since kernel 0.99. I'm not a kernel hacker, more of a user and a programmer at the application layer. But I've always got lost whenever I want to do something complex involving Linux sound. So I've decided out of sheer bravado to try to describe the range of solutions to Linux sound issues. Of course, I'm way out of my depth, but that makes it a challenge, not a hindrance!

I'm going to rely on the people who really know what they are doing. So rather than re-invent everything from scratch I'm going to borrow the words of experts whenever I can. But the responsibility will still be mine, so please forgive and correct all the errors that I will make...

<div>

If you like this book, please consider contributing using PayPal:

<br/>

<a href="https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=jan%40newmarch%2ename&lc=AU&item_name=LinuxSound&currency_code=AUD&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted">

<img src="https://www.paypalobjects.com/WEBSCR-640-20110401-1/en_AU/i/btn/btn_donateCC_LG.gif">

</a>

<br/>

Or Flattr me:

<a href="https://flattr.com/submit/auto?
  user_id=jannewmarch&url=http://jan.newmarch.name&
  title=Linux%20Sound&
  description=Programming%20and%20Using%20Linu%20 Sound&
  language=en_GB&tags=linux,sound,alsa,pulseaudio,JavaSound,MIDI&category=text">

<img src="https://api.flattr.com/button/flattr-badge-large.png" 
  alt="Flattr this book" />
</a>

</div>

Copyright © Jan Newmarch jan@newmarch.name 

<a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/3.0/"><img alt="Creative Commons License" style="border-width:0" src="http://i.creativecommons.org/l/by-nc-sa/3.0/88x31.png" /></a>


This work is licensed under a Creative Commons [Attribution-NonCommercial-ShareAlike 3.0 Unported License](http://creativecommons.org/licenses/by-nc-sa/3.0/).
