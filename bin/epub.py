#! /usr/bin/python
# -*- coding: UTF-8 -*-

import sys, os, os.path, stat, glob, getopt, time, random, codecs
import re, shutil, uuid, json, zipfile
import xml.sax.saxutils
import urllib2, urlparse
from lxml import etree
from lxml import cssselect

'''
TODO - download epub cover from google, amazone and open library

log from calibre:

Starting cover download for: PyGTK 2.0 Tutorial 
Query: PyGTK 2.0 Tutorial [u'Unknown'] {} 

****************************** Google Covers ****************************** 
Request extra headers: [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/0.2.153.1 Safari/525.19')] 
Failed to download valid cover 
Took 0.340224981308 seconds 
No cached cover found, running identify
No cover found 

******************************************************************************** 

****************************** Amazon.com Covers ****************************** 
Request extra headers: [('User-agent', 'Mozilla/5.0 (Windows NT 5.2; rv:2.0.1) Gecko/20100101 Firefox/4.0.1')] 
Failed to download valid cover 
Took 0.911316871643 seconds 
No cached cover found, running identify
Trying alternate results page markup
No matches found with query: u'http://www.amazon.com/s/?sort=relevanceexprank&field-title=PyGTK+2+0+Tutorial&search-alias=stripbooks&unfiltered=1'
No cover found 

******************************************************************************** 

****************************** Open Library Covers ****************************** 
Request extra headers: [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.2.11) Gecko/20101012 Firefox/3.6.11')] 
Failed to download valid cover 
Took 1.09672546387e-05 seconds 

******************************************************************************** 
'''

pattern_newline = re.compile(r'\r?\n')

# template strings for files
#
_T_mimetype = 'application/epub+zip'

_T_style = u'''body { background: white; margin: 1em 1em; }
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
p.reflow-br { text-indent: 2em; }
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

# /index.html for browser (instead of epub)
_T_index = u'''<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
  <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
  <title>{title}</title>
  <link rel="stylesheet" type="text/css" href="style.css" />
  <!--<script src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.3/jquery-ui.min.js"></script>-->
  <script src="/lib/jquery.js"></script>
  <script type="text/javascript">{js}</script>
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
# javascripts contain {}, so they are not recommended to be in templates
_T_JS = u'''
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
    $('#index').hide(100, function(){$(this).show(); });
}
'''

# /META-INF/container.xml
_T_container_xml = u'''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0"
           xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf"
           media-type="application/oebps-package+xml"/>
   </rootfiles>
</container>
'''

# head of content.opf, need close </package>
_T_opf = u'''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="uuid_id" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/"
     xmlns:dcterms="http://purl.org/dc/terms/"
     xmlns:opf="http://www.idpf.org/2007/opf"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <dc:identifier id="uuid_id" opf:scheme="uuid">{uuid}</dc:identifier>
    <dc:language>en</dc:language>
    <dc:title>{title}</dc:title>
    <dc:creator opf:role="aut">{author}</dc:creator>
    <meta name="cover" content="{cover}" />
  </metadata>
'''
_T_opf_item = u'''    <item id="{Id}" href="{href}" media-type="{mime}" />
'''
_T_opf_itemref = u'''    <itemref idref="{idref}" />
'''
_T_opf_itemref_cover = u'''    <itemref idref="cover" linear="no" />
'''
#    <itemref idref="normal-first-content" />
_T_opf_reference = u'''    <reference href="{href}" title="{title}" type="{type}" />
'''



# head of toc.ncx, need close </ncx>
_T_toc = u'''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="eng">
  <head>
    <meta content="{uuid}" name="dtb:uid"/>
    <meta content="2" name="dtb:depth"/>
    <meta content="epub.py" name="dtb:generator"/>
  </head>
'''
#    <meta content="0" name="dtb:totalPageCount"/>
#    <meta content="0" name="dtb:maxPageNumber"/>

_T_toc_docTitle = u'''  <docTitle>
    <text>{title}</text>
  </docTitle>
'''
# replace UUID, TEXT, SRC
_T_toc_navPoint = u'''    <navPoint id="{uuid}" playOrder="{order}">
      <navLabel>
        <text>{text}</text>
      </navLabel>
      <content src="{href}"/>
    </navPoint>
'''



