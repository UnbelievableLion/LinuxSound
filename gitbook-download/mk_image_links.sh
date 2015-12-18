#!/bin/bash

for d in `find . -type d`
do
	for f in ../$d/*.png ../$d/*.jpg ../$d/*.gif
	do
		ln $f $d
	done
done
