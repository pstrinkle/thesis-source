#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Just me toying around with threads, so I can get some speedup!

import sys
import time
import math
import threading
import multiprocessing

def whatsit(start, cnt):
    #print "start: %d cnt %d" % (start, cnt)
    time.sleep(5)

def main():
    cpus = multiprocessing.cpu_count()

    stuff = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    threads = []

    cnt = int(math.ceil((float(len(stuff)) / cpus)))

    print "len :  %d" % len(stuff)
    print "cpus:  %d" % cpus
    print "count: %d" % cnt
    #if len(stuff) % 2: print "isodd"
    
    remains = len(stuff)

    for i in range(0, cpus):
        
        start = i * cnt
        
        if start > len(stuff) - 1:
            break

        # not likely still necessary
        #if len(stuff) % 2 and i == cpus-1:
            #cnt += 1

        if cnt > remains:
            cnt = remains

        print "process: "
        for j in range(start, start + cnt):
            print "%d\t" % stuff[j]

        #t = threading.Thread(target=whatsit,args=(start, cnt,))
        #threads.append(t)
        #t.start()
        
        remains -= cnt

    #for t in threads:
        #t.join()

if __name__ == "__main__":
    main()
