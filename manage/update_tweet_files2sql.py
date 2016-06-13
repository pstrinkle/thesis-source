#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Summer 2011
#
# Because I got worried that I would hit the limit of the number of files you're
# allowed to have; this moves the system back into a single flat file database.
#

import re
import sys
import codecs
import sqlite3
import datetime

sys.path.append("tweetlib")
import tweetdatabase as td

def usage():
    sys.stderr.write("usage: %s <stream|main> <input_file> <sqlite_db>\n" \
                     % sys.argv[0])

def main():

    # --------------------------------------------------------------------------
    # Did they provide the correct args?
    if len(sys.argv) != 4:
        usage()
        sys.exit(-1)

    startTime = datetime.datetime.now()

    type = sys.argv[1]
    input_file = sys.argv[2]
    database_file = sys.argv[3]

    if type == "stream":
        tweetTbl = "s_tweets"
    elif type == "main":
        tweetTbl = "tweets"
    else:
        usage()
        sys.exit(-1)

    print "database: %s" % database_file
    print "table: %s" % tweetTbl

    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row

    c = conn.cursor()
    
    # just so the screen changes as it goes.
    cnt = 0

    # --------------------------------------------------------------------------
    with codecs.open(input_file, "r", "utf-8") as fin:
        
        for tweet in fin:
            i = re.search("<user_id>(\d+)</user_id>", tweet)
            
            if i:
                user_id = int(i.group(1))
                cnt += 1
                print "%d - %d" % (user_id, cnt)
                
                try:
                    c.execute("insert into %s values (?,?,?,?,?,?,?,?,?,?,?)" % tweetTbl, td.tweet_insert(user_id, tweet))
                except sqlite3.IntegrityError:
                    print "already existed"
            else:
                print "what!"

    # --------------------------------------------------------------------------
    # Close it down.
    conn.commit()
    conn.close()

    # --------------------------------------------------------------------------
    # Done.

    print "total runtime: ",
    print (datetime.datetime.now() - startTime)

if __name__ == "__main__":
    main()
