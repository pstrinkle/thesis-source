#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Summer 2011
#
# This builds a massive table of information, including how many users have geo
# tweets. how many tweets have been collected.  etc.
#

import re
import os
import sys
import codecs

sys.path.append("tweetlib")
import tweetdatabase as td

def usage():
    print "usage: %s <database_folder> <output_file>" % sys.argv[0]

def main():

    # Did they provide the correct args?
    if len(sys.argv) != 3:
        usage()
        sys.exit(-1)

    # --------------------------------------------------------------------------
    # Parse the parameters.
    database_folder = sys.argv[1]
    output = sys.argv[2]

    print "database folder: %s" % database_folder
    
    # collecting certain information can be done more rapidly with grep -rn/wc -l.
    stats = {
                      'user_count'     : 0, # number of users
                      'user_geo_count' : 0, # number of users with geo tags
                      'user_twt_count' : 0, # number of users with tweets (collected)
                      'user_frd_count' : 0  # number of users with friends (identified)
                      }
    
    # --------------------------------------------------------------------------
    # Search the database file for certain things.
    for input_file in td.fileWalk(database_folder):
        #print "processing: %s, len(since_ids): %d" % (input_file, len(since_ids))
        with codecs.open(input_file, "r", 'utf-8') as f:
            ux = f.read()
            usr = re.search("\t<id>(\d+?)</id>\n", ux)
            if usr:
                stats['user_count'] += 1
                if "<geo>" in ux:
                    stats['user_geo_count'] += 1
                if "<tweets>" in ux:
                    stats['user_twt_count'] += 1
                if "<friends>" in ux:
                    stats['user_frd_count'] += 1
            else:
                sys.stderr.write("invalid user file: %s" % input_file)
                sys.exit(-1)

    # --------------------------------------------------------------------------
    # Output results.
    
    with open(output, "w") as f:
        for x in stats:
            f.write("%s:%d\n" % (x, stats[x]))

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
