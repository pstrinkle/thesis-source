#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Fall 2012
#
# This appears to be the code I was using before I transitioned to 
# master_control.

import sys
import sqlite3
from json import dumps, loads
from datetime import timedelta

import boringmatrix as bm

def usage():
    """."""

    print "usage: %s <sqlite_db> <stopwords.in> <singletons.in> <output_file> <interval in seconds> <note begins>" % sys.argv[0]
    
    # XXX: I would use pickle, but these are human-readable.
    print "\tsqlite_db := the input database."
    print "\tstopwords.in := json dump of a stop word array."
    print "\tsingletons.in := json dump of a single word array."
    print "\toutput_file := currently just dumps whatever the current meaning of results is."
    print "\tinterval in seconds := is the time slicing to use."
    print "\tnote begins := the note column in the sqlite_db starts with this text."

def main():
    """."""

    # Did they provide the correct args?
    if len(sys.argv) != 7:
        usage()
        sys.exit(-1)

    # --------------------------------------------------------------------------
    # Parse the parameters.
    database_file = sys.argv[1]
    stopwords_file = sys.argv[2]
    singletons_file = sys.argv[3]
    
    output_name = sys.argv[4]
    interval = int(sys.argv[5])
    note_begins = sys.argv[6]

    with open(stopwords_file, 'r') as fin:
        stopwords = loads(fin.read())
    
    with open(singletons_file, 'r') as fin:
        singletons = loads(fin.read())
    
    remove_em = []
    remove_em.extend(stopwords)
    remove_em.extend(singletons)

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

    # datetime.timedelta(0, 1) (days, seconds)
    # you can just add these to datetime.datetime objects.
    #
    # (endtime - starttime) gives you a datetime.timedelta object.

    print "starttime: %s" % starttime
    print "endtime: %s" % endtime
    
    results = {}

    # --------------------------------------------------------------------------
    # Search the database file for certain things.
    with sqlite3.connect(database_file) as conn:
        conn.row_factory = sqlite3.Row
        curr = conn.cursor()
        
        while currtime + delta < endtime:
            start = bm.long_from_datetime(currtime)
            currtime += delta
            end = bm.long_from_datetime(currtime)
            
            results[start] = []
            
            print "range: %d %d" % (start, end)
            
            # build the text for that time-slice into one document, removing
            # the stopwords provided by the user as well as the singleton
            # list, neatly also provided by the user.

            for row in curr.execute(query % (note_begins, start, end)):
                results[start].append(bm.localclean(row['cleaned_text']))
            
            tmp_local = " ".join(results[start]) # join into one line
            # then split and strip out bad words.
            results[start] = \
                bm.BoringMatrix([word for word in tmp_local.split(" ") \
                                 if word not in remove_em and len(word) > 2])
            results[start].compute()
            
            #print dumps(results, cls=BoringMatrixEncoder, indent=4)
            #sys.exit(0)

    with open(output_name, 'w') as fout:
        fout.write(dumps(results, cls=bm.BoringMatrixEncoder, indent=4))
    
    # results = json.loads(results.in, object_hook=as_boring)

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
