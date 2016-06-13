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
        
        if path.lower().endswith(misc.PATH_DISQUALIFIERS):
            continue

        with open(path, "r") as fin:
            sys.stderr.write(path + "\n")
            contents = fin.read(20 * 1024)
            hash = hashlib.sha512(contents).hexdigest()
            
            value = "%s : %d" % (path, os.stat(path).st_size)
            
            try:
                file_hashes[hash].append(value)
            except KeyError:
                file_hashes[hash] = []
                file_hashes[hash].append(value)

    for hash in file_hashes:
        if len(file_hashes[hash]) > 1:
            print "found possible duplicates:"
            for f in file_hashes[hash]:
                print "\t%s" % f
            
if __name__ == "__main__":
    main()
