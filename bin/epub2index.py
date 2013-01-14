#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, os.path, stat, glob, getopt, codecs
import re, shutil, uuid, json, zipfile
from bs4 import BeautifulSoup
from lxml import etree as ET

class EIndex(object):
    ''' EIndex generate index.html from epub '''
    
    templHtml = u'''<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
  <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
  <title>{title}</title>
  <link rel="stylesheet" type="text/css" href="style.css" />
  <!--<script src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.3/jquery-ui.min.js"></script>-->
  <script src="/lib/jquery.js"></script>
  <script type="text/javascript">{js}
  </script>
</head>

<body>
<div id="index"> <div>{content}</div> </div>
<div id="content-wrapper">
  <h1>{title}</h1>
  <div id="content"> </div>
</div>
</body>
</html>
'''
    templJS = u'''
$(document).ready(function() {
    $('.ci').click(function() {
        npage($(this).attr("src"))
    });
    $('.ci:first-of-type').click();
});
function npage(href)
{
    $.get(href, function(data) {
            body = $('body', data);
            body.find('[src]').each(function(){
                src = $(this).attr('src');
                $(this).attr('src', src);
                });
            $('#content').html(body).scrollTop();
            }, 'xml');
    $('#index').hide(10).delay(200).show(10);
}
'''
    templCSS = u'''
body { background: white; margin: 1em 1em; }
pre {
  border-top: thin solid black;
  border-bottom: thin solid black;
  padding: 0.6cm 2px;
}
div.box { margin: 1em; padding: 1em; border: thin solid black; }
div#book-cover { width: 600px; height: 800px; padding: 16px; text-align: center; }
div#book-cover-title { font-size: 64px; margin: 5cm 0px 1cm 0px; }
div#book-cover-title2 { font-size: 18px; margin: 0px 0px 1cm 0px; }
div#book-cover-author { font-size: 32px; margin: 1cm 0px; }
div#book-cover-other { font-size: 16px; margin: 1cm 0px; }
#cover-image { position: relative; }
#cover-image img { display: block; margin: 2px auto; -width: 96%; }

#index {
    position: fixed;
    max-width: 50px;
    max-height: 80%;
    background: skyblue;
    padding: 10px;
    overflow: hidden;
}
#index>div { max-width: 1px; visibility: hidden; }
#index:hover>div { max-width: none; visibility: visible; }
#index:hover {
    max-width: 40%;
    overflow: auto;
    border: thin solid black;
}
#index div.ci1 { margin-left: 0em; }
#index div.ci2 { margin-left: 2em; }

#content-wrapper {
    margin-left: 50px;
}
'''
    
    def __init__(self):
        self.has0 = False
        pass

    def parse_ncx(self):
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
            t = self.get_title(f)
            h = self.hlevel(f)
            self.nav.append({ 'href': t, 'label': t, 'level': h })
    
    def parse(self):
        self.nav = []
        if not self.parse_ncx():
            self.parse_files()
        ci = []
        for i in self.nav:
            ci.append(u'<div class="ci{level} ci" src="{href}">{label}</div>'.format(**i))
        s = '\n'.join(ci)
        #print s
        with codecs.open('index.html', 'w', encoding='utf8') as fp:
            sc = EIndex.templHtml.format(title=self.title, content=s, js=EIndex.templJS)
            fp.write(sc)
        with codecs.open('style.css', 'w', encoding='utf8') as fp:
            sc = EIndex.templCSS
            fp.write(sc)
    
    def hlevel(self, name):
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
        
    def get_title(self, url):
        try:
            with open(url) as fp:
                bs = BeautifulSoup(fp)
            t = bs.find('title')
            return t.string if t else None
        except Exception as ex:
            print('get_title(%s): %s' % (url, str(ex)))


def main():
    app = EIndex()
    app.parse()

if __name__ == '__main__':
    main()

