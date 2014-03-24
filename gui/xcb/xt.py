#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
    A simple demo to show the basic usage of xpyb (xcb python bind)

    name convention
    xcb uses lower_case_and_underscore, while xpyb uses CamelCase for
    X protocol names (from XML), for python reserved word or numbers,
    prefix them with _ (e.g. _class, _1)

    xcb         Connection
    conn        core                    xcb.xproto.xprotoExtension
    core        conn
                128 X11 core protocols (e.g. CreateWindow)
                send_request

'''

import xcb
from xcb.xproto import *
from collections import deque


class Xt(object):
    def __init__(self, display, name=None):
        self.name = name
        self.conn = xcb.connect(display)
        self.setup = self.conn.get_setup()
        self.cookie = deque([])
        self._atom_byvalue = {}
        self._atom_byname = {}
        self.event_cb = {}
        self.error_cb = {}
        self.reply_cb = {}

    def terminate(self):
        self.conn.disconnect()
        self.conn = None
        self.setup = None
        self._atom_byname = None
        self._atom_byvalue = None

    def generate_id(self):
        return self.conn.generate_id()

    def screen(self, scr_num = 0):
        return self.setup.roots[scr_num]

    def flush(self):
        self.conn.flush()

    def run(self):
        try:
            while True:
                if not self.runIteration():
                    break
        except Exception as e:
            print 'xt.run exception: %s' % str(e)
            pass
        self.terminate()

    def runIteration(self):
        x11 = self.conn.core
        scr = self.setup.roots[0]
        try:
            event = self.conn.wait_for_event()
        except xcb.ConnectException as error:
            print 'Connect error'
            raise
        except xcb.ProtocolException as error:
            print 'Protocol error'
            raise
        except IOError:     # X connection broken
            raise

        if isinstance(event, ExposeEvent):
            print 'ExposeEvent: %x (%d,%d) %dx%d count=%d' % (
                    event.window,
                    event.x, event.y, event.width, event.height,
                    event.count)
        elif isinstance(event, ButtonPressEvent):
            print 'ButtonPressEvent: detail=%d event=%x (%d,%d) root=%x (%d,%d) state=%d' % (
                        event.detail,
                        event.event, event.event_x, event.event_y,
                        event.root, event.root_x, event.root_y,
                        event.state)
            if event.detail == 3:
                return False
            for cookie in self.cookie:
                reply = cookie.reply()
                print 'atom name=' + str(reply.name.buf())
            self.cookie = deque([])
        elif isinstance(event, KeyPressEvent):
            print 'KeyPressEvent: detail=%d event=%x state=%d' % (
                    event.detail, event.event, event.state)
        else:
            print 'Something ' + event.__class__.__name__

        return True

    def register_event_handle(self, name, cb):
        if name in self.event_cb:
            self.event_cb[name].append(cb)
        else:
            self.event_cb[name] = [cb]

    def atom(self, arg, only_if_exists = True):
        if arg is None:
            return None
        elif isinstance(arg, int):      # get name from value
            if arg in self._atom_byvalue: return self._atom_byvalue[arg]
            cookie = self.conn.core.GetAtomName(arg)
            reply = cookie.reply()
            name = str(reply.name.buf())
            self._atom_byvalue[arg] = name
            self._atom_byname[name] = arg
            return name
        elif isinstance(arg, str):      # get value from name
            if arg in self._atom_byname: return self._atom_byname[arg]
            cookie = self.conn.core.InternAtom(only_if_exists, len(arg), arg)
            atom = cookie.reply().atom
            if atom:
                self._atom_byvalue[atom] = arg
                self._atom_byname[arg] = atom
            return atom
        else:
            raise "BadValue"

class XtWindow(object):
    def __init__(self, parent = None,
                 x = 0, y = 0, width = 1, height = 1, depth = 0, **arg):
        if isinstance(parent, XtWindow):
            self.xt = parent.xt
            self.parent = parent
        elif isinstance(parent, Xt):
            self.xt = parent
            self.parent = None
        else:
            raise 'BadParent'
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.depth = depth
        self.borderw = 0
        self.wclass = WindowClass.InputOutput
        self.visual = 0
        self.id = 0 #arg['id']
        if not self.id:
            self.id = self.xt.generate_id()
        if self.parent:
            self.pid = self.parent.id
        else:
            self.pid = self.xt.screen().root

        mask = 0
        values = []
        mask = CW.BackPixel|CW.EventMask
        scr = self.xt.screen()
        values.append(scr.white_pixel)
        values.append(EventMask.ButtonPress|EventMask.Exposure|EventMask.KeyPress)
        self.xt.conn.core.CreateWindow(self.depth, self.id, self.pid,
                self.x, self.y, self.width, self.height, self.borderw,
                self.wclass, self.visual,
                mask, values)
        self.mapped = False

    def map(self):
        if not self.mapped:
            self.xt.conn.core.MapWindow(self.id)
            self.mapped = True

    def unmap(self):
        if self.mapped:
            self.xt.conn.core.UnmapWindow(self.id)
            self.mapped = False

class XcbApp(Xt):
    def __init__(self, name, display=None, arg = None):
        Xt.__init__(self, display, name)
        self.arg = dict(arg) if arg else {}
        self.cookie = deque([])
        self.prop = self.atom('ATOM')
        self.type = self.atom('type')
        print 'atoms: prop=%s type=%s' % (str(self.prop), str(self.type))

        scr = self.screen()
        self.win = XtWindow(self, width=640, height=480)
        self.win.map()
        self.flush()


if __name__ == '__main__':
    import sys, os
    import getopt
    import re
    copt, arg = getopt.getopt(sys.argv[1:], 'xd:p:t:f:', [
            'display=', 'prop=', 'type=', 'format=', 'hex'])
    opt = { 'display' : None, 'type': 'CARDINAL',
            'format': 32, 'hex': 0 }
    for n,v in copt:
        if n == '-d' or n == '--display':
            opt['display'] = v
        elif n == '-p' or n == '--prop':
            opt['prop'] = v
        elif n == '-t' or n == '--type':
            opt['type'] = v
        elif n == '-f' or n == '--format':
            opt['format'] = int(v)
        elif n == '-x' or n == '--hex':
            opt['hex'] = 1
        else:
            print('{0}: {1}'.format(n, v))
    for i,v in opt.items():
        print 'opt[{0}]={1}'.format(i,v)

    # now parse and decode value list
    vlist = []
    for i in arg:
        b = 10
        if opt['hex'] or re.match('0x[\da-f]+', i, re.I) or not re.match('\d+$', i):
            b = 16
        try:
            v = int(i, b)
            vlist.append(v)
        except Exception:
            print 'bad data: {0}'.format(i)
    opt['values'] = vlist
    print 'values={0}'.format(opt['values'])

    if len(vlist) > 0:
        n = len(vlist)

    #opt['display'] = 'wario:0'
    #xt = Xt(opt.get('display'))
    app = XcbApp('xpyb.SendEvent', opt.get('display'), opt)
    app.run()

