#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Spring 2011
#
# This tries to build a word level histogram (sketch) for each
# day's tweets.
# OR
# This tries to build a word level histogram (sketch) for each
# hour's tweets.
#
# This opens the xml file holding the tweets, and builds a giant
# tweet for each day, by appending the previous day's tweets.
#
# My goal is tokenize the string and then remove the words that aren't.
#

import os
import sys
import operator

sys.path.append(os.path.join("..", "tweetlib"))
sys.path.append(os.path.join("..", "modellib"))
import tweetclean
import tweetdate
import vectorspace

def usage():
    print "usage: %s (daily|hourly) <input file> <out:matrix file> <out:similarity file>" % sys.argv[0]

def main():
    # Weirdly in Python, you have free access to globals from within main().

    hourlyInterval = 0 # are we building hourly or daily histograms?
    docLength = 0      # total count of all terms
    daysTweets = {}    # dictionary of the tweets by date as integer
                                          # dictionary of the tweets by date-hour as integer
                                          
    docFreq = {}       # dictionary of in how many documents the "word" appears
    invdocFreq = {}    # dictionary of the inverse document frequencies
    docTermFreq = {}   # dictionary of term frequencies by date as integer
    docTfIdf = {}      # similar to docTermFreq, but holds the tf-idf values

    # Did they provide the correct args?
    if len(sys.argv) != 5:
        usage()
        sys.exit(-1)

    # Parse command line
    if sys.argv[1] == "hourly":
        hourlyInterval = 1
    elif sys.argv[1] == "daily":
        pass
    else:
        usage()
        sys.exit(-1)

    # Pull lines
    with open(sys.argv[2], "r") as f:
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
        if hourlyInterval:
            date = tweetdate.buildDateInt(info[0])
        else:
            date = tweetdate.buildDateDayInt(info[0])

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
    
    docLength = {}
    
    for day in daysTweets.keys():
        docTermFreq[day] = {} # Prepare the dictionary for that document.
        
        # Calculate Term Frequencies for this day/document.
        # Skip 1 letter words.
        for w in daysTweets[day].split(' '):
            if len(w) > 1:
                try:
                    docLength[day] += 1
                except KeyError:
                    docLength[day] = 1
                
                try:
                    docTermFreq[day][w] += 1
                except KeyError:
                    docTermFreq[day][w] = 1

        # Contribute to the document frequencies.
        for w in docTermFreq[day]:
            try:
                docFreq[w] += 1
            except KeyError:
                docFreq[w] = 1

    # --------------------------------------------------------------------------
    # Dump how many unique terms were identified by spacing splitting.
    # Dump how many days of tweets we collected.
    # For each day of tweets, dump how many unique terms were identified by space splitting.
    #
    print "sizeof documents: %s" % docLength
    print "sizeof docFreq: %d" % len(docFreq)         # this is how many unique terms
    print "sizeof docTermFreq: %d" % len(docTermFreq) # this is how many days

    for day in docTermFreq:
        print "sizeof docTermFreq[%s]: %d" % (str(day), len(docTermFreq[day])) # this is how many unique terms were in that day
        #print docTermFreq[day]

    # --------------------------------------------------------------------------
    # Remove singletons -- standard practice.
    # Skipped with tweets for now...

    # Calculate the inverse document frequencies.
    invdocFreq = vectorspace.calculate_invdf(len(docTermFreq), docFreq)
    
    # Calculate the tf-idf values.
    docTfIdf = vectorspace.calculate_tfidf(docLength, docTermFreq, invdocFreq)

    # Recap of everything we have stored.
    # docLength      is the total count of all terms
    # daysTweets     is the dictionary of the tweets by date as integer
    # docFreq        is the dictionary of in how many documents the "word" appears
    # invdocFreq     is the dictionary of the inverse document frequencies
    # docTermFreq    is the dictionary of term frequencies by date as integer
    # docTfIdf       is similar to docTermFreq, but holds the tf-idf values

    # Sort the lists by decreasing value and dump the information.
    # TODO: Upgrade this to print the top 15-20 or so.
    sorted_keys = sorted(docTfIdf.keys())

    print "token:weight"
    for day in sorted_keys:
        print str(day) + ":---"
        sorted_tokens = sorted(
                               docTfIdf[day].items(),
                               key=operator.itemgetter(1), # (1) is value
                               reverse=True)
        for k, v in sorted_tokens:
            print k + ":" + str(v)

    # Dump the matrix.
    with open(sys.argv[3], "w") as f:
        f.write(vectorspace.dumpMatrix(docFreq, docTfIdf) + "\n")

    # Computer cosine similarities between sequential days.
    sorted_days = sorted(docTfIdf.keys())
    with open(sys.argv[4], "w") as f:
        # -1 because each goes +1
        for i in xrange(0, len(sorted_days) - 1):
            f.write("similarity(%s, %s) = " % (str(sorted_days[i]), str(sorted_days[i + 1])))
            f.write(str(vectorspace.cosineCompute(docTfIdf[sorted_days[i]], docTfIdf[sorted_days[i + 1]])) + "\n")

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()

