#include <gtk/gtk.h>

static void cb_destroy(GtkWidget*, gpointer);
static gboolean cb_delete_event(GtkWidget*, GdkEvent*, gpointer);

// this is just an example
// client data passed to signal/event callback can be anything
typedef struct {
    char* msg;
} ClientData;

int main(int argc, char* argv[])
{
    GtkWidget *window;
    GtkWidget *label;
    ClientData data = { "data-passed-to-signal" };

    gtk_init(&argc, &argv);     // initialize gtk toolkit

    // build GUI
    window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(window), "Hello World!");
    gtk_container_set_border_width(GTK_CONTAINER(window), 10);
    gtk_widget_set_size_request(window, 200, 100);

    label = gtk_label_new("Hello world");
    gtk_container_add(GTK_CONTAINER(window), label);

    // connect signals and event (if applicable)
    g_signal_connect(G_OBJECT(window), "destroy",
                G_CALLBACK(cb_destroy), &data);
    g_signal_connect(G_OBJECT(window), "delete-event",
                G_CALLBACK(cb_delete_event), NULL);

    // show widgets tree and fall into event loop
    gtk_widget_show_all(window);
    gtk_main();

    return 0;
}

static void
cb_destroy(GtkWidget *widget, gpointer client_data)
{
    ClientData *pdata = (ClientData*) client_data;
    g_print("destroy signal: %s\n", pdata ? pdata->msg : "");
    gtk_main_quit();    // break the current event loop
}

static gboolean
cb_delete_event(GtkWidget *widget, GdkEvent *event, gpointer client_data)
{
    g_print("Delete-event\n");
    sleep(1);           // let you see clearly the callback sequence

    return FALSE;       // continue event-process-chain
    // default delete-event-process on window is to emit "destroy" signal
}