# template of xhtml for cover
_T_cover = u'''
 <div id="cover-image">
   <img src="{cover}" />
 </div>
'''
_T_cover_text = u'''
 <div id="book-cover">
   <div id="book-cover-title">{title}</div>
   <div id="book-cover-title2">{title2}</div>
   <div id="book-cover-author">{author}</div>
   <div id="book-cover-other">{other}</div>
 </div>
'''
# template of xhtml, replace title, content
_T_xhtml = u'''<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
  <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
  <title>{title}</title>
  <link rel="stylesheet" href="style.css" type="text/css" />
</head>

<body>
 {content}
</body>
</html>
'''



class EPub:
    selector = "div.htmlcontent"
    _mime = {                   # MIME table from file extension
        '.jpeg':     'image/jpeg',
        '.jpg':      'image/jpeg',
        '.png':      'image/png',
        '.bmp':      'image/bmp',
        '.gif':      'image/gif',
        '.svg':      'image/svg+xml',
    
        '.py':       'text/x-python',
        '.html':     'application/xhtml+xml',
        '.xhtml':    'application/xhtml+xml',
        '.css':      'text/css'
    }


    def __init__(self, cfg):
        ''' Load configuration, setup directory structures for output
            and build data structures
        '''
        self.cfg = cfg
        self.root = cfg.get('root')
        self.src = cfg.get('src')
        self.title = cfg.get('title', 'Unknown')
        self.author = cfg.get('author', 'Unknown')

        self.manifest = []
        self.toc = []
        self.order = 1              # seed of toc order, increase for each page
        self.uuid = uuid.uuid1()
        self.has0 = False

        # setup directory structure
        try:
            shutil.rmtree(self.root, True)
        except Exception as ex: pass
        try:
            os.makedirs(self.root)
        except OSError as e: pass
        try:
            os.makedirs(self.root + '/META-INF')
        except OSError as e: pass
        try:
            os.makedirs(self.root + '/OEBPS/Images')
        except OSError as e: pass

        # create intrinsic files
        fname = self.root + '/META-INF/container.xml'
        with codecs.open(fname, 'w', 'utf-8') as f:
            f.write(_T_container_xml)
        fname = self.root + '/mimetype'
        with codecs.open(fname, 'w', 'utf-8') as f:
            f.write(_T_mimetype)
        fname = self.root + '/OEBPS/style.css'        
        with codecs.open(fname, 'w', 'utf-8') as f:
            f.write(_T_style)

        # process cover
        cover = self.cfg['cover']
        if not cover:
            # not defined in configuration/command-line, search file pattern
            try:
                cpat = 'cover.*'
                if self.src is not None:
                    cpat = self.src + "/" + cpat
                cover = glob.glob(cpat)[0]
            except: pass
        if cover:
            # check file exists and has mime
            # if only the file name is given and it is not in cwd,
            # check in src as well
            if not os.path.exists(cover):
                if os.path.dirname(cover) is None and self.src is not None:
                    cover = os.path.join(self.src, cover)
            if os.path.exists(cover):
                if not self.defaultMime(os.path.basename(cover)):
                    cover = None
            else:
                cover = None
        if cover:
            # copy the image file and generate cover page
            img,isDup = self.copyResFile(cover)
            if not isDup:
                self.addManifest(img, Id='cover-image')
            rname = '{0}/OEBPS/cover.xhtml'.format(self.root)
            with codecs.open(rname, 'w', 'utf-8') as fp:
                sc = _T_cover.format(cover=unicode(img))
                fp.write(_T_xhtml.format(title=u'Cover', content=sc))
            self.addTOC(href=u'cover.xhtml', Id=u'cover', text=u'Cover')
        else:
            # no cover image available, create a text page that
            # contains title and author
            rname = '{0}/OEBPS/cover.xhtml'.format(self.root)
            with codecs.open(rname, 'w', 'utf-8') as fp:
                sc = _T_cover_text.format(
                       title=self.title,
                       title2=self.cfg['title2'],
                       author=self.author,
                       other=self.cfg['other'])
                fp.write(_T_xhtml.format(title='Cover', content=sc))
            self.addTOC(href='cover.xhtml', Id='cover', text='Cover')

        
    def parse(self, count = None, pattern = '*.htm*', verbose = False):
        ''' parse html files in the source directory
                count     first <count> files only (default for all)
                pattern   glob pattern
        '''
        if self.src is not None:
            pattern = self.src + "/" + pattern
        flist = glob.glob(pattern)
        flist.sort()
        if count is None and self.cfg['count'] > 0:
            count = self.cfg['count']
        if count is not None:
            count = int(count)
            if count > 0:
                flist = flist[:count]
        if verbose:
            self.dump_xpath()
        for f in flist:
            # parse all (html) files, but skip index.(x)htm(l)
            if re.search(r'index.*?\.x?html?$', f, flags=re.I):
                continue
            self.parsePage(f)
            if verbose: print f
        self.addManifest('style.css', 'style.css', 'text/css')
        self.exportContent()
        self.exportTOC()
        self.exportIndex()
        

    def zip(self):
        ''' zip everything under root to create a epub file '''
        if self.cfg['epub']:
            zfname = unicode(self.cfg['epub'])
        else:   # not specified, use the name of source directory
            src = self.src
            if src is None or src == '.':
                src = os.getcwd()
            src = os.path.basename(src)
            zfname = '%s.epub' % src
            self.cfg['epub'] = zfname
        zf = zipfile.ZipFile(zfname, 'w', zipfile.ZIP_DEFLATED)
        path = self.root    # root of epub structure, ./epub by default
        for root, dirs, files in os.walk(path):
            for f in files:
                rf = os.path.join(root, f)      # real file name
                af = os.path.relpath(rf, path)  # archive file name
                zf.write(rf, af)
        zf.close()


    def parsePage(self, fname):
        ''' parse a page, copy/convert img files, extract mainContent
        into xhtml, add into manifester and toc list'''
        print "parsePage: " + fname
        cfg = self.cfg
        page = MyPage(fname, self.cfg.get('encoding'))
        page.filter(cfg.get('xpath'), cfg.get('unwrap', False))
        page.cleanPage()
        # copy all images into /OEBPS/Images
        for i in page.images():
            try:
                fimg = i.get('src')
                if re.match(r'http://.*', fimg):
                    page.remove(i)
                    continue
                if self.src is not None:
                    fimg = os.path.join(self.src, fimg)
                nf,isDup = self.copyResFile(fimg)
                if not isDup:
                    self.addManifest(nf)
                if fimg != nf: i.set('src', nf)
            except Exception as (e):
                print 'parsePage.img ({0} - {1}): {2}'.format(fname, fimg, e)
        rname = os.path.splitext(os.path.basename(fname))[0] + ".xhtml"
        title = page.title()
        if title:
            title = xml.sax.saxutils.escape(title)
        try:
            with codecs.open(u"{0}/OEBPS/{1}".format(self.root, rname), "w", 'utf-8') as fp:
                c = page.output(reflow=cfg.get('reflow'), pagewidth=cfg.get('pagewidth'), autopara=cfg.get('autopara'))
                txt = _T_xhtml.format(title=title, content=c)
                fp.write(txt)
        except Exception as ex:
            print "parsePage error: ", ex
        self.addTOC(unicode(rname), text=title)


    def addManifest(self, href, Id=None, mime=None):
        ''' add an item in manifest list '''
        if mime is None:
            mime = self.defaultMime(href)
        Id = self.enId(Id, href)
        href = self.enHref(href)
        self.manifest.append({'href': href, 'Id': Id, 'mime': mime })
    

    def addTOC(self, href, text=None, Id=None, mime=None):
        ''' add an item in TOC list '''
        if mime is None:
            mime = self.defaultMime(href)
        Id = self.enId(Id, href)
        href = self.enHref(href)
        uid = uuid.uuid1()      # uuid4() random
        hn = self.hlevel(href) 
        self.toc.append({'idref': Id, 'text': text,
                'href': href, 'level': hn, 'uuid': uid, 'order': self.order })
        self.addManifest(href, Id, mime)
        self.order += 1
    

    def exportIndex(self, tocUUID=None):
        ''' Export /index.html, which is not used by epub but used by browsing
            when expanded.
        '''
        try:
            sa = [ u'<div class="ci ci{level}" src="{href}">{text}<div>'.format(**x)
                for x in self.toc ]
            si = u'\n'.join(sa)
            with codecs.open(self.root + '/OEBPS/index.html', 'w', 'utf-8') as fp:
                fp.write(_T_index.format(title=self.cfg['title'], content=si, js=_T_JS))
        except Exception as ex:
            print('Fail to export index.html: {0}, skipped'.format(ex))


    def exportTOC(self, tocUUID=None):
        ''' export /toc.ncx '''
        with codecs.open(self.root + "/OEBPS/toc.ncx", "w", 'utf-8') as fp:
            fp.write(_T_toc.format(uuid=self.uuid))

            fp.write(_T_toc_docTitle.format(title=self.title))
            
            fp.write(u"  <navMap>\n")
            for s in self.toc:
                fp.write(_T_toc_navPoint.format(**s))
            fp.write(u"  </navMap>\n")

            fp.write(u"</ncx>\n")


    def exportContent(self):
        ''' export OEBPS/content.opf, which list/map all resources such as
            xhtml, images, toc etc
        '''
        with codecs.open(self.root + "/OEBPS/content.opf", "w", 'utf-8') as fp:
            ss = _T_opf.format(uuid=self.uuid,
                title=self.title, author=self.author, cover=self.cfg['cover'])
            fp.write(ss)
            
            fp.write(u"  <manifest>\n")
            fp.write(_T_opf_item.format(Id=u'ncx',
                href=u'toc.ncx', mime=u'application/x-dtbncx+xml'))
            for s in self.manifest:
                fp.write(_T_opf_item.format(**s))
            fp.write(u"  </manifest>\n")
            
            fp.write(u"  <spine toc=\"ncx\">\n")
            for s in self.toc:
                fp.write(_T_opf_itemref.format(**s))
            fp.write(u"  </spine>\n")
            
            if self.cfg['cover'] is not None:
                fp.write(u"    <guide>\n")
                fp.write(_T_opf_reference.format(type=u'cover',
                    title=u'Cover', href=u'cover.xthml'))
                fp.write(u"    </guide>\n")

            fp.write(u"</package>\n")


    def enHref(self, href):
        ''' encode href by converting space( ) into %20'''
        return re.sub(u' ', u'%20', href)            


    def enId(self, Id, href=None):
        ''' encode id by converting space( ) into dash(-)'''
        if Id is None:
            Id = re.sub(ur'^.*\/', u'', href)
        return re.sub(u' ', u'-', Id)


    def defaultMime(self, fname):
        ''' get MIME from file name (extension)'''
        try:
            ext = os.path.splitext(os.path.basename(fname))[1]
            return unicode(EPub._mime[ext])
        except:
            return None


    def copyResFile(self, name, dst = 'Images'):
        ''' Copy a file into resource folder /res.
        
        If the resource name (filename) doesn't exist in the resource folder,
        it is considered a new resource and is simply copied into the folder
        without checking/comparing content (for performance purpose);
        If the resource name exists in the folder already, the contents are
        further compared. If the content is the same, reuse that file, other
        wise a new name is generated with sequence appended.
        
        Return: actual file name, duplicated
        '''
        bname = os.path.basename(name)
        root = "{0}/OEBPS/".format(self.root)
        rname = "{0}/{1}".format(dst, bname)
        if os.path.exists(root + rname):
            if self.isSameContent(name, root + rname):
                return rname, True        # re-use the existed file
            bname = self.getAlternativeName(bname, dst)
            rname = "{0}/{1}".format(dst, bname)
        try:
            shutil.copy(name, root + rname)
        except Exception as ex:
            print 'copyResFile ({0} --> {1}): {2}'.format(name, dst, ex)
        return rname, False


    def isSameContent(self, f1, f2):
        ''' Compare (binary) content of two files.
        This is used to decide wheather to duplicate resource files.
        '''
        st1 = os.stat(f1)
        st2 = os.stat(f2)
        if stat.S_ISREG(st1.st_mode) and stat.S_ISREG(st2.st_mode):
            if st1.st_size != st2.st_size:
                return False
            with open(f1) as fp:
                c1 = fp.read()
            with open(f2) as fp:
                c2 = fp.read()
            return c1 == c2
        else:
            return False


    def getAlternativeName(self, f, dst = 'Images'):
        ''' Get an alternative name when two files conflict in names in /res folder.
        The solution is to add sequence number in basename.
        This is obviously not suitable in multiple processes.
        '''
        base, ext = os.path.splitext(os.path.basename(f))
        n = 2
        res = '{0}/OEBPS/{1}/'.format(self.root, dst)
        while True:
            aname = "{0}-{1}{2}".format(base, n, ext)
            if not os.path.exists(res + aname):
                return aname
            n += 1            


    def hlevel(self, name):
        ''' get <hn> level (n=1,2,...etc) according to filename pattern '''
        name = os.path.basename(name)
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


    def dump_xpath(self):
        xpath = self.cfg.get('xpath')
        if xpath is None:
            print 'Xpath is None'
        elif isinstance(xpath, str) or isinstance(xpath, unicode):
            print 'Xpath=%s' % xpath
        elif isinstance(xpath, list):
            print 'Xpath is a list'
            for i in xpath:
                print '    ', i
        else:
            print 'Xpath unknown'


