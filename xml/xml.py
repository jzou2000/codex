#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import sys, os, os.path, re, codecs
from lxml import etree
#from bs4 import BeautifulSoup as BS

class MyPage(object):
    gbdec = codecs.getdecoder('gb18030')
    pattern_charset = re.compile(r'charset=(gb[-_0-9]+)', re.IGNORECASE)
    
    def __init__(self, fname):
        self.fname = fname
        encoding = 'utf8'
        with open(fname) as fp:
            self.raw_text = fp.read()
        match = MyPage.pattern_charset.search(self.raw_text)
        if match:
            self.encoding = match.group(1)
            #print('encoding=%s' % self.encoding)
            #v = MyPage.gbdec(self.raw_text)
            #self.text = MyPage.pattern_charset.sub('charset=UTF-8', v[0], 1)
            v = unicode(self.raw_text, 'gb18030')
            self.text = MyPage.pattern_charset.sub('charset=UTF-8', v, 1)
            #print unicode(self.text)
        else:
            self.text = self.raw_text
        self.root = etree.HTML(self.text)
    
    def tostring(self, elem=None, pretty_print=True, method='html'):
        if elem is None:
            elem = self.root
        return etree.tostring(elem, pretty_print = pretty_print, method = method, encoding='utf8')

    def xpath(self, path):    
        return self.root.xpath(path)
    
    def text_only(self, elem = None, withtail = False):
        if elem is None:
            elem = self.root
        a = []
        if elem.text:
            a.append(elem.text.strip())
        for c in elem:
            cs = self.text_only(c, True)
            if cs:
                a.append(cs)
        if elem.tag == 'br':
            a.append('\n')
        if withtail and elem.tail:
            a.append(elem.tail.strip())
        if a:
            return ' '.join(a)
        else:
            return ''

    def show_tree(self, tag, depth=None, seq=None, indent=2):
        if depth:
            sleading = ' ' * (depth * indent)
        else:
            sleading = ''
            depth = 0
        a = []
        if seq:
            a.append('%s%d:<%s>' % (sleading, seq, tag.tag))
        else:
            a.append('%s<%s>' % (sleading, tag.tag))
        if tag.text:
            a.append('%s    text: %s' % (sleading, tag.text.strip()))
        if tag.tail:
            a.append('%s    tail: %s' % (sleading, tag.tail.strip()))
        depth += 1
        i = 1
        for c in tag:
            s = self.show_tree(c, depth, i, indent)
            if s:
                a.append(s)
            i+=1
        if a:
            return '\n'.join(a)
        else:
            return ''


def get_arg(n, default):
    try:
        return sys.argv[n]
    except:
        return default

if __name__ == '__main__':
    #fname = get_arg(1, 'ty.html')
    #xpath = get_arg(2, '//td[@width="702"]/p[1]')
    fname = get_arg(1, 'tyi.html')
    xpath = get_arg(2, '//td[@width="702"]//div[@align="center"]//a')
    page = MyPage(fname)
    tags = page.xpath(xpath)
    if not tags:
        print 'Not found'
    else:
        for i,c in enumerate(tags):
            #print '%s %d' % ('-'*40, i+1)
            #print page.show_tree(c)
            #print page.text_only(c)
            print '%-40s %s' % (c.text.strip(), c.get('href'))
#    result = page.tostring(tags[0], method='xml')
#    print(result)
