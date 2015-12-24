import sys
import string

if len(sys.argv) > 1:
    fname = sys.argv[1] # "../Karaoke/Malata/index.html"

in_p = False
ending_block = False

def sin(str, sub):
    if string .find(str, sub) == -1:
        return False
    return True

def block_start(line):
    if sin(line, '<ul>') or sin(line, '<pre') or sin(line, '<blockquote>') or sin(line, '<table>') or sin(line, '<dl>') or sin(line, '<figure>'):
        return True
    return False

def block_end(line):
    if sin(line, '</ul>') or sin(line, '</pre') or sin(line, '</blockquote>') or sin(line, '</table>') or sin(line, '</dl>') or sin(line, '</figure>'):
        return True
    return False

with open(fname) as f:
    for line in f:
        if sin(line, '<img') and not sin(line, 'alt'):
            line = string.replace(line, '<img', '<img alt=""')

        if sin(line, '<!-- empty -->'):
            line = string.replace(line, '<!-- empty -->', '/* empty */')

        if sin(line, '<p>'):
            in_p = True
        elif sin(line, '</p>'):
            in_p = False

        if in_p:
            if block_start(line):
                print "</p>\n", line,
                in_p = False
            else:
                print line,
        else:
            if ending_block:
                stripped = string.lstrip(line)
                if len(stripped) > 0:
                    ending_block = False
                    if stripped[0] <> '<' or sin(stripped, '</p>'):
                        print '<p>'

            print line,
            if block_end(line):
                ending_block = True