class MyPage(object):
    '''
    Extract content from downloaded html files, using lxml and various
    filters.
    '''
    pattern_charset = re.compile(r'charset=([-_0-9a-z]+)', re.IGNORECASE)
    pattern_gb = re.compile(r'gb[-_0-9]+$', re.IGNORECASE)
    h_all = '|'.join(['.//h%d' % i for i in range(1,10)])

    def __init__(self, src=None, encoding=None):
        ''' Load html file using lxml.etree. Because lxml doesn't handle
            encoding well enough, detect charset="encoding" first.
            The content is converted into unicode.
            
            cfg:
            encoding    used unless charset is defined in html
            xpath       string or list define filter(s)
            unwrap      unwrap filter tags
        '''
        self.encoding = encoding
        self.text = None
        if src is not None:
            self.load(src)
        
        
    def load(self, fname):
        ''' Load page from file
        '''
        try:
            self.fname = fname
            with open(self.fname) as fp:
                text = fp.read()
            self.decode(text)
            #print self.text.encode('utf8')
        except Exception, ex:
            print("Fail to load from file {}\n{}".format(self.fname, ex))
            raise ex


    def loadUrl(self, url, cache=None):
        ''' Load page from URL
            if cache specified
                save in the cache after loading if it doens't exist
                load from the cache if it exists
        '''
        self.url = url
        self.cache = cache
        try:
            f = None
            if self.cache is not None and os.path.exists(self.cache):
                # cache exists and use it instead
                fname = self.cache
                f = open(self.cache, 'r')
            else:
                fname = self.url
                f = urllib2.urlopen(self.url)
            text = f.read()
            f.close()
            self.decode(text)
            if self.cache is not None and not os.path.exists(self.cache):
                # cache specified but it doesn't exist, create one
                with open(self.cache, 'w') as f:
                    f.write(self.text.encode('utf8'))
        except Exception, ex:
            print("Fail to load url {}\n{}".format(self.url, ex))
            raise ex


    def filter(self, xpath, unwrap=True, dump=False):
        ''' Apply filter to mypage
            
            cfg:
            xpath       string or list define filter(s)
            unwrap      unwrap filter tags
        '''
        self.root = etree.HTML(self.text)
        body = self.root.xpath('//body')[0]
        self.mypage = etree.Element('div', id='__mypage__')
        nselected = 0
        tbody = re.compile(r'\btbody\b', re.IGNORECASE)
        if xpath is None or xpath == '//body':
            self.mypage = body
            return
        elif isinstance(xpath, basestring):
            # xpath is a string
            xpath = tbody.sub('', xpath)
            for t in self.root.xpath(xpath):
                self.moveto(t, self.mypage, unwrap=unwrap)
                nselected += 1
                #print etree.tostring(self.mypage, encoding='utf8')
        elif isinstance(xpath, list):
            # xpath is a list of strings, those start with '-' for stripping
            add_list = []
            remove_list = []
            for s in xpath:
                if s[0] == '-':
                    remove_list.append(tbody.sub('', s[1:]))
                else:
                    add_list.append(tbody.sub('', s))
            for p in add_list:
                p = tbody.sub('', p)
                for t in self.root.xpath(p):
                    for rp in remove_list:
                        rp = tbody.sub('', rp)
                        for r in t.xpath(rp):
                            self.remove(r)
                    self.moveto(t, self.mypage, unwrap=unwrap)
                    nselected += 1
        else:
            raise Exception('unknown xpath')
        if dump:
            dumptag(self.mypage)
        if nselected == 0:
            raise Exception('nothing selected')


    def decode(self, text, encoding=None):
        ''' Decode html text into unicode, using encoding
            unless charset is specified in text.
            
            Return a tuple (decoded-text, 
        '''
        match = MyPage.pattern_charset.search(text)
        if match:
            self.encoding = match.group(1)
        if self.encoding is None:
            text = unicode(text)
        else:
            # GB18030 is superset of all GB encodings set
            if MyPage.pattern_gb.match(self.encoding):
                text = unicode(text, 'gb18030')
            else:
                text = unicode(text, self.encoding)
        text = MyPage.pattern_charset.sub('charset=UTF-8', text, 1)
        self.text = re.sub(ur'\r\n', u'\n', text)


    def images(self):
        ''' list all tags <img>'''
        return self.mypage.xpath('.//img')


    def links(self):
        ''' list all tags <a> with @href '''
        return self.mypage.xpath('.//a[@href]')


    def title(self, by_level=False):
        ''' return title of the page if exists
            by_level    True: find h1, else h2, else h3 and so on
                        False: find first h1/2/3 what ever
        '''
        try:
            if by_level:
                for i in range(1,10):
                    h = self.mypage.xpath('.//h%d' % i)
                    if h: return h[0].text
            else:
                # get first head, what ever
                h = self.mypage.xpath(MyPage.h_all)
                if h: return h[0].text
            txt = tag2text(self.mypage)
            if txt:
                for i, t in enumerate(pattern_newline.split(txt)):
                    #print '%s(%d): [%s]' % (self.fname, i, t)
                    tt = t.strip()
                    if tt:
                        return tt
                    if i > 10: break
            return ''
        except Exception as ex:
            print 'MyPage.title:', ex
            return ''

    
    def t_append(self, f, t):
        ''' convenient function for f+t, None is treated as "" '''
        if t:
            if f:
                f += t
            else:
                f = t
        return f


    def unwrap(self, tag):
        ''' unwrap a node tag
        '''
        pa = tag.getparent()
        i = 0
        for t in pa:           # find the index of tag in parent
            if tag is t:
                break
            i += 1
        if tag.text:
            if i == 0:
                pa.text = self.t_append(pa.text, tag.text)
            else:
                p = pa[i - 1]
                p.tail = self.t_append(p.tail, tag.text)
        for t in tag:
            pa.insert(i, t)
            i += 1
        if tag.tail:
            if i == 0:
                pa.text = self.t_append(pa.text, tag.tail)
            else:
                p = pa[i-1]
                p.tail = self.t_append(p.tail, tag.tail)
        pa.remove(tag)


    def unwrap_text(self, tag, pretty=True, encoding='unicode'):
        ''' Return text that is print without tag itself
        '''
        text = []
        if tag.text:
            text.append(tag.text)
        for t in tag:
            text.append(etree.tostring(t, pretty_print=pretty, encoding=encoding))
        return ''.join(text)


    def remove(self, tag):
        ''' Remove a tag (and all its descendants) from the tree. '''
        parent = tag.getparent()
        if parent is not None:
            parent.remove(tag)


    def moveto(self, tag, parent, index=-1, unwrap = False):
        ''' Move tag from its original place to parent
            unwrap the tag if unwrap = True
            index < 0 means append
        '''
        n = len(parent)
        if index >= 0 and index < n:
            parent.insert(index, tag)
        else:
            parent.append(tag)
        if unwrap:
            self.unwrap(tag)


    def cleanPage(self):
        ''' clean page '''
        # Unwrap all in-page anchors, which has attribute "name" for
        #    navigating in page, i.e. href=page#name
        skip = None     # todo?
        if skip:
            pattern = re.compile(skip)
        for a in self.mypage.xpath('.//a[@name]'):
            name = a.get('name', '')
            if not (skip and pattern.match(name)):
                self.unwrap(a)
        # clean class/id for h1, h2, ...
        for t in self.mypage.xpath(MyPage.h_all):
            att = t.attrib
            if 'class' in att: del att['class']
            if 'id' in att: del att['id']
        # clean onclick/class for anchors
        for t in self.mypage.xpath('.//a[@onclick]'):
            del t.attrib['onclick']
        for t in self.mypage.xpath('.//a[@class]'):
            del t.attrib['class']
        # remove hidden inputs, script, iframe
        for t in self.mypage.xpath('.//input[@type="hidden"] | .//script | .//iframe'):
            self.remove(t)
        # unwrap font
        for t in self.mypage.xpath('.//font'):
            self.unwrap(t)
        # unwrap tables that have only one <td> for "boxed" (safari)
        for t in self.mypage.xpath('.//table'):
            tds = t.xpath('.//td')
            if len(tds) == 1:
                td = tds[0]
                p = t.getparent()
                if p:
                    p.replace(t, td)
                    self.unwrap(td)
        # remove "Code View: Scroll/Show All" (safari)
        cs = cssselect.CSSSelector('div.codeSegmentsExpansionLinks')
        for t in cs(self.mypage):
            self.remove(t)
        # remove comment container (O'Reilly)
        cs = cssselect.CSSSelector('div.comment_container')
        for t in cs(self.mypage):
            self.remove(t)


    def output(self, prettify=True, reflow=False, pagewidth=None, autopara=False):
        ''' Output mypage into a (unicode) string '''
        try:
            for a in self.mypage.xpath('//a[@href]'):
                self.unwrap(a)
            if reflow:
                reflow_br(self.mypage, pagewidth)
                prettify = True
            return self.unwrap_text(self.mypage, pretty = prettify)
        except Exception as ex:
            print "Exception(MyPage.output):", ex
            return ''


