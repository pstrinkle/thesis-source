#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Fall 2012
#
# This outputs the the similarity values per interval comparison.
#

import os
import sys
import random
import subprocess
from json import loads, dumps

import boringmatrix

NOTE_BEGINS = ("i495", "boston")

def terms_in_common(boring_a, boring_b):
    """Given boringmatrixA, and boringmatrixB, how many terms are there in 
    common."""
    
    count = 0
    for term in boring_a.term_matrix:
        if term in boring_b.term_matrix:
            count += 1

    return count

def set_resemblance(boring_a, boring_b):
    """Given two boringmatrices, computer the set resemblance, which is the
    intersection over the union."""
    
    intersection = 0
    union = 0
    
    if len(boring_a.term_matrix) == 0 or len(boring_b.term_matrix) == 0:
        return 0.0
    
    for term in boring_a.term_matrix:
        if term in boring_b.term_matrix:
            intersection += 1
        else:
            union += 1
    for term in boring_b.term_matrix:
        if term not in boring_a.term_matrix:
            union += 1

    return float(intersection) / union

def output_similarity_gnuplot(vector, output, use_file_out = False):
    """vector here is a dictionary keyed on the datetimestamp as long, with the
    value as the cosine (or other) similarity."""

    skey = sorted(vector.keys())
    start = skey[0]
    end = skey[-1]

    out = []
    random.seed()
    
    path = "%d.%d" % (random.getrandbits(random.randint(16, 57)),
                      random.getrandbits(random.randint(16, 57)))

    for idx in range(0, len(skey)):
        out.append("%d %f" % (idx, vector[skey[idx]]))

    if use_file_out:
        with open("%s.data" % output, 'w') as fout:
            fout.write("\n".join(out))

    with open(path, 'w') as fout:
        fout.write("\n".join(out))

    params = "set terminal postscript\n"
    params += "set output '%s.eps'\n" % output
    params += "set xlabel 't'\n"
    params += "set ylabel 'similarity scores'\n"
    params += "plot '%s' t '%d - %d'\n" % (path, start, end)
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
    if len(sys.argv) < 5 or len(sys.argv) > 6:
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
    # Compute the cosine similarities. 
    # YOU NEED TO CALL .compute() before this or you'll get garbage.
    vector_sums = boringmatrix.get_vectorsums(results, NOTE_BEGINS)
    
    count_cosine = {}
    weight_cosine = {}

    # ----------------------------------------------------------------------
    # Compute the similarity and counts for the given models as well as the
    # entropy.
    for start in results[NOTE_BEGINS[0]]:
        # These are identical... as they should be.  Really, I should be 
        # using these.
        # Totally different than those above.
        count_cosine[int(start)] = \
            boringmatrix.boring_count_similarity(results[NOTE_BEGINS[0]][start],
                                                 results[NOTE_BEGINS[1]][start])

        weight_cosine[int(start)] = \
            boringmatrix.boring_weight_similarity(results[NOTE_BEGINS[0]][start],
                                                  results[NOTE_BEGINS[1]][start])
            
    # Consider using a few panes.
    output_similarity_gnuplot(vector_sums, 
                              "%s_sims" % output_name, 
                              use_file_out)
    output_similarity_gnuplot(count_cosine,
                              "%s_sims_count" % output_name,
                              use_file_out)
    output_similarity_gnuplot(weight_cosine,
                              "%s_sims_weight" % output_name,
                              use_file_out)

    for start in count_cosine:
        if count_cosine[start] > 0.8:
            print start
            print terms_in_common(results[NOTE_BEGINS[0]][start], results[NOTE_BEGINS[1]][start])
            print set_resemblance(results[NOTE_BEGINS[0]][start], results[NOTE_BEGINS[1]][start])
            print "x" * 20

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
    