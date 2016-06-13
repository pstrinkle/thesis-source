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
import codecs
import sqlite3

output_name = ""

# oldest_id is min(id), since_id is max(id)
def output(current_id, text):
    global output_name
    with codecs.open(output_name, "a", 'utf-8') as f:
        f.write("<id>%d</id><text>%s</text>\n" % (current_id, text))

def usage():
    print "usage: %s <sqlite_db> <owner_id> <output_file>" % sys.argv[0]

def main():
    global output_name

    # Did they provide the correct args?
    if len(sys.argv) != 4:
        usage()
        sys.exit(-1)

    # --------------------------------------------------------------------------
    # Parse the parameters.
    database_file = sys.argv[1]
    owner_id = int(sys.argv[2])
    output_name = sys.argv[3]
    
    print "database folder: %s\nowner id: %d\noutput file: %s" \
        % (database_file, owner_id, output_name)

    # this won't return the 3 columns we care about.
    query = "select id, contents as text from tweets where owner = %d;" \
        % owner_id

    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row

    c = conn.cursor()

    # --------------------------------------------------------------------------
    # Search the database file for certain things.
    for row in c.execute(query):
        output(row['id'], row['text'])

    # --------------------------------------------------------------------------
    # Done.
    conn.close()

if __name__ == "__main__":
    main()
