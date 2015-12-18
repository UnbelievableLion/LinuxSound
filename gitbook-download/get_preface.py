

import urllib;
import os
import string
from HTMLParser import HTMLParser


class ChapterParser(HTMLParser):

    in_preface = False
    preface_file = None

    def __init__(self, dirname):
        HTMLParser.__init__(self)
        self.dirname = dirname
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def handle_starttag(self, tag, attrs):
        #print "Encountered a start tag:", tag
        if tag == "div":
            for attr in attrs:
                if attr[0] == "class" and attr[1] == "preface":
                    self.in_preface = True
                    self.preface_file = open(self.dirname + "README.md", "w")


    def handle_endtag(self, tag):
       # print "Encountered an end tag :", tag
        if tag == "div":
            self.in_preface = False
            if self.preface_file <> None:
                self.preface_file.close()
                self.preface_file = None

    def handle_data(self, data):
        #print "Encountered some data  :\"", data, "\""
        if self.in_preface:
            print data
            self.preface_file.write(string.strip(data))


class TableOfContentsParser(HTMLParser):
    in_contents = False
    in_li = False
    in_aref = False
    url = ""
    depth = 0

    def handle_starttag(self, tag, attrs):
        #print "Encountered a start tag:", tag

        # ol starts a new chapter
        # ul starts a new section in a chapter
        if self.in_contents and tag == "ol":
            self.depth = self.depth + 1
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
        if self.in_contents and tag == "ol":
            self.depth = self.depth - 1
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

        # print chapter heading
        if self.in_contents and self.depth == 1 and self.in_aref:
            #print "depth",self. depth, data
            print "Parsing chapter ", self.url
            sock = urllib.urlopen("http://localhost/LinuxSound/"+self.url+"index.html")
            chapterSource = sock.read()
            sock.close()
            chapter_parser = ChapterParser(self.url)
            chapter_parser.feed(chapterSource)
            #print "+ [", data, "] (", self.url, ")"


sock = urllib.urlopen("http://localhost/LinuxSound")
htmlSource = sock.read()
sock.close()
# print htmlSource

print "# Contents"

parser = TableOfContentsParser()
parser.feed(htmlSource)
