#! /usr/bin/python
# -*- coding: UTF-8 -*-

import os, sys, re, getopt, time, random, codecs
import json
import urllib, urlparse
from bs4 import BeautifulSoup

''' pingfandeshijie

  div.main
    h1
    div.info                                    x
    div.content
      div[style: float|clear,id,clsss]          x
      h3[id='comments']            x
      class=ad-.*, navigation, respond
      ol.class=commentlist
'''

def UrlPath(url):
    ''' divide url into path/file '''
    m = re.match(r'(.*)/(.*)', url)
    if m:
        return m.group(1), m.group(2)
    else:
        return None, url

def loadJson(fname):
    ''' Load configuration from json file '''
    try:
        print "load json from " + fname
        with codecs.open(fname, 'r', 'utf-8') as fp:
            return json.load(fp)
    except Exception as ex:
        print 'Fail to load json:' + ex
        raise ex

def dumpJson(jo):
    ''' Dump the content of json object '''
    print json.dumps(jo, sort_keys=True, indent=4, encoding='utf-8')

class MyTask:
    '''Get a list of url'''
    def __init__(self, opt):
        self.opt = opt

    def run1(self, base, pattern, col):
        for s in col:
            fname = pattern.format(s)
            url = '{0}/{1}'.format(base, fname)
            target = UrlTarget(url, fname)
            target.download()
            time.sleep(2.3)

    def run(self):
        ''' load files from an index page, file URLs in index'''
        url = self.opt['url']
        url_path, fname = UrlPath(url)
        if url_path is None:
            url_path = 'http://vip.book.sina.com.cn/book'
        upr = urlparse.urlparse(url)
        soup = MySoup(url, 'index-url.html')
        itag = soup.get(self.opt['selectorIndex'])

        links = itag.find_all('a')
        nn = 1
        fnameTemp = u'{seq:03d}.html'
        for h in links:
            if 'target' in h:
                del h['target']
            title = h.string
            href = str(h['href'])
            if re.match(r'^http:', href):
                pass
            if re.match(r'^/', href):
                href = upr[1] + href # ParseResult.netloc
            else:
                href = '{}/{}'.format(url_path, href)


            fname = fnameTemp.format(seq=nn)
            h['href'] = fname

            v = u'{}\n    {}={}'.format(title, fname, href)
            print v.encode('UTF-8')
            if not os.path.exists(fname):
                spage = MySoup(href, fname)
                beef = spage.get(self.opt['selectorPage'])
                spage.save(beef, fname, title)
                ri = random.randint(1,100)/10.0
                print 'sleep({:.1f})...'.format(ri)
                time.sleep(ri)
            nn += 1

        soup.save(itag, 'index.html', self.opt['title'])


class MySoup(BeautifulSoup):
    '''
    Extract content from URL, and convert encoding into utf-8
    '''
    _temp = ur'''<html>
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

    def __init__(self, url, cache=None):
        self.url = url
        self.cache = cache
        try:
            f = None
            if self.cache is not None and os.path.exists(self.cache):
                fname = self.cache
                f = open(self.cache, 'r')
            else:
                fname = self.url
                f = urllib.urlopen(self.url)
            page = f.read()
            f.close()
            if self.cache is not None and not os.path.exists(self.cache):
                with open(self.cache, 'w') as f:
                    f.write(page)

            m = re.search(r'charset=([^ "\']+)', page, flags=re.I)
            if m:
                encoding = m.group(1)
                print 'encoding={}\n    {}'.format(encoding, fname)
                charset = 'charset={}'.format(encoding)
                page = unicode(page, encoding)
                page = re.sub(charset, 'charset=UTF-8', page, flags=re.I)
            #print page.encode('utf-8')
            BeautifulSoup.__init__(self, page)
        except Exception, ex:
            print("Fail to load url {}\n{}".format(self.url, ex))
            raise ex

    def save(self, soup, fname, title=None):
        #print u'save: fname={} title={}'.format(fname, title)
        c = soup.prettify()
        t = title
        s = MySoup._temp.format(title=unicode(t), content=c)
        with codecs.open(fname, 'w', 'utf-8') as fp:
            fp.write(s)

    def get(self, selector):
        if 'selector' not in selector:
            raise Exception('selector is not defined')
        tags = self.select(selector['selector'])
        if len(tags) < 1:
            raise Exception('"{}" not found in {}'.format(selector['selector'], self.url))
        if len(tags) == 1:
            tag = tags[0]
        else:
            tag = self.new_tag('div')
            for i in tags:
                tag.append(i)

        if 'include' in selector:
            sfi = selector['include']
            if isinstance(sfi, unicode):
                for i in tag.select(sfi):
                    i['mybs'] = 1
            elif isinstance(sfi, list):
                for f in sfi:
                    for i in tag.select(f):
                        i['mybs'] = 1
            else:
                raise Exception('unknown include')
            itags = tag.select('[mybs]')
            if len(itags) == 0:
                return None
            elif len(itags) == 1:
                tag = itags[0]
                del tag['mybs']
            else:
                tag = self.new_tag('div')
                for i in itags:
                    del i['mybs']
                    tag.append(i)

        if 'exclude' in selector:
            sfx = selector['exclude']
            if isinstance(sfx, unicode):
                for i in tag.select(sfx):
                    i.extract()
            elif isinstance(sfx, list):
                for x in sfx:
                    for i in tag.select(x):
                        i.extract()
            else:
                raise Exception('unknown exclude')

        return tag

class UrlTarget:
    def __init__(self, url, fname=None):
        ''' download URL into fname
            if fname is not specified, try to extract the  from the URL
        '''
        self.url = url
        if fname is None:
            match = re.match(r'.+/(.*)', self.url)
            if match:
                self.fname = match.group(1)
            else:
                raise Exception('no file name in URL')
        else:
            self.fname = fname
        print('url={}, file={}'.format(self.url, self.fname))

    def download(self):
        try:
            f = urllib.urlopen(self.url)
            s = f.read()
            f.close()
            with open(self.fname, 'w') as f:
                f.write(s)
        except Exception, ex:
            print('Exception: %s\n' % ex)


if __name__ == '__main__':

    def usage():
        print '''geturl.py -j json'''


    try:
        opt_short = 'j:'
        opt_long = ['url=', 'index=']
        opts, files = getopt.getopt(sys.argv[1:], opt_short, opt_long)
    except getopt.GetoptError as err:
        print err
        sys.exit(2)
    opt = {}

    for o,v in opts:
        if o == '-j':
            for jk, jv in loadJson(v).items():
                opt[jk] = jv
        elif o == '--help' or o == '-h':
            usage()
            sys.exit(0)
        elif o == '--url':
            opt['url'] = v
        elif o == '--index':
            opt['index'] = v
        elif o == '--name':
            opt['name'] = v

    testIndex = False
    testPage = False
    if testIndex:
        bs = MySoup(opt['url'], cache=opt['sample']['index'])
        beef = bs.get(opt['selectorIndex'])
        bs.save(beef, 'aaa.html', 'testIndex')
    if testPage:
        bs = MySoup(opt['url'], cache=opt['sample']['page'])
        beef = bs.get(opt['selectorPage'])
        bs.save(beef, 'bbb.html', 'testPage')

    task = MyTask(opt)
    task.run()

    #task.run1('http://www.pingfandeshijie.com', 'di-san-bu-{0:02d}.html', range(1, 55))

