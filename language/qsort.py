#! /usr/bin/env python

import sys, time, random

''' Use quick sort algorithm for data from shuffle.py

The result on a linux (fedora 18) with 4 cores @2.40G 4GB Mem

[jzou@luigi language]$ ./qsort.py r1m.txt
load:  1.0
duplicate:  0.03
qsort:  7.8
validate:  0.29
buildin:  0.92

For reference run on the same machine
---------------------------------------------------------
             C        C++      java     perl
load:        0.16     0.17     0.70     0.46
duplicate    0.00     0.00     0.00     0.18
qsort:       0.27     0.50     0.15    12.88
qsort(O3):   0.12     0.12
validate:    0.00     0.03     0.00     0.12
buildin:     0.26     0.50     0.58     1.12
buildin(O3): 0.26     0.10

c++: std::sort
java: ArrayList.sort
perl: 5.16

It's about 15 times slower for 'pure' python codes.

'''


def dumpq(data, title=None):
    if title is not None:
        print title
    print ' '.join([ str(i) for i in data])

_clock_now = 0;
def click():
    global _clock_now
    v = time.clock()
    elapse = v - _clock_now
    _clock_now = v
    return elapse

def _qsort(data, start, end):
    if start >= end:
        return
    m = int((start + end) / 2)
    pivot = data[m]
    if m < end:
        data[m], data[end] = data[end], data[m]
    m = start
    for i in range(start, end):
        if data[i] < pivot:
            data[m], data[i] = data[i], data[m]
            m += 1
    data[m], data[end] = data[end], data[m]
    _qsort(data, start, m - 1)
    _qsort(data, m + 1, end)

def qsort(data):
    _qsort(data, 0, len(data) - 1)


if __name__ == '__main__':
    data = []
    try:
        click()
        with open(sys.argv[1], 'r') as fp:
            for line in fp:
                data.extend([ int(s) for s in line.split(' ')])
        print 'load: ', click()

        click()
        d2 = data[:]    # make a copy for compare
        print 'duplicate: ', click()

        click()
        qsort(data)
        print 'qsort: ', click()

        click()
        for i in range(len(data)):
            if data[i] != i:
                print 'qsort failed'
                break
        print 'validate: ', click()

        click()
        d2.sort()
        print 'buildin: ', click()

    except Exception as ex:
        print 'Exception: ', ex


