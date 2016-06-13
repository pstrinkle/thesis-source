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
import sqlite3

sys.path.append("tweetlib")
import tweetxml

def usage():
    print "usage: %s <sqlite_db> <excludes_list> (-all N|-nf N|-nt N|-gt N|-mint N M|-maxt N M)" % sys.argv[0]
    print "\t-nf N := users with no friends listed, first N users"
    print "\t-nt N := users with no tweets listed, first N users"
    print "\t-gt N := users with geo tags in at least one tweet, first N users"
    print "\t-mint N M := users with at least M tweets retrieved, first N users"
    print "\t-maxt N M := users with at most M tweets retrieved, first N users"
    print ""
    print "\tif N is 0; it doesn't limit the output"

def main():

    # Did they provide the correct args?
    if len(sys.argv) < 5 or len(sys.argv) > 6:
        usage()
        sys.exit(-1)

    # --------------------------------------------------------------------------
    # Parse the parameters.
    database_file = sys.argv[1]
    excludes_file = sys.argv[2]
    param = sys.argv[3]
    user_val = int(sys.argv[4])
    
    print "database folder: %s" % database_file
    print "excludes file: %s" % excludes_file
    print "first %d users" % user_val

    if len(sys.argv) == 6:
        if param == "-mint":
            min_tweets_cnt = int(sys.argv[5])
            print "min_tweets_cnt: %d" % min_tweets_cnt
            query = "select owner, min(id), max(id) from tweets group by owner having count(id) > %d" % min_tweets_cnt
        elif param == "-maxt":
            max_tweets_cnt = int(sys.argv[5])
            print "max_tweets_cnt: %d" % max_tweets_cnt
            query = "select owner, min(id), max(id) from tweets group by owner having count(id) < %d" % max_tweets_cnt
        else:
            usage()
            sys.exit(-1)
    elif len(sys.argv) == 5:
        if param == "-nf":
            # this won't return the 3 columns we care about.
            query = "select owner, min(id), max(id) from tweets where owner in (select user from users where friends is null) group by owner;"
        elif param == "-nt":
            query = "select user as owner, min(0), max(0) from users where user not in (select distinct owner from tweets);"
        elif param == "-gt":
            query = "select owner, min(id), max(id) from tweets where owner in (select distinct owner from tweets where geo is not null) group by owner;"
        elif param == "-all":
            query = "select owner, min(id), max(id) from tweets group by owner;"
        else:
            usage()
            sys.exit(-1)
    else:
        usage()
        sys.exit(-1)

    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row

    c = conn.cursor()

    excludes = []
    with codecs.open(excludes_file, "r", "utf-8") as f:
        for line in f:
            i = re.search("<id>(\d+?)</id>", line)
            if i:
                excludes.append(int(i.group(1)))

    # --------------------------------------------------------------------------
    # Search the database file for certain things.
    output_sofar = 0
    
    for row in c.execute(query):
        if output_sofar > user_val and user_val != 0:
            break
        if row['owner'] not in excludes:
            print "%s" % \
                tweetxml.output(row['owner'], row['min(id)'], row['max(id)'])
            output_sofar += 1

    # --------------------------------------------------------------------------
    # Done.
    conn.close()

if __name__ == "__main__":
    main()