def most_common_width(txt):
    ''' return the most common width in a list of strings '''
    tnc = {}
    for t in txt:
        if t is None: continue      # don't count blank lines
        n = len(t.strip())
        if n == 0: continue         # don't count blank lines
        if n in tnc:
            tnc[n] += 1
        else:
            tnc[n] = 1
    rn, rw = 0, 0
    for t, w in tnc.items():
        if w > rw:
            rn, rw = t, w
    return rn


def append_tag_string(txt_list, tag, with_tail=True, inline=False):
    ''' Append a tag (as a text) to a list of text.
        inline=True     append to the last line instead of appending as
                        a new line
    '''
    if tag.text is None:
        t = ''
    else:
        t = tag.text.strip()
    if with_tail:
        if tag.tail is not None:
            t += tag.tail.strip()
    if t:
        if inline and txt_list:
            txt_list[-1] += ' ' + t
        else:
            txt_list.extend(pattern_newline.split(t))
    else:
        txt_list.append('')
    return t


def reflow_br(tag, pagewidth=None, autopara=False):
    ''' Reflow a block of text (div or p or others) that are manually 
        formatted by hard-coded <br/>. This is quite common in many
        Chinese pages converted from text file.
    '''
    txt = []
    #dump_tag(tag)
    append_tag_string(txt, tag, with_tail = False)
    tag.text = None
    for c in tag:
        #print 'reflow_br: <%s>' % c.tag
        if c.tag == 'a':
            t = append_tag_string(txt, tag, inline = True)
        elif c.tag == 'br':
            t = append_tag_string(txt, c)
        else:
            t = txt.extend(pattern_newline.split(tag2text(c, True)))
        #print 'None' if t is None else t.encode('utf8')
        tag.remove(c)
    if pagewidth is None:
        nw = most_common_width(txt)
    else:
        nw = pagewidth
    paragraphs = []
    latest_para = ''
    for t in txt:
        n = len('' if t is None else t)
        #print ('%d/%d: %s' % (n, nw, t)).encode('utf8')
        if autopara or nw < 1 or n < nw - 2:
            paragraphs.append(latest_para + t)
            latest_para = ''
        else:
            latest_para += t
    if latest_para:
        paragraphs.append(latest_para)
    for p in paragraphs:
        st = etree.SubElement(tag, 'p', {'class': 'reflow-br'})
        st.text = p


