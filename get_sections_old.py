
import urllib;
import os
import string
from HTMLParser import HTMLParser
import collections


class ChapterParser(HTMLParser):

    in_section = False
    section_file = None
    tag_counter = collections.Counter()
    indent = 0

    def __init__(self, dirname):
        HTMLParser.__init__(self)
        self.dirname = dirname
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def handle_starttag(self, tag, attrs):
        print "Encountered a start tag:", tag
        self.tag_counter[tag] += 1

        if tag == "h2":
            self.in_section = False
            if self.section_file <> None:
                self.section_file.close()

        elif tag == "li":
            self.section_file.write("+  ".rjust(self.indent-1))

        elif tag == "a":
            for attr in attrs:
                if attr[0] == "href":
                    self.a_url = attr[1]
                    print "Found an href ", attr[1]
        
        elif tag == "pre":
            #self.section_file.write("Strating a pre\n")
            lang = ""
            for attr in attrs:
                if attr[0] == "class":
                    lang = attr[1]
            if self.in_section:
                self.section_file.write("```" + lang + "\n")

        elif tag == "bockquote":
            self.section.write("> ")

        elif tag == "img" and self.in_section:
            for attr in attrs:
                if attr[0] == "src":
                    self.section_file.write("![alt text](" + attr[1] +")")
        
        elif tag == "ul" or tag == "ol" or tag == "dl":
            self.indent += 1


    def handle_endtag(self, tag):
       # print "Encountered an end tag :", tag
        self.tag_counter[tag] -= 1

        if tag == "h2":
            self.in_section = True
        
        elif tag == "li":
            self.section_file.write("\n")

        elif tag == "pre":
            #self.section_file.write("Ending a pre\n")
            if self.in_section:
                # we didn't print a newline at end of program
                # so put one in before closing program
                self.section_file.write("\n```\n")

        elif tag == "ul" or tag == "ol" or tag == "dl":
            self.indent -= 1



    def handle_data(self, data):
        # Care must be taken to test the innermost tags
        # first such as "a", before the outer tags like "li"

        #print "Encountered some data  :\"", data, "\""
        if self.tag_counter["h2"] > 0:
            print data
            # sanity: no / in filename
            data = string.replace(data, "/", " or ")
            # new section file
            self.section_file = open(self.dirname + 
                                     self.lose_spaces(data) +
                                     ".md",
                                     "w")
            self.section_file.write("# " + data + "\n")

        elif self.in_section:
            if self.tag_counter["h3"] > 0:
                self.section_file.write("### " + data + "\n")

            elif self.tag_counter["h4"] > 0:
                self.section_file.write("#### " + data + "\n")

            elif self.tag_counter["a"] > 0:
                #print "url is ", self.a_url
                #print "data is ", data
                self.section_file.write(" [" + data + "] (" + self.a_url + ")\n")

            elif self.tag_counter["code"] > 0:
                if self.tag_counter["pre"] > 0:
                    self.write_program_lines(data)
                else:
                    self.section_file.write(" `" + data + "`")
                    
            elif self.tag_counter["pre"] > 0:
                # sometimes I have <pre><code>, sometimes just <pre>
                self.write_program_lines(data)
                    
            elif self.tag_counter["dt"] > 0:
                self.section_file.write("+ __" + data + "__:\n ")

            else:
                self.section_file.write(string.strip(data) + "\n")

    def handle_entityref(self, name):
        if name == 'gt':
            print "Got a gt\n"
            self.handle_data('>')
        elif name == 'lt':
            self.handle_data('<')

    def lose_spaces(self, str):
        return str.replace(" ", "")

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
            chapter_parser.feed(chapterSource)
            #print "+ [", data, "] (", self.url, ")"


sock = urllib.urlopen("http://localhost/LinuxSound")
htmlSource = sock.read()
sock.close()

parser = TableOfContentsParser()
parser.feed(htmlSource)
