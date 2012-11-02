#! /usr/bin/python

import os, re, time
import urllib

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

class MyTask:
    '''Get a list of url'''
    def run1(self, base, pattern, col):
        for s in col:
            fname = pattern.format(s)
            url = '{0}/{1}'.format(base, fname)
            target = UrlTarget(url, fname)
            target.download()
            time.sleep(2.3)

class UrlTarget:
    def __init__(self, url, fname=None):
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
    task = MyTask()
    task.run1('http://www.pingfandeshijie.com', 'di-san-bu-{0:02d}.html', range(1, 55))

