#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Fall 2012
#
# This outputs the matrix as a CSV.
#

import sys
from json import dumps, loads
from operator import itemgetter

import boringmatrix

NOTE_BEGINS = ("i495", "boston")

def usage():
    """Print the massive usage information."""
    
    usg = \
    """usage: %s -in <model_data> -out <output_file> [-short] [-ftm] [-mtm]
    -short - terms that appear more than once in at least one slice are used for any other things you output.
    -frm - output full_term_matrix_out
    -mtm - output merged_term_matrix_out, uses stm for output, merges the two locations into one model for each t."""

    print usg % sys.argv[0]

def main():
    """."""

    # Did they provide the correct args?
    if len(sys.argv) < 5 or len(sys.argv) > 6:
        usage()
        sys.exit(-1)

    use_short_terms = False
    full_term_matrix_out = False
    merged_term_matrix_out = False

    # could use the stdargs parser, but that is meh.
    try:
        for idx in range(1, len(sys.argv)):
            if "-in" == sys.argv[idx]:
                model_file = sys.argv[idx + 1]
            elif "-out" == sys.argv[idx]:
                output_name = sys.argv[idx + 1]
            elif "-short" == sys.argv[idx]:
                use_short_terms = True
            elif "-ftm" == sys.argv[idx]:
                full_term_matrix_out = True
            elif "-mtm" == sys.argv[idx]:
                merged_term_matrix_out = True
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

    if use_short_terms and full_term_matrix_out:
        raise Exception("Cannot use short and full at the same time buddy")

    # ----------------------------------------------------------------------
    # Output a CSV with a model built from merging boston and i495 for each
    # t.  Using the short list, or whatever is set.
    if merged_term_matrix_out:
        merged = {}
        for start in results[NOTE_BEGINS[0]]:
            x = boringmatrix.BoringMatrix(None)

            for note in NOTE_BEGINS:
                for term in results[note][start].term_matrix:
                    val = results[note][start].term_matrix[term]
                        
                    try:
                        x.term_matrix[term] += val
                    except KeyError:
                        x.term_matrix[term] = val
                        
                    x.total_count += val

            if use_short_terms:
                x.drop_not_in(sterm_list)

            x.compute()
            merged[start] = x

        if use_short_terms:
            boringmatrix.output_full_matrix(sterm_list,
                                            merged,
                                            "%s_merged.csv" % output_name)
        else:
            boringmatrix.output_full_matrix(term_list,
                                            merged,
                                            "%s_merged.csv" % output_name)
    elif full_term_matrix_out:
        for note in NOTE_BEGINS:
            output = "%s_%s_full.csv" % (output_name, note)
            boringmatrix.output_full_matrix(term_list,
                                            results[note],
                                            output)
    elif use_short_terms:
        for note in results:
            output = "%s_%s.csv" % (output_name, note)
            boringmatrix.output_full_matrix(sterm_list,
                                            results[note],
                                            output)

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
    