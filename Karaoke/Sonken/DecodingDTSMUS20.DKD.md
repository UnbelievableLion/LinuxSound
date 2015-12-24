
##  Decoding  DTSMUS20.DKD 


I'm on a Linux system and I use Linux/Unix utilities and applications.
      Equivalents exist under other O/S's such as Windows and Apple.

###  Song information 


The Unix command `strings`lists all the ASCII 8-bit encoded
      strings in a file that are at least 4 characters long. Running
      this command on all the DVD files shows that  DTSMUS20.DKD is the 
      only one with lots of english-language strings, and these
      strings are the song titles on the DVD.


A brief selection is

```

	
	  Come To Me
	  Come To Me Boy
	  Condition Of My Heart
	  Fly To The Sky
	  Cool Love
	  Count Down
	  Cowboy
	  Crazy
	
      
```


The actual strings that would show on your disk depends of course
      on the songs on it. You would need some english language titles
      on it for this to work, of course!


To make further progress you need a binary editor. I use `bvi`. `emacs`has a binary editor
      mode as well. Search in there for a song title you know is
      on the disk. For example, searching for the Beatles "Here Comes The Sun"
      shows the block

```

	
	  000AA920  12 D3 88 48 65 72 65 20 43 6F 6D 65 73 20 54 68 ...Here Comes Th
	  000AA930  65 20 52 61 69 6E 20 41 67 61 69 6E 00 45 75 72 e Rain Again.Eur
	  000AA940  79 74 68 6D 69 63 73 00 1F 12 D3 89 48 65 72 65 ythmics.....Here
	  000AA950  20 43 6F 6D 65 73 20 54 68 65 20 53 75 6E 00 42  Comes The Sun.B
	  000AA960  65 61 74 6C 65 73 00 1B 12 D3 8A 48 65 72 65 20 eatles.....Here
	  000AA970  46 6F 72 20 59 6F 75 00 46 69 72 65 68 6F 75 73 For You.Firehous
	
      
```


The string  "Here Comes The Sun" starts at 0xAA94C followed by 
      a null byte. This is followed at 0xAA95F by the null-terminated
      "Beatles". Immediately before this is 4 bytes.
      The length of these two strings (including the null bytes) and the 4 bytes 
      is 0x1F and this is the first of the 4 preceding bytes.
      So the block consists of a 4-byte header followed by a null-terminated
      song title followed by a null-terminated artist.
      Byte 1 is the length of the song information block including the
      4 byte header.


