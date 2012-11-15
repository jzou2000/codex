#! /usr/bin/env python

'''DemoDialogApp

This demo shows the different usage of modal and modeless (nonmodal) dialogs.

The two types of dialogs difference
                modal             modeless
create flags    DIALOG_MODAL
show            run()             show()
destroy         implicit in run   explicit

Class hiearchy
        gtk.Dialog
          MyDialog               shows common work in dialog
            DemoModal            shows a customized button
            DemoModeless         shows response & destroy

'''

import pygtk
pygtk.require('2.0')
import gtk

class DemoDialogApp(gtk.Window):

    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title(self.__class__.__name__)
        self.set_border_width(10)
        self.set_size_request(300, 200)
        self.connect('destroy', self.on_destroy)
        self.connect('delete-event', self.on_delete_event)
        
        vbox = gtk.VBox()        #homogenous, spacing
        
        # build a button to create/show a modal dialog
        self.pb_modal = gtk.Button('Modal')
        self.pb_modal.connect('clicked', self.on_modal, None)
        vbox.pack_start(self.pb_modal) # expand,fill,padding
        
        # build a button to create/show a modeless dialog
        self.pb_modeless = gtk.Button('Modeless')
        self.pb_modeless.connect('clicked', self.on_modeless, None)
        vbox.pack_start(self.pb_modeless) # expand,fill,padding
        
        self.add(vbox)
        self.show_all()
        
    def run(self):
        gtk.main()
        
    def on_delete_event(self, widget, event, data = None):
        return False
        
    def on_destroy(self, widget, data = None):
        gtk.main_quit()
        
    def on_modal(self, widget, data = None):
        button = gtk.Button('OK')
        button.connect('clicked', self.on_modal_ok)
        dlg = DemoModal(title='Modal Demo', parent=self,
                buttons = ('Customized', 1,
                           gtk.STOCK_OK, gtk.RESPONSE_OK,
                           gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        dlg.set_size_request(500, 300)
        # Modal dialog use method run() to show and get result from return
        #   gtk_dialog_run() is just a convenient way to
        #   connect the signal 'response' and return its data
        result = dlg.run()
        dlg.destroy()
        print('on_modal result=' + str(result))

    def on_modal_ok(self, widget, data=None):
        print('on_modal_ok')
        gtk.main_quit()
        
    def on_modeless(self, widget, data = None):
        dlg = DemoModeless(title='Modeless Demo', parent=self,
                buttons = (gtk.STOCK_OK, gtk.RESPONSE_OK,
                           gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        # Modeless dialog use method show() to show as a normal window
        dlg.show()
        print('on_modeless')

class MyDialog(gtk.Dialog):
    ''' Common part for dialogs
        It is used for tracing create/destroy of dialogs in this demo.
    '''
    def __init__(self, title=None, parent=None, flags=0, buttons=None):
        flags |= gtk.DIALOG_DESTROY_WITH_PARENT
        gtk.Dialog.__init__(self, title, parent, flags, buttons)
        print('MyDialog created: {}'.format(id(self)))
        self.connect('destroy', self.on_destroy)
        # followings are just for demonstrating
        self.set_size_request(200, 200)
        label = gtk.Label('Dialogs are groovy')
        self.vbox.pack_start(label)
        self.vbox.show_all()
    def on_destroy(self, widget, data=None):
        print('MyDialog distroyed: {}'.format(id(self)))

class DemoModal(MyDialog):
    def __init__(self, title=None, parent=None, flags=0, buttons=None):
        flags |= gtk.DIALOG_MODAL
        MyDialog.__init__(self, title, parent, flags, buttons)

class DemoModeless(MyDialog):
    def __init__(self, title=None, parent=None, flags=0, buttons=None):
        flags &= ~gtk.DIALOG_MODAL
        MyDialog.__init__(self, title, parent, flags, buttons)
        # gtk_dialog_run() does the same work except destroying dialog
        self.connect('response', self.on_response)
    def on_response(self, widget, data =None):
        print('response of Modeless.{} self={} response={}'.format(
                id(widget), id(self), data))
        widget.destroy()


if __name__ == '__main__':
    app = DemoDialogApp()
    app.run()

