
##  Swing song table UI 


There is a principal song table containing all the songs.
      This may have filters applied to it to show, say, only the
      Beatles songs.
      In addition, the visitors to my house have built up a collection
      of "favourite" songs. Each of these is its own song table.
      The UI for this is the Swing application `SongTableSwing.java`:

```

	
package newmarch.songtable;

import java.awt.*;
import java.awt.event.*;
import javax.swing.event.*;
import javax.swing.*;
import javax.swing.SwingUtilities;
import java.util.regex.*;
import java.io.*;
import java.net.Socket;
import java.net.InetAddress;

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
	if (args.length >= 1 && 
	    args[0].startsWith("-h")) {
	    System.err.println("Usage: java SongTableSwing [song songdir|songfile]");
	    System.err.println("  -sSongStore");
	    System.exit(0);
	}

	allSongs = null;
	try {
	    allSongs = new SongTable(args);
	} catch(Exception e) {
	    System.err.println(e.toString());
	    System.exit(1);
	}

	JFrame frame = new JFrame();
	frame.setTitle("Song Table");

	Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
	frame.setSize(800, ((int)screenSize.getHeight())*5/6);
	frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
	
	SongTableSwing panel = new SongTableSwing(allSongs);
	frame.getContentPane().add(panel);

	frame.setVisible(true);

	JFrame favourites = new JFrame();
	favourites.setTitle("Favourites");
	favourites.setSize(600,  ((int)screenSize.getHeight())*3/4);
	favourites.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
	
	AllFavourites lists = new AllFavourites(panel);
	favourites.getContentPane().add(lists);

	favourites.setVisible(true);

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

	// Support DnD
	list.setDragEnabled(true);

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
	    return;
	}

	for (int n = findIndex + 1; n < model.getSize(); n++) {
	    SongInformation info = (SongInformation) model.getElementAt(n);

	    if ((title.length() != 0) && (artist.length() != 0)) {
		if (info.titleMatch(title) && info.artistMatch(artist)) {
		    findIndex = n;
		    list.setSelectedIndex(n);
		    list.ensureIndexIsVisible(n);
		    break;
		}
	    } else {
		if ((title.length() != 0) && info.titleMatch(title)) {
		    findIndex = n;
		    list.setSelectedIndex(n);
		    list.ensureIndexIsVisible(n);
		    break;
		} else if ((artist.length() != 0) && info.artistMatch(artist)) {
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
	model.clear();
	int n = 0;
	java.util.Iterator<SongInformation> iter = allSongs.iterator();
	while(iter.hasNext()) {
	    model.add(n++, iter.next());
	}
    }
    /**
     * "play" a song by printing its file path to standard out.
     * Can be used in a pipeline this way
     */
    public void playSong() {
	String SERVERIP = "192.168.1.110"; 
	int SERVERPORT = 13000;
	PrintWriter out;
	
	SongInformation song = (SongInformation) list.getSelectedValue();
	if (song == null) {
	    return;
	}
	System.out.println(song.path);

	try {
	    InetAddress serverAddr = InetAddress.getByName(SERVERIP);
	    Socket socket = new Socket(serverAddr, SERVERPORT);
				 
	    //send the message to the server
	    out = new PrintWriter(
				  new BufferedWriter(
						     new OutputStreamWriter(socket.getOutputStream())), 
				  true);
	    // Avoid println to socket for Windows
	    out.print(song.path + "\n");
	    out.flush();
	    socket.close();
				
	} catch (Exception e) {
	    System.err.println(e.toString());
	}
    }

    public SongInformation getSelection() {
	return (SongInformation) (list.getSelectedValue());
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





The favourites classes are `AllFavourites.java`:

```

	package newmarch.songtable;

import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import java.util.Vector;
import java.nio.file.*;
import java.io.*;
import java.net.URL;

public class AllFavourites extends JTabbedPane {
    public static String FAVOURITES_DIR = "http://192.168.1.101:8000/KARAOKE/favourites/";

    private SongTableSwing songTable;
    public Vector<FavouritesInfo> favourites = new Vector<FavouritesInfo>();

    public AllFavourites(SongTableSwing songTable) {
	this.songTable = songTable;

	loadFavourites();

	NewPanel newP = new NewPanel(this);
	addTab("NEW", null, newP);
    }

