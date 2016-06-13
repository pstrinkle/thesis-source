#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Fall 2012
#
# This outputs the input model for new terms processing.
#
# Of value, I was originally using arrays to store everything, but the 
# implementation they're using underneath is really really infinitely slow.
#
# When I switched to dictionaries, it went from:
#number of slices: 863
#Full Dictionary: 49417
#Short Dictionary: 14625
#real    34m6.738s
#
# to:
#number of slices: 863
#Full Dictionary: 49417
#Short Dictionary: 14625
#
#real    0m3.992s
#
# Holy shit.
#

import os
import sys
import random
import subprocess
from json import loads

import boringmatrix

NOTE_BEGINS = ("i495", "boston")

def output_percentage_growth(results, output, use_file_out = False):
    """."""

    title = "Percentage of Distinct New Terms per Interval"
    skey = sorted(results[NOTE_BEGINS[0]].keys())
    start = skey[0]
    end = skey[-1]

    aterms = {}
    bterms = {}

    out = []
    random.seed()
    
    path = "%d.%d" % (random.getrandbits(random.randint(16, 57)),
                      random.getrandbits(random.randint(16, 57)))

    for idx in range(0, len(skey)-1):
        count1 = 0
        count2 = 0

        list1 = results[NOTE_BEGINS[0]][skey[idx]].term_matrix
        list2 = results[NOTE_BEGINS[1]][skey[idx]].term_matrix
        
        for term in list1:
            if term not in aterms:
                aterms[term] = 1

        for term in list2:
            if term not in bterms:
                bterms[term] = 1

        # aterms and bterms now have all the terms from the current interval.
        nlist1 = results[NOTE_BEGINS[0]][skey[idx+1]].term_matrix
        ncount1 = len(results[NOTE_BEGINS[0]][skey[idx+1]].term_matrix)

        nlist2 = results[NOTE_BEGINS[1]][skey[idx+1]].term_matrix
        ncount2 = len(results[NOTE_BEGINS[1]][skey[idx+1]].term_matrix)
        
        # ncount1 and ncount2 are the number of distinct terms in the next 
        # interval
        # for each term in the next interval, was it in the previous?
        # if it wasn't, increment the counter so we can get some growth 
        # percentages.

        for term in nlist1:
            if term not in aterms:
                aterms[term] = 1 # we don't really need this step.
                count1 += 1

        for term in nlist2:
            if term not in bterms:
                bterms[term] = 1 # we don't really need this step.
                count2 += 1

        out.append("%d %f %f" % (idx,
                                 (float(count1)/ncount1)*100,
                                 (float(count2)/ncount2)*100))
    
    if use_file_out:
        with open("%s.data" % output, 'w') as fout:
            fout.write("\n".join(out))

    with open(path, 'w') as fout:
        fout.write("\n".join(out))

    params = "set terminal postscript\n"
    params += "set output '%s.eps'\n" % output
    params += "set title '%s'\n" % title
    params += "set xlabel 't'\n"
    params += "set ylabel 'percentage of terms in next interval not in previous'\n"
    params += "plot '%s' using 1:2 t '%s: %d - %d' lc rgb 'red', " \
        % (path, NOTE_BEGINS[0], start, end)
    params += "'%s' using 1:3 t '%s: %d - %d' lc rgb 'blue'\n" \
        % (path, NOTE_BEGINS[1], start, end)
    params += "q\n"

    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)
    
    os.remove(path)

