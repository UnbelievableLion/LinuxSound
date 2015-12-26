#!/bin/bash

grep PART ../index.html |
while read part
do
    part=${part/<h3>/}
    part=${part/<\/h3>/}
    echo $part
    part_num=`echo $part | awk '{print $2}' | sed 's/://'`
    echo $part > PART${part_num}.md
done
