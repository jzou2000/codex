#include <gtk/gtk.h>

static gboolean cb_delete_event(GtkWidget*, GdkEvent*, gpointer);
static void cb_destroy(GtkWidget*, gpointer);
static void cb_modal(GtkWidget*, gpointer);
static void cb_modeless(GtkWidget*, gpointer);
static void cb_modeless_response(GtkWidget*, gpointer);
static GtkWidget* build_dialog(GtkWidget*, const char*, const char*);


int main(int argc, char* argv[])
{
    GtkWidget *window;
    GtkWidget *vbox, *btn_modal, *btn_modeless;

    setbuf(stdout, NULL);
    gtk_init(&argc, &argv);     // initialize gtk toolkit

    // build widget tree
    window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(window), "DemoDialog");
    gtk_widget_set_size_request(window, 500, 400);
    g_print("window=%p\n", window);

    // build GUI - widget tree
    vbox = gtk_vbox_new(TRUE, 5);
    btn_modal = gtk_button_new_with_label("Modal Dialog");
    g_print("btn_modal=%p\n", btn_modal);
    gtk_box_pack_start_defaults(GTK_BOX(vbox), btn_modal);
    btn_modeless = gtk_button_new_with_label("Modeless Dialog");
    g_print("btn_modeless=%p\n", btn_modeless);
    gtk_box_pack_start_defaults(GTK_BOX(vbox), btn_modeless);
    gtk_container_add(GTK_CONTAINER(window), vbox);

    // connect signals
    g_signal_connect(G_OBJECT(window), "delete-event",
            G_CALLBACK(cb_delete_event), NULL);
    g_signal_connect(G_OBJECT(window), "destroy",
            G_CALLBACK(cb_destroy), NULL);
    g_signal_connect(G_OBJECT(btn_modal), "clicked",
            G_CALLBACK(cb_modal), window);
    g_signal_connect(G_OBJECT(btn_modeless), "clicked",
            G_CALLBACK(cb_modeless), window);

    // show widget tree and fall into gtk event loop
    gtk_widget_show_all(window);
    gtk_main();

    return 0;
}

static gboolean
cb_delete_event(GtkWidget *widget, GdkEvent* event, gpointer data)
{
    return FALSE;
}
static void
cb_destroy(GtkWidget *widget, gpointer data)
{
    gtk_main_quit();
}


static void
cb_modal(GtkWidget *widget, gpointer data)
{
    int rc;
    GtkWidget *self = GTK_WIDGET(data);
    GtkWidget *dlg = build_dialog(self, "ModalDialog",
            "This is a modal dialog");
    rc = gtk_dialog_run(GTK_DIALOG(dlg));   // show/loop/hide
    printf("gtk_dialog_run=%d\n", rc);
    gtk_widget_destroy(dlg);
}
static void
cb_modeless(GtkWidget *widget, gpointer data)
{
    GtkWidget *parent = GTK_WIDGET(data);
    GtkWidget *dlg = build_dialog(parent, "ModelessDialog",
            "This is a modeless dialog");
    g_print("widget=%p parent=%p dlg=%p\n", widget, parent, dlg);

    /* a modeless dialog has to do all jobs of gtk_dialog_run() except two:
     *     1. set GTK_DIALOG_MODAL
     *     2. invoke another gtk_main_loop() (thus not call gtk_main_quit())
     */
    g_signal_connect(G_OBJECT(dlg), "response",
            G_CALLBACK(cb_modeless_response), dlg);
    gtk_widget_show_all(dlg);
}
static void
cb_modeless_response(GtkWidget *widget, gpointer data)
{
    int response = (int) data;
    g_print("widget=%p data=%d\n", widget, response);
    gtk_widget_destroy(widget);
}
/*******************************************************************************
  Build a dialog, which is simply a toplevel window divided into two parts
      vbox                functional area (container for child widgets)
      action_area         container for action buttons (emit "response")
  in addition, the convenient function also does these for you
      1. set transient_for parent
      2. set destroy_with_parent property
      3. set type hint to GDK_WINDOW_TYPE_HINT_DIALOG
      4. bind signal "response"

  There is not much difference between modal and modeless dialogs:
      1. set GTK_DIALOG_MODAL in attribute (impletely set by gtk_dialog_run)
      2. call gtk_dialog_run() for modal dialog

  In fact, gtk_dialog_run() is just a convenient function that implements:
      1. set GTK_DIALOG_MODAL in attribute
      2. sets its own "response" handle to colloect response value
      3. show dialog and invoke a new level gtk_main_loop()
      4. save response and gtk_main_quit() in response handle
      5. hide dialog and return response

*******************************************************************************/
static GtkWidget*
build_dialog(GtkWidget* parent, const char* title, const char* msg)
{
    GtkWidget *dlg, *label;

    dlg = gtk_dialog_new_with_buttons(title, GTK_WINDOW(parent),
            GTK_DIALOG_DESTROY_WITH_PARENT,// |GTK_DIALOG_MODAL for modals
            // buttons and their responses
            GTK_STOCK_OK, GTK_RESPONSE_OK,
            GTK_STOCK_CANCEL, GTK_RESPONSE_CANCEL,
            NULL);

    label = gtk_label_new(msg);
    gtk_box_pack_start_defaults(GTK_BOX(GTK_DIALOG(dlg)->vbox), label);
    gtk_widget_set_size_request(GTK_WIDGET(dlg), 300, 200);

    return dlg;
}

