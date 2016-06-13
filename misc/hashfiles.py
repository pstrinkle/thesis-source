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
    file_hashes = {}
    
    for path in misc.get_file(startpoint):
        with open(path, "r") as path:
            contents = path.read()
            hash = hashlib.sha512(contents).hexdigest()
            
            try:
                file_hashes[hash].append(path)
            except KeyError:
                file_hashes[hash] = []
                file_hashes[hash].append(path)

    for hash in file_hashes:
        if len(file_hashes[hash]) > 1:
            print "found possible duplicates"
            for path in file_hashes[hash]:
                print "\t%s" % path
            
if __name__ == "__main__":
    main()
