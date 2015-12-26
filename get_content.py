#!/usr/bin/python

import urllib;
from HTMLParser import HTMLParser
import string
import sys

# Pull the LinuxSound/index.html off my site jan.newmarch.name
# search for all the part, chapter and section headings
# and write them into SUMMARY.md by default
# argv[1] can overwrite the default filename

if len(sys.argv) > 1:
    summary = sys.argv[1]
else:
    summary = 'SUMMARY.md'

class ContentsParser(HTMLParser):
    in_contents = False
    in_li = False
    in_aref = False
    url = ""
    depth = 0

    part_num = 1

    def write_preface(self):
        # this breaks if done in __init__, don't know why
        self.contents_file = open(summary, "w")
        self.contents_file.write("# Contents\n\n")
        self.contents_file.write("* [Introduction](README.md)\n")
   
    def handle_starttag(self, tag, attrs):
        #print "Encountered a start tag:", tag

        # ol starts a new chapter
        # ul starts a new section in a chapter
        if self.in_contents and( tag == "ul" or tag == "ol"):
            self.depth += 1
        if tag == "li":
            self.in_li = True

        # chapter has url in an href inside the li
        if tag == "a":
            self.in_aref = True
            for attr in attrs:
                if attr[0] == "href":
                    self.url = attr[1]

    def handle_endtag(self, tag):
        #print "Encountered an end tag :", tag
        # leaving the chapter or contents section?
        if self.in_contents and( tag == "ul" or tag == "ol"):
            self.depth -= 1
            if self.depth == 0:
                self.in_contents = False
        if tag == "li":
            self.in_li = False;
        if tag == "a":
            self.in_aref = False

    def handle_data(self, data):
        #print "Encountered some data  :\"", data, "\""

        # starting contents section?
        if data.find("Contents") >= 0:
            #print "Got contents section"
            self.in_contents = True

        # print PART heading
        if self.in_contents and string.find(data, "PART") >= 0:
            self.contents_file.write("\n* [" + string.strip(data) + "](PART" + str(self.part_num) + ".md)\n")
            self.part_num += 1

        # print chapter heading
        if self.in_contents and self.depth == 1 and self.in_aref:
            #print "depth",self. depth, data
            print "  * [", data, "](", self.url, ")"
            self.contents_file.write("   + [" + string.strip(data)  + "](" +  self.url + "README.md)\n")

        # print section heading
        if self.in_contents and self.depth == 2:
            #print "depth",self. depth, data
            print "    * [", data, "] (", \
                self.url+self.lose_spaces(data), ")"
            self.contents_file.write("      + [" +  string.strip(data) + "](" + \
                                     self.url+self.lose_spaces(data) + ".md)\n")
                

    def lose_spaces(self, str):
        s =  str.replace(" ", "")
        return s.replace("\n", "")

sock = urllib.urlopen("http://localhost/LinuxSound")
htmlSource = sock.read()
sock.close()
# print htmlSource

print "# Contents"

parser = ContentsParser()
parser.write_preface()
parser.feed(htmlSource)
