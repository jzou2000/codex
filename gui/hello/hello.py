#! /usr/bin/python

# initialize toolkit
import pygtk
pygtk.require('2.0')
import gtk

class Hello(gtk.Window):
    def __init__(self, title):
        ''' build GUI '''
        gtk.Window.__init__(self)
        # other attributes, e.g. title, border, default-size, etc
        self.set_title('%s: %s' % (self.__class__.__name__, title))

        # build GUI: create, connect-signal, pack
        self.button = gtk.Button('Hello world')
        self.button.connect('clicked', self.on_hello_clicked)
        self.add(self.button)

        # other signals
        self.connect('destroy', self.on_destroy)
        self.connect('delete-event', self.on_delete_event)

        # show GUI
        self.set_size_request(200, 100)
        self.show_all()

    def run(self):
        ''' toolkit framework event-loop '''
        gtk.main()

    def on_destroy(self, widget, data=None):
        ''' sample of signal callback '''
        print('on_destroy')
        gtk.main_quit()

    def on_delete_event(self, widget, event, data=None):
        ''' sample of event callback '''
        print('on_delete_event')
        return False    # keep event bubbling

    def on_hello_clicked(self, widget, data=None):
        ''' sample of control signal callback '''
        print('on_hello_clicked')

# start of application of unit test
if __name__ == '__main__':
    app = Hello('Demo')
    app.run()

