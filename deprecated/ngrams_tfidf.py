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

    docLength = 0 # total count of all terms
    daysTweets = {}    # dictionary of the tweets by date as integer
    invdocFreq = {}    # dictionary of the inverse document frequencies
    docFreq = {}       # dictionary of document frequencies
    daysHisto = {}     # dictionary of the n-grams by date as integer

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
    docLength = {}

    for day in sorted(daysTweets.keys()):
        daysHisto[day] = {} # initialize the sub-dictionary

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
            try:
                docLength[day] += 1
            except KeyError:
                docLength[day] = 1

            try:
                daysHisto[day][wu] += 1
            except KeyError:
                daysHisto[day][wu] = 1

            try:
                docFreq[wu] += 1
            except KeyError:
                docFreq[wu] = 1

    # Calculate the inverse document frequencies.
    invdocFreq = vectorspace.calculate_invdf(len(daysHisto), docFreq)

    # Calculate the tf-idf values.
    daysHisto = vectorspace.calculate_tfidf(docLength, daysHisto, invdocFreq)

    # Dump the matrix.
    #print vectorspace.dumpMatrix(docFreq, daysHisto) + "\n"

    # Computer cosine similarities between sequential days.
    sorted_days = sorted(daysHisto.keys())
    for i in range(0, len(sorted_days) - 1):
        print "similarity(%s, %s) = " % (str(sorted_days[i]), str(sorted_days[i + 1])),
        print vectorspace.cosineCompute(daysHisto[sorted_days[i]], daysHisto[sorted_days[i + 1]])

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()

