#! /usr/bin/python
# -*- coding: UTF-8 -*-

import sys, os, os.path, glob, codecs, re
import zipfile
from lxml import etree
from lxml import cssselect

class EbFrame:
    _frame = u'''<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
  <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
  <title>TITLE</title>
  <link rel="stylesheet" type="text/css" href="style.css" />
</head>

<frameset cols="25%,75%">
  <frame src="findex.html" name="LeftFrame">
  <frame src="FIRST" name="RightFrame">
</frameset>
</html>
'''
    _frame_left = u'''<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
  <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
  <base target="RightFrame"/>
  <style>
    a.ci { display: block; white-space: nowrap; }
    a.ci2 { margin-left: 2em; }
  </style>
</head>
<body>
ANCHORS
</body>
</html>
'''
    def __init__(self, fnindex = 'index.html'):
        self.index = fnindex
        with open(self.index) as fp:
            text = fp.read()
        self.root = etree.HTML(text)
        try:
            self.title = self.root.xpath('//head/title')[0].text
        except:
            self.title = ''

    def run(self):
        nf = self.backup(self.index)
        if nf:
            print "rename " + self.index + ' ' + nf
        anchors = self.root.xpath('//div[contains(@class,"ci")]')
        first = ''
        if anchors is not None or len(anchors) > 0:
            first = anchors[0].attrib['src']

        s = EbFrame._frame.replace('TITLE', self.title)
        s = s.replace('FIRST', first)
        with open(self.index, 'w') as fp:
            fp.write(s.encode('utf-8'))
        al = []
        for a in anchors:
            #print 'class=%s [%s]\n' % (a.attrib['class'], a.text)
            al.append(u'  <a class="%s" href="%s">%s</a>' %
                    (a.attrib['class'], a.attrib['src'], a.text))
        s = u'\n'.join(al)
        s = EbFrame._frame_left.replace('ANCHORS', s)
        f = 'findex.html'
        nf = self.backup(f)
        if nf:
            print('rename %s %s\n' % (f, nf))
        with open(f, 'w') as fp:
            fp.write(s.encode('utf-8'))

    def backup(self, f, nmax = 100):
        ''' Backup the file f, try to avoid overriding existing files.
            The rename rule, for example index.html to index-n.html
            where n = 0, 1, 2, .. upto 99 and fails
        '''
        if not os.path.exists(f):
            return None
        if nmax <= 0:
            nmax = 100
        (root, ext) = os.path.splitext(f)
        for i in range(nmax):
            s = '{0}-{1}{2}'.format(root, i, ext)
            if not os.path.exists(s):
                os.rename(f, s)
                return s
        return None

if __name__ == '__main__':
    ebf = EbFrame()
    ebf.run()