def tag2text(tag, withtail = False):
    ''' Remove tags and leave text only.
        This function applies recursive to the whole sub-tree.
        New lines are added before and after block-display tags.
    '''
    if tag is None:
        return u''
    a = []
    if tag.tag in [ 'div', 'p', 'br', 'table', 'ul', 'ol' ]:
        a.append(u'\n')
    if tag.text:
        a.append(tag.text)
    for c in tag:
        cs = tag2text(c, True)
        if cs:
            a.append(cs)
    if withtail and tag.tail:
        a.append(tag.tail)
    if a:
        return u''.join(a)
    else:
        return ''


def dump_tag(tag, pretty_print=False):
    print etree.tostring(tag, pretty_print=pretty_print, encoding='utf8')


def get_urls(argv, verbose=False, test=False):
    ''' load files from an index page, file URLs in index'''
    cfg = getConfig(argv)
    folder = cfg.get('src', '')
    encoding = cfg.get('encoding')
    url = cfg.get('url')
    ipage = MyPage(encoding=encoding)
    ipage.loadUrl(url, os.path.join(folder, 'index-cache.html'))
    ipage.filter(cfg.get('xpath-i'), unwrap=False)
    links = ipage.links()

    nn = 1
    fnameTemp = u'{seq:03d}.html'
    for a in links:
        title = a.text
        if title is None:
            title=''
        else:
            title = title.strip()
        href = urlparse.urljoin(url, a.get('href'))
        fname = os.path.join(folder, fnameTemp.format(seq=nn))
        a.set('href', fname)
        v = u'{}\n    {}={}'.format(title, fname, href)
        print v.encode('UTF-8')
        if not (test or os.path.exists(fname)):
            spage = MyPage(encoding=encoding)
            spage.loadUrl(href, fname)
            #todo- write title back
            sleep_time = random.randint(1,100)/10.0
            print 'sleep({:.1f})...'.format(sleep_time)
            time.sleep(sleep_time)
        nn += 1
    sys.exit(0)


