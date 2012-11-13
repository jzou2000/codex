#! /usr/bin/python

import time, os
import threading

class Demo(threading.Thread):
    sid = 0

    def __init__(self, name):
        threading.Thread.__init__(self)
        Demo.sid = Demo.sid + 1
        self.name = name
        self.id = Demo.sid
        print ('Demo({})={}\n'.format(self.name, self.id))

    def run(self):
        repeat = 10
        for i in range(repeat):
            s = ' ' * (self.id * 16)
            print('{0} {1}: {2}'.format(s, self.name, i))
            time.sleep(1.2)
            



if __name__ == '__main__':
	app1 = Demo('app1')
	app2 = Demo('app2')
	app1.start()
	app2.start()
	app1.join()
	app2.join()
	
