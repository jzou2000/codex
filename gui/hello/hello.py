#! /usr/bin/python

import pygtk
pygtk.require('2.0')
import gtk

class Hello(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title(self.__class__.__name__)
        self.set_border_width(10)

        self.label = gtk.Button('Hello world')
        self.label.connect('clicked', self.on_hello, None)
        self.add(self.label)

        self.connect('destroy', self.on_destroy)
        self.connect('delete-event', self.on_delete_event)

        self.show_all()

    def on_destroy(self, widget, data=None):
        print('on_destroy')
        gtk.main_quit()

    def on_delete_event(self, widget, event, data=None):
        print('on_delete_event')
        return False

    def on_hello(self, widget, data=None):
        print('on_hello')

    def main(self):
        gtk.main()

if __name__ == '__main__':
    app = Hello()
    app.main()

