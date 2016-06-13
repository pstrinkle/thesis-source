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
import sqlite3
import logging

logging.basicConfig(
                    format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)

from gensim import corpora, models

sys.path.append(os.path.join("..", "tweetlib"))
import tweetclean

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
    stopwords = tweetclean.import_stopwords(stop_file)

    # --------------------------------------------------------------------------
    # Read in the database
    query_tweets = "select id, contents as text from tweets where owner = %d;"
    users_tweets = {}

    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row

    c = conn.cursor()

    for row in c.execute(query_tweets % user_id):
        if row['text'] is not None:
            users_tweets[row['id']] = \
                tweetclean.cleanup(row['text'], True, True)

    conn.close()

    # only words that are greater than one letter and not in the stopword list.
    texts = [[word for word in users_tweets[uid].split() \
              if word not in stopwords and len(word) > 1] \
                for uid in users_tweets]

    # remove words that appear only once
    all_tokens = sum(texts, [])
    tokens_once = set(word for word in set(all_tokens) \
                      if all_tokens.count(word) == 1)
    texts = [[word for word in text \
              if word not in tokens_once] for text in texts]

    dictionary = corpora.Dictionary(texts)
    # store the dictionary, for future reference
    dictionary.save('%d.dict' % user_id)

    corpus = [dictionary.doc2bow(text) for text in texts]
    # store to disk, for later use
    corpora.MmCorpus.serialize('%d.mm' % user_id, corpus)

    # is this different...
    corpus = corpora.MmCorpus('%d.mm' % user_id)
    
    model = models.ldamodel.LdaModel(
                                     corpus,
                                     id2word=dictionary,
                                     chunksize=100,
                                     passes=20,
                                     num_topics=100)
    model.save('%d.lda' % user_id)

    lda = models.ldamodel.LdaModel.load('%d.lda' % user_id)

    #lda.show_topics(topics=1, topn=1, log=False, formatted=True)
    # Unlike what the documentation might have you believe, you have to pull it
    # back as a string if you want to use it.
    topic_strings = lda.show_topics(topics= -1, formatted=True)
    print "#topics: %d" % len(topic_strings)
    for topic in topic_strings:
        print topic

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
