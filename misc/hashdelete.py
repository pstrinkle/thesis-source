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
    deleted = 0
    
    for path in misc.get_file(startpoint):
        
        if path.lower().endswith(misc.PATH_DISQUALIFIERS):
            continue
        
        with open(path, "r") as f:
            sys.stderr.write(path + "\n")
            
            contents = f.read()
            hash = hashlib.sha512(contents).hexdigest()
            
            if hash in file_hashes:
                sys.stderr.write("possible duplicate\n")
                alen = os.stat(file_hashes[hash]).st_size
                blen = os.stat(path).st_size
                
                # They're the same size.
                if alen == blen:
                    f2 = open(file_hashes[hash])
                    contents2 = f2.read()
                    f2.close()
                    
                    if contents == contents2:
                        print "deleted: %s" % path
                        #os.unlink(path)
                        deleted += blen
                
            else:
                file_hashes[hash] = path

    print "Deleted: %d bytes" % deleted

if __name__ == "__main__":
    main()
