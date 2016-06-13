#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Fall 2012
#
# This outputs the input model as tf-idf.

import sys
from json import dumps, loads

import boringmatrix

sys.path.append("../modellib")
import vectorspace

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
    # Just build a dictionary of the documents.
    results_as_dict = {}
    doc_length = {}
    doc_freq = {}
    top_terms_slist = None

    for note in results:
        for start in results[note]:
                    
            doc_id = "%s-%d" % (note, start)

            results_as_dict[doc_id] = results[note][start].term_matrix.copy()
            doc_length[doc_id] = results[note][start].total_count

            for term in results_as_dict[doc_id]:
                try:
                    doc_freq[term] += 1
                except KeyError:
                    doc_freq[term] = 1

    invdoc_freq = vectorspace.calculate_invdf(len(results_as_dict), doc_freq)

    doc_tfidf = \
        vectorspace.calculate_tfidf(doc_length, results_as_dict, invdoc_freq)

    with open("%s_%s" % (output_name, "top_tfidf.json"), 'w') as fout:
        fout.write(dumps(vectorspace.top_terms_overall(doc_tfidf,
                                                       TOP_TERM_CNT),
                         indent=4))

    top_terms_slist = \
        vectorspace.top_terms_overall(results_as_dict, int(len(doc_freq)*.10))

    with open("%s_%s" % (output_name, "top_tf.json"), 'w') as fout:
        fout.write(dumps(top_terms_slist, indent=4))

    for note in results:
        for start in results[note]:
            results[note][start].drop_not_in(top_terms_slist)
            results[note][start].compute()
                
        boringmatrix.output_full_matrix(top_terms_slist,
                                        results[note],
                                        "%s_%s_tops.csv" % (output_name, note))

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
    