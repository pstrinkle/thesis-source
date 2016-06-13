#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Summer 2011
#
# This builds strips out user entries from a master file given a removal
# file.
#

import sys
import re

def usage():
    print "usage: %s <major file> <removal file> <output file>" % sys.argv[0]

def main():

    # Did they provide the correct args?
    if len(sys.argv) != 4:
        usage()
        sys.exit(-1)

    # Pull Master File
    with open(sys.argv[1], "r") as f:
        master_lines = f.readlines()

    # Pull Removal File
    with open(sys.argv[2], "r") as f:
        removal_lines = f.readlines()
        for i in range(len(removal_lines)):
            removal_lines[i] = removal_lines[i].replace("\n", "").strip()
    
    x = 1
    y = 0
    with open(sys.argv[3], "w") as f:
        for master_line in master_lines:
            m = re.search(r"(\d+?) ", master_line)
            if m:
                print "handling line: %d" % x
                if m.group(1) in removal_lines:
                    print "found guy!"
                    y += 1
                else:
                    f.write(master_line)
            x += 1
    
    print "lines processed: %d" % x
    print "lines removed: %d" % y

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