Byte 2 of the header block is 0x12. jim75 at [
	Decoding JBK 6628 DVD Karaoke Disc
      ](http://old.nabble.com/Decoding-JBK-6628-DVD-Karaoke-Disc-td12261269.html) discovered the document [
	JBK_Manual%5B1%5D.doc
      ](http://old.nabble.com/file/p12261269/JBK_Manual%255B1%255D.doc) .
      In there is a list of country codes:

```

	
	  00 : KOREAN
	  01 : CHINESE( reserved )
	  02 : CHINESE
	  03 : TAIWANESE
	  04 : JAPANESE
	  05 : RUSSIAN
	  06 : THAI
	  07 : TAIWANESE( reserved )
	  08 : CHINESE( reserved )
	  09 : CANTONESE
	  12 : ENGLISH
	  13 : VIETNAMESE
	  14 : PHILIPPINE
	  15 : TURKEY
	  16 : SPANISH
	  17 : INDONESIAN
	  18 : MALAYSIAN
	  19 : PORTUGUESE
	  20 : FRENCH
	  21 : INDIAN
	  22 : BRASIL
	
      
```


The Beatle's song has 0x12 in byte 2 of the header and this matches
      the country codes in the table. This is confirmed by looking at
      other language files (later).


I've discovered later that the WMA files have their own codes.
      So far I have seen

```

	
	  83 : CHINESE WMA
	  92 : ENGLISH WMA
	  94 : PHILIPPINE WMA
	
      
```


I guess you can see the pattern with the earlier ones!


Bytes 3 and 4 of the header are 0xD389 which is 54153 in decimal.
      This is one less than the song number in the book (54154).
      So bytes 3 and 4 are a 16-bit short integer, one less than the
      song index in the book.


This pattern is repeated throughout the file, so that each record
      is of this format.

###  Beginning/end of data 


There is a long sequence of bytes near the beginning of the file
      "01 01 01 01 01 ...".
      This finishes on my file at 0x9F23. By comparing the index number
      with those in my song book, I confirm this is the start of the Korean
      songs, and probably the start of all songs.
      I haven't found any table giving me this start value.


Checking a number
      of songs gives me this table:

+ English songs start at 60x9562D, song 24452 type 0x12
+ Cantonese at 0x8F5D2, song 13701 type 3
+ Korean at 0x9F23, song 37847 type 0
+ Indonesian at 0x11F942, song 42002 type 0x17
+ Hindi at 0x134227, song 45058 type 0x21
+ Phillipine at 0xD5D20, song 62775 type 0x14
+ Russian at 0x110428, song 41012 type 5
+ Spanish at 0xF5145, song 26487 type 0x16
+ Mandarin (1 char) at 0x413BE, song 1388 type 3

I can't find the Vietnamese songs, though. There don't seem to
      any on my disk. My song book is lying!
      I guess there is some table somewhere giving these start points, but 
      I haven't found it - these were all found by looking at my song
      book and then in the file.


The end of the block is signalled by a sequence of 
      "FF FF FF FF ..." at 0x136C92.


But there is lots of stuff
      both before and after the song information block.
      I don't know what it means.

###  Chinese songs 


The first English song in my book is "Gump by Al Wierd", song
      number 24452. In the table of contents file DTSMUS20.DK this is at
      0x9562D (611885). The entry before this is
      "20 03 3A 04 CE D2 B4 F2 C1 CB D2 BB CD A8 B2 BB CB B5 BB B0 B5 C4 B5 E7 BB B0 B8 F8 C4 E3 00 00". The song code is "3A 04" i.e. 14852 which is song
      number 14853 (one offset, remember!). When I play that song on my
      karaoke machine I'm in luck: the first character of the song is "我",
      which I recognise as the word "I" (in Pinyin: wo3). 
      It's encoding in the file is "CE D2".
      I've got Chinese input installed on my computer so I can search for this
      Chinese character.


A Google search for "unicode value of 我" shows me

```

	
	  [RESOLVED] Converting Unicode Character Literal to Uint16 variable ...
	  www.codeguru.com › ... › C++ (Non Visual C++ Issues)
	  5 posts - 2 authors - 1 Jul 2011

          I've determined that the unicode character '我' has a hex value of 
          0x6211 by looking it up on the "GNOME Character Map 2.32.1" 
          and if I do this....
	
      
```


and then looking up 0x6211 on [
	Unicode Search 
      ](http://www.khngai.com/chinese/tools/codeunicode.php) gives gold:

```

	
	  Unicode	6211 (25105)
	  GB Code	CED2 (4650)
	  Big 5 Code	A7DA
	  CNS Code	1-4A3C
	
      
```


There's the CED2 in the second line as GB Code.
      So there you go: the character set is GB
      (probably GB2312 with EUC-CN encoding) with code for 我 as CED2.


Just to make sure: using the table by Mary Ansell at [
	GB Code Table
      ](http://www.ansell-uebersetzungen.com/gborder.html) the bytes "CE D2 B4 F2 C1 CB D2 BB CD A8 B2 BB CB B5 BB B0 B5 
      C4 B5 E7 BB B0 B8 F8 C4 E3" translate into
      "我 打 了 一 通 ..." which is indeed the song.

###  Other languages 


I'm not familiar with other language encodings so haven't investigated
      the Thai, Vietnamese, etc.
      The Korean seems to be EUC-KR.

###  Programs 


The earlier investigations by others have created programs in C or C++.
      These are generally standalone programs. I would like to build a
      collection of reusable modules, so I have chosen Java as
      implementation language.

####  Java goodies 


Java is a good O/O language which supports good design.
      It includes a Midi player and Midi classes.
      It supports multiple language encodings so it is easy to
      switch from, say GB-2312 to Unicode.
      It has good cross-platform GUI support.

####  Java baddies 


Java doesn't support unsigned integer types. This sucks _really_ badly here since so many data types are unsigned for these programs. 
      Even bytes in Java are signed :-(.
      Here are some of the tricks :-(.

+ Make all types the next size up: byte to int, int to long, long to long...
	  Just hope that unsigned longs aren't really needed
+ If you need an unsigned byte and you've got an int, and you need
	  it to fit into 8 bits, cast to a byte and hope it's not too big :-(
+ Typecast all over the place to keep the compiler happy 
	  e.g. when a byte is required  from an int, ` (byte) n `
+ Watch signs all over the place. If you want to right shift a number,
	  the operator >> preserves sign extensions so eg in binary
	  1XYZ... shifts to 1111XYZ.. You need to use  >>> which results
	  in 0001XYZ.
+ If you want to assign an unsigned byte to an int, watch signs again.
	  You may need
```

	    
	      n = b ≥ 0 ? b : 256 - b
	    
	  
```

+ To build an unsigned int from 2 unsigned bytes, signs will stuff you again:
	  n = (b1 << 8) + b2 will get it wrong if either b1 or b2 is -ve.
	  Instead use
```

	    
	      n = ((b1 ≥ 0 ? b1 : 256 - b1) << 8) + (b2 ≥ 0 ? b2 : 256 - b2)
	    
	  
```
(no joke!)
####  Classes 


The song class contains information about a single song and is given here:
      SongInformation.java

```

	
      


public class SongInformation {


    // Public fields of each song record
    /**
     *  Song number in the file, one less than in songbook
     */
    public long number;

    /**
     * song title in Unicode
     */
    public String title;

    /**
     * artist in Unicode
     */
    public String artist;

    /**
     * integer value of language code
     */
    public int language;

    public static final int  KOREAN = 0;
    public static final int  CHINESE1 = 1;
    public static final int  CHINESE2 = 2;
    public static final int  TAIWANESE3 = 3 ;
    public static final int  JAPANESE = 4;
    public static final int  RUSSIAN = 5;
    public static final int  THAI = 6;
    public static final int  TAIWANESE7 = 7;
    public static final int  CHINESE8 = 8;
    public static final int  CANTONESE = 9;
    public static final int  ENGLISH = 0x12;
    public static final int  VIETNAMESE = 0x13;
    public static final int  PHILIPPINE = 0x14;
    public static final int  TURKEY = 0x15;
    public static final int  SPANISH = 0x16;
    public static final int  INDONESIAN = 0x17;
    public static final int  MALAYSIAN = 0x18;
    public static final int  PORTUGUESE = 0x19;
    public static final int  FRENCH = 0x20;
    public static final int  INDIAN = 0x21;
    public static final int  BRASIL = 0x22;
    public static final int  CHINESE131 = 131;
    public static final int  ENGLISH146 = 146;
    public static final int  PHILIPPINE148 = 148;

    public SongInformation(long number,
			   String title,
			   String artist,
			   int language) {
	this.number = number;
	this.title = title;
	this.artist = artist;
	this.language = language;
    }

    public String toString() {
	return "" + (number+1) + " (" + language + ") \"" + title + "\" " + artist;
    }

    public boolean titleMatch(String pattern) {
	// System.out.println("Pattern: " + pattern);
	return title.matches("(?i).*" + pattern + ".*");
    }

    public boolean artistMatch(String pattern) {
	return artist.matches("(?i).*" + pattern + ".*");
    }

    public boolean numberMatch(String pattern) {
	Long n;
	try {
	    n = Long.parseLong(pattern) - 1;
	    //System.out.println("Long is " + n);
	} catch(Exception e) {
	    //System.out.println(e.toString());
	    return false;
	}
	return number == n;
    }


    public boolean languageMatch(int lang) {
	return language == lang;
    }
}

	
      
```


The song table class holds a list of song information objects and is given by
       SongTable.java

```

	
      
import java.util.Vector;
import java.io.FileInputStream;
import java.io.*;
import java.nio.charset.Charset;

// public class SongTable implements java.util.Iterator {
// public class SongTable extends  Vector<SongInformation> {
public class SongTable {

    private static final String SONG_INFO_FILE = "/home/newmarch/Music/karaoke/sonken/DTSMUS20.DKD";
    private static final long INFO_START = 0x9F23;

    public static final int ENGLISH = 0x12;
    
    private static Vector<SongInformation> allSongs;

    private Vector<SongInformation> songs = 
	new Vector<SongInformation>  ();

    public static long[] langCount = new long[0x23];

    public SongTable(Vector<SongInformation> songs) {
	this.songs = songs;
    }

    public SongTable() throws java.io.IOException, 
			      java.io.FileNotFoundException {
	FileInputStream fstream = new FileInputStream(SONG_INFO_FILE);
	fstream.skip(INFO_START);
	while (true) {
	    int len;
	    int lang;
	    long number;

	    len = fstream.read();
	    lang = fstream.read();
	    number = readShort(fstream);
	    if (len == 0xFF && lang == 0xFF && number == 0xFFFFL) {
		break;
	    }
	    byte[] bytes = new byte[len - 4];
	    fstream.read(bytes);
	    int endTitle;
	    // find null at end of title
	    for (endTitle = 0; bytes[endTitle] != 0; endTitle++)
		;
	    byte[] titleBytes = new byte[endTitle];
	    byte[] artistBytes = new byte[len - endTitle - 6];

	    System.arraycopy(bytes, 0, titleBytes, 0, titleBytes.length);
	    System.arraycopy(bytes, endTitle + 1,
			     artistBytes, 0, artistBytes.length);
	    String title = toUnicode(lang, titleBytes);
	    String artist = toUnicode(lang, artistBytes);
	    // System.out.printf("artist: %s, title: %s, lang: %d, number %d\n", artist, title, lang, number);
	    SongInformation info = new SongInformation(number,
						       title,
						       artist,
						       lang);
	    songs.add(info);

	    if (lang > 0x22) {
		//System.out.println("Illegal lang value " + lang + " at song " + number);
	    } else {
		langCount[lang]++;
	    }
	}
	allSongs = songs;
    }

    public void dumpTable() {
	for (SongInformation song: songs) {
	    System.out.println("" + (song.number+1) + " - " +
			       song.artist + " - " +
			       song.title);
	}
    }

    public java.util.Iterator<SongInformation> iterator() {
	return songs.iterator();
    }

    private int readShort(FileInputStream f)  throws java.io.IOException {
	int n1 = f.read();
	int n2 = f.read();
	return (n1 << 8) + n2;
    }

    private String toUnicode(int lang, byte[] bytes) {
	switch (lang) {
	case SongInformation.ENGLISH:
	case SongInformation.ENGLISH146:
	case SongInformation.PHILIPPINE:
	case SongInformation.PHILIPPINE148:
	    // case SongInformation.HINDI:
	case SongInformation.INDONESIAN:
	case SongInformation.SPANISH:
	    return new String(bytes);

	case SongInformation.CHINESE1:
	case SongInformation.CHINESE2:
	case SongInformation.CHINESE8:
	case SongInformation.CHINESE131:
	case SongInformation.TAIWANESE3:
	case SongInformation.TAIWANESE7:
	case SongInformation.CANTONESE:
            Charset charset = Charset.forName("gb2312");
            return new String(bytes, charset);

	case SongInformation.KOREAN:
	    charset = Charset.forName("euckr");
            return new String(bytes, charset);

	default:
	    return "";
	}
    }

    public SongInformation getNumber(long number) {
	for (SongInformation info: songs) {
	    if (info.number == number) {
		return info;
	    }
	}
	return null;
    }

    public SongTable titleMatches( String pattern) {
	Vector<SongInformation> matchSongs = 
	    new Vector<SongInformation>  ();

	for (SongInformation song: songs) {
	    if (song.titleMatch(pattern)) {
		matchSongs.add(song);
	    }
	}
	return new SongTable(matchSongs);
    }

     public SongTable artistMatches( String pattern) {
	Vector<SongInformation> matchSongs = 
	    new Vector<SongInformation>  ();

	for (SongInformation song: songs) {
	    if (song.artistMatch(pattern)) {
		matchSongs.add(song);
	    }
	}
	return new SongTable(matchSongs);
    }

      public SongTable numberMatches( String pattern) {
	Vector<SongInformation> matchSongs = 
	    new Vector<SongInformation>  ();

	for (SongInformation song: songs) {
	    if (song.numberMatch(pattern)) {
		matchSongs.add(song);
	    }
	}
	return new SongTable(matchSongs);
    }

    public String toString() {
	StringBuffer buf = new StringBuffer();
	for (SongInformation song: songs) {
	    buf.append(song.toString() + "\n");
	}
	return buf.toString();
    }
	
    public static void main(String[] args) {
	// for testing
	SongTable songs = null;
	try {
	    songs = new SongTable();
	} catch(Exception e) {
	    System.err.println(e.toString());
	    System.exit(1);
	}
	songs.dumpTable();
	System.exit(0);

	// Should print "54151 Help Yourself Tom Jones"
	System.out.println(songs.getNumber(54150).toString());

	// Should print "18062 ä¼¦å·´(ææ­) ä¼¦å·´"
	System.out.println(songs.getNumber(18061).toString());

	System.out.println(songs.artistMatches("Tom Jones").toString());
	/* Prints
54151 Help Yourself Tom Jones
50213 Daughter Of Darkness Tom Jones
23914 DELILAH Tom Jones
52834 Funny Familiar Forgotten Feelings Tom Jones
54114 Green green grass of home Tom Jones
54151 Help Yourself Tom Jones
55365 I (WHO HAVE NOTHING) TOM JONES
52768 I Believe Tom Jones
55509 I WHO HAVE NOTHING TOM JONES
55594 I'll Never Fall Inlove Again Tom Jones
55609 I'm Coming Home Tom Jones
51435 It's Not Unusual Tom Jones
55817 KISS Tom Jones
52842 Little Green Apples Tom Jones
51439 Love Me Tonight Tom Jones
56212 My Elusive Dream TOM JONES
56386 ONE DAY SOON Tom Jones
22862 THAT WONDERFUL SOUND Tom Jones
57170 THE GREEN GREEN GRASS OF HOME TOM JONES
57294 The Wonderful Sound Tom Jones
23819 TILL Tom Jones
51759 What's New Pussycat Tom Jones
52862 With These Hands Tom Jones
57715 Without Love Tom Jones
57836 You're My World Tom Jones
	*/

	for (int n = 1; n < langCount.length; n++) {
	    if (langCount[n] != 0) {
		System.out.println("Count: " + langCount[n] + " of lang " + n);
	    }
	}

	// Check Russian, etc
	System.out.println("Russian " + '\u0411');
	System.out.println("Korean " + '\u0411');
	System.exit(0);
    }
}
	
      
```


You may need to adjust the constant values in the file-based 
      constructor for this to work properly for you.


A Java program using Swing to allow display and searching of the song
      titles is
      SongTableSwing.java

```

	
      
import java.awt.*;
import java.awt.event.*;
import javax.swing.event.*;
import javax.swing.*;
import javax.swing.SwingUtilities;
import java.util.regex.*;
import java.io.*;

public class SongTableSwing extends JPanel {
   private DefaultListModel model = new DefaultListModel();
    private JList list;
    private static SongTable allSongs;

    private JTextField numberField;
    private JTextField langField;
    private JTextField titleField;
    private JTextField artistField;

    // This font displays Asian and European characters.
    // It should be in your distro.
    // Fonts displaying all Unicode are zysong.ttf and Cyberbit.ttf
    // See http://unicode.org/resources/fonts.html
    private Font font = new Font("WenQuanYi Zen Hei", Font.PLAIN, 16);
    // font = new Font("Bitstream Cyberbit", Font.PLAIN, 16);
    
    private int findIndex = -1;

    /**
     * Describe <code>main</code> method here.
     *
     * @param args a <code>String</code> value
     */
    public static final void main(final String[] args) {
	allSongs = null;
	try {
	    allSongs = new SongTable();
	} catch(Exception e) {
	    System.err.println(e.toString());
	    System.exit(1);
	}

	JFrame frame = new JFrame();
	frame.setTitle("Song Table");
	frame.setSize(1000, 800);
	frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
	
	SongTableSwing panel = new SongTableSwing(allSongs);
	frame.getContentPane().add(panel);

	frame.setVisible(true);
    }

    public SongTableSwing(SongTable songs) {

	if (font == null) {
	    System.err.println("Can't fnd font");
	}
		
	int n = 0;
	java.util.Iterator<SongInformation> iter = songs.iterator();
	while(iter.hasNext()) {
	    model.add(n++, iter.next());
	    // model.add(n++, iter.next().toString());
	}

	BorderLayout mgr = new BorderLayout();
 
	list = new JList(model);
	// list = new JList(songs);
	list.setFont(font);
	JScrollPane scrollPane = new JScrollPane(list);

	setLayout(mgr);
	add(scrollPane, BorderLayout.CENTER);

	JPanel bottomPanel = new JPanel();
	bottomPanel.setLayout(new GridLayout(2, 1));
	add(bottomPanel, BorderLayout.SOUTH);

	JPanel searchPanel = new JPanel();
	bottomPanel.add(searchPanel);
	searchPanel.setLayout(new FlowLayout());

	JLabel numberLabel = new JLabel("Number");
	numberField = new JTextField(5);

	JLabel langLabel = new JLabel("Language");
	langField = new JTextField(8);

	JLabel titleLabel = new JLabel("Title");
	titleField = new JTextField(20);
	titleField.setFont(font);

	JLabel artistLabel = new JLabel("Artist");
	artistField = new JTextField(10);
	artistField.setFont(font);

	searchPanel.add(numberLabel);
	searchPanel.add(numberField);
	// searchPanel.add(langLabel);
	// searchPanel.add(langField);
	searchPanel.add(titleLabel);
	searchPanel.add(titleField);
	searchPanel.add(artistLabel);
	searchPanel.add(artistField);

	titleField.getDocument().addDocumentListener(new DocumentListener() {
		public void changedUpdate(DocumentEvent e) {
		    // rest find to -1 to restart any find searches
		    findIndex = -1;
		    // System.out.println("reset find index");
		}
		public void insertUpdate(DocumentEvent e) {
		    findIndex = -1;
		    // System.out.println("reset insert find index");
		}
		public void removeUpdate(DocumentEvent e) {
		    findIndex = -1;
		    // System.out.println("reset remove find index");
		}
	    }
	    );
	artistField.getDocument().addDocumentListener(new DocumentListener() {
		public void changedUpdate(DocumentEvent e) {
		    // rest find to -1 to restart any find searches
		    findIndex = -1;
		    // System.out.println("reset insert find index");
		}
		public void insertUpdate(DocumentEvent e) {
		    findIndex = -1;
		    // System.out.println("reset insert find index");
		}
		public void removeUpdate(DocumentEvent e) {
		    findIndex = -1;
		    // System.out.println("reset insert find index");
		}
	    }
	    );

	titleField.addActionListener(new ActionListener(){
                public void actionPerformed(ActionEvent e){
		    filterSongs();
                }});
	artistField.addActionListener(new ActionListener(){
                public void actionPerformed(ActionEvent e){
		    filterSongs();
                }});
	numberField.addActionListener(new ActionListener(){
                public void actionPerformed(ActionEvent e){
		    filterSongs();
                }});

	JPanel buttonPanel = new JPanel();
	bottomPanel.add(buttonPanel);
	buttonPanel.setLayout(new FlowLayout());

	JButton find = new JButton("Find");
	JButton filter = new JButton("Filter");
	JButton reset = new JButton("Reset");
	JButton play = new JButton("Play");
	buttonPanel.add(find);
	buttonPanel.add(filter);
	buttonPanel.add(reset);
	buttonPanel.add(play);

	find.addActionListener(new ActionListener() {
		public void actionPerformed(ActionEvent e) {
		    findSong();
		}
	    });

	filter.addActionListener(new ActionListener() {
		public void actionPerformed(ActionEvent e) {
		    filterSongs();
		}
	    });

	reset.addActionListener(new ActionListener() {
		public void actionPerformed(ActionEvent e) {
		    resetSongs();
		}
	    });

	play.addActionListener(new ActionListener() {
		public void actionPerformed(ActionEvent e) {
		    playSong();
		}
	    });
 
     }

    public void findSong() {
	String number = numberField.getText();
	String language = langField.getText();
	String title = titleField.getText();
	String artist = artistField.getText();

	if (number.length() != 0) {
	    try {

		long num = Integer.parseInt(number) - 1;
		for (int n = 0; n < model.getSize(); n++) {
		    SongInformation info = (SongInformation) model.getElementAt(n);
		    if (info.number == num) {
			list.setSelectedIndex(n);
			list.ensureIndexIsVisible(n);
			return;
		    }
		}
	    } catch(Exception e) {
		System.err.println("Not a number");
		numberField.setText("");
	    }

	    return;
	}

	/*
	System.out.println("Title " + title + title.length() + 
			   "artist " + artist + artist.length() +
			   " find start " + findIndex +
			   " model size " + model.getSize());
	if (title.length() == 0 && artist.length() == 0) {
	    System.err.println("no search terms");
	    return;
	}
	*/

	//System.out.println("Search " + searchStr + " from index " + findIndex);
	for (int n = findIndex + 1; n < model.getSize(); n++) {
	    SongInformation info = (SongInformation) model.getElementAt(n);
	    //System.out.println(info.toString());

	    if ((title.length() != 0) && (artist.length() != 0)) {
		if (info.titleMatch(title) && info.artistMatch(artist)) {
		    // System.out.println("Found " + info.toString());
			findIndex = n;
			list.setSelectedIndex(n);
			list.ensureIndexIsVisible(n);
			break;
		}
	    } else {
		if ((title.length() != 0) && info.titleMatch(title)) {
		    // System.out.println("Found " + info.toString());
		    findIndex = n;
		    list.setSelectedIndex(n);
		    list.ensureIndexIsVisible(n);
		    break;
		} else if ((artist.length() != 0) && info.artistMatch(artist)) {
		    // System.out.println("Found " + info.toString());
		    findIndex = n;
		    list.setSelectedIndex(n);
		    list.ensureIndexIsVisible(n);
		    break;

		}
	    }

	}
    }

    public void filterSongs() {
	String title = titleField.getText();
	String artist = artistField.getText();
	String number = numberField.getText();
	SongTable filteredSongs = allSongs;

	if (allSongs == null) {
	    // System.err.println("Songs is null");
	    return;
	}

	if (title.length() != 0) {
	    filteredSongs = filteredSongs.titleMatches(title);
	}
	if (artist.length() != 0) {
	    filteredSongs = filteredSongs.artistMatches(artist);
	}
	if (number.length() != 0) {
	    filteredSongs = filteredSongs.numberMatches(number);
	}

	model.clear();
	int n = 0;
	java.util.Iterator<SongInformation> iter = filteredSongs.iterator();
	while(iter.hasNext()) {
	    model.add(n++, iter.next());
	}
    }

    public void resetSongs() {
	artistField.setText("");
	titleField.setText("");
	numberField.setText("");
	model.clear();
	int n = 0;
	java.util.Iterator<SongInformation> iter = allSongs.iterator();
	while(iter.hasNext()) {
	    model.add(n++, iter.next());
	}
    }
    /**
     * "play" a song by printing its id to standard out.
     * Can be used in a pipeline this way
     */
    public void playSong() {
	SongInformation song = (SongInformation) list.getSelectedValue();
	if (song == null) {
	    return;
	}
	long number = song.number + 1;
	System.out.println("" + number);
    }


    class SongInformationRenderer extends JLabel implements ListCellRenderer {

	public Component getListCellRendererComponent(
						      JList list,
						      Object value,
						      int index,
						      boolean isSelected,
						      boolean cellHasFocus) {
	    setText(value.toString());
	    return this;
	}
    }
}
	
      
```


When "play" is selected it will print the song id to standard output for use in
      a pipeline.
