#! /usr/bin/python
# -*- coding: UTF-8 -*-

import sys, os, os.path, stat, glob, getopt, codecs
import re, shutil, uuid, json, zipfile
from bs4 import BeautifulSoup

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
#cover-image { position: relative; }
#cover-image img { display: block; margin: 2px auto; -width: 96%; }
'''

    # /index.html for browser (instead of epub)
    _T_index = u'''<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
  <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
  <title>{title}</title>
  <link rel="stylesheet" href="style.css" type="text/css" />
</head>

<body>
<h1>{title}</h1>
<ol>
{content}
</ol>
</body>
</html>
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

    def __init__(self, cfg):
        # load configuration and defaults
        self.src = cfg.setdefault('src')
        self.root = cfg.setdefault('root', 'epub')
        self.selector = cfg.setdefault('selector', 'div.htmlcontent') # safari
        self.unwrap = cfg.setdefault('unwrap', False)
        self.title = unicode(cfg.setdefault('title', 'Unknown'))
        self.author = unicode(cfg.setdefault('author', 'Unknown'))
        self.cover = cfg.setdefault('cover')
        self.epub = cfg.setdefault('epub')
        self.encode = cfg.setdefault('encode', 'utf-8')
        self.dry = cfg.setdefault('dry')
        self.count = cfg.setdefault('count', 0)

        self.manifest = []
        self.toc = []
        self.order = 1
        self.uuid = uuid.uuid1()

        if self.dry: return

        # setup directory structure
        try:
            shutil.rmtree(self.root, True)
        except Exception as ex: pass
        try:
            os.makedirs(self.root)
        except OSError as e: pass
        try:
            os.makedirs(self.root + "/META-INF")
        except OSError as e: pass
        try:
            os.makedirs(self.root + "/OEBPS/Images")
        except OSError as e: pass

        # create intrinsic files
        fname = self.root + '/META-INF/container.xml'
        with codecs.open(fname, 'w', 'utf-8') as f:
            f.write(EPub._T_container_xml)
        fname = self.root + '/mimetype'
        with codecs.open(fname, 'w', 'utf-8') as f:
            f.write(EPub._T_mimetype)
        fname = self.root + '/OEBPS/style.css'        
        with codecs.open(fname, 'w', 'utf-8') as f:
            f.write(EPub._T_style)

        # process cover
        if not self.cover:
            # not defined in configuration/command-line, search file pattern
            try:
                cpat = 'cover.*'
                if self.src is not None:
                    cpat = self.src + "/" + cpat
                cover = glob.glob(cpat)
                self.cover = cover[0]
            except: pass
        if self.cover:
            # check file exists and has mime
            # if only the file name is given and it is not in cwd,
            # check in src as well
            if not os.path.exists(self.cover):
                if os.path.dirname(self.cover) is None and self.src is not None:
                    self.cover = os.path.join(self.src, self.cover)
            if os.path.exists(self.cover):
                if not self.defaultMime(os.path.basename(self.cover)):
                    self.cover = None
            else:
                self.cover = None
        if self.cover:
            # copy the image file and generate cover page
            img,isDup = self.copyResFile(self.cover)
            if not isDup:
                self.addManifest(img, Id='cover-image')
            rname = '{0}/OEBPS/cover.xhtml'.format(self.root)
            with codecs.open(rname, 'w', 'utf-8') as fp:
                sc = EPub._T_cover.format(cover=unicode(img))
                fp.write(EPub._T_xhtml.format(title=u'Cover', content=sc))
            self.addTOC(href=u'cover.xhtml', Id=u'cover', text=u'Cover')

        
    def parse(self, count = 0, pattern = '*.htm*', verbose = False):
        ''' parse html files in the source directory
        count          first count files only (default for all files)
        pattern        glob pattern
        '''
        if self.src is not None:
            pattern = self.src + "/" + pattern
        flist = glob.glob(pattern)
        flist.sort()
        if count == 0 and self.count > 0:
            count = self.count
        count = int(count)
        if count > 0:
            flist = flist[:count]
        for f in flist:
            self.parsePage(f)
            if verbose: print f
        self.addManifest(u"style.css", u"style.css", u"text/css")
        self.exportContent()
        self.exportTOC()
        self.exportIndex()
        
    def zip(self):
        ''' zip everything under root to create a epub file '''
        if self.epub:
            zfname = unicode(self.epub)
        else:   # not specified, use the name of source directory
            src = self.src if self.src else os.getcwd()
            src = os.path.basename(src)
            zfname = u'{0}.epub'.format(src)
            self.epub = zfname
        if self.dry:
            print u'create zip {0}'.format(zfname)
            return

        zf = zipfile.ZipFile(zfname, 'w', zipfile.ZIP_DEFLATED)
        path = self.root
        for root, dirs, files in os.walk(path):
            for f in files:
                rf = os.path.join(root, f)      # real file name
                af = os.path.relpath(rf, path)  # archive file name
                zf.write(rf, af)
        zf.close()

    def parsePage(self, fname):
        ''' parse a page, copy/convert img files, extract mainContent
        into xhtml, add into manifester and toc list'''
        soup = MySoup(fname, self.encode, self.selector)
        soup.extractInPageAnchors()
        soup.cleanPage()
        # copy all images into /OEBPS/Images
        for c in soup.images():
            try:
                fimg = c['src']
                if self.src is not None:
                    fimg = os.path.join(self.src, fimg)
                nf,isDup = self.copyResFile(fimg)
                if not isDup:
                    self.addManifest(nf)
                if fimg != nf: c['src'] = nf
            except Exception as (e):
                print 'parsePage.img ({0} - {1}): {2}'.format(fname, fimg, e)
        rname = os.path.splitext(os.path.basename(fname))[0] + ".xhtml"
        title = soup.title()
        try:
            with codecs.open(u"{0}/OEBPS/{1}".format(self.root, rname), "w", 'utf-8') as fp:
                c = soup.output(selector=self.selector, unwrap=self.unwrap)
                txt = EPub._T_xhtml.format(title=title, content=c)
                fp.write(txt)
        except Exception as ex:
            print "parsePage: ", ex
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
        self.toc.append({'idref': Id, 'text': text, 'href': href, 'uuid': uid, 'order': self.order })
        self.addManifest(href, Id, mime)
        self.order += 1
    
    def exportIndex(self, tocUUID=None):
        ''' export /index.html for browser '''
        sa = [ u'  <li><a href="{0}">{1}</a></li>'.format(x['href'], x['text'])
                for x in self.toc ]
        si = u'\n'.join(sa)
        with codecs.open(self.root + '/OEBPS/index.html', 'w', 'utf-8') as fp:
            fp.write(EPub._T_index.format(title=self.title, content=si))

    def exportTOC(self, tocUUID=None):
        ''' export /toc.ncx '''
        with codecs.open(self.root + "/OEBPS/toc.ncx", "w", 'utf-8') as fp:
            fp.write(EPub._T_toc.format(uuid=self.uuid))

            fp.write(EPub._T_toc_docTitle.format(title=self.title))
            
            fp.write(u"  <navMap>\n")
            for s in self.toc:
                fp.write(EPub._T_toc_navPoint.format(**s))
            fp.write(u"  </navMap>\n")

            fp.write(u"</ncx>\n")


    def exportContent(self):
        ''' export /content.opf '''
        with codecs.open(self.root + "/OEBPS/content.opf", "w", 'utf-8') as fp:
            ss = EPub._T_opf.format(uuid=self.uuid,
                title=self.title, author=self.author, cover=self.cover)
            fp.write(ss)
            
            fp.write(u"  <manifest>\n")
            fp.write(EPub._T_opf_item.format(Id=u'ncx',
                href=u'toc.ncx', mime=u'application/x-dtbncx+xml'))
            for s in self.manifest:
                fp.write(EPub._T_opf_item.format(**s))
            fp.write(u"  </manifest>\n")
            
            fp.write(u"  <spine toc=\"ncx\">\n")
            for s in self.toc:
                fp.write(EPub._T_opf_itemref.format(**s))
            fp.write(u"  </spine>\n")
            
            if self.cover is not None:
                fp.write(u"    <guide>\n")
                fp.write(EPub._T_opf_reference.format(type=u'cover',
                    title=u'Cover', href=u'cover.xthml'))
                fp.write(u"    </guide>\n")

            fp.write(u"</package>\n")


    def enHref(self, href):
        '''encode href by converting space( ) into %20'''
        return re.sub(u' ', u'%20', href)            
        
    def enId(self, Id, href=None):
        '''encode id by converting space( ) into dash(-)'''
        if Id is None:
            Id = re.sub(ur'^.*\/', u'', href)
        return re.sub(u' ', u'-', Id)
    
    def defaultMime(self, fname):
        '''get MIME from file name (extension)'''
        try:
            ext = os.path.splitext(os.path.basename(fname))[1]
            return unicode(EPub._mime[ext])
        except:
            return None
        
    def copyResFile(self, name, dst = 'Images'):
        ''' Copy a file into resource folder /res, when filename
        is duplicated, check the content. If the content is the same,
        reuse that file, other wise a new name is generated with sequence appended.
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
        ''' Compare content of two files.
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

