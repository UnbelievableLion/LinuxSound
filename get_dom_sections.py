#!/usr/bin/python

import urllib;
import os
import string
from bs4 import BeautifulSoup
from bs4.diagnose import diagnose
from HTMLParser import HTMLParser

class ChapterParser():
    
    section_file = None
    
    def __init__(self, dirname):
        self.dirname = dirname
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def lose_spaces(self, str):
        return str.replace(" ", "")

    def parse(self, source):

        #self.section_file = open(self.dirname + 
        #                         self.lose_spaces(data) +
        #                         ".md",
        #                         "w")
        #self.section_file = open("tmp.md", 'w')

        soup = BeautifulSoup(source, from_encoding="utf-8")
        #soup = BeautifulSoup(html_source, "lxml")
        #soup = BeautifulSoup(html_source, "html5lib")
        #soup = BeautifulSoup(html_source, "lxml")

        h2_list = soup.find_all("h2")
        for h2 in h2_list:

            print "   ", h2.string

            # close previous section file and open new one
            if self.section_file <> None:
                self.section_file.close()

            self.section_file = open(self.dirname + 
                                     self.lose_spaces(h2.string) +
                                     ".md",
                                     "w")
            section_tags = []
            self.section_file.write("\n## " + h2.string + "\n")
            node = h2
            while True:
                sibling = node.next_sibling
                node = sibling

                if sibling == None:
                    #print "End of list"
                    break


                if type(sibling).__name__ == 'Tag':
                    #print "    Sibling:", sibling.name
                    if sibling.name == "h2":
                        #print "Found next h2"
                        break
                        
                    section_tags.append(sibling)

            self.parse_all_tags(section_tags)
        #print "End of h2's"

    def parse_all_tags(self, tags):
        #print "Parsing h2 sibling tags"
        for tag in tags:
            # print "  Parsing h2 sibling tag", tag
            self.parse_tag(tag)

    def parse_tag(self, tag):
 
        if type(tag).__name__ == 'NavigableString':
            # string.strip messes up on a utf-8 unicode string
            self.section_file.write(string.strip(tag.string.encode('utf-8')))           
            return

        #print "Parsing tag", tag.name
        if tag.name == 'h3':
            self.section_file.write("\n### " + tag.string + "\n")
        
        elif tag.name == 'h4':
            self.section_file.write("\n#### " + tag.string + "\n")
        
        elif tag.name == 'a':
            href = tag['href']
            text = tag.string
            if text <> None:
                self.section_file.write(' [' + text.encode('utf-8') + '](' + href + ') ')

        elif tag.name == 'li':
            self.section_file.write("\n")

            # are we in a blockquote?
            for p in tag.parents:
                if p.name == 'blockquote':
                     self.section_file.write("> ")

            self.section_file.write("+ ")
            children = tag.children
            self.parse_all_tags(children)

        elif tag.name == 'dt':
            #self.section_file.write("\n+ __" + string.strip(tag.string) + "__:\n")

            self.section_file.write("\n")

            # are we in a blockquote?
            for p in tag.parents:
                if p.name == 'blockquote':
                     self.section_file.write("> ")

            self.section_file.write("+ __")
            children = tag.children
            self.parse_all_tags(children)
            self.section_file.write("__:\n")

        elif tag.name == 'p':
            self.section_file.write("\n\n")

            # are we in a blockquote?
            for p in tag.parents:
                if p.name == 'blockquote':
                    self.section_file.write("> ")

            children = tag.children
            self.parse_all_tags(children)
            self.section_file.write("\n")

        elif tag.name == 'blockquote':
            self.section_file.write("\n\n   > ")
            children = tag.children
            self.parse_all_tags(children)
            self.section_file.write("\n\n")

        elif tag.name == 'img':
            image = tag['src']
            self.section_file.write("![alt text](" + image +")")

        elif tag.name == 'code':
            parent = tag.parent
            if parent.name == 'pre':
                self.section_file.write("\n```")
                self.write_program_lines(tag.string)
                self.section_file.write("\n```\n")
            else:
                self.section_file.write(' `' + tag.string + '`')

        elif tag.name == 'pre':
            self.section_file.write("\n```\n")

            # <pre><code> has a tag.string but
            # <pre> alone requires looking at children???
            children = tag.children
            for c in children:
                self.section_file.write(c.string.encode('utf-8'))
            self.section_file.write("\n```\n")

        elif tag.name == 'em':
             self.section_file.write(" _" + string.strip(tag.string) +"_ ")
  
        elif tag.name == 'br':
             self.section_file.write("\n\n\n")
        else:
            children = tag.children
            self.parse_all_tags(children)
            #print tag.string

    def write_program_lines(self, str):
        # write out str by lines

        lines = string.split(str, "\n")

        # terminate all lines except last with \n:
        # HTML reader will chop half-way through a line
        # and entities ('&lt;') are a data chunk of their own 
        num_lines = len(lines)
        n = 0
        for line in lines:
            self.section_file.write(line)
            if n < num_lines-1:
                self.section_file.write("\n")
            n += 1

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
            chapter_parser.parse(chapterSource)
            #print "+ [", data, "](", self.url, ")"


sock = urllib.urlopen("http://localhost/LinuxSound")
htmlSource = sock.read()
sock.close()

parser = TableOfContentsParser()
parser.feed(htmlSource)


#sock = urllib.urlopen("http://localhost/LinuxSound/Sampled/Codecs/index.html")
#html_source = sock.read()
#html_source = html_source.encode('utf-8').decode('ascii', 'ignore')
#sock.close()

#diagnose(html_source.encode('utf-8'))

#converter = DocumentToMarkdown()
#converter.parse(html_source)



#h2 = soup.h2
#print h2.contents



#toplevel_list = soup.contents
#for toplevel in toplevel_list:
#    print toplevel
