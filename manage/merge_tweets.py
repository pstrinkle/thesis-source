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
    print "usage: %s <file 1> <file 2> ... <file n> <output_file>" % sys.argv[0]
    print "       cat file1 and 2 into output file"
    print "       the output_file is an xml database of the tweets sorted by user id"
    print "       sadly it is redundant in xml form"

def main():

    # Did they provide the correct args?
    if len(sys.argv) < 4:
        usage()
        sys.exit(-1)

    input_files = []
    
    # starts at one... so we need to take it out of the upper limit?
    for i in range(1, len(sys.argv) - 1):
        input_files.append(sys.argv[i])
    
    output_file = sys.argv[len(sys.argv) - 1]
    
    print input_files
    print output_file

    tweets = {}
    line_count = 0
    tweet_count = 0
    set_count = 0
    for input_file in input_files:
        with codecs.open(input_file, "r", 'utf-8') as fout:
            lines = fout.readlines()
            print "lines read: %d" % len(lines)
            for i in range(len(lines)):
                l = lines[i].strip()
                
                line_count += 1
                info = re.search("<user_id>(\d+?)</user_id>", l)
                if info:
                    tid = int(info.group(1))
                    if tid not in tweets:
                        tweets[tid] = []
                    if l not in tweets[tid]:
                        tweets[tid].append(l)
                        set_count += 1
                    tweet_count += 1
                else:
                    sys.stderr.write("non matching line: '%s'" % l)

                # so we always have 100 percentage increments.
                if i % (len(lines) / 100) == 0:
                    print "%f%%" % ((float(i) / len(lines)) * 100)

    print "user count:  %d" % len(tweets)
    print "line count: %d" % line_count
    print "tweet count: %d" % tweet_count
    print "set count: %d" % set_count

    # Sort by user id.
    tweetkeys = tweets.keys()
    tweetkeys.sort()
    
    with codecs.open(output_file, "w", 'utf-8') as fout:
        for tk in tweetkeys:
            for tw in tweets[tk]:
                fout.write(tw + u"\n")

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
