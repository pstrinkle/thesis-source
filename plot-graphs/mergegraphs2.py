#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

##
# @author: Patrick Trinkle
# Summer 2011
#
# @summary: Given a path to a bunch of data files, make one points file.
#

import os
import re
import sys

def usage():
    """."""

    print "usage: %s <input folder> <output file>" % sys.argv[0]
    print "\tthe files must be long lat count for this version"

def main():
    """."""

    # Did they provide the correct args?
    if len(sys.argv) != 3:
        usage()
        sys.exit(-1)

    folder = sys.argv[1]
    files = [os.path.join(folder, path) for path in os.listdir(folder) \
             if ".data" in path]
    output = sys.argv[2]

    # --------------------------------------------------------------------------
    # Build gnuplot input.
    
    points = {}
    
    for path in files:

        with open(path, "r") as fout:
            lines = fout.readlines()
            
            for line in lines:
                line_m = re.search("(.+? .+?) (\d+?)\n", line)
                
                if line_m:
                    longlat = line_m.group(1)
                    val = int(line_m.group(2))
                    
                    try:
                        points[longlat] += val
                    except KeyError:
                        points[longlat] = val

    with open(output, "w") as fout:
        fout.write("# lat long count\n")
        
        for point in points:
            fout.write("%s %d\n" % (point, points[point]))

    print "len: %d" % len(points)

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
