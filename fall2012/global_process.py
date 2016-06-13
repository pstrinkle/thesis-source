#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Fall 2012
#
# This outputs the input model for global processing.

import os
import sys
import random
import subprocess
from json import dumps, loads

import boringmatrix

sys.path.append("../modellib")
import vectorspace

TOP_TERM_CNT = 1000
NOTE_BEGINS = ("i495", "boston")

def output_full_matrix(terms, vectors, output):
    """Output the vectors over the terms, this is for each t for a specific 
    location."""

    x = boringmatrix.dump_weights_matrix(terms, vectors)

    with open(output, 'w') as fout:
        fout.write(x)

def build_gtermlist(global_views):
    """Given the thing for globals, go through and build list."""

    terms = {}
    for start in global_views:
        for term in global_views[start].term_matrix:
            try:
                terms[term] += 1
            except KeyError:
                terms[term] = 1
    
    return sorted(terms.keys())

def output_distinct_graphs(results, output, use_file_out = False):
    """Prints a series of distinct term counts for each time interval."""

    title = "Number of Distinct Terms in Top-Level Hierarchical per Interval"
    skey = sorted(results.keys())
    start = skey[0]
    end = skey[-1]

    out = []
    random.seed()
    
    path = "%d.%d" % (random.getrandbits(random.randint(16, 57)),
                      random.getrandbits(random.randint(16, 57)))

    for idx in range(0, len(skey)):
        out.append("%d %d" % (idx, len(results[skey[idx]].term_matrix)))

    if use_file_out:
        with open("%s.data" % output, 'w') as fout:
            fout.write("\n".join(out))

    with open(path, 'w') as fout:
        fout.write("\n".join(out))

    params = "set terminal postscript\n"
    params += "set output '%s.eps'\n" % output
    params += "set title '%s'\n" % title
    params += "set xlabel 't'\n"
    params += "set ylabel 'distinct terms'\n"
    params += "plot '%s' using 1:2 t '%s: %d - %d' lc rgb 'red'\n" \
        % (path, 'global', start, end)
    params += "q\n"

    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)
    
    os.remove(path)
    

def output_global_new_terms(results, output, use_file_out = False):
    """At each X, indicate on the Y axis how many new terms were introduced."""

    title = "New Terms in Top-Level Hierarchical Model per Interval"
    skey = sorted(results.keys())
    start = skey[0]
    end = skey[-1]

    aterms = {}

    out = []
    random.seed()
    
    path = "%d.%d" % (random.getrandbits(random.randint(16, 57)),
                      random.getrandbits(random.randint(16, 57)))

    for idx in range(0, len(skey)):
        count1 = 0

        list1 = results[skey[idx]].term_matrix

        for term in list1:
            if term not in aterms:
                aterms[term] = 1
                count1 += 1

        out.append("%d %d" % (idx, count1))

    if use_file_out:
        with open("%s.data" % output, 'w') as fout:
            fout.write("\n".join(out))

    with open(path, 'w') as fout:
        fout.write("\n".join(out))

    params = "set terminal postscript\n"
    params += "set output '%s.eps'\n" % output
    params += "set title '%s'\n" % title
    params += "set xlabel 't'\n"
    params += "set ylabel 'new distinct terms'\n"
    params += "plot '%s' using 1:2 t '%s: %d - %d' lc rgb 'red'\n" \
        % (path, 'global', start, end)
    params += "q\n"

    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)
    
    os.remove(path)

def output_global_entropy(entropies, output, use_file_out = False):
    """Output the basic global entropy chart."""

    title = "Entropy of Top-Level Hierarch per Interval"
    skey = sorted(entropies.keys())
    start = skey[0]
    end = skey[-1]

    out = []
    random.seed()
    
    path = "%d.%d" % (random.getrandbits(random.randint(16, 57)),
                      random.getrandbits(random.randint(16, 57)))

    for idx in range(0, len(skey)):
        out.append("%d %f" % (idx, entropies[skey[idx]]))

    if use_file_out:
        with open("%s.data" % output, 'w') as fout:
            fout.write("\n".join(out))

    with open(path, 'w') as fout:
        fout.write("\n".join(out))

    params = "set terminal postscript\n"
    params += "set output '%s.eps'\n" % output
    params += "set title '%s'\n" % title
    params += "set xlabel 't'\n"
    params += "set ylabel 'entropy (nats)'\n"
    params += "plot '%s' using 1:2 t '%s: %d - %d' lc rgb 'red'\n" \
        % (path, "global", start, end)
    params += "q\n"

    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)
    
    os.remove(path)

def output_global_inverse_entropy(entropies, output, use_file_out = False):
    """Output the basic global entropy chart."""

    title = "1-Entropy of Top-Level Hierarch per Interval"
    skey = sorted(entropies.keys())
    start = skey[0]
    end = skey[-1]

    out = []
    random.seed()

    path = "%d.%d" % (random.getrandbits(random.randint(16, 57)),
                      random.getrandbits(random.randint(16, 57)))

    for idx in range(0, len(skey)):
        val = entropies[skey[idx]]
        if val > 0.0:
            out.append("%d %f" % (idx, 1.0 - val))
        else:
            out.append("%d %f" % (idx, 0.0))

    if use_file_out:
        with open("%s.data" % output, 'w') as fout:
            fout.write("\n".join(out))

    with open(path, 'w') as fout:
        fout.write("\n".join(out))

    params = "set terminal postscript\n"
    params += "set output '%s.eps'\n" % output
    params += "set title '%s'\n" % title
    params += "set xlabel 't'\n"
    params += "set ylabel '(1 - entropy) (nats)'\n"
    params += "plot '%s' using 1:2 t '%s: %d - %d' lc rgb 'red'\n" \
        % (path, "global", start, end)
    params += "q\n"

    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)

    os.remove(path)

