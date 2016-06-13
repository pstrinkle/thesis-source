#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Summer 2011
#
# Because I got worried that I would hit the limit of the number of files you're
# allowed to have; this moves the system back into a single flat file database.
#
# Okay.  I don't have a column for the total tweets; because that number is 
# increasing all the time; so why care?

import re
import sys
import codecs
import sqlite3
import datetime

sys.path.append("tweetlib")
import tweetxml as tx
import tweetdatabase as td

def usage():
    """."""
    
    sys.stderr.write("usage: %s <stream|main> <input_file> <sqlite_db>\n" \
                    % sys.argv[0])

def main():
    """."""

    # --------------------------------------------------------------------------
    # Did they provide the correct args?
    if len(sys.argv) != 4:
        usage()
        sys.exit(-1)

    start_time = datetime.datetime.now()

    db_type = sys.argv[1]
    input_file = sys.argv[2]
    database_file = sys.argv[3]

    if db_type == "stream":
        tweet_tbl = "s_tweets"
    elif db_type == "main":
        tweet_tbl = "tweets"
    else:
        usage()
        sys.exit(-1)

    # This test is just running to see how big the database file gets when it's 
    # just users.
    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row

    c = conn.cursor()

    # --------------------------------------------------------------------------
    # Read in the database files and write out the giant database file.    
    with codecs.open(input_file, "r", "utf-8") as fin:
        for tweet in fin:
            i = re.search("<user_id>(\d+?)</user_id>.+?<id>(\d+?)</id>", tweet)
            if i:
                user_id = int(i.group(1))
                
                print user_id
                twt_id = int(i.group(2))

                c.execute("select * from %s where id = ?" \
                          % tweet_tbl, (twt_id,))

                row = c.fetchone()

                if row == None:
                    sys.stderr.write("missing tweet id %d\n" % twt_id)
                    conn.close()
                    sys.exit(-1)

                if not td.compare_tweets(
                                         tx.Tweet(user_id, tweet),
                                         td.DbTweet(row)):
                    sys.stderr.write("non-match, argh on tweet id %d!\n" \
                                     % twt_id)
                    conn.close()
                    sys.exit(-1)
            else:
                print "ugh"

    # --------------------------------------------------------------------------
    # Close it down.
    conn.close()

    # --------------------------------------------------------------------------
    # Done.

    print "total runtime: ",
    print (datetime.datetime.now() - start_time)

if __name__ == "__main__":
    main()
