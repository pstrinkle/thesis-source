#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Spring 2011
#
# This tries to build a 3-gram level histogram (sketch) for each
# day's tweets.
#
# This opens the ~xml file holding the tweets, and builds a giant
# tweet for each day, by appending the previous day's tweets.
#
# My goal is tokenize the string and then remove the words that aren't.
#
# TODO: Add command line parameters.
#

import os
import sys

sys.path.append(os.path.join("..", "tweetlib"))
sys.path.append(os.path.join("..", "modellib"))
import tweetdate
import tweetclean
import vectorspace

def usage():
    print "usage: %s <input file>" % sys.argv[0]

def main():

    daysTweets = {} # dictionary of the tweets by date as integer
    docFreq = {}    # dictionary of document frequencies
    daysHisto = {}  # dictionary of the n-grams by date as integer

    # Did they provide the correct args?
    if len(sys.argv) != 2:
        usage()
        sys.exit(-1)

    # Pull lines
    with open(sys.argv[1], "r") as f:
        tweets = f.readlines()

    print "tweets: %d" % len(tweets)

    # --------------------------------------------------------------------------
    # Process tweets
    for i in tweets:
        # Each tweet has <created>DATE-TIME</created> and <text>DATA</text>.
        #
        # So we'll have a dictionary<string, string> = {"date", "contents"}
        #
        # So, we'll just append to the end of the string for the dictionary
        # entry.
        info = tweetclean.extract(i)
        if info == None:
            sys.exit(-1)
        
        # Build day string
        # This needs to return -1 on error, so I'll need to test it.
        date = tweetdate.buildDateInt(info[0])

        # Do some cleanup
        newTweet = tweetclean.cleanup(info[1])

        # Add this tweet to the collective tweet for the day.
        if date in daysTweets:
            daysTweets[date] += " " + newTweet
        else:
            daysTweets[date] = newTweet

    # End of: "for i in tweets:"
    # Thanks to python and not letting me use curly braces.

    # --------------------------------------------------------------------------
    # Process the collected tweets
    print "tweet days: %d" % len(daysTweets)
    gramSize = 3

    for day in sorted(daysTweets.keys()):
        daysHisto[day] = {} # initialize the sub-dictionary
        totalDaysTerms = 0  # for normalizing the term frequencies, so days with more tweets don't skew values.

        # This gives me values, starting at 0, growing by gramSize for length of the tweet.
        # range(0, len(daysTweets[day]), gramSize)
        # This should give you values, starting at 0 for length of the tweet.
        # range(0, len(daysTweets[day]), 1)
        #
        for j in range(0, len(daysTweets[day]), gramSize):
            # this doesn't seem to do the sliding window I was expecting but rather just chunks it.
            w = daysTweets[day][j:j + gramSize]
            
            # wu is a special format that will not screw with whitespace
            wu = "_%s_" % w
            totalDaysTerms += 1
            
            try:
                daysHisto[day][wu] += 1
            except KeyError:
                daysHisto[day][wu] = 1

            try:
                docFreq[wu] += 1
            except KeyError:
                docFreq[wu] = 1

        # print results to file for day.
        # unsorted
        for gram in daysHisto[day]:
            # I am making it smaller by the size of the document.
            v = float(daysHisto[day][gram]) / totalDaysTerms
            daysHisto[day][gram] = v

    # daysHisto Contains normalized term frequencies, not tf-idf values.
    # Normalized to account for the length of the document.  It would not
    # be difficult to modify it to contain tf-idf values.  It would just have
    # to wait until all processing is complete.

    # Dump the matrix.
    print vectorspace.dumpMatrix(docFreq, daysHisto) + "\n"

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()

