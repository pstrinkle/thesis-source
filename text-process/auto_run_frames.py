#! /usr/bin/python
"""Runs build_frames.py repatedly via auto-generated configuration files."""

__author__ = 'tri1@umbc.edu'

##
# @author: Patrick Trinkle
# Spring 2012
#
# @summary: Runs build_frames.py with auto-generated varied parameters.
#

import os
import sys
import subprocess

sys.path.append(os.path.join("..", "tweetlib"))
from tweetdate import MONTHS

def usage():
    """Standard usage message."""

    sys.stderr.write("%s <output_file>\n" % sys.argv[0])
    sys.stderr.write("\tedit the script to change the template\n")

def main():
    """Main."""

    if len(sys.argv) != 2:
        usage()
        sys.exit(-1)

    output_file = sys.argv[1]
    
    output = ""
    config_file = "temp.cfg"
    
    # maybe we should read the template in from an input file.
    template = \
"""
[input]
database_file = /Users/pstrink/dissert/tweets/tweets.db
# root_dir is currently unused.
root_dir = /Users/pstrink/dissert/tweets/
year = %d
month = %s
stopwords = ../stopwords.txt
remove_singletons = True
build_rgb_images = True
build_grey_images = False
build_csv_files = False
full_users = False

[run100]
output_folder = %d_%s_100
request_value = 100
"""

    # --------------------------------------------------------------------------
    # Build list of config files.
    #
    # We ran to run from 2006_Jan to 2012_Feb ?

    for year in range(2005, 2012):
        for month in MONTHS:
            with open(config_file, 'w') as fout:
                fout.write(template % (year, month, year, month))

            print "running: %d_%s" % (year, month)

            # ------------------------------------------------------------------
            # Launch framemaker for each configuration file.
            process = \
                subprocess.Popen(
                                 ['python', 'build_frames.py', config_file],
                                 shell=False,
                                 stdout=subprocess.PIPE)

            output += process.communicate()[0]
            #print process.communicate()[0]

    # --------------------------------------------------------------------------
    # Done.

    with open(output_file, 'w') as fout:
        fout.write(output)

if __name__ == "__main__":
    main()