def output_global_inverse_entropy_json(global_models, entropies, output, x):
    """Output the top values of the global bit, when inverse entropy is >= X.
    """

    skey = sorted(entropies.keys())
    output_model = {}

    for key in skey:
        val = entropies[key]
        if val > 0.0:
            inv = 1.0 - val
            if inv >= x:
                output_model[key] = \
                    vectorspace.top_terms(global_models[key].term_weights, 5)

    with open(output, 'w') as fout:
        fout.write(dumps(output_model, indent=4))

    print "Intervals Identified: %d" % len(output_model)

def usage():
    """Print the massive usage information."""

    print "usage: %s -in <model_data> -out <output_file> [-file] [-json] [-counts] [-entropy] [-top] [-matrix]" % sys.argv[0]
    print "-short - terms that appear more than once in at least one slice are used for any other things you output."
    print "-file - output as a data file instead of running gnuplot."

def main():
    """."""

    # Did they provide the correct args?
    if len(sys.argv) < 5 or len(sys.argv) > 10:
        usage()
        sys.exit(-1)

    use_file_out = False
    output_counts = False
    output_json = False
    output_matrix = False
    output_entropy = False
    output_top = False

    # could use the stdargs parser, but that is meh.
    try:
        for idx in range(1, len(sys.argv)):
            if "-in" == sys.argv[idx]:
                model_file = sys.argv[idx + 1]
            elif "-out" == sys.argv[idx]:
                output_name = sys.argv[idx + 1]
            elif "-file" == sys.argv[idx]:
                use_file_out = True
            elif "-json" == sys.argv[idx]:
                output_json = True
            elif "-matrix" == sys.argv[idx]:
                output_matrix = True
            elif "-counts" == sys.argv[idx]:
                output_counts = True
            elif "-entropy" == sys.argv[idx]:
                output_entropy = True
            elif "-top" == sys.argv[idx]:
                output_top = True
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

    # ----------------------------------------------------------------------
    # Compute the entropy value for the global hierarchical model given the
    # two input models.
    global_views = {}
    entropies = {}

    # Hierarchical model builder.
    for start in results[NOTE_BEGINS[0]]:
        global_views[start] = \
            boringmatrix.HierarchBoring(results[NOTE_BEGINS[0]][start],
                                        results[NOTE_BEGINS[1]][start])

        global_views[start].compute()
        entropies[start] = boringmatrix.basic_entropy(global_views[start])
    
    if output_counts:
        output_distinct_graphs(global_views,
                               "%s_global_distinct" % output_name,
                               use_file_out)
        output_global_new_terms(global_views,
                                "%s_global_newterms" % output_name,
                                use_file_out)

    if output_entropy:
        output_global_entropy(entropies,
                              "%s_global_entropy" % output_name,
                              use_file_out)
        output_global_inverse_entropy(entropies,
                                      "%s_inv_global_entropy" % output_name,
                                      use_file_out)

    if output_matrix:
        gterm_list = build_gtermlist(global_views)
        output_full_matrix(gterm_list,
                           global_views,
                           "%s_global.csv" % output_name)

    if output_json:
        output = "%s_global_top_models.json" % output_name
        output_global_inverse_entropy_json(global_views, 
                                           entropies,
                                           output,
                                           0.045)

    # -------------------------------------------------------------------------
    # Just build a dictionary of the documents.
    if output_top:
        results_as_dict = {}
        doc_length = {}
        doc_freq = {}
        top_terms_slist = None

        for start in global_views:
            doc_id = str(start)

            results_as_dict[doc_id] = global_views[start].term_matrix.copy()
            doc_length[doc_id] = global_views[start].total_count

            for term in results_as_dict[doc_id]:
                try:
                    doc_freq[term] += 1
                except KeyError:
                    doc_freq[term] = 1

        invdoc_freq = \
            vectorspace.calculate_invdf(len(results_as_dict), doc_freq)

        doc_tfidf = \
            vectorspace.calculate_tfidf(doc_length,
                                        results_as_dict,
                                        invdoc_freq)

        output = "%s_%s" % (output_name, "global_top_tfidf.json")
        with open(output, 'w') as fout:
            fout.write(dumps(vectorspace.top_terms_overall(doc_tfidf,
                                                           TOP_TERM_CNT),
                             indent=4))

        top_terms_slist = \
            vectorspace.top_terms_overall(results_as_dict,
                                          int(len(doc_freq)*.10))

        output = "%s_%s" % (output_name, "global_top_tf.json")
        with open(output, 'w') as fout:
            fout.write(dumps(top_terms_slist, indent=4))

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
    