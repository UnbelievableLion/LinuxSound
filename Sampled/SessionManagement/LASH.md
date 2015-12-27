
##  LASH 


This was the earliest successful session mananager for Linux audio but has since
fallen out of use. It does not seem to be in the Ubuntu repositories any more.


One of the applications requiring LASH is `jack_mixer`.
Even worse, it uses the Python `LASH`module from the `python-lash.2.7.4-0ubuntu`package.
The only copy I can find requires
a version of Python less than 2.7 and the installed  version of Python
is 2.7.4. This is an application which at present will not benefit from
current session management tools - while it might run
as Level 1 with LASH, it can only run at Level 0 with other session managers.


So there are Jack applications which require LASH for session management
but no such support seems to exist any more.
