#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Fall 2012
#
# This outputs variations in the number of terms whose frequency is greater 
# than some specified parameter.
#

import os
import sys
import random
import subprocess
from json import loads

import boringmatrix

NOTE_BEGINS = ("i495", "boston")

def number_greater_than(term_matrix, base_value):
    """The matrix of terms to search, and the value they must be greater than.
    
    The parameter name 'minimum' is therefore misleading.
    """

    count = 0

    for value in term_matrix.values():
        if value > base_value:
            count += 1

    return count

def output_count_graphs(vector_a, vector_b, output, value, use_file_out = False):
    """Prints a series of distinct term counts for each time interval.
    
    The vector_a is as such: vector[timestart]."""
    
    title = "Number of Terms w/ Freq > %d per Interval" % value
    skey = sorted(vector_a.keys())
    start = skey[0]
    end = skey[-1]

    out = []
    random.seed()

    path = "%d.%d" % (random.getrandbits(random.randint(16, 57)),
                      random.getrandbits(random.randint(16, 57)))

    for idx in range(0, len(skey)):
        boring_a = vector_a[skey[idx]]
        boring_b = vector_b[skey[idx]]

        len_a = number_greater_than(boring_a.term_matrix, value)
        len_b = number_greater_than(boring_b.term_matrix, value)

        out.append("%d %d %d" % (idx, len_a, len_b))

    if use_file_out:
        with open("%s.data" % output, 'w') as fout:
            fout.write("\n".join(out))

    with open(path, 'w') as fout:
        fout.write("\n".join(out))

    params = "set terminal postscript\n"
    params += "set output '%s.eps'\n" % output
    params += "set title '%s'\n" % title
    params += "set xlabel 't'\n"
    params += "set ylabel 'number of terms'\n"
    params += "plot '%s' using 1:2 t '%s: %d - %d' lc rgb 'red', " \
        % (path, NOTE_BEGINS[0], start, end)
    params += "'%s' using 1:3 t '%s: %d - %d' lc rgb 'blue'\n" \
        % (path, NOTE_BEGINS[1], start, end)
    params += "q\n"

    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)
    
    os.remove(path)

def usage():
    """Print the massive usage information."""

    print "usage: %s -in <model_data> -out <output_file> -value X [-short] [-file]" % sys.argv[0]
    print "-value X - term frequencies strictly greater than X"
    print "-short - terms that appear more than once in at least one slice are used for any other things you output."
    print "-file - output as a data file instead of running gnuplot."

def main():
    """."""

    # Did they provide the correct args?
    if len(sys.argv) < 7 or len(sys.argv) > 9:
        usage()
        sys.exit(-1)

    use_short_terms = False
    use_file_out = False
    value = 0

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
            elif "-value" == sys.argv[idx]:
                value = int(sys.argv[idx + 1])
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

    term_list = boringmatrix.build_termlist(results) # length of this is used to normalize
    sterm_list = boringmatrix.build_termlist2(results) # length of this is used to normalize

    print "Full Dictionary: %d" % len(term_list)
    print "Short Dictionary: %d" % len(sterm_list)

    # ----------------------------------------------------------------------
    # Prune out low term counts; re-compute.
    if use_short_terms:
        for note in results:
            for start in results[note]:
                results[note][start].drop_not_in(sterm_list)
                results[note][start].compute()

    output_count_graphs(results[NOTE_BEGINS[0]],
                        results[NOTE_BEGINS[1]],
                        "%s_counters_gt_%d" % (output_name, value),
                        value,
                        use_file_out)

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
    