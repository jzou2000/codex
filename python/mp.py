#! /usr/bin/env python
# -*- coding: utf-8 -*-

import threading
from multiprocessing import Process, cpu_count
import time, os
import readline

class MyLock(object):
    ''' scope-base locker (like C++ RAII) that
     automatically release lock when the object goes out of scope
    '''
    def __init__(self, lock):
        self.lock = lock
        self.lock.acquire()

    def __del__(self):
        self.lock.release()

class Scope(object):
    ''' scope tracer
    '''
    def __init__(self, name):
        self.name = name
        print '++++++++ enter %s' % self.name

    def __del__(self):
        print '-------- leave %s' % self.name

class ScopeE(object):
    ''' scope tracer
    '''
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        print '++++++++ enter %s' % self.name

    def __exit__(self, exctype, excvalue, trace):
        print '-------- leave %s (%s %s %s)' % (self.name, str(exctype), str(excvalue), str(trace))



class MyTask(threading.Thread):
    def __init__(self, name = None, count=10, interval=0.4):
        #threading.Thread.__init__(self, name = name)
        super(MyTask, self).__init__(name=name)
        self.lock = threading.RLock()
        self.count = count
        self.interval = interval
        self.flagEnd = False

    def run(self):
        title = '    MyTask(%s)' % self.name
        for i in range(self.count):
            if self.isStop():
                print '%s: abort' % title
                break
            print '%s %d' % (title, i)
            time.sleep(self.interval)

    def stop(self):
        print 'require to stop'
        l = MyLock(self.lock)
        self.flagEnd = True

    def isStop(self):
        l = MyLock(self.lock)
        return self.flagEnd


class ProcessMonitor(object):
    def __init__(self):
        pass

    def start(self):
        '''
        :return:
        '''
        pass

    def startLocalTask(self):
        pass

    def myloop(self):
        '''

        :return:
        '''
        pass


def mywork(name, n, u):
    for i in range(n):
        time.sleep(u)
        print '%s %d' % (name, i)

def child():
    print 'this is child'
    #os.execlp('perl', 'perl', 'hello.pl')
    os.execl('hello', 'hello')
    #os.system('perl hello.pl')
    print 'return from execlp'



if __name__ == '__main__':
    import sys
    for i in range(2):
        with ScopeE('a %s' % i):
            print "hello"
        print i

    sys.exit(0)

    t = MyTask('task1')
    t.start()
    mywork('main', 4, .7)
    t.stop()
    t.join()

    '''
    n = cpu_count()
    #p = Process(target = foo, args=('CHILD', 10, .3))
    p = Process(target = child)
    p.start()
    mywork('Parent', 3, 1.8)
    p.join()
    '''
    print 'End'

