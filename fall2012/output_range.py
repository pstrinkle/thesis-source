#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Fall 2012
#
# Just dump some info.

import sys
import sqlite3

NOTE_BEGINS = ("i495", "boston")

def usage():
    """Print the massive usage information."""

    print "usage: %s -db <database_file>" % sys.argv[0]

def main():
    """."""

    # Did they provide the correct args?
    if len(sys.argv) != 3:
        usage()
        sys.exit(-1)

    database_file = None

    # could use the stdargs parser, but that is meh.
    try:
        for idx in range(1, len(sys.argv)):
            if "-db" == sys.argv[idx]:
                database_file = sys.argv[idx + 1]
    except IndexError:
        usage()
        sys.exit(-2)

    # --------------------------------------------------------------------------
    # Search the database file for the earliest timestamp and latest.

    early_query = "select min(yyyymmddhhmmss) as early, max(yyyymmddhhmmss) as late from tweets;"
    earliest = 0
    latest = 0
    count_query = "select count(*) from tweets where "

    with sqlite3.connect(database_file) as conn: 
        conn.row_factory = sqlite3.Row
        curr = conn.cursor()
        curr.execute(early_query)
        row = curr.fetchone()

        earliest = row['early']
        latest = row['late']

        print "earliest: %s" % str(earliest)
        print "latest: %s" % str(latest)

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
