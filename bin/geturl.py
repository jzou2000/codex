#! /usr/bin/python
# -*- coding: UTF-8 -*-

import os, sys, re, getopt, time, random, codecs
import json
import urllib2, urlparse
from bs4 import BeautifulSoup

'''
example usage of urlparse

>>> import urlparse
>>> ref = "http://site/doc/index.html"
>>> u1 = "a.html"
>>> u2 = 'ch1/s1.html'
>>> u3 = '/book/ch2/s2.html'
>>> urlparse.urlparse(ref)
ParseResult(scheme='http', netloc='site', path='/doc/index.html', params='', query='', fragment='')
>>> ref2 = "http://site/doc"
>>> urlparse.urlparse(ref2)
ParseResult(scheme='http', netloc='site', path='/doc', params='', query='', fragment='')
>>> urlparse.urljoin(ref, u1)
'http://site/doc/a.html'
>>> urlparse.urljoin(ref, u2)
'http://site/doc/ch1/s1.html'
>>> urlparse.urljoin(ref, u3)
'http://site/book/ch2/s2.html'
>>> 

'''


def loadJson(fname):
    ''' Load configuration from json file '''
    try:
        with codecs.open(fname, 'r', 'utf-8') as fp:
            return json.load(fp)
    except Exception as ex:
        print 'Fail to load json: ' + ex
        raise ex

def dumpJson(jo):
    ''' Dump the content of json object '''
    print json.dumps(jo, sort_keys=True, indent=4, encoding='utf-8')




class MyTask:
    '''Get a list of url'''
    def __init__(self, opt):
        self.opt = opt

    def run(self):
        ''' load files from an index page, file URLs in index'''
        url = self.opt['url']
        soup = MySoup(url, 'index-cache.html')
        tagIndex = soup.get(self.opt['selectorIndex'])

        nn = 1
        fnameTemp = u'{seq:03d}.html'
        for h in tagIndex.find_all('a'):
            if 'target' in h:
                del h['target']
            title = h.string
            href = urlparse.urljoin(url, str(h['href']))
            fname = fnameTemp.format(seq=nn)
            h['href'] = fname

            v = u'{}\n    {}={}'.format(title, fname, href)
            print v.encode('UTF-8')
            if not os.path.exists(fname):
                spage = MySoup(href, fname)
                beef = spage.get(self.opt['selectorPage'])
                spage.save(beef, fname, title)
                sleep_time = random.randint(1,100)/10.0
                print 'sleep({:.1f})...'.format(sleep_time)
                time.sleep(sleep_time)
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
                # cache exists and use it instead
                fname = self.cache
                f = open(self.cache, 'r')
            else:
                fname = self.url
                f = urllib2.urlopen(self.url)
            page = f.read()
            f.close()
            if self.cache is not None and not os.path.exists(self.cache):
                # cache specified but it doesn't exist, create one
                with open(self.cache, 'w') as f:
                    f.write(page)
            # check encoding and convert into utf-8 if it is not
            #     alternation: use from_encoding="encoding"
            #         todo: can from_encoding replace charset=?
            m = re.search(r'charset=([^ "\']+)', page, flags=re.I)
            if m:
                encoding = m.group(1)
                ##print 'encoding={}\n    {}'.format(encoding, fname)
                charset = 'charset={}'.format(encoding)
                if re.match(r'gb2312', encoding, re.IGNORECASE):
                    encoding = 'gb18030'
                page = unicode(page, encoding)
                page = re.sub(charset, 'charset=UTF-8', page, flags=re.IGNORECASE)
            BeautifulSoup.__init__(self, page)
        except Exception, ex:
            print("Fail to load url {}\n{}".format(self.url, ex))
            raise ex

    def save(self, soup, fname, title=None, template = None):
        ''' save soup into a file using given template '''
        if template is None:
            template = MySoup._temp
        s = template.format(title=unicode(title), content=soup.prettify())
        with codecs.open(fname, 'w', 'utf-8') as fp:
            fp.write(s)

    def get(self, selector):
        ''' get a soup object according to the selector
            return object can be an object exists in self, or a new created div
            if multiple objects are selected.

            steps to get the result
            1. choose the 'root' from selector.selector
            2. choose from 'include' list
            3. remove from 'exclude' list
            
            each item (include/exclude) can be a css-selector or an xpath
            an xpath is identifed by preceeding 'xpath:'
            
        '''
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
            incList = []
            if isinstance(sfi, unicode):
                incList.extend(tag.select(sfi))
            elif isinstance(sfi, list):
                [ incList.extend(tag.select(f)) for f in sfi ]
            else:
                raise Exception('unknown include')
            if len(incList) == 0:
                return None
            elif len(incList) == 1:
                tag = incList[0]
            else:
                tag = self.new_tag('div')
                [tag.append(i) for i in incList]

        if 'exclude' in selector:
            sfx = selector['exclude']
            if isinstance(sfx, unicode):
                [ i.extract() for i in tag.select(sfx) ]
            elif isinstance(sfx, list):
                [ i.extract() for x in sfx for i in tag.select(x) ]
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

    def download(self):
        try:
            with urllib2.urlopen(self.url) as f:
                s = f.read()
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

    #task = MyTask(opt)
    #task.run()

    #task.run1('http://www.pingfandeshijie.com', 'di-san-bu-{0:02d}.html', range(1, 55))

