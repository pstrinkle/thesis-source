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
import string
import codecs
import datetime

sys.path.append("tweetlib")
import tweetdatabase as td

sys.path.append("modellib")
import geomodel as gm

options = ("-llc", "-wdh", "-wdh3", "-cdo")

def output(parameter, folder, id, guy):
    distinct = len(guy.locations)
    total = len(guy)
        
    # more occurrences, than distinct locations.
    if distinct > 0:

        print "id: %d\ncoords: %d\ndistinct: %d" % (id, len(guy), len(guy.locations))
            
        if parameter == options[0]:
            with open(os.path.join(folder, "%d_geo_total.data" % id), "w") as f:    
                f.write(guy.dumpLatLongCount(0)) # use 180 to get everybody into one quadrant
        elif parameter == options[1]:
            with open(os.path.join(folder, "%d_geo_weekdays.data" % id), "w") as f:    
                f.write(guy.dumpWeekDayHourly())
        elif parameter == options[2]: # plot with impulses (i) to get lines that should look nice.
            with open(os.path.join(folder, "%d_geo_weekdays3d.data" % id), "w") as f:
                f.write(guy.dumpWeekDayHourly3d())
        elif parameter == options[3]:
            with open(os.path.join(folder, "%d_geo_distcnt.data" % id), "w") as f:
                guy.buildCentroid()
                f.write(guy.dumpCentroidDistanceOccurrence(False))

        print "-"*80

def usage():
    print "usage: %s <task> <database_Folder> <out_folder>" % sys.argv[0]
    print "\t<task> := (-llc|-wdh|-wdh3|-cdo)"
    print "\t\tllc  := lat long count                (id_geo_total.data)"
    print "\t\twdh  := weekday hourly                (id_geo_weekdays.data)"
    print "\t\twdh3 := weekday hourly 3d             (id_geo_weekdays3d.data)"
    print "\t\tcdo  := centroid distance occurrences (id_geo_distcnt.data)"

def main():

    # Did they provide the correct args?
    if len(sys.argv) != 4:
        usage()
        sys.exit(-1)
        
    param = sys.argv[1]
    if param not in options:
        usage()
        sys.exit(-1)

    startTime = datetime.datetime.now()

    # --------------------------------------------------------------------------
    # Parse the parameters.
    database_folder = sys.argv[2]
    output_folder = sys.argv[3]

    # --------------------------------------------------------------------------
    # Search the database file for certain things.
    for input_file in td.fileWalk(database_folder):
        with codecs.open(input_file, "r", 'utf-8') as f:
            ux = f.read()
            usr = re.search("\t<id>(\d+?)</id>\n", ux)
            if usr:
                if "<geo>" in ux:
                    guy = gm.LocationBundle()
                    
                    start = string.find(ux, "<tweets>")
                    end = string.find(ux, "</tweets>")
                    
                    if start == -1 or end == -1:
                        pass
                    else:
                        user_tweets = ux[start:end].split("<tweet>")
                        for tweet in user_tweets:

                            if "<geo>" in tweet:
                                timestr = re.search("<created>\"(.+)\"</created>", tweet)
                                loc = re.search("<geo>(.+)</geo>", tweet)

                                if timestr and loc:
                                    guy.add_tweet(timestr.group(1), loc.group(1))

                        #users[int(usr.group(1))] = guy
                        # The old version would build up the dictionary of users, then
                        # handle the geo-stuff during the output phase.
                        #
                        # However, when I wrote this code I had maybe 11,000 users with tweets
                        # and ~300,000 user files; and now I have over a million users with at least
                        # one tweet...  It makes more sense to not bother storing everything and, just
                        # output as it goes.
                        output(param, output_folder, int(usr.group(1)), guy)    

    # --------------------------------------------------------------------------
    # Done.
    
    print "total runtime: ",
    print (datetime.datetime.now() - startTime)

if __name__ == "__main__":
    main()