def output_new_terms(results, output, use_file_out = False):
    """At each X, indicate on the Y axis how many new terms were introduced."""

    title = "Number of Distinct New Terms per Interval"
    skey = sorted(results[NOTE_BEGINS[0]].keys())
    start = skey[0]
    end = skey[-1]

    aterms = {}
    bterms = {}

    out = []
    random.seed()
    
    path = "%d.%d" % (random.getrandbits(random.randint(16, 57)),
                      random.getrandbits(random.randint(16, 57)))

    for idx in range(0, len(skey)):
        count1 = 0
        count2 = 0

        list1 = results[NOTE_BEGINS[0]][skey[idx]].term_matrix
        list2 = results[NOTE_BEGINS[1]][skey[idx]].term_matrix

        for term in list1:
            if term not in aterms:
                aterms[term] = 1
                count1 += 1

        for term in list2:
            if term not in bterms:
                bterms[term] = 1
                count2 += 1

        out.append("%d %d %d" % (idx, count1, count2))

    if use_file_out:
        with open("%s.data" % output, 'w') as fout:
            fout.write("\n".join(out))

    with open(path, 'w') as fout:
        fout.write("\n".join(out))

    params = "set terminal postscript\n"
    params += "set output '%s.eps'\n" % output
    params += "set title '%s'\n" % title
    params += "set log y\n"
    params += "set xlabel 't'\n"
    params += "set ylabel 'new distinct terms'\n"
    params += "plot '%s' using 1:2 t '%s: %d - %d' lc rgb 'red', " \
        % (path, NOTE_BEGINS[0], start, end)
    params += "'%s' using 1:3 t '%s: %d - %d' lc rgb 'blue'\n" \
        % (path, NOTE_BEGINS[1], start, end)
    params += "q\n"

    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)
    
    os.remove(path)

def usage():
    """Print the massive usage information."""

    print "usage: %s -in <model_data> -out <output_file> [-short] [-file]" % sys.argv[0]
    print "-short - terms that appear more than once in at least one slice are used for any other things you output."
    print "-file - output as a data file instead of running gnuplot."

def main():
    """."""

    # Did they provide the correct args?
    if len(sys.argv) < 5 or len(sys.argv) > 7:
        usage()
        sys.exit(-1)

    use_short_terms = False
    use_file_out = False

    # could use the stdargs parser, but that is meh.
    try:
        for idx in range(1, len(sys.argv)):
            if "-in" == sys.argv[idx]:
                model_file = sys.argv[idx + 1]
            elif "-out" == sys.argv[idx]:
                output_name = sys.argv[idx + 1]
            elif "-short" == sys.argv[idx]:
                use_short_terms = True
            elif "-file" == sys.argv[idx]:
                use_file_out = True
    except IndexError:
        usage()
        sys.exit(-2)

    if len(NOTE_BEGINS) != 2:
        sys.stderr.write("use this to compare two sets.\n")
        sys.exit(-1)

    # not building the model.
    results = None

    if model_file is None:
        sys.exit(-1)
        
    if output_name is None:
        sys.exit(-1)

    with open(model_file, 'r') as moin:
        results = loads(moin.read(), object_hook=boringmatrix.as_boring)
        # dict(loads(moin.read(), object_hook=as_boring))

    # ----------------------------------------------------------------------
    # Compute the term weights.
    boringmatrix.fix_boringmatrix_dicts(results)

#        for start in results[NOTE_BEGINS[0]]:
#            for note in NOTE_BEGINS:
#                total = 0.0
#                for term in results[note][start].term_weights:
#                    total += results[note][start].term_weights[term]
#                print total,
# 1.0 is the total weight, yay.

    print "number of slices: %d" % len(results[NOTE_BEGINS[0]])

    # ----------------------------------------------------------------------
    # Prune out low term counts; re-compute.
    if use_short_terms:
        sterm_list = boringmatrix.build_termlist2(results)
        
        for note in results:
            for start in results[note]:
                results[note][start].drop_not_in(sterm_list)
                results[note][start].compute()

    # output how many new terms you have at each interval.
    output_new_terms(results, "%s_term_growth" % output_name, use_file_out)

    # output the percentage of new terms at each interval, to show how 
    # worthless smoothing gets.
    output_percentage_growth(results,
                             "%s_percentage_new" % output_name,
                             use_file_out)

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
    