#include <gtk/gtk.h>

int main(int argc, char* argv[])
{
    GtkWidget *window;

    gtk_init(&argc, &argv);     // initialize gtk toolkit

    // build widget tree
    window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(window), "Blank");

    // show widget tree and fall into gtk event loop
    gtk_widget_show(window);
    gtk_main();

    return 0;
}