class MySoup(BeautifulSoup):
    '''
    Extract content from downloaded html files, using BeautifulSoup
    '''
    def __init__(self, src, encode = 'utf-8', selector = None):
        if os.path.exists(src):
            with codecs.open(src, 'r', encode) as fp:
                BeautifulSoup.__init__(self, fp)
            self.filename = src
            self.sourceString = None
        else:
            BeautifulSoup.__init__(self, src)
            self.filename = None
            self.sourceString = src
        self.selector = selector
        c = self.select(selector)
        if c:
            self.mainContent = c[0]
        else:
            self.mainContent = self.body
        self.img = []
        self.styles = [ c.get('href')
            for c in self.find_all('meta', rel= 'stylesheet') ]
    
    def images(self):
        ''' list all <img> in mainContent'''
        return self.mainContent.find_all('img')
    
    def title(self):
        ''' return title of the page if exists'''
        try:
            # get first head, what ever
            t = self.mainContent.find(re.compile(r'^h\d'))
            if t:
                return unicode(t.get_text())
            # -- alternate: get 1st h1, else 1st h2, else 1st h3
            # t = (self.mainContent.h1 or
            #        self.mainContent.h2 or self.mainContent.h3)
            # if len(t) > 0:
            #     return str(' '.join(t.stripped_strings))
            s = unicode(self.head.title.string)
            s = re.sub(ur'.*>\s*', u'', s)
            return s
        except Exception as ex:
            print 'MySoup.title:', ex
            return None
    
    def extractInPageAnchors(self, pattern=None):
        anchors = self.mainContent.select('a[name]')
        if pattern is None:
            pattern = r'^sec'
        for c in anchors:
            try:
                name = c['name']
                if re.match(pattern, name): pass
                elif c.string is None or c.tag == '':
                    c.extract()
            except: pass
        
    def cleanPage(self):
        ''' clean page '''
        # clean class/id for h1, h2, ...
        for h in self.mainContent.find_all(re.compile(r'^h\d')):
            if 'class' in h: del h['class']
            if 'id' in h: del h['id']
        # clean onclick/class for anchors
        for a in self.mainContent.select('a[onclick]'):
            del a['onclick']
        for a in self.mainContent.select('a[class]'):
            del a['class']
        # decompose hidden inputs
        for h in self.mainContent.select('input[type="hidden"]'):
            h.decompose()
        # decompose script
        for h in self.mainContent.select('script'):
            h.decompose()
        # decompose iframe
        for h in self.mainContent.select('iframe'):
            h.decompose()
        # unwrap font
        for h in self.mainContent.select('font'):
            h.unwrap()
        # unwrap tables that have only one <td> for "boxed" (safari)
        for t in self.mainContent.select('table'):
            tds = t.select('td')
            if len(tds) == 1:
                tag = tds[0]
                tag.name = 'div'
                tag['class'] = 'box'
                t.replace_with(tag)
        # decompose "Code View: Scroll/Show All" (safari)
        for h in self.mainContent.select('div.codeSegmentsExpansionLinks'):
            h.decompose()
        # decompose comment container (O'Reilly)
        for h in self.mainContent.select('div.comment_container'):
            h.decompose()
        
    def output(self, prettify=False, selector=None, unwrap=False):
        try:
            if selector:
                mo = re.match(r'tianya-?(.*)', selector)
                if mo is not None:
                    return self.tianya(mo.group(1))
                else:
                    tag = self.select(selector)
                    if not tag: return
                    tag = tag[0]
            else:
                tag = self.mainContent 

            # extract anchors
            for a in self.mainContent.select('a[href]'):
                a.unwrap()
            if unwrap:
                tag.name = 'div'
                for a in [ x for x in tag.attrs ]:
                    if a != 'class':
                        del tag[a]

            if prettify:
                return unicode(tag.prettify())
            else:
                return unicode(tag)
        except Exception as ex:
            print "Exception(MySoup.output):", ex
            return ''

    def tianya(self, mode=None):
        if mode:
            tag = self.find_all('td')[1]
        else:
            tag = self.find_all('td')[1]
        for s in tag.find_all(['div', 'p', 'a']):
            s.extract()
        for s in tag.find_all(['center', 'font']):
            s.unwrap()
        try:
            ps = []
            for s in tag.stripped_strings:
                if s in [u'下一页', u'上一页', u'后一页', u'前一页', u'回目录', u'回首页']:
                    continue
                ps.append(u'<p>{0}</p>\n'.format(s))
            return unicode(u''.join(ps))
        except Exception as ex:
            print('tianya:', ex)








