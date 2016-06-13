#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Summer 2011
#
# This attempts to collate the tweet files and remove duplicates
# given an entire folder of xml files, instead of using sort/uniq
# on a per file basis.
#

import re
import sys
import codecs

def usage():
    print "usage: %s <xml_tweets>" % sys.argv[0]

def main():

    # --------------------------------------------------------------------------
    # Did they provide the correct args?
    if len(sys.argv) != 2:
        usage()
        sys.exit(-1)

    tweets_input = sys.argv[1]
    
    bad = []
    for i in range(0, 31):
        # newline and tab.  Tweets cannot have newline, but they can have tab.
        if i != 0x0a and i != 0x09:
            bad.append(chr(i))

    # --------------------------------------------------------------------------
    # Read in the new tweets
    #
    # The trick is to read in the user file first, then add the tweets for that 
    # user.
    with codecs.open(tweets_input, "r", 'utf-8') as f:
        for line in f:
            l = line.strip()
            twt_info = \
                re.search("<user_id>(\d+?)</user_id><tweet>(.+?)</tweet>", l)
            
            if twt_info:
                for b in bad: # now checks for invalid values.
                    if b in l:
                        sys.stderr.write("invalid character '%s'" % l)
                        sys.exit(-2)
                pass
            else:
                sys.stderr.write("non-matching '%s'" % l)
                sys.exit(-2)

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
