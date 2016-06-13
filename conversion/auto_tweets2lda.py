#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Summer 2011
#
# Given one of my tweet XML repos, this formats the data to be input for Prof 
# Blei's LDA-C code.
#
# Under LDA, the words of each document are assumed exchangeable. 
# Thus, each document is succinctly represented as a sparse vector of word 
# counts.
#
# The data is a file where each line is of the form:
# [M] [term_1]:[count] [term_2]:[count] ...  [term_N]:[count]
# where [M] is the number of unique terms in the document, and the [count] 
# associated with each term is how many times that term appeared in the 
# document.  Note that [term_1] is an integer which indexes the term; it is not 
# a string.

import os
import sys
import sqlite3

sys.path.append("tweetlib")
import tweetdate
import tweetclean

def getIndx(vocab, term):
    """
    Given a vocabulary array and a term, return the index into the array; returns
      -1 if not present.
    """
    for i in xrange(len(vocab)):
        if term == vocab[i]:
            return i

    return -1

def usage():
    print "usage: %s <database> <minimum> <input stopwords> <out_folder>" % \
        sys.argv[0]

def main():

    # Did they provide the correct args?
    if len(sys.argv) != 5:
        usage()
        sys.exit(-1)

    database_file = sys.argv[1]
    minimum = int(sys.argv[2])
    stop_file = sys.argv[3]
    output_folder = sys.argv[4]

    # --------------------------------------------------------------------------
    # Pull stop words
    stopwords = tweetclean.importStopWords(stop_file)

    # --------------------------------------------------------------------------
    # Read in the database
    query_collect = "select owner from tweets group by owner having count(*) >= %d;"
    query_tweets = "select id, contents as text from tweets where owner = %d;"

    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    users = []

    for row in c.execute(query_collect % (minimum)):
        users.append(row['owner'])


    # --------------------------------------------------------------------------
    # Process those tweets by user set.
    for u in users:

        users_tweets = {}
        docTermFreq = {}   # dictionary of term frequencies by date as integer
        vocab = []         # array of terms

        for row in c.execute(query_tweets % u):
            users_tweets[row['id']] = row['text']

        # ----------------------------------------------------------------------
        # Process tweets
        for id in users_tweets:

            if users_tweets[id] == None: # this happens, lol.
                continue

            users_tweets[id] = tweetclean.cleanup(users_tweets[id], True, True)
        
            # Calculate Term Frequencies for this id/document.
            # Skip 1 letter words.

            # let's make a short list of the words we'll accept.
            pruned = [w for w in users_tweets[id].split(' ') \
                      if len(w) > 1 and w not in stopwords]

            # skip documents that only have one word.
            if len(pruned) < 2:
                continue

            docTermFreq[id] = {} # Prepare the dictionary for that document.

            for w in pruned:
                try:
                    docTermFreq[id][w] += 1
                except KeyError:
                    docTermFreq[id][w] = 1

                # slow. maybe linear search? maybe switch to a sorted method?
                if w not in vocab:
                    vocab.append(w)

        vocab.sort()

        # ----------------------------------------------------------------------
        # Build the vocab.txt file
        with open(os.path.join(output_folder, "%d.vocab" % u), 'w') as f:
            f.write("\n".join(vocab))
    
        # ----------------------------------------------------------------------
        # Given the vocab array, build the document term index + counts:
        sorted_tweets = sorted(docTermFreq.keys())
        data = ""
    
        for id in docTermFreq:
            print "%d" % id
            data += "%d " % len(docTermFreq[id])
        
            for term in docTermFreq[id]:
                indx = getIndx(vocab, term)
                if indx == -1:
                    sys.exit(-1)
                data += "%d:%d " % (indx, docTermFreq[id][term])
            
            data += "\n"

        with open(os.path.join(output_folder, "%d.dat" % u), "w") as f:
            f.write(data)
    
    # end for each user.

    # --------------------------------------------------------------------------
    # Done.
    conn.close()

if __name__ == "__main__":
    main()