def usage():
    print '''epub.py  <source_folder>
        where source_folder contains all pages, configure is
        read from <source_folder>/epub.json and the output
        is epub/
        
        epub.py --test test_file
'''


def getConfig(argv = None):
    ''' load configuration from json and command-line options '''
    #default configuration
    cfg = {
        'src':      None,
        'root':     'epub',
        'xpath':    'div.htmlcontent',  # safari-online
        'title':    'Unknown',
        'title2':   '',
        'author':   'Unknown',
        'other':    '',
        'cover':    None,
        'epub':     None,               # name of epub
        'unwrap':   True,
        'reflow':   False,
        'encoding': 'utf-8',
        'count':    0,
    }

    if argv is not None and len(argv) > 0: cfg['src'] = argv[0]
    if cfg['src']:
        if not os.path.exists(cfg['src']):
            print 'source {0} doesn\'t exist\n'.format(cfg['src'])
            sys.exit(2)
        jname = '{0}/epub.json'.format(cfg['src'])
    else:
        jname = 'epub.json'
    if os.path.exists(jname):
        try:
            with codecs.open(jname, 'r', 'utf-8') as fp:
                for k,v in json.load(fp).items():
                    cfg[k] = v
        except Exception as ex:
            print 'Fail to load json:' + ex
    return cfg


