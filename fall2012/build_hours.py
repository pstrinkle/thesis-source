#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Fall 2012
#
# This outputs the input model for new terms processing.
#
#

import os
import re
import sys
import random
import sqlite3
import subprocess

NOTE_BEGINS = ("i495", "boston")

def output_distinct_terms_per_hour(database_file, output, use_file_out = False):
    """At each X, indicate on the Y axis how many new terms were introduced."""

    query = "select yyyymmddhhmmss from tweets where note like '%s%%';"
    title = "Number of Tweets per Hour"

    out = []
    random.seed()

    path = "%d.%d" % (random.getrandbits(random.randint(16, 57)),
                      random.getrandbits(random.randint(16, 57)))

    hours_counts = {}

    with sqlite3.connect(database_file) as conn:
        conn.row_factory = sqlite3.Row
        curr = conn.cursor()

        for note in NOTE_BEGINS:
            hours_counts[note] = \
                { 0 : 0,  1 : 0,  2 : 0,  3 : 0,  4 : 0,  5 : 0,  6 : 0,  7 : 0,
                  8 : 0,  9 : 0, 10 : 0, 11 : 0, 12 : 0, 13 : 0, 14 : 0, 15 : 0,
                 16 : 0, 17 : 0, 18 : 0, 19 : 0, 20 : 0, 21 : 0, 22 : 0, 23 : 0}

            for row in curr.execute(query % (note)):
                hour_m = re.search("\d{8}(\d{2})\d{4}", str(row[0]))
                if hour_m:

                    hour_val = int(hour_m.group(1))
                    # UTC to EST in early Oct 2012.
                    if hour_val < 4:
                        ofs = 4 - hour_val
                        hour_val = 24 - ofs

                    try:
                        hours_counts[note][hour_val] += 1
                    except KeyError:
                        hours_counts[note][hour_val] = 1

    for hour in sorted(hours_counts[NOTE_BEGINS[0]]):
        out.append("%d %d %d" % (hour, 
                                 hours_counts[NOTE_BEGINS[0]][hour],
                                 hours_counts[NOTE_BEGINS[1]][hour]))

    if use_file_out:
        with open("%s.data" % output, 'w') as fout:
            fout.write("\n".join(out))

    with open(path, 'w') as fout:
        fout.write("\n".join(out))

    params = "set terminal postscript eps color\n"
    params += "set output '%s.eps'\n" % output
    params += "set title '%s'\n" % title
    params += "set log y\n"
    params += "set xlabel 'hour'\n"
    params += "set xtics 0, 1, 23\n"
    params += "set ylabel 'tweets'\n"
    params += "plot '%s' using 1:2 t '%s' lc rgb 'red', " \
        % (path, NOTE_BEGINS[0])
    params += "'%s' using 1:3 t '%s' lc rgb 'blue'\n" \
        % (path, NOTE_BEGINS[1])
    params += "q\n"

    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)
    
    os.remove(path)

def usage():
    """Print the massive usage information."""

    print "usage: %s -in <database_file> -out <output_file> [-file]" \
        % sys.argv[0]
    print "-short - terms that appear more than once in at least one slice are used for any other things you output."
    print "-file - output as a data file instead of running gnuplot."

def main():
    """."""

    # Did they provide the correct args?
    if len(sys.argv) < 5 or len(sys.argv) > 6:
        usage()
        sys.exit(-1)

    use_file_out = False
    database_file = None

    # could use the stdargs parser, but that is meh.
    try:
        for idx in range(1, len(sys.argv)):
            if "-in" == sys.argv[idx]:
                database_file = sys.argv[idx + 1]
            elif "-out" == sys.argv[idx]:
                output_name = sys.argv[idx + 1]
            elif "-file" == sys.argv[idx]:
                use_file_out = True
    except IndexError:
        usage()
        sys.exit(-2)

    if len(NOTE_BEGINS) != 2:
        sys.stderr.write("use this to compare two sets.\n")
        sys.exit(-1)

    if database_file is None:
        sys.exit(-1)
        
    if output_name is None:
        sys.exit(-1)

    # ----------------------------------------------------------------------
    # Output how many new terms you have at each interval.
    output_distinct_terms_per_hour(database_file,
                                   "%s_tweets_per_hour" % (output_name),
                                   use_file_out)

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
    