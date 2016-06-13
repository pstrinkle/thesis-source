#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Summer 2011
#
# Because I got worried that I would hit the limit of the number of files you're allowed to have; this
# moves the system back into a single flat file database.
#
# UGH: This version double_unescapes more, and doesn't escape anything.  I'm assuming the insert python handles this correctly.

import os
import re
import sys
import datetime
import tweetdatabase as td

def usage():
    sys.stderr.write("usage: %s <user_list> <database_folder>\n" % sys.argv[0])

def main():

    # --------------------------------------------------------------------------
    # Did they provide the correct args?
    if len(sys.argv) != 3:
        usage()
        sys.exit(-1)

    startTime = datetime.datetime.now()

    user_file = sys.argv[1]
    database_folder = sys.argv[2]
    
    # --------------------------------------------------------------------------
    # Read in the database files and write out the giant database file.
    with open(user_file, "r") as f:
        for line in f:
            id = re.search("<id>(\d+?)</id>", line)
            if id == None:
                sys.stderr.write("ah!, bailing here\n")
                sys.exit(-1)

            # get it ready for insertion
            user_id = int(id.group(1))
            path = td.getPath(database_folder, user_id)
            
            print user_id
            
            try:
                os.unlink(path)
            except Exception:
                pass

    # --------------------------------------------------------------------------
    # Done.

    print "total runtime: ",
    print (datetime.datetime.now() - startTime)

if __name__ == "__main__":
    main()
