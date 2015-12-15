#  PinYin 

For Chinese language files, one of my aims was to display the PinYin (Romanised form)
      of the Chinese hierographic characters. For this, I need to be able rewrite any sequence
      of Chinese characters into their PinYin form. I couldn't find a list of characters and
      their corresponding characters. The closest is the
 [
	Chinese-English Dictionary
      ] (http://www.mandarintools.com/worddict.html)
from which you can download the dictionary as a text file. Typical lines in this file are
```

	
不賴 不赖 [bu4 lai4] /not bad/good/fine/
	
      
```
Each line has the Traditional characters followed by the Simplified characters, the PinYin
      in [...] and then English meanings.

I used the following shell script to make a list of character/PinYin pairs:
```

	
#!/bin/bash

# get pairs of character + pinyin by throwing away other stuff in the dictionary

awk '{print $2, $3}' cedict_ts.u8 | grep -v '[A-Z]' | 
  grep -v '^.[^ ]' | sed -e 's/\[//' -e 's/\]//' -e 's/[0-9]$//' | 
    sort | uniq -w 1 > pinyinmap.txt
	
      
```
to give lines such as
```

	
好 hao
妁 shuo
如 ru
妃 fei
	
      
```


This can then be read into a Java Map, and then quick lookups can be done
      to translate Chinese to PinYin.

