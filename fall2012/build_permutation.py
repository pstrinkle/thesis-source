#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Fall 2012
#
# This outputs the input model for set resemblance processing.  Process 
# permutation entropy.  When I ran it, nothing came back.  Perhaps the data was
# too sparse.

import sys
from json import dumps, loads

import boringmatrix

NOTE_BEGINS = ("i495", "boston")
TOP_TERM_CNT = 1000

def sorted_indices(full_list):
    """Return a list of the sorted indices for full_list."""
    
    return [i[0] for i in sorted(enumerate(full_list), key=lambda x:x[1])]

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
    # Compute the permutation entropy for the window.
    #
    # Use set resemblance to get entropy probability value.
    for note in results:

        sorted_indices_dict = {}
        for start in results[note]:
            full_list = results[note][start].build_fulllist(term_list)
            indices = sorted_indices(full_list)

            try:
                sorted_indices_dict[str(indices)] += 1
            except KeyError:
                sorted_indices_dict[str(indices)] = 1
    
    # Compare to the number of slices.
    print "number of sorted indices: %d" % len(sorted_indices_dict)

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
    