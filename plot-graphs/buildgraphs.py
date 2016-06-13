#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

##
# @author: Patrick Trinkle
# Summer 2011
#
# @summary: Given a path to a bunch of data files, plot them into a big eps 
# file.
#

import os
import sys
import subprocess

def usage():
    print "usage: %s <input folder> <output file>" % sys.argv[0]

def main():

    # Did they provide the correct args?
    if len(sys.argv) != 3:
        usage()
        sys.exit(-1)

    folder = sys.argv[1]
    files = [name for name in os.listdir(folder) if ".data" in name]
    output = sys.argv[2]

    # --------------------------------------------------------------------------
    # Build gnuplot input.
    
    params = "set terminal postscript\n"
    params += "set output '%s'\n" % output
    params += "set log xy\n"
    params += "set xlabel 'km from centroid'\n"
    params += "set ylabel '# occurrences'\n"
    
    for name in files:

        path = os.path.join(folder, name)
            
        params += "plot '%s' t 'User %s geo-location posts'\n" % (path, name)
    
    params += "q\n"

    print params

    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