    private void loadFavourites() {
	//String userHome = System.getProperty("user.home");
	/*
	Path favouritesPath = FileSystems.getDefault().getPath(userHome, 
							    ".karaoke",
							    "favourites");
	*/

	try {
	    URL url = new URL(FAVOURITES_DIR);
	    InputStreamReader reader = new InputStreamReader(url
							     .openConnection().getInputStream());
	    BufferedReader in = new BufferedReader(reader);
	    String line = in.readLine();
	    while (line != null) {
		if (line.startsWith(".")) {
		    // ignore .htacess etc
		    continue;
		}
		favourites.add(new FavouritesInfo(null, line, null));
		line = in.readLine();
	    }
	    in.close();
	    reader.close();

	    for (FavouritesInfo f: favourites) {
		// TODO checkout the Songtable constructors - messy 
		f.songTable = new SongTable(new Vector<SongInformation>());
		f.songTable.loadTableFromStore(FAVOURITES_DIR +
					   f.owner);

		Favourites fav = new Favourites(songTable, 
						f.songTable, 
						f.owner);
		addTab(f.owner, null, fav, f.owner);
	    }
	} catch(Exception e) {
	    System.out.println(e.toString());
	}

	/*
	Path favouritesPath = FileSystems.getDefault().getPath(FAVOURITES_DIR);
	try {
	    DirectoryStream<Path> stream = 
		Files.newDirectoryStream(favouritesPath);
	    for (Path entry: stream) {
		int nelmts = entry.getNameCount();
		Path last = entry.subpath(nelmts-1, nelmts);
		if (last.toString().startsWith(".")) {
		    // ignore .htaccess etc
		    continue;
		}
		System.err.println("Favourite: " + last.toString());
		File storeFile = entry.toFile();
		
		FileInputStream in = new FileInputStream(storeFile); 
		ObjectInputStream is = new ObjectInputStream(in);
		Vector<SongInformation> favouriteSongs = 
		    (Vector<SongInformation>) is.readObject();
		in.close();
		for (SongInformation s: favouriteSongs) {
		    System.err.println("Fav: " + s.toString());
		}

		SongTable favouriteSongsTable = new SongTable(favouriteSongs);
		Favourites f = new Favourites(songTable, 
					      favouriteSongsTable, 
					      last.toString());
		addTab(last.toString(), null, f, last.toString());
		System.err.println("Loaded favs " + last.toString());
	    }
	} catch(Exception e) {
	    System.err.println(e.toString());
	}
	*/
    }

    class NewPanel extends JPanel {
	private JTabbedPane pane;

	public NewPanel(final JTabbedPane pane) {
	    this.pane = pane;

	    setLayout(new FlowLayout());
	    JLabel nameLabel = new JLabel("Name of new person");
	    final JTextField nameField = new JTextField(10);
	    add(nameLabel);
	    add(nameField);

	    nameField.addActionListener(new ActionListener(){
		    public void actionPerformed(ActionEvent e){
			String name = nameField.getText();

			SongTable songs = new SongTable(new Vector<SongInformation>());
			Favourites favs = new Favourites(songTable, songs, name);
			
			pane.addTab(name, null, favs);
		    }});

	}
    }

    class FavouritesInfo {
	public SongTable songTable;
	public String owner;
	public Image image;
	
	public FavouritesInfo(SongTable songTable,
			      String owner,
			      Image image) {
	    this.songTable = songTable;
	    this.owner = owner;
	    this.image = image;
	}
    }

}

      
```


and

```

	
package newmarch.songtable;

import java.awt.*;
import java.awt.event.*;
import javax.swing.event.*;
import javax.swing.*;
import javax.swing.table.*;
import javax.swing.SwingUtilities;
import java.util.regex.*;
import java.io.*;
import java.nio.file.FileSystems;
import java.nio.file.*;
import java.net.Socket;
import java.net.InetAddress;
import java.util.Vector;

public class Favourites extends JPanel {
    private DefaultListModel model = new DefaultListModel();
    private JList list;

    private JTable table;
    private DefaultTableModel tmodel = new DefaultTableModel();

    // whose favorites these are
    private String user;

    // songs in this favourites list
    private final SongTable favouriteSongs;

    // pointer back to main song table list
    private final SongTableSwing songTable;

    // This font displays Asian and European characters.
    // It should be in your distro.
    // Fonts displaying all Unicode are zysong.ttf and Cyberbit.ttf
    // See http://unicode.org/resources/fonts.html
    private Font font = new Font("WenQuanYi Zen Hei", Font.PLAIN, 16);
    
    private int findIndex = -1;

