#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Spring 2012
#
# This attempts to convert tweets to the gensim input format.
#
# Abandoned.
#

import sys


def usage():
    print "usage: %s <database> <user_id> <input stopwords>" % sys.argv[0]

def main():

    # Did they provide the correct args?
    if len(sys.argv) != 4:
        usage()
        sys.exit(-1)

    database_file = sys.argv[1]
    user_id = int(sys.argv[2])
    stop_file = sys.argv[3]
    
    # --------------------------------------------------------------------------
    # Pull stop words
    stopwords = tweetclean.importStopWords(stop_file)

    # --------------------------------------------------------------------------
    # Read in the database
    query_tweets = "select id, contents as text from tweets where owner = %d;"
    users_tweets = {}
    
    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row

    c = conn.cursor()

    for row in c.execute(query_tweets % user_id):
        users_tweets[row['id']] = row['text']

    conn.close()

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