def dumptag(tag, pretty_print=False, with_tail=True):
    print etree.tostring(tag, pretty_print=pretty_print, with_tail=with_tail, encoding='utf8')


def test():
    cfg['xpath'] = '//p[@class="cn"]'
    cfg['xpath'] = '//td[@width="702"]/p[@align="left"][1]'
    cfg['unwrap'] = True
    page = MyPage('ty.htm', cfg)
    print page.output(reflow=True).encode('utf8')
    sys.exit(0)
    

def testPage(argv):
    cfg = getConfig()
    #cfg['dumpload'] = True
    page = MyPage(src=argv[0], encoding = cfg.get('encoding'))
    page.filter(cfg.get('xpath'), cfg.get('unwrap', False), cfg.get('dumpload'))
    page.cleanPage()
    print '='*40
    print 'Title=', page.title().encode('utf8')
    print '='*40
    #print etree.tostring(page.mypage, pretty_print=True, encoding='utf8')
    print page.output(reflow=cfg.get('reflow', False), pagewidth=cfg.get('pagewidth'), autopara=cfg.get('autopara')).encode('utf8')
    sys.exit(0)


def run(argv):
    cfg = getConfig(argv)
    epub = EPub(cfg)
    epub.parse(verbose=True)
    print 'compressing ...'
    epub.zip()
    print '-'*40, 'done'


if __name__ == "__main__":
    try:
        opt_short = None
        opt_long = [ 'test', 'load', 'load-test' ]
        opts, files = getopt.getopt(sys.argv[1:], opt_short, opt_long)
    except getopt.GetoptError as err:
        print err
        usage()
        sys.exit(2)
    
    for o,v in opts:
        if o == '--test':
            testPage(files)
        if o == '--load':
            get_urls(files)
        if o == '--load-test':
            get_urls(files, test=True)
    run(files)