    public Favourites(final SongTableSwing songTable, 
		      final SongTable favouriteSongs, 
		      String user) {
	this.songTable = songTable;
	this.favouriteSongs = favouriteSongs;
	this.user = user;

	if (font == null) {
	    System.err.println("Can't find font");
	}


	System.out.println("Favourites for user: " + user);
	
	tmodel.addColumn("ID");
	tmodel.addColumn("Artist");
	tmodel.addColumn("Title");
	tmodel.addColumn("Path");
	
	int n = 0;
	java.util.Iterator<SongInformation> iter = favouriteSongs.iterator();
	while(iter.hasNext()) {
	    SongInformation info = iter.next();
	    if (info == null)
		continue;
	    /*
	    System.out.println("UID for SongInformation " + 
			       ObjectStreamClass.lookup(info.getClass()).getSerialVersionUID());
	    */
	    model.add(n++, info);

	    tmodel.addRow(info.toVector());
	}



	BorderLayout mgr = new BorderLayout();
 
	list = new JList(model);
	list.setFont(font);

	table = new JTable(tmodel);
	table.setRowSorter(new TableRowSorter(tmodel));
	// hide column 3
	table.removeColumn(table.getColumnModel().getColumn(3));
	table.setFillsViewportHeight(true);
	table.setFont(font);
	table.getColumnModel().getColumn(0).setPreferredWidth(100);
	table.getColumnModel().getColumn(0).setMaxWidth(100);
	table.getColumnModel().getColumn(1).setPreferredWidth(200);
	table.getColumnModel().getColumn(1).setMaxWidth(200);
	table.setRowHeight(24);

	//JScrollPane scrollPane = new JScrollPane(list);
	JScrollPane scrollPane = new JScrollPane(table);

	setLayout(mgr);
	add(scrollPane, BorderLayout.CENTER);

	JPanel bottomPanel = new JPanel();
	bottomPanel.setLayout(new GridLayout(2, 1));
	add(bottomPanel, BorderLayout.SOUTH);

	JPanel searchPanel = new JPanel();
	bottomPanel.add(searchPanel);
	searchPanel.setLayout(new FlowLayout());

	JPanel buttonPanel = new JPanel();
	bottomPanel.add(buttonPanel);
	buttonPanel.setLayout(new FlowLayout());

	JButton addSong = new JButton("Add song to list");
	JButton deleteSong = new JButton("Delete song from list");
	JButton play = new JButton("Play");

	buttonPanel.add(addSong);
	buttonPanel.add(deleteSong);
	buttonPanel.add(play);

	play.addActionListener(new ActionListener() {
		public void actionPerformed(ActionEvent e) {
		    playSong();
		}
	    });

	deleteSong.addActionListener(new ActionListener() {
		public void actionPerformed(ActionEvent e) {
		    /*
		    SongInformation song = (SongInformation) list.getSelectedValue();
		    model.removeElement(song);
		    favouriteSongs.songs.remove(song);
		    */

		    int realIndex = table.convertRowIndexToModel(table.getSelectedRow());
		    tmodel.removeRow(realIndex);
		    favouriteSongs.songs.removeElementAt(realIndex);
		    saveToStore();
		}
	    });

	addSong.addActionListener(new ActionListener() {
		public void actionPerformed(ActionEvent e) {
		    SongInformation song = songTable.getSelection();
		    //model.addElement(song);
		    tmodel.addRow(song.toVector());
		    favouriteSongs.songs.add(song);
		    saveToStore();
		}
	    });
     }

    private void saveToStore() {
	try {
	    /*
	    String userHome = System.getProperty("user.home");
	    Path storePath = FileSystems.getDefault().getPath(userHome, 
							      ".karaoke",
							      "favourites",
							      user);
	    File storeFile = storePath.toFile();
	    */

	    //favouriteSongs.saveTableToStore("/server/KARAOKE/favourites/" + user);
	    favouriteSongs.saveTableToStore(AllFavourites.FAVOURITES_DIR + user);

	    /*
	    File storeFile = new File("/server/KARAOKE/favourites/" + user);
	    FileOutputStream out = new FileOutputStream(storeFile); 
	    ObjectOutputStream os = new ObjectOutputStream(out);
	    os.writeObject(favouriteSongs.songs); 
	    os.flush(); 
	    out.close();
	    */
	} catch(Exception e) {
	    System.err.println("Can't save favourites file " + e.toString());
	}
    }


    /**
     * "play" a song by printing its file path to standard out.
     * Can be used in a pipeline this way
     */
    public void playSong() {
	/*
	SongInformation song = (SongInformation) list.getSelectedValue();
	if (song == null) {
	    return;
	}
	System.out.println(song.path.toString());
	*/
	String path = table.getModel().getValueAt(
			      table.convertRowIndexToModel(
							   table.getSelectedRow()), 3).toString();
	System.out.println(path);

	String SERVERIP = "192.168.1.110"; 
	int SERVERPORT = 13000;
	PrintWriter out;
	
	try {
	    InetAddress serverAddr = InetAddress.getByName(SERVERIP);
	    Socket socket = new Socket(serverAddr, SERVERPORT);
				 
	    //send the message to the server
	    out = new PrintWriter(
				  new BufferedWriter(
						     new OutputStreamWriter(socket.getOutputStream())), 
				  true);
	  
	    // Avoid println - on Windows it is \r\n
	    //out.print(song.path + "\n");
	    out.print(path + "\n");
	    out.flush();
	    socket.close();
				
	} catch (Exception e) {
	    System.err.println(e.toString());
	}

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



