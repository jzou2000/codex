#! /usr/bin/python

import pygtk
import gtk

class Blank:
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.show()

    def main(self):
        gtk.main()

if __name__ == '__main__':
    app = Blank()
    app.main()

