#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
    A simple demo to show the basic usage of xpyb (xcb python bind)

    name convention
    xcb uses lower_case_and_underscore, while xpyb uses CamelCase for
    X protocol names (from XML), for python reserved word or numbers,
    prefix them with _ (e.g. _class, _1)

    xcb         Connection
                Cookie, VoidCookie
                Response, Error, Event
                Exception, ConnectE.., ExtensionE.., ProtocolE..
                Extension, ExtensionKey
                Request, Reply
                Struct, Union,

                connect
                popcount                -- count number of bits in bitmask
                type_pad                -- number of padding bytes for type
                wrap
                _add_core
                _add_ext
                _resize_obj

    conn        core                    xcb.xproto.xprotoExtension
                pref_screen             int

                disconnect
                flush
                generate_id
                get_file_descriptor
                get_maximum_request_length
                get_setup
                has_error
                prefetch_maximum_request_length
                wait_for_event
                poll_for_event

    core        conn
                first_error
                first_event
                key
                major_opcode

                128 X11 core protocols (e.g. CreateWindow)
                send_request

'''

import xcb
from xcb.xproto import *
from collections import deque

class Hello(object):
    def __init__(self, name):
        self.name = name
        self.conn = xcb.connect()
        self.xdpyinfo()

    def xdpyinfo(self):
        '''
    setup       bitmap_format_bit_order, bitmap_format_scanline_pad
                image_byte_order
                length
                max_keycode, min_keycode
                maximum_request_length
                motion_buffer_size
                pixmap_formats, pixmap_formats_len
                protocol_major_version, protocol_minor_version, release_number
                resource_id_base, resource_id_mask,
                roots, roots_len
                status, vendor, vendor_len

    screen[0]   conn.get_setup().roots[0]
                allowed_depths, allowed_depths_len
                backing_stores, save_unders
                black_pixel, white_pixel
                current_input_masks,
                height_in_millimeters, height_in_pixels
                width_in_millimeters, width_in_pixels
                max_installed_maps, min_installed_maps
                root, root_depth, root_visual, default_colormap
        '''
        self.setup = self.conn.get_setup()
        root = self.setup.roots[0]
        print '    root=0x%x' % root.root
        print '    size=%dx%d' % (root.width_in_pixels, root.height_in_pixels)
        print '    w/b=0x%x/0x%x' % (root.white_pixel, root.black_pixel)

    def terminate(self):
        self.conn.disconnect()
        self.conn = None

    def run(self):
        conn = self.conn
        x11 = conn.core
        root = conn.get_setup().roots[0]
        wid = conn.generate_id()
        print self.name + ' is running'
        print 'wid=0x%x' % wid
        atom_name = 'Hello 1'
        atom = self.get_atom(atom_name)
        print 'atom ' + atom_name + '=' + str(atom)
        x11.CreateWindow(0, wid, root.root,     # depth, id, parent
                0, 0, 640, 480, 0,              # x,y,w,h,bw
                WindowClass.InputOutput, 0,     # _class, visual
                CW.BackPixel|CW.EventMask,      # value_mask
                [ root.white_pixel,             # value_list
                  EventMask.ButtonPress|EventMask.Exposure|EventMask.KeyPress])
        x11.MapWindow(wid)
        conn.flush()
        self.cookie = deque([])
        self.atom = 1
        while True:
            try:
                event = conn.wait_for_event()
            except xcb.ConnectException, error:
                print 'Connect error'
                break
            except xcb.ProtocolException, error:
                print 'Protocol error'
                break
            except IOError:     # X connection broken, e.g. closed by WM
                break
            except IOError, error:
                print 'Unexcept error: (' + error.__class__.__name__ + ') ' + str(error)
                break

            e = event
            if isinstance(event, ExposeEvent):
                print 'ExposeEvent: %x (%d,%d) %dx%d count=%d' % (e.window, e.x, e.y, e.width, e.height, e.count)
            elif isinstance(event, ButtonPressEvent):
                print 'ButtonPressEvent: detail=%d root=%x event=%x (%d,%d) root(%d,%d) state=%d' % (e.detail, e.root, e.event,
                        e.event_x, e.event_y, e.root_x, e.root_y,
                        e.state)
                if e.detail == 3:
                    break
                for cookie in self.cookie:
#                    cookie = self.cookie.popleft()
                    reply = cookie.reply()
                    print 'atom name=' + str(reply.name.buf())
                self.cookie = deque([])
            elif isinstance(event, KeyPressEvent):
                print 'KeyPressEvent: detail=%d event=%x state=%d' % (
                        e.detail, e.event, e.state)
                self.cookie.append(self.get_atom_name_a(self.atom))
                self.atom += 1
            else:
                print 'Something ' + e.__class__.__name__

        self.terminate()

    def get_atom_name(self, atom):
        cookie = self.conn.core.GetAtomName(atom)
        reply = cookie.reply()
        return str(reply.name.buf())

    def get_atom_name_a(self, atom):
        return self.conn.core.GetAtomName(atom)

    def get_atom(self, name, only_if_exist=True):
        cookie = self.conn.core.InternAtom(only_if_exist, len(name), name)
        return cookie.reply().atom

    def get_atom_a(self, name, only_if_exist=True):
        return self.conn.core.InternAtom(only_if_exist, len(name), name)


if __name__ == '__main__':
    app = Hello('xpyb.hello')
    app.run()

