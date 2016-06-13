#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Summer 2011
#
# ---...
#

import os
import re
import sys
import sqlite3
import datetime

sys.path.append("tweetlib")
import tweetdatabase as td

def addPlaces(current_places, location):
    """Add lat, long, counts from guy to current_places."""

    latlong_m = re.search("(.+?), (.+?)$", location)
    if latlong_m:
        lat = float(latlong_m.group(1)) # likely unnecessary thing here.
        longitude = float(latlong_m.group(2))

        try:
            current_places["%f %f" % (longitude, lat)] += 1
        except KeyError:
            current_places["%f %f" % (longitude, lat)] = 1

def usage():
    """."""

    print "usage: %s <database> <out_file>" % sys.argv[0]

def main():
    """."""

    # Did they provide the correct args?
    if len(sys.argv) != 3:
        usage()
        sys.exit(-1)

    places = {}

    startTime = datetime.datetime.now()

    # --------------------------------------------------------------------------
    # Parse the parameters.
    database = sys.argv[1]
    output_file = sys.argv[2]
    
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row

    c = conn.cursor()

    # --------------------------------------------------------------------------
    # Search the database file for certain things.
    for row in c.execute("select geo from tweets where geo is not null"):
        addPlaces(places, row['geo'])

    for row in c.execute("select geo from s_tweets where geo is not null"):
        addPlaces(places, row['geo'])

    # if I swap the row thing out for the row_factor it might work better?

    # --------------------------------------------------------------------------
    # Done.
    
    conn.close()
  
    with open(output_file, "w") as fout:
        fout.write("# long lat count\n")
        for place in places:
            fout.write("%s %d\n" % (place, places[place]))

    print "total runtime: ",
    print (datetime.datetime.now() - startTime)

if __name__ == "__main__":
    main()
