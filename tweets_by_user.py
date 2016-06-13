#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Spring 2012
#
# This attempts to collate the tweet files and remove duplicates
# given an entire folder of xml files, instead of using sort/uniq
# on a per file basis.

import sys
import sqlite3

# oldest_id is min(id), since_id is max(id)
def output(current_id, text):
    print "<owner>%d</owner><count>%d</count>" % (current_id, text)

def usage():
    print "usage: %s <sqlite_db> <minimum>" % sys.argv[0]

def main():

    # Did they provide the correct args?
    if len(sys.argv) != 3:
        usage()
        sys.exit(-1)

    # --------------------------------------------------------------------------
    # Parse the parameters.
    database_file = sys.argv[1]
    minimum = int(sys.argv[2])
    
    print "database: %s" % database_file
    print "minimum: %d" % minimum

    # this won't return the 3 columns we care about.
    query = "select owner, count(*) as count from tweets group by owner having count(*) >= %d order by count(*) desc;" % minimum

    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row

    c = conn.cursor()

    # --------------------------------------------------------------------------
    # Search the database file for certain things.
    for row in c.execute(query):
        output(row['owner'], row['count'])

    # --------------------------------------------------------------------------
    # Done.
    conn.close()

if __name__ == "__main__":
    main()
