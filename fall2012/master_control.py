#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Fall 2012
#

import os
import sys
import random
import sqlite3
import subprocess
from json import dumps, loads

from datetime import timedelta

import boringmatrix as bm

NOTE_BEGINS = ("i495", "boston")
TOP_TERM_CNT = 1000

def build_basic_model(stopwords_file,
                      singletons_file,
                      database_file,
                      interval,
                      output_name,
                      step_intervals):
    """Build the output model."""

    remove_em = []

    if stopwords_file is not None:
        with open(stopwords_file, 'r') as fin:
            remove_em.extend(loads(fin.read()))

    if singletons_file is not None:
        with open(singletons_file, 'r') as fin:
            remove_em.extend(loads(fin.read()))

    # this won't return the 3 columns we care about.
    # XXX: This doesn't select by note.
    query = "select id, cleaned_text from tweets where note like '%s%%' and (yyyymmddhhmmss >= %d and yyyymmddhhmmss < %d);"

    # --------------------------------------------------------------------------
    # Search the database file for the earliest timestamp and latest.

    early_query = "select min(yyyymmddhhmmss) as early, max(yyyymmddhhmmss) as late from tweets;"
    earliest = 0
    latest = 0

    with sqlite3.connect(database_file) as conn: 
        conn.row_factory = sqlite3.Row
        curr = conn.cursor()
        curr.execute(early_query)
        row = curr.fetchone()

        earliest = row['early']
        latest = row['late']

        # the timestamps are YYYYMMDDHHMMSS -- so I need to convert them into 
        # datetime.datetime objects; easy.
        # okay, so they want the timestamps to step forward slowly.
        # can use datetime.timedelta correctly updates the datetime value, which
        # we'll then need to convert back to the timestamp long.

    starttime = bm.datetime_from_long(earliest)
    endtime = bm.datetime_from_long(latest)
    currtime = starttime
    delta = timedelta(0, interval)
    halfdelta = timedelta(0, interval / 2)

    # datetime.timedelta(0, 1) (days, seconds)
    # you can just add these to datetime.datetime objects.
    #
    # (endtime - starttime) gives you a datetime.timedelta object.

    print "starttime: %s" % starttime
    print "endtime: %s" % endtime
    
    results = {}
    for note in NOTE_BEGINS:
        results[note] = {}

    # --------------------------------------------------------------------------
    # Search the database file for certain things.
    with sqlite3.connect(database_file) as conn:
        conn.row_factory = sqlite3.Row
        curr = conn.cursor()
        
        while currtime + delta < endtime:
            start = bm.long_from_datetime(currtime)
            
            ending = currtime + delta # should be full interval
            
            end = bm.long_from_datetime(ending)
            
            # move starting point forward
            if step_intervals:
                currtime += halfdelta
            else:
                currtime += delta

            print "range: %d %d" % (start, end)

            # build the text for that time-slice into one document, removing
            # the stopwords provided by the user as well as the singleton
            # list, neatly also provided by the user.            
            for note in NOTE_BEGINS:
                local_cluster = []

                for row in curr.execute(query % (note, start, end)):
                    local_cluster.append(bm.localclean(row['cleaned_text']))

                tmp_local = " ".join(local_cluster) # join into one line
                    # then split and strip out bad words.
                # why join and then split immediately thereafter, :P
                # in creating the BoringMatrix it splits, so why not just feed
                # it an array.
                results[note][start] = \
                    bm.BoringMatrix([word for word in tmp_local.split(" ") \
                                     if word not in remove_em and len(word) > 2])

    with open(output_name, 'w') as fout:
        # added items, you then cast result afterwards.
        # fout.write(dumps(results.items(), cls=BoringMatrixEncoder, sort_keys=True, indent=4))
        fout.write(dumps(results,
                         cls=bm.BoringMatrixEncoder,
                         sort_keys=True,
                         indent=4))

    print "Finished Building Model over Range."

def usage():
    """Print the massive usage information."""

    print "usage: %s -out <output_file> -db <sqlite_db> [-sw <stopwords.in>] [-si <singletons.in>] -i <interval in seconds> [-step]" % sys.argv[0]

    usg = \
"""\tsqlite_db := the input database.
\tstopwords.in := json dump of a stop word array.
\tsingletons.in := json dump of a single word array.
\toutput_file := currently just dumps whatever the current meaning of results is.
\tinterval in seconds := is the time slicing to use.
\t-step := should it do half-step t models -- sliding window.
"""

    print usg
    
    # Need to consider having the output fall out in sets for varied windows...

def main():
    """."""

    # Did they provide the correct args?
    if len(sys.argv) < 3:
        usage()
        sys.exit(-1)

    # --------------------------------------------------------------------------
    # Parse the parameters.

    model_file = None
    output_name = None
    database_file = None
    stopwords_file = None
    singletons_file = None
    interval = None
    build_model = False
    step_intervals = False
    use_short_terms = False
    use_file_out = False

    # could use the stdargs parser, but that is meh.
    try:
        for idx in range(1, len(sys.argv)):
            if "-in" == sys.argv[idx]:
                model_file = sys.argv[idx + 1]
            elif "-out" == sys.argv[idx]:
                output_name = sys.argv[idx + 1]
            elif "-db" == sys.argv[idx]:
                database_file = sys.argv[idx + 1]
                build_model = True
            elif "-sw" == sys.argv[idx]:
                stopwords_file = sys.argv[idx + 1]
            elif "-si" == sys.argv[idx]:
                singletons_file = sys.argv[idx + 1]
            elif "-i" == sys.argv[idx]:
                interval = int(sys.argv[idx + 1])
            elif "-short" == sys.argv[idx]:
                use_short_terms = True
            elif "-file" == sys.argv[idx]:
                use_file_out = True
            elif "-step" == sys.argv[idx]:
                step_intervals = True
    except IndexError:
        usage()
        sys.exit(-2)

    if len(NOTE_BEGINS) != 2:
        sys.stderr.write("use this to compare two sets.\n")
        sys.exit(-1)

    # --------------------------------------------------------------------------
    # Do the stuff.

    if build_model:
        build_basic_model(stopwords_file,
                          singletons_file,
                          database_file,
                          interval,
                          output_name,
                          step_intervals)

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
