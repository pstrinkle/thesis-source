#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Spring 2012
#
# This attempts to process tweets with LDA from the gensim library 
# implementation.
#

import os
import sys
import math
import time
import sqlite3
import logging
import threading
import multiprocessing

#logging.basicConfig(
#                    format='%(asctime)s : %(levelname)s : %(message)s',
#                    level=logging.INFO)

from gensim import corpora, models

sys.path.append(os.path.join("..", "tweetlib"))
import tweetclean

def usage():
    print "usage: %s <database> <min> <max> <stopwords> <output_folder>" \
        % sys.argv[0]

def thread_main(database_file, output_folder, users, stopwords, start, cnt):
    """
    Process the users in your range!
    
    Each thread gets its own hook into the database, so they don't interfere.
    
    I could use the whole Queue thing... but I don't feel like trying to get 
    that to work as well.
    """

    query_tweets = "select id, contents as text from tweets where owner = %d;"
    users_tweets = {}

    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row

    c = conn.cursor()

    # --------------------------------------------------------------------------
    # Process this thread's users.
    for j in xrange(start, start + cnt):
        user_id = users[j]
        print "processing: %d" % user_id
        for row in c.execute(query_tweets % user_id):
            if row['text'] is not None:
                users_tweets[row['id']] = \
                    tweetclean.cleanup(row['text'], True, True)

        # only words that are greater than one letter and not in the stopword 
        # list.
        texts = [[word for word in users_tweets[uid].split() \
                  if word not in stopwords and len(word) > 1] \
                    for uid in users_tweets]

        # ----------------------------------------------------------------------
        # remove words that appear only once
        all_tokens = sum(texts, [])
        tokens_once = set(word for word in set(all_tokens) \
                          if all_tokens.count(word) == 1)
        texts = [[word for word in text if word not in tokens_once] \
                    for text in texts]

        dictionary = corpora.Dictionary(texts)
        # store the dictionary, for future reference
        #dictionary.save(os.path.join("lda_out", '%d.dict' % user_id))

        corpus = [dictionary.doc2bow(text) for text in texts]
        # store to disk, for later use
        #corpora.MmCorpus.serialize(
        #                           os.path.join(
        #                                        output_folder,
        #                                        '%d.mm' % user_id),
        #                           corpus)

        # ----------------------------------------------------------------------
        # is this different...
        #corpus = \
        #    corpora.MmCorpus(os.path.join(output_folder, '%d.mm' % user_id))
    
        lda = models.ldamodel.LdaModel(
                                       corpus,
                                       id2word=dictionary,
                                       chunksize=100,
                                       passes=20,
                                       num_topics=100)
        #lda.save('%d.lda' % user_id)

        # ----------------------------------------------------------------------
        topic_strings = lda.show_topics(topics= -1, formatted=True)
        # shit, they share an output_file, so they could interrupt each other.
        ### so switch to individual files...
        ###
        with open(os.path.join(output_folder, "%d.topics" % user_id), "w") as f:
            f.write("user: %d\n#topics: %d\n" % (user_id, len(topic_strings)))
            for topic in topic_strings: # could use .join
                f.write("%s\n" % str(topic))

    conn.close()

def main():

    # Did they provide the correct args?
    if len(sys.argv) != 6:
        usage()
        sys.exit(-1)

    cpus = multiprocessing.cpu_count()

    database_file = sys.argv[1]
    minimum = int(sys.argv[2])
    maximum = int(sys.argv[3])
    stop_file = sys.argv[4]
    output_folder = sys.argv[5]

    if minimum >= maximum:
        usage()
        sys.exit(-2)

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

    # --------------------------------------------------------------------------
    # Pull stop words
    stopwords = tweetclean.import_stopwords(stop_file)

    # --------------------------------------------------------------------------
    # Read in the database
    query_collect = \
        "select owner from tweets group by owner having count(*) >= %d and count(*) < %d;"

    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row

    c = conn.cursor()

    # --------------------------------------------------------------------------
    # Search the database file for users.
    users = []
    start_time = time.clock()

    for row in c.execute(query_collect % (minimum, maximum)):
        users.append(row['owner'])

    print "%fs" % (time.clock() - start_time)

    conn.close()

    # --------------------------------------------------------------------------
    # Process those tweets by user set.

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

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
