#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
'''
    A chat client that demonstrates python usage in the fields:
    1. simple pygtk gui - TextView, paned, button
    2. simple socket client
    3. gobject.io_add_watch
    
    usage: chat.py name server
    
            name        any string used to identify this client
            server      host:port, a chat server receives connections
                        and echo input to all clients
'''

import pygtk
pygtk.require('2.0')
import gtk, gobject
import sys, os, re, socket


class Chatter(object):
    ''' A chatter client '''

    DEFAULT_PORT = 9988

    def __init__(self, name = None, server = None):
        self.name = name or 'Noname'
        self.server = server or 'localhost'
        self.io_id = None
        self.sock = None
        self.build_gui()
        self.connect()
    
    def build_gui(self):
        self.gui = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.gui.set_title('Chatter - ' + self.name)
        self.gui.set_border_width(10)
        self.gui.set_size_request(400, 300)
        
        self.pane = gtk.VPaned()
        
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.text_history = gtk.TextView()
        self.text_history.set_editable(False)
        sw.add(self.text_history)
        self.pane.add1(sw)
        
        self.btn_send = gtk.Button('Send')
        self.btn_send.connect('clicked', self.on_send_clicked)
        self.enter_to_send = gtk.CheckButton('Enter To Send')
        self.enter_to_send.connect('toggled', self.on_enter_to_send)
        vbox = gtk.VBox(False, False)
        vbox.pack_start(self.btn_send, False, True, 0)
        vbox.pack_start(self.enter_to_send, False, True, 0)
        
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.text_input = gtk.TextView()
        sw.add(self.text_input)

        hbox = gtk.HBox(False, False)
        hbox.pack_end(vbox, False, False, 5)
        hbox.pack_end(sw, True, True, 1)
        
        self.pane.add2(hbox)
        self.pane.show_all()
        self.gui.add(self.pane)
        self.gui.show()
        self.gui.connect('destroy', self.on_destroy)
        
    def on_destroy(self, widget, data = None):
        try:
            if self.io_id:
                gobject.remove_source(self.io_id)
                self.io_id = None
            if self.sock:
                self.sock.close()
        except Exception as ex:
            print('on_destroy: %s' % str(ex))
        gtk.main_quit()

    def on_enter_to_send(self, widget, data = None):
        self.btn_send.set_sensitive(not self.enter_to_send.get_active())
    
    def on_send_clicked(self, widget, data = None):
        self.send_msg()
        
    def send_msg(self):
        ''' get text from input field and clear it,
            send to the server, append to the history in the same time.
        '''
        tb = self.text_input.get_buffer()
        msg = tb.props.text
        tb.set_text('')
        if self.sock:
            self.sock.send(msg)
            self.append_msg(msg, True)
        else:
            self.append_msg('Not connect yet', True)

    def disconnect(self):
        ''' disconnct from the server, remove from the monitoring list '''
        try:
            if self.io_id:
                gobject.source_remove(self.io_id)
                self.io_id = None
            if self.sock:
                self.sock.close()
                self.sock = None
        except: pass
        
    def connect(self):
        ''' connect to the server and add to io monitor list '''
        self.disconnect()
        try:
            m = re.match(r'(.*?)(:(.+))?$', self.server)
            if m:
                host = m.group(1)
                port = m.group(3) or Chatter.DEFAULT_PORT
                print('connect to (%s:%d)' % (host, int(port)))
            else:
                print('bad format: server=%s', self.server)
                raise Exception('bad format')
            self.sock = socket.create_connection((host, port))
            self.io_id = gobject.io_add_watch(self.sock.fileno(),
                gobject.IO_IN|gobject.IO_HUP|gobject.IO_ERR, self.on_msg_received)
        except Exception as ex:
            print('create_connect(%s) failed: %s' % (self.server, str(ex)))
            if self.sock:
                self.sock.close()
                self.sock = None
    
    def on_msg_received(self, source, condition):
        ''' callback of io monitor, called when data is received, hang-up or error '''
        if condition == gobject.IO_IN:
            try:
                msg = self.sock.recv(4096)
            except Exception as ex:
                msg = 'Fail to readline: %s' % str(ex)
                self.disconnect()
        else:
            if condition == gobject.IO_HUP:
                msg = 'IO_HUP'
            elif condition == gobject.IO_ERR:
                msg = 'IO_HUP'
            else:
                msg = 'Unknown'
            self.disconnect()
        self.append_msg(msg)
        return self.sock is not None
    
    def append_msg(self, msg, from_myself = False):
        ''' append text to history, including received or sent '''
        tb = self.text_history.get_buffer()
        iter = tb.get_end_iter()
        tb.insert(iter, msg)
        
if __name__ == '__main__':
    n = len(sys.argv)
    myname = sys.argv[1] if n > 1 else 'me'
    server = sys.argv[2] if n > 1 else 'localhost'
    app = Chatter(myname, server)
    gtk.main()

