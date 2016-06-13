#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Summer 2011
#

import os
import sys
import datetime

def usage():
    sys.stderr.write("usage: %s <file_list>\n" % sys.argv[0])

def main():

    # --------------------------------------------------------------------------
    # Did they provide the correct args?
    if len(sys.argv) != 2:
        usage()
        sys.exit(-1)

    start_time = datetime.datetime.now()

    user_file = sys.argv[1]
    
    # --------------------------------------------------------------------------
    # Read in the database files and write out the giant database file.
    with open(user_file, "r") as fin:
        for path in fin:
            print path.strip()
            
            try:
                os.unlink(path.strip())
            except Exception:
                pass

    # --------------------------------------------------------------------------
    # Done.

    print "total runtime: ",
    print (datetime.datetime.now() - start_time)

if __name__ == "__main__":
    main()
