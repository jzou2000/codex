#! /usr/bin/python
# -*- coding: UTF-8 -*-

import re
from bs4 import BeautifulSoup



class xnode:
    def __init__(self, tag = None, n = None):
        self.tag = tag
        self.n = n

class XPath:

    def __init__(self, xpath):
        self.xpath = xpath
        node = re.split(r'/', self.xpath)
        self.node = [ self.parseNode(n) for n in node ]
        if len(self.node) == 0 or self.node[-1].tag is None:
            raise Exception('Bad xpath: {}'.format(self.xpath))

    def showPath(self):
        for t in self.node:
            print('tag={}[{}]'.format(t.tag or '', t.n or ''))

    def parseNode(self, token):
        ''' parse a node in xpath
            currently support format "tag[digit|last]"
        '''
        if token == '':
            return xnode()
        m = re.match(r'([*a-z_0-9-]+)(\[(.*?)\])?', token, flags=re.I)
        if m:
            return xnode(m.group(1), m.group(3))
        else:
            raise Exception('    not match: {}'.format(token))

    def find(self, doc):
        ''' find all tags in doc that matches xpath
        '''
        n = 0
        if self.node[0].tag is None:
            # start from root, we always do that
            n = 1
        return self._find(doc, n)

    def _find(self, doc, n):
        ''' find all tags in one of node chain
            doc         current doc.node
            n           n-th node in xpath
        '''
        print '-'*40
        print '_find({}) tag={}[{}]'.format(n, self.node[n].tag, self.node[n].n)
        print doc
        node = self.node[n]
        result = []
        if node.tag is None:
            # descendants (at any depth)
            while (self.node[n].tag is None):
                n += 1
            node = self.node[n] 
            tags = self._findTag(doc, node.tag, node.n, recursive=True)
        else:
            # children (direct descendants) only
            tags = self._findTag(doc, node.tag, node.n)

        if n + 1 == len(self.node):
            # this is the last node in xpath chain
            result = tags
        else:
            print '----found leve={} {} tags'.format(n, len(tags))
            for tc in tags:
                print '----{}'.format(tc.name)
            for tc in tags:
                result.extend(self._find(tc, n + 1))
        return result

    def _findTag(self, doc, tag = '*', n = None, recursive = False):
        ''' find a tag from childre/descendents by name and sequence '''
        print 'find tag({}[{}]) {}'.format(tag, n or '', 'recursively' if recursive else '')
        result = []
        nmax = len(doc.contents)
        print '    {} children'.format(nmax)
        ti = 0
        for i, c in enumerate(doc.contents):
            found = False
            try:
                print '        {} {}'.format(i, c.name)
                if tag == '*' or c.name == tag:
                    ti += 1
                    if n is None or self.matchSequence(ti, n, nmax):
                        found = True
            except Exception, ex:
                pass
                #print 'Exception: {}'.format(ex)
            if found:
                print '    append tag {} No.{}'.format(c.name, ti)
                result.append(c)
            if recursive:
                print 'recursivly call'
                result.extend(self._findTag(c, tag, n, recursive))
        print '_findTag return'
        return result

    def matchSequence(self, i, n = None, nmax = None):
        print 'match i={} n={} {}'.format(i, n, type(n))
        if isinstance(n, int):
            # compare integer directly
            return i == n
        elif isinstance(n, str):
            # compare string 
            if re.match(r'\d+$', n):
                return i == int(n)
            if n == 'last':
                return nmax is None or i == nmax;
        raise Exception('unknown sequence')

if __name__ == '__main__':
    doc = '''
<html>
<head><title>sample</title></head>
<body>
<table><tbody><tr><td>something at head</td></tr></tbody></table>

<table><tbody>
<tr>
  <td>block 1</td>
</tr>
<tr>
  <td>content</td>
</tr>
<tr>
  <td>block 3</td>
</tr>
</tbody></table>

<table><tbody><tr><td>something more</td></tr></tbody></table>
<table><tbody><tr><td>something even more</td></tr></tbody></table>
<table><tbody><tr><td>tail</td></tr></tbody></table>
</body>
</html>
'''
    path = '/html/body/table[2]/tbody/tr[2]'
#    path = '/html/body/table[2]'
    xp = XPath(path)
    bs = BeautifulSoup(doc)
    #print 'dump top children'
    #for c in bs:
    #    print c.name
    print '\nNow going to find'
    tag = xp.find(bs)
    print '='*50
    print '\nresult'
    for i,t in enumerate(tag):
        print '-'*20, i + 1, '-'*20
        print t


