#! /usr/bin/python
"""Gets all the created fields from the database and updates the yyyymm 
field."""

__author__ = 'tri1@umbc.edu'

##
# @author: Patrick Trinkle
# Spring 2012
#
# @summary: Gets all the created frields from the database and updates the 
# yyyymm field.
#

import sys
import sqlite3

sys.path.append("tweetlib")
from tweetdate import MONTHS, str_yearmonth

def usage():
    sys.stderr.write("%s database_file\n" % sys.argv[0])

def main():
    """Main."""
    
    # --------------------------------------------------------------------------
    # Did they provide the correct args?
    if len(sys.argv) != 2:
        usage()
        sys.exit(-1)
        
    database_file = sys.argv[1]

    update_query = \
    """update tweets set yyyymm=%d where created like '%%%s%%%d%%';"""

    #conn = sqlite3.connect(database_file)
    #conn.row_factory = sqlite3.Row

    for year in range(2005, 2012):
        for month in MONTHS:
            yyyymm = int(str_yearmonth(year, int(MONTHS[month])))
            # month_str, year_val
            print update_query % (yyyymm, month, year)
            
            # Maybe it should call "executescript()" and get fed a script
            # generated the from the loop.  Probably faster.
            #conn.cursor().execute(update_query % (yyyymm, month, year))

    #conn.commit()
    #conn.close()

if __name__ == "__main__":
    main()
