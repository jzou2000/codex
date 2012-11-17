#! /usr/bin/env python

''' A simple example that shows running an application in multiple displays.
    The application is reusing DemoDialogApp from demodialog.py
'''
import pygtk
pygtk.require('2.0')
import gtk


from demodialog import *

dpy = gtk.gdk.Display('wario:0')
scn = dpy.get_default_screen()

w1 = DemoDialogApp('local display')
w2 = DemoDialogApp('remote display')
w2.set_screen(scn)

gtk.main()

