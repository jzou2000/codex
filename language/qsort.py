#! /usr/bin/env python

import sys, time, random

''' Use quick sort algorithm for data from shuffle.py

The result on a linux (fedora 18) with 4 cores @2.40G 4GB Mem

[jzou@luigi language]$ ./qsort.py r1m.txt
load:  1.07
qsort:  7.82
validate:  0.3
build-in sort(): 0.93

for reference to C++ version
    load: 0.19
    qsort: 0.50
    validate: 0.03
    std::sort: 0.50

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
        c1 = click()

        click()
        d2 = data[:]    # make a copy for compare
        c5 = click()

        click()
        qsort(data)
        c2 = click()

        click()
        for i in range(len(data)):
            if data[i] != i:
                print 'qsort failed'
                break
        c3 = click()

        click()
        d2.sort()
        c4 = click()

        print 'load: ', c1
        print 'qsort: ', c2
        print 'validate: ', c3
        print 'duplicate: ', c5
        print 'build-in sort(): ', c4
    except Exception as ex:
        print 'Exception: ', ex


