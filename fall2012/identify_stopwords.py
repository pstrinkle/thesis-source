#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Spring 2012
#
# This attempts to collate the tweet files and remove duplicates
# given an entire folder of xml files, instead of using sort/uniq
# on a per file basis.
#
# Run tweets_by_user.py

import sys
import sqlite3
from json import dumps
from operator import itemgetter

import boringmatrix

sys.path.append("../modellib")
import vectorspace

def usage():
    """."""

    print "usage: %s X <sqlite_db> <cleaned_tokens.out> <dict.out> <newstops.out> <singles.out>" % sys.argv[0]
    print "\tX the first so many tokens to consider stop words."
    print "\tcleaned_tokens.out := sorted, cleaned document frequency dictionary."
    print "\tdict.out := alphabetically sorted tokens."
    print "\tnewstops.out := top X tokens."
    print "\tsingles.out := the singletons for the entire dataset."

def main():
    """."""

    # Did they provide the correct args?
    if len(sys.argv) != 7:
        usage()
        sys.exit(-1)

    # --------------------------------------------------------------------------
    # Parse the parameters.
    top_count = int(sys.argv[1])
    database_file = sys.argv[2]
    output_name = sys.argv[3]
    dict_out = sys.argv[4]
    stop_out = sys.argv[5]
    singles_out = sys.argv[6]

    # this won't return the 3 columns we care about.
    query = "select id, cleaned_text from tweets;"

    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row

    curr = conn.cursor()

    # --------------------------------------------------------------------------
    # Search the database file for certain things.

    docs = {}
    stopwords = []

    for row in curr.execute(query):
        # skip ones that have no value, also instead of having to re-clean.
        if len(row['cleaned_text']) > 0:
            docs[row['id']] = boringmatrix.localclean(row['cleaned_text'])

    print "processing %d docs" % len(docs)
    doc_length, doc_freq, doc_termfreq = vectorspace.build_termfreqs(docs, stopwords)
    singles = vectorspace.build_singletons(doc_freq)

    print "total terms: %d" % sum([doc_length[key] for key in doc_length])

#    print doc_freq
#    print doc_termfreq

    for single in singles:
        del doc_freq[single]

    sorted_tokens = sorted(
                           doc_freq.items(),
                           key=itemgetter(1), # (1) is value
                           reverse=True)

    top_count = min(top_count, len(sorted_tokens))
    for idx in xrange(0, top_count):
        stopwords.append(sorted_tokens[idx][0])

    print "len(stop): %d" % len(stopwords)

    with open(output_name, 'w') as fout:
        fout.write(dumps(sorted_tokens, indent=4))

    with open(dict_out, 'w') as dout:
        dout.write(dumps(sorted(doc_freq), indent=4))

    with open(stop_out, 'w') as sout:
        sout.write(dumps(stopwords, indent=4))

    with open(singles_out, 'w') as sout:
        sout.write(dumps(singles, indent=4))

    # --------------------------------------------------------------------------
    # Done.
    conn.close()

if __name__ == "__main__":
    main()
