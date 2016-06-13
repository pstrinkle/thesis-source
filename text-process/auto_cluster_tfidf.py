#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

##
# @author: Patrick Trinkle
# Spring 2012
#
# @summary: This script is meant to encompass: tweets_by_user, 
# pull_from_database, and cluster_words.
#
# This will find the users from the specified database with at least X tweets
# in the database.  It will then pull those tweets one user at a time and then
# attempts to clean them up and categorize them by clustering by their tf-idf
# similarities and choosing the highest scored terms as the category label.
#
# The tweet centroids are merged if their similarity score is greater than the
# standard deviation of all similarities in the user's set.
#
# The tf-idf library code here is of my own design.  It is fairly standard, 
# except I don't throw out singletons.  Maybe I should?

import os
import sys
import math
import time
import sqlite3
import threading
import multiprocessing

sys.path.append(os.path.join("..", "tweetlib"))
import tweetclean

sys.path.append(os.path.join("..", "modellib"))
import vectorspace
import centroid

def usage():
    print "usage: %s <sqlite_db> <min> <max> <stopwords> <output_folder>" \
        % sys.argv[0]

def thread_main(database_file, output_folder, users, stopwords, start, cnt):
    """
    What, what! : )
    """
    query_tweets = "select id, contents as text from tweets where owner = %d;"
    users_tweets = {}

    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row

    # --------------------------------------------------------------------------
    # Process this thread's users.
    for u in xrange(start, start + cnt):
        user_id = users[u]
        users_tweets = {}
        output = "%d\t%d\t%d\t%fm"

        start = time.clock()

        for row in conn.cursor().execute(query_tweets % user_id):
            if row['text'] is not None:
                users_tweets[row['id']] = \
                    tweetclean.cleanup(row['text'], True, True)

        curr_cnt = len(users_tweets)

        doc_tfidf, ignore = vectorspace.build_doc_tfidf(users_tweets, stopwords)

        # ----------------------------------------------------------------------
        centroids = centroid.cluster_documents(doc_tfidf)

        duration = (time.clock() - start) / 60 # for minutes

        print output % (user_id, curr_cnt, len(centroids), duration)

        with open(os.path.join(output_folder, "%d.topics" % user_id), "w") as f:
            f.write("user: %d\n#topics: %d\n" % (user_id, len(centroids)))
            # Might be better if I just implement __str__ for Centroids.
            for cen in centroids:
                f.write("%s\n" % str(centroids[cen]))
            f.write("-------------------------------------------------------\n")

    conn.close()

def main():

    # Did they provide the correct args?
    if len(sys.argv) != 6:
        usage()
        sys.exit(-1)

    cpus = multiprocessing.cpu_count()

    # --------------------------------------------------------------------------
    # Parse the parameters.
    database_file = sys.argv[1]
    minimum = int(sys.argv[2])
    maximum = int(sys.argv[3])
    stop_file = sys.argv[4]
    output_folder = sys.argv[5]
  
    if minimum >= maximum:
        usage()
        sys.exit(-2)

    # Pull stop words
    stopwords = tweetclean.import_stopwords(stop_file)

    kickoff = \
"""
-------------------------------------------------------------------
parameters  :
  database  : %s
  minimum   : %d
  maximum   : %d
  output    : %s
  stop      : %s
-------------------------------------------------------------------
"""

    print kickoff % (database_file, minimum, maximum, output_folder, stop_file) 

    # this won't return the 3 columns we care about.
    query_collect = "select owner from tweets group by owner having count(*) >= %d and count(*) < %d;"

    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row

    c = conn.cursor()

    # --------------------------------------------------------------------------
    # Search the database file for users.
    users = []

    start = time.clock()

    for row in c.execute(query_collect % (minimum, maximum)):
        users.append(row['owner'])

    print "query time: %f" % (time.clock() - start)
    print "users: %d\n" % len(users)

    conn.close()

    # --------------------------------------------------------------------------
    # Process those tweets by user set.

    print "usr\tcnt\tend\tdur"

    cnt = int(math.ceil((float(len(users)) / cpus)))
    remains = len(users)
    threads = []

    for i in range(0, cpus):
        start = i * cnt

        if cnt > remains:
            cnt = remains

        t = threading.Thread(
                             target=thread_main,
                             args=(
                                   database_file,
                                   output_folder,
                                   users,
                                   stopwords,
                                   start,
                                   cnt,))
        threads.append(t)
        t.start()

        remains -= cnt

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()

