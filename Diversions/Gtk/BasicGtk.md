
##  Basic Gtk 


Gtk is a fairly standard GUI toolkit. Simple programs
      are described in many tutorials such as [
	First programs in GTK+
      ](http://zetcode.com/tutorials/gtktutorial/firstprograms/) Refer to such tutorials for the basics in Gtk programming.


We just include the following example without explanation
      which uses three child widgets, two buttons and one label. 
      The label will hold an integer number. 
      The buttons will increase or decrease this number.

```

	#include <gtk/gtk.h>

	gint count = 0;
	char buf[5];

	void increase(GtkWidget *widget, gpointer label)
	{
  	    count++;

	    sprintf(buf, "%d", count);
	    gtk_label_set_text(GTK_LABEL(label), buf);
	}

	void decrease(GtkWidget *widget, gpointer label)
	{
	    count--;

	    sprintf(buf, "%d", count);
	    gtk_label_set_text(GTK_LABEL(label), buf);
	}

	int main(int argc, char** argv) {

	    GtkWidget *label;
	    GtkWidget *window;
	    GtkWidget *frame;
	    GtkWidget *plus;
	    GtkWidget *minus;

	    gtk_init(&argc, &argv);

	    window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
	    gtk_window_set_position(GTK_WINDOW(window), GTK_WIN_POS_CENTER);
	    gtk_window_set_default_size(GTK_WINDOW(window), 250, 180);
	    gtk_window_set_title(GTK_WINDOW(window), "+-");

	    frame = gtk_fixed_new();
	    gtk_container_add(GTK_CONTAINER(window), frame);

	    plus = gtk_button_new_with_label("+");
	    gtk_widget_set_size_request(plus, 80, 35);
	    gtk_fixed_put(GTK_FIXED(frame), plus, 50, 20);

	    minus = gtk_button_new_with_label("-");
	    gtk_widget_set_size_request(minus, 80, 35);
	    gtk_fixed_put(GTK_FIXED(frame), minus, 50, 80);

	    label = gtk_label_new("0");
	    gtk_fixed_put(GTK_FIXED(frame), label, 190, 58); 

	    gtk_widget_show_all(window);

	    g_signal_connect(window, "destroy",
	    G_CALLBACK (gtk_main_quit), NULL);

	    g_signal_connect(plus, "clicked", 
	    G_CALLBACK(increase), label);

	    g_signal_connect(minus, "clicked", 
	    G_CALLBACK(decrease), label);

	    gtk_main();

	    return 0;
	}
      
```


Gtk, like every other GUI toolkit, has a large number of widgets.
      These are listed in the [
	GTK+ 3 Reference Manual
      ](https://developer.gnome.org/gtk3/3.0/) .
      This includes the widget [
	GtkImage
      ](https://developer.gnome.org/gtk3/3.0/GtkImage.html) .
      As would be expected from the name, it can take a set of pixels from somewhere
      and build them into an image which can be displayed.


The following example is from [
	CS 23 Software Design and Implementation Lecture notes GTK+ Programming
      ](http://www.cs.dartmouth.edu/~xy/cs23/gtk.html) and shows an image loaded from a file:

```

#include <gtk/gtk.h>

int main( int argc, char *argv[])
{
	GtkWidget *window, *image;

	gtk_init(&argc, &argv);

	window = gtk_window_new(GTK_WINDOW_TOPLEVEL);

	gtk_window_set_position(GTK_WINDOW(window), GTK_WIN_POS_CENTER);
	gtk_window_set_default_size(GTK_WINDOW(window), 230, 150);
	gtk_window_set_title(GTK_WINDOW(window), "Image");
	gtk_window_set_resizable(GTK_WINDOW(window), FALSE);

	gtk_container_set_border_width(GTK_CONTAINER(window), 2);

	image = gtk_image_new_from_file("pic/60cm.gif");
	gtk_container_add(GTK_CONTAINER(window), image);

	g_signal_connect(G_OBJECT(window), "destroy", G_CALLBACK(gtk_main_quit), NULL);
	gtk_widget_show_all(window);
	gtk_main();

	return 0;
}
      
```
