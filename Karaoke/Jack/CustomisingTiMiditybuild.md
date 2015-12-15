#  Customising TiMidity build 

The version of TiMidity from the Ubuntu distro crashes if
      I try to dynamically load another interface. As the code is
      stripped, it is not possible to find out why.
      So to add a new interface we need to build TiMidity
      from source.

The commands I now use are
```

 `
./configure --enable-audio=alsa,jack \
            --enable-interface=xaw,gtk \
            --enable-server \
            --enable-dynamic
make clean
make
	`

```
An interface with key, say 'k', can then be run
      with Jack output by
```

 `
timidity -d. -ik -Oj --trace  --trace-text-meta 54154.mid
	`

```


