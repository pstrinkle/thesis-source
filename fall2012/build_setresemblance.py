#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Fall 2012
#
# This outputs the input model for set resemblance processing.  The idea here
# was to determine entropy over the window by clustering the models into bins
# and using that as the entropy input.

import sys
from json import dumps, loads

import boringmatrix
import termset

NOTE_BEGINS = ("i495", "boston")
TOP_TERM_CNT = 1000

def usage():
    """Print the massive usage information."""

    print "usage: %s -in <model_data> -out <output_file> [-short]" % sys.argv[0]
    print "-short - terms that appear more than once in at least one slice are used for any other things you output."

def main():
    """."""

    # Did they provide the correct args?
    if len(sys.argv) < 5 or len(sys.argv) > 6:
        usage()
        sys.exit(-1)

    use_short_terms = False

    # could use the stdargs parser, but that is meh.
    try:
        for idx in range(1, len(sys.argv)):
            if "-in" == sys.argv[idx]:
                model_file = sys.argv[idx + 1]
            elif "-out" == sys.argv[idx]:
                output_name = sys.argv[idx + 1]
            elif "-short" == sys.argv[idx]:
                use_short_terms = True
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

    # ----------------------------------------------------------------------
    # Convert to sets and compute the set resemblances, see if any are 
    # high, compared to each other at each t.
    termSets = {}
    for start in results[NOTE_BEGINS[0]]:
        set_a = termset.TermSet(results[NOTE_BEGINS[0]][start],
                                "%s.%s" % (NOTE_BEGINS[0], str(start)))
        set_b = termset.TermSet(results[NOTE_BEGINS[1]][start],
                                "%s.%s" % (NOTE_BEGINS[1], str(start)))

        termSets[start] = termset.set_resemblance(set_a, set_b)

    #print sorted(
    #             termSets.items(),
    #             key=itemgetter(1), # (1) is value
    #             reverse=True)

    # ------------------------------------------------------------------
    # Convert to sets and compute the set resemblances for the goal of 
    # clustering all the sets so that I can build a "table" for each t 
    # in T, the bin ID of Xt, Yt | counts --> so I have probabilities 
    # to build the entropy computation for the window.
    termSetsFull = []
    for note in results:
        for start in results[note]:
            termSetsFull.append(termset.TermSet(results[note][start],
                                                "%s.%s" % (note, str(start))))

    resem_matrix = {}
    length = len(termSetsFull)

    for i in xrange(0, length):
        resem_matrix[i] = {}

        for j in xrange(i + 1, length):
            resem_matrix[i][j] = termset.set_resemblance(termSetsFull[i],
                                                         termSetsFull[j])

    resem_values = {}
    for i in resem_matrix:
        for j in resem_matrix[i]:
            try:
                resem_values[resem_matrix[i][j]] += 1
            except KeyError:
                resem_values[resem_matrix[i][j]] = 1

    #print dumps(sorted(resem_values, reverse=True), indent=4)
    
    print "Resemblance Values Computed"

    resem_histogram = {0.1 : 0, 0.2 : 0, 0.3 : 0, 0.4 : 0, 0.5 : 0,
                       0.6 : 0, 0.7 : 0, 0.8 : 0, 0.9 : 0, 1.0 : 0}

    for value in resem_values.keys():
        if value <= 0.1:
            resem_histogram[0.1] += resem_values[value]
        elif value <= 0.2:
            resem_histogram[0.2] += resem_values[value]
        elif value <= 0.3:
            resem_histogram[0.3] += resem_values[value]
        elif value <= 0.4:
            resem_histogram[0.4] += resem_values[value]
        elif value <= 0.5:
            resem_histogram[0.5] += resem_values[value]
        elif value <= 0.6:
            resem_histogram[0.6] += resem_values[value]
        elif value <= 0.7:
            resem_histogram[0.7] += resem_values[value]
        elif value <= 0.8:
            resem_histogram[0.8] += resem_values[value]
        elif value <= 0.9:
            resem_histogram[0.9] += resem_values[value]
        else:
            resem_histogram[1.0] += resem_values[value]

    print dumps(resem_histogram, indent=4)
    
    ## TODO: Make bar graph with gnuplot?

    #print sorted(
    #             resem_matrix.items(),
    #             key=itemgetter(1), # (1) is value
    #             reverse=True)

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
    