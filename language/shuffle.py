#! /usr/bin/env python

import sys, time, random

''' Generate a list shuffle integers and save them in a file.
    The file can be used as source for different sort/search algorithms.
'''

if len(sys.argv) == 2 and sys.argv[1] == '-h':
    print 'usage: shuffle.py count-of-element [ output-file-name = stdout ]'
    sys.exit()

try:
    count = int(sys.argv[1])
    if count < 20:
        count = 20
except Exception as ex:
    count = 20

c1 = time.clock()
nv = range(count)
c2 = time.clock()
random.seed()
random.shuffle(nv)
c3 = time.clock()
maxlen = 78

# output integers in lines upto maxlen chars
try:
    fp = open(sys.argv[2], 'w')
except Exception as ex:
    fp = sys.stdout

c4 = time.clock()
s = []                  # buffered line
sn = 0                  # chars in buffered line
for i in nv:
    si = str(i)
    ni = len(si)
    if sn > 0:
        sn += ni + 1    # plus a space before the new item
    else:
        sn = ni
    if sn > maxlen:     # flush buffered line
        fp.write(' '.join(s))
        fp.write('\n')
        s = []
        sn = ni
    s.append(si)
if s > 0:               # last line if exists
    fp.write(' '.join(s))
    fp.write('\n')
c5 = time.clock()
if fp != sys.stdout:
    fp.close()

print 'create: ', c2-c1
print 'shuffle: ', c3-c2
print 'output: ', c5-c4

''' The result on a linux (fedora 18) with 4 cores @2.40G 4GB Mem

[jzou@luigi language]$ ./shuffle.py 1000000 r1m.txt
create:  0.05
shuffle:  0.75
output:  1.54
[jzou@luigi language]$ ./shuffle.py 5000000 r5m.txt
create:  0.26
shuffle:  4.02
output:  8.08
[jzou@luigi language]$ ls -lh *.txt
-rw-rw-r-- 1 jzou jzou 6.6M Mar  5 11:56 r1m.txt
-rw-rw-r-- 1 jzou jzou  38M Mar  5 11:56 r5m.txt

'''

