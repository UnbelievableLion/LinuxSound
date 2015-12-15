

import urllib;
from HTMLParser import HTMLParser

class ContentsParser(HTMLParser):
    in_contents = False
    in_li = False
    in_aref = False
    url = ""
    depth = 0
    contents_file = open("SUMMARY.md", "w")

    def handle_starttag(self, tag, attrs):
        #print "Encountered a start tag:", tag

        # ol starts a new chapter
        # ul starts a new section in a chapter
        if self.in_contents and( tag == "ul" or tag == "ol"):
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
        if self.in_contents and( tag == "ul" or tag == "ol"):
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
            print "+ [", data, "] (", self.url, ")"
            self.contents_file.write("+ [" + data + "] (" +  self.url + ")\n")

        # print section heading
        if self.in_contents and self.depth == 2:
            #print "depth",self. depth, data
            print "   + [", data, "] (", \
                self.url+self.lose_spaces(data), ")"
            self.contents_file.write("   + [" +  data + "] (" + \
                self.url+self.lose_spaces(data) + ")\n")
                

    def lose_spaces(self, str):
        return str.replace(" ", "")

sock = urllib.urlopen("http://localhost/LinuxSound")
htmlSource = sock.read()
sock.close()
# print htmlSource

print "# Contents"

parser = ContentsParser()
parser.feed(htmlSource)
