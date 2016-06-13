#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Summer 2011
#
# Stuff.
#

import sys
import random

def usage():
    """Parameters."""
    
    sys.stderr.write("usage: %s num_val range <ouput>\n" % sys.argv[0])

def main():

    if len(sys.argv) != 4:
        usage()
        sys.exit(-1)
    
    num_val = int(sys.argv[1])
    range_val = int(sys.argv[2])
    file_out = sys.argv[3]
    
    # uses system time
    random.seed()
    
    with open(file_out, "w") as f:
        values = [random.randint(1, range_val) for i in range(num_val)]
        
        f.write("%d\n".join(values))
    
        print "sum: %d" % sum(values)

if __name__ == "__main__":
    main()
