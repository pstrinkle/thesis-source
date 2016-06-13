#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Fall 2012
#
# This outputs the input model for PCA processing.

import sys
from json import dumps, loads
import os

import boringmatrix

NOTE_BEGINS = ("i495", "boston")
TOP_TERM_CNT = 1000

def usage():
    """Print the massive usage information."""

    print "usage: %s -in <model_data> -out <output_file> [-short]" % sys.argv[0]
    print "-short - terms that appear more than once in at least one slice are used for any other things you output."
    # the PCA C code currently doesn't support floating point.
    print "-pca1 - Output folder of files, one per document for full term set, as term counts"

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
    # Output each slice for each area as a new-line broken up term count
    # file.  These values aren't normalized, so they're not terribly useful
    # yet.
    outdir = "%s_%s" % (output_name, "pca1")

    if os.path.exists(outdir):
        os.rmdir(outdir)

    os.mkdir(outdir)

    if use_short_terms:
        the_terms = sterm_list
    else:
        the_terms = term_list

    for note in results:
        for start in results[note]:
            filename = "%s-%d" % (note, start)

            values = []

            for term in the_terms:
                # Could probably just index with a try/catch.
                if term in results[note][start].term_matrix:
                    value = results[note][start].term_matrix[term]
                else:
                    value = 0
                values.append(value)

            try:
                data_str = "\n".join(["%d" % value for value in values])
            except TypeError, e:
                print type(values), type(values[0]), values[0], values[1]
                print e
                sys.exit(-2)
                    
            with open(os.path.join(outdir, filename), 'w') as fout:
                fout.write(data_str)

    print "params: %d %d" % (len(results[note]) * 2, len(the_terms))


    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
    