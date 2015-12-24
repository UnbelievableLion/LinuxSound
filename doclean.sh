#!/bin/bash

dir=$1

python cleanup.py ../$dir/index.html > tmp || exit 1
mv ../$dir/index.html ../$dir/index.html.old
cp tmp ../$dir/index.html
cp -p ../$dir/index.html /server/LinuxSound/$dir/
