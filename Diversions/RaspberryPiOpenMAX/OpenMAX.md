
##  OpenMAX 


We discussed OpenMAX in general in the chapter [ OpenMAX](../../Sampled/OpenMAX/) , applying it to sound on the 
      RPi and other systems. OpenMAX is an _extremely_ difficult API
      to work with - if you have any sense you will walk away right now.
      By [ dom: ](http://www.raspberrypi.org/forums/memberlist.php?mode=viewprofile&u=754) "I have written a fair bit of openmax client code and find it very hard. 
      You have to get an awful lot right before you get anything useful out.
      Just lots of OMX_ErrorInvalidState, and OMX_ErrorBadParameter messages if you are lucky. 
      Nothing happening at all if you are not..." 
      dom is quite correct - I estimate that my productivity in dealing with this API
      is done from the proverbial 10 lines per day to less than 10 lines per week.
      And lots of that is staring at the screen in complete bewilderment as to why
      it isn't working, with no error messages or anything to tell me
      what is going on (or isn't).
