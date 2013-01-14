#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' Expand .epub file into a folder
    .epub is actually a zip file, only contents under OEBPS/ are extracted.
    
    Another scritp epub2index can be called to generate index.html from toc.ncx
    
'''

import sys, os, os.path
import re, zipfile

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
        sub, fname = os.path.split(fn)
        if sub:
            if path:
                sub = os.path.join(path, sub)
            if not os.path.exists(sub):
                os.makedirs(sub)
        dat = ar.read(i)
        if sub:
            fname = os.path.join(sub, fname)
        elif path:
            fname = os.path.join(path, fname)
        with open(fname, 'w') as fp:
            fp.write(dat)
    ar.close()
    
if __name__ == '__main__':
    epub2html(*sys.argv[1:])
