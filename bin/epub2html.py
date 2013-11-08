#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' Expand .epub file into a folder
    .epub is actually a zip file, only contents under OEBPS/ are extracted.
    After extraction, a frame-based index.html is created from toc.ncx.
    Original index.html is backup if it exists.

'''

import sys, os, os.path, codecs, re, zipfile
from lxml import etree as ET

class EIndex(object):
    ''' EIndex generate a frame-based index.html from epub expansion '''
    
    templIndex = u'''<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
  <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
  <title>{title}</title>
  <link rel="stylesheet" type="text/css" href="style.css" />
</head>

<frameset cols="25%,75%">
  <frame src="findex.html" name="LeftFrame">
  <frame src="{firstpage}" name="RightFrame">
</frameset>
</html>
'''
    templLeft = u'''<?xml version="1.0" encoding="utf-8" standalone="no"?>
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
    
    def __init__(self):
        self.has0 = False
        pass

    def parse_ncx(self):
        ''' parse ncx file to build self.nav '''
        try:
            et = ET.parse('toc.ncx')
            root = et.getroot()
            dns = ''    # default namespace
            if root.nsmap and root.nsmap.has_key(None):
                dns = '{%s}' % root.nsmap[None]
            tag = root.find('%sdocTitle/%stext' % (dns, dns))
            if tag is not None:
                self.title = tag.text
            nav = root.find(dns + 'navMap')
            if nav is not None:
                for i in nav:
                    tag = i.find('%snavLabel/%stext'%(dns,dns))
                    l = tag.text if tag is not None else ''
                    tag = i.find('%scontent' % dns)
                    s = tag.get('src') if tag is not None else ''
                    h = self.hlevel(s)
                    if l and s and h > 0:
                        self.nav.append({'label': l, 'href': s, 'level': h})
            return True
        except Exception as ex:
            print('parse_ncx: %s' % str(ex))
            return False
            
    def parse_files(self):
        pattern = r'(\d+|[a-z])\d+\.x?html$'
        flist = filter(lambda i: re.match(pattern, i, re.I), os.listdir('.'))
        flist.sort()
        for f in flist:
            t = self.title(f)
            h = self.hlevel(f)
            self.nav.append({ 'href': t, 'label': t, 'level': h })
    
    def parse(self):
        f = 'index.html'
        nf = self.backup(f)
        if nf:
            print('rename %s %s\n' % (f, nf))
        self.nav = []
        if not self.parse_ncx():
            self.parse_files()
        ci = [u'  <a class="ci ci{level}" href="{href}">{label}</a>'.format(**i) for i in self.nav]
        with codecs.open('findex.html', 'w', 'utf-8') as fp:
            fp.write(EIndex.templLeft.replace('ANCHORS', u'\n'.join(ci)))
        with codecs.open('index.html', 'w', encoding='utf8') as fp:
            fp.write(EIndex.templIndex.format(title=self.title, firstpage=self.nav[0]['href']))
    
    def hlevel(self, name):
        ''' detect head level according to the (x)html file name pattern '''
        pattern = r'(\d+|[a-z])(\d{2})\.x?html$'
        mat = re.match(pattern, name, re.I)
        if mat:
            si = mat.group(2)
            if si == '00':
                if not self.has0:
                    self.has0 = True
                return 1
            elif self.has0:
                return 2
            elif si == '01':
                return 1
            else:
                return 2
        else:
            return 0
        
    def title(self, url):
        ''' extract title from url '''
        try:
            with open(url) as fp:
                text = fp.read()
                et = ET.HTML(text)
            return et.xpath('//title')[0].text
        except Exception as ex:
            print('title(%s): %s' % (url, str(ex)))

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

def epub2html(epubName, path=None):
    ar = zipfile.ZipFile(epubName, 'r', zipfile.ZIP_DEFLATED)
    if path:
        if not os.path.exists(path):
            os.makedirs(path)
    pat = re.compile(r'^OEBPS\/')
    for i in ar.infolist():
        fn = i.filename
        if not re.match(pat, fn): continue
        fn = re.sub(pat, '', fn)
        if fn is None or len(fn) == 0: continue
        sub, fname = os.path.split(fn)
        if sub:
            if path:
                sub = os.path.join(path, sub)
            if not os.path.exists(sub):
                os.makedirs(sub)
        dat = ar.read(i)
        if len(fname) == 0 or len(dat) == 0: continue
        if sub:
            fname = os.path.join(sub, fname)
        elif path:
            fname = os.path.join(path, fname)
        print fname
        with open(fname, 'w') as fp:
            fp.write(dat)
    ar.close()
    if path:
        cwd = os.getcwd()
        os.chdir(path)
    app = EIndex()
    app.parse()
    if path:
        os.chdir(cwd)
    
if __name__ == '__main__':
    epub2html(*sys.argv[1:])

