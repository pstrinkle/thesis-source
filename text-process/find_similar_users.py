#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

##
# @author: Patrick Trinkle
# Spring 2012
#
# @summary: This program builds a tf-idf matrix.
#

import os
import sys
import sqlite3

sys.path.append(os.path.join("..", "tweetlib"))
import tweetclean

sys.path.append(os.path.join("..", "modellib"))
import vectorspace
import centroid

def data_pull(database_file, query):
    """Pull the data from the database."""
    
    user_tweets = {}
    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row
    
    for row in conn.cursor().execute(query):
        if row['text'] is not None:
            data = tweetclean.cleanup(row['text'], True, True)
            try:
                user_tweets[row['owner']].append(data)
            except KeyError:
                user_tweets[row['owner']] = []
                user_tweets[row['owner']].append(data)

    conn.close()

    return user_tweets

def usage():
    """Standard usage message."""
    
    print "%s <database_file> <minimum> <maximum> <stop_file> <output>" % \
        sys.argv[0]

def main():
    """Main."""

    if len(sys.argv) != 6:
        usage()
        sys.exit(-1)

    # --------------------------------------------------------------------------
    # Parse the parameters.
    database_file = sys.argv[1]
    minimum = int(sys.argv[2])
    maximum = int(sys.argv[3])
    stop_file = sys.argv[4]
    output_file = sys.argv[5]

    if minimum >= maximum:
        print "minimum is larger than maximum"
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

    print kickoff % (database_file, minimum, maximum, output_file, stop_file) 

    # this won't return the 3 columns we care about.
    query_collect = "select owner from tweets group by owner having count(*) >= %d and count(*) < %d"
    query_prefetch = "select owner, id, contents as text from tweets where owner in (%s);"

    query = query_prefetch % query_collect

    user_tweets = data_pull(database_file, query % (minimum, maximum))

    print "data pulled"
    print "user count: %d" % len(user_tweets)

    # --------------------------------------------------------------------------
    # Convert to a documents into one document per user.

    docperuser = {} # array representing all the tweets for each user.

    for user_id in user_tweets:
        docperuser[user_id] = " ".join(user_tweets[user_id])

    if len(docperuser) == 1:
        sys.stderr.write("Insufficient data for tf-idf, only 1 document\n")
        sys.exit(-3)

    tfidf, dictionary = vectorspace.build_doc_tfidf(docperuser, stopwords, True)
    
    # --------------------------------------------------------------------------
    # Build Centroid List
    centroids = []

    for doc, vec in tfidf.iteritems():
        centroids.append(centroid.Centroid(str(doc), vec))

    similarities = centroid.get_sims(centroids)
    average_sim = centroid.find_avg(centroids, True, similarities)
    stddev_sim = centroid.find_std(centroids, True, similarities)
    
    print "mean: %.10f\tstd: %.10f" % (average_sim, stddev_sim)
    
    # --------------------------------------------------------------------------
    # Merge centroids by highest similarity of at least threshold
    # the standard deviation is a distance, for the value you must position it.
    threshold = (average_sim + stddev_sim)

    while len(centroids) > 1:
        print "centroids: %d" % len(centroids)
        i, j, sim = centroid.find_max(centroids)
        print "\t%d, %d, %f" % (i, j, sim)

        # @warning: This is fairly crap.
        if sim >= threshold:
            centroids[i].add_centroid(centroids[j])
            del centroids[j]
            print "merged with sim: %.10f" % sim
        else:
            break

    print "len(centroids): %d" % len(centroids)
    print "avg(centroids): %.10f" % average_sim
    print "std(centroids): %.10f" % stddev_sim
    
    for cen in centroids:
        print centroid.top_term_tuples(cen, 10)

    with open(output_file, "w") as fout:
        for cen in centroids:
            fout.write("%s\n" % cen)

    sys.exit(0)

    # Maybe I should determine the top tf-idf values per document and then make
    # that my dictionary of terms. =)
    #
    # Originally, I intended to use clustering to get topics, but really those
    # are just high tf-idf terms that are common among certain documents...

    top_dict = set()

    for doc_id in tfidf:
        terms = vectorspace.top_terms(tfidf[doc_id], 250)
        #print "terms of %d: %s" % (doc_id, terms)
        for term in terms:
            top_dict.add(term)

    print "total top terms (not the set): %d" % (250 * len(tfidf))
    print "top dict: %d" % len(top_dict)

    # Dump the matrix.
    with open(output_file, "w") as fout:
        #fout.write(vectorspace.dump_raw_matrix(dictionary, tfidf) + "\n")
        fout.write(vectorspace.dump_raw_matrix(top_dict, tfidf) + "\n")

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
