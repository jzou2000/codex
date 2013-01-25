#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import sys, os, os.path, re, codecs
from lxml import etree
from lxml.cssselect import CSSSelector

class MyPage(object):
    pattern_charset = re.compile(r'charset=(gb[-_0-9]+)', re.IGNORECASE)
    
    def __init__(self, fname):
        self.fname = fname
        encoding = 'utf8'
        with open(fname) as fp:
            self.raw_text = fp.read()
        match = MyPage.pattern_charset.search(self.raw_text)
        if match:
            self.encoding = match.group(1)
            v = unicode(self.raw_text, 'gb18030')
            self.text = MyPage.pattern_charset.sub('charset=UTF-8', v, 1)
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
    
    def strip_br(self, tag):
        p = re.compile(r'<br\s*\/?>', re.I)
        txt = p.split(etree.tounicode(tag, pretty_print=True))
        for i,t in enumerate(txt):
            t = t.strip()
            n = len(t)
            print '%d: %2d [%s]' % (i+1, n, t)
        print 'common_width=%d' % common_width(txt)
        return ''  #'\n'.join(txt)

def common_width(txt):
    tnc = {}
    for t in txt:
        n = len(t)
        if n in tnc:
            tnc[n] = tnc[n] + 1
        else:
            tnc[n] = 1
        #print ' %d cnt=%d [%s]' % (n, tnc[n], t)
    nmax = max(tnc.values())
    #print 'common_width()=%d'%nmax
    for t in tnc:
        #print 'n=%d count=%d' % (t, tnc[t])
        pass
    for t in tnc:
        if tnc[t] == nmax:
            return t

def get_arg(n, default):
    try:
        return sys.argv[n]
    except:
        return default

def p0(page, c):
    return page.show_tree(c)

def p1(page, c):
    return page.text_only(c)

def p2(page, c):
    return '%-40s %s' % (c.text.strip(), c.get('href'))

def p3(page, c):
    #return etree.tounicode(c, pretty_print=True)
    #return p1(page,c)
    return page.strip_br(c)

testcase = [
    [ 'ty.html',    '//td[@width="702"]/p[1]' , p1 ],
    [ 'tyi.html',   '//td[@width="702"]//div[@align="center"]//a', p2 ],
    [ 'sample-1.html', '//*[@id="body"]/p[@class="en"]', p3 ],
    [ 'sample-1.html', '//*[@id="body"]/p[@class="cn"]', p3 ],
]

if __name__ == '__main__':
    tc = testcase[int(get_arg(1, 1)) - 1]
    fname = tc[0]
    xpath = tc[1]
    page = MyPage(fname)
    tags = page.xpath(xpath)
    if not tags:
        print 'Not found'
    else:
        for i,c in enumerate(tags):
            print '%s %d' % ('-'*40, i+1)
            print tc[2](page, c)
