#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

##
# @author: Patrick Trinkle
# Summer 2011
#
# @summary: Stuff.
#

import os
import sys
import hashlib
import misc

def usage():
    """Parameters."""

    sys.stderr.write("usage: %s path\n" % sys.argv[0])

def main():

    if len(sys.argv) != 2:
        usage()
        sys.exit(-1)

    startpoint = sys.argv[1]
    fileHashes = {}
    
    for path in misc.get_file(startpoint):

        if path.lower().endswith(misc.PATH_DISQUALIFIERS):
            continue
            
        with open(path, "r") as f:
            sys.stderr.write(path + "\n")
                
            contents = f.read()
            hash = hashlib.sha512(contents).hexdigest()
            
            try:
                fileHashes[hash].append(path)
            except KeyError:
                fileHashes[hash] = []
                fileHashes[hash].append(path)

    for hash in fileHashes:
        if len(fileHashes[hash]) > 1:
            print "found possible duplicates"
            for f in fileHashes[hash]:
                print "\t%s : %d" % (f, os.stat(f).st_size)
            
if __name__ == "__main__":
    main()
