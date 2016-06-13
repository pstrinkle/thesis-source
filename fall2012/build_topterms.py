#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Fall 2012
#
# This outputs variations in the number of terms whose frequency is greater 
# than some specified parameter.
#

import sys
from json import loads, dumps

import boringmatrix

sys.path.append("../modellib")
import vectorspace

NOTE_BEGINS = ("i495", "boston")

def usage():
    """Print the massive usage information."""

    print "usage: %s -in <model_data> -out <output_file>" % sys.argv[0]

def main():
    """."""

    # Did they provide the correct args?
    if len(sys.argv) != 5:
        usage()
        sys.exit(-1)

    # could use the stdargs parser, but that is meh.
    try:
        for idx in range(1, len(sys.argv)):
            if "-in" == sys.argv[idx]:
                model_file = sys.argv[idx + 1]
            elif "-out" == sys.argv[idx]:
                output_name = sys.argv[idx + 1]
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

    print "Full Dictionary: %d" % len(term_list)

    new_matrix = {}
    for note in results:
        for start in results[note]:
            for term, value in results[note][start].term_matrix.items():
                try:
                    new_matrix[term] += value
                except KeyError:
                    new_matrix[term] = value

    with open("%s_top_terms_tuples.json" % output_name, 'w') as fout:
        fout.write(dumps(vectorspace.top_terms_tuples(new_matrix, 10000), indent=4))
 
    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
    