if __name__ == "__main__":

    def usage():
        print '''epub.py [options] [ source ]

        -j              get config from json file
        -c|--cover      cover image file, jpg/png/svg please
        -a|--author     author of the book (default: Unknown)
        -t|--title      title of the book (default: Unknown)
        -e|--epub       name of epub
        -s|--selector   selector of content (default: div.htmlcontent)
        -u|--unwrap     unwrap selector (default: false)
        -r|--root       epub root directory (default: epub)
        --count         first count files (for debug only)
        --encode        default is UTF-8
        --dry           dry run

        settings in json are overridden by command-line options
'''

    def getConfig():
        ''' load configuration from json and command-line options '''
        #default configuration
        cfg = {
            'src':      None,
            'root':     'epub',
            'selector': 'div.htmlcontent',
            'title':    'Unknown',
            'author':   'Unknown',
            'cover':    None,
            'epub':     None,
            'unwrap':   False,
            'encode':   'utf-8',
            'count':    0,
        }

        try:
            opt_short = 'c:a:t:s:j:hr:e:du'
            opt_long = ['cover=', 'author=', 'title=',
                        'selector=', 'help', 'root=',
                        'count=', 'unwrap', 'dry' ]
            opts, files = getopt.getopt(sys.argv[1:], opt_short, opt_long)
        except getopt.GetoptError as err:
            print err
            usage()
            sys.exit(2)
    
        # check/load source and default config
        if len(files) > 0:
            src = files[0]
            if not os.path.exists(src):
                print 'source {0} doesn\'t exist\n'.format(src)
                sys.exit(2)
        else:
            src = os.getcwd()
        cfg['src'] = src
        defaultJson = '{0}/epub.json'.format(src)
        if os.path.exists(defaultJson):
            for jk,jv in loadJson(defaultJson).items():
                cfg[jk] = jv

        # load configuration first from json if defined
        for o,v in opts:
            if o == '-j':
                for jk,jv in loadJson(v).items():
                    cfg[jk] = jv
            elif o == '-h' or o == '--help':
                usage()
                sys.exit(0)

        # use command to set or to override json
        for o,v in opts:
            if o == '-j': pass          # processed already
            elif o == '-a' or o == '--author':
                cfg['author'] = v
            elif o == '-t' or o == '--title':
                cfg['title'] = v
            elif o == '-c' or o == '--cover':
                cfg['cover'] = v
            elif o == '-s' or o == '--selector':
                cfg['selector'] = v
            elif o == '-e' or o == '--epub':
                cfg['epub'] = v
            elif o == '-r' or o == '--root':
                cfg['root'] = v
            elif o == '-u' or o == '--unwrap':
                cfg['unwrap'] = True
            elif o == '--encode':
                cfg['encode'] = v
            elif o == '--count':
                print 'count=', v
                cfg['count'] = v
            elif o == '--dry':
                cfg['dry'] = True
    
        return cfg
    
    def loadJson(name):
        ''' Load configuration from json file '''
        try:
            with codecs.open(name, 'r', 'utf-8') as fp:
                return json.load(fp)
        except Exception as ex:
            print 'Fail to load json:' + ex
            return {}




    cfg = getConfig()
    # google-doc: div#gc-content div
    epub = EPub(cfg)
    epub.parse(verbose=True)
    print 'compressing ...'
    epub.zip()
    print '-'*40, 'done'

