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
        print self.xpath
        for t in self.node:
            print('tag={0}[{1}]'.format(t.tag or '', t.n or ''))

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
        print '_find({0}) tag={1}[{2}]'.format(n, self.node[n].tag, self.node[n].n)
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
            print '----found leve={0} {1} tags'.format(n, len(tags))
            for tc in tags:
                print '----{0}'.format(tc.name)
            for tc in tags:
                result.extend(self._find(tc, n + 1))
        return result

    def _findTag(self, doc, tag = '*', n = None, recursive = False):
        ''' find a tag from childre/descendents by name and sequence '''
        try:
            myname = doc.name
        except:
            return []
        print myname + '.findTag({0}[{1}]) {2}'.format(tag, n or '', '+' if recursive else '')
        result = []
        nmax = len(doc.contents)
        print '    {0} children'.format(nmax)
        ti = 0
        for i, c in enumerate(doc.contents):
            found = False
            try:
                print '        {0} {1}'.format(i, c.name)
                if tag == '*' or c.name == tag:
                    ti += 1
                    if n is None or self.matchSequence(ti, n, nmax):
                        found = True
            except Exception, ex:
                pass
                #print 'Exception: {0}'.format(ex)
            if found:
                print '    append tag {0} No.{1}'.format(c.name, ti)
                result.append(c)
            elif recursive:
                print '    recursivly call'
                result.extend(self._findTag(c, tag, n, recursive))
        print myname + '.findTag return'
        return result

    def matchSequence(self, i, n = None, nmax = None):
        print 'match i={0} n={1} {2}'.format(i, n, type(n))
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
        <tr> <td>block 1</td> </tr>
        <tr> <td>content</td> </tr>
        <tr> <td>block 3</td> </tr>
    </tbody></table>
    
    <table><tbody><tr><td>something more</td></tr></tbody></table>
    <div class="frame">
      <div id="title">
          <p>Title</p>
      </div>
      <p>introduction</p>
      <div class="content text">
      Once upon a time, there are three little pigs.
      </div>
      <div class="text">
      Other stories
      </div>
      powered by
    </div>
    <table><tbody><tr><td>something even more</td></tr></tbody></table>
    <table><tbody><tr><td>tail</td></tr></tbody></table>
</body>
</html>
'''
    path = '//table[2]/tbody/tr[2]'
#    path = '/html/body/table[2]'
    xp = XPath(path)
    xp.showPath()
    bs = BeautifulSoup(doc)
    doc = bs.html
    #print 'dump top children'
    #for c in bs:
    #    print c.name
    print '\nNow going to find'
    tag = xp.find(doc)
    print '='*50
    print '\nresult'
    for i,t in enumerate(tag):
        print '-'*20, i + 1, '-'*20
        print t


