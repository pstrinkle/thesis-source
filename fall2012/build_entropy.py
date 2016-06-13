#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Fall 2012
#
# This outputs the input model for entropy processing.
#

import os
import sys
import random
import subprocess
from json import dumps, loads
from math import log

import boringmatrix

sys.path.append("../modellib")
import vectorspace

NOTE_BEGINS = ("i495", "boston")

def output_basic_entropy(entropies, output, use_file_out = False):
    """Output the basic entropy chart."""

    title = "Entropy of each Vector"
    skey = sorted(entropies[NOTE_BEGINS[0]].keys())
    start = skey[0]
    end = skey[-1]

    out = []
    random.seed()
    
    path = "%d.%d" % (random.getrandbits(random.randint(16, 57)),
                      random.getrandbits(random.randint(16, 57)))

    for idx in range(0, len(skey)):
        out.append("%d %f %f" % (idx,
                                 entropies[NOTE_BEGINS[0]][skey[idx]],
                                 entropies[NOTE_BEGINS[1]][skey[idx]]))

    if use_file_out:
        with open("%s.data" % output, 'w') as fout:
            fout.write("\n".join(out))

    with open(path, 'w') as fout:
        fout.write("\n".join(out))

    params = "set terminal postscript\n"
    params += "set output '%s.eps'\n" % output
    params += "set title '%s'\n" % title
    params += "set xlabel 't'\n"
    params += "set ylabel 'entropy scores'\n"
    params += "plot '%s' using 1:2 t '%s: %d - %d' lc rgb 'red', " \
        % (path, NOTE_BEGINS[0], start, end)
    params += "'%s' using 1:3 t '%s: %d - %d' lc rgb 'blue'\n" \
        % (path, NOTE_BEGINS[1], start, end)
    params += "q\n"
    
    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)
    
    os.remove(path)

def output_inverse_entropy(entropies, output, use_file_out = False):
    """Output the basic entropy chart."""

    title = "1-Entropy of each Vector"
    skey = sorted(entropies[NOTE_BEGINS[0]].keys())
    start = skey[0]
    end = skey[-1]

    out = []
    random.seed()
    
    path = "%d.%d" % (random.getrandbits(random.randint(16, 57)),
                      random.getrandbits(random.randint(16, 57)))

    for idx in range(0, len(skey)):
        val1 = entropies[NOTE_BEGINS[0]][skey[idx]]
        val2 = entropies[NOTE_BEGINS[1]][skey[idx]]

        if val1 > 0.0:
            out1 = 1.0 - val1
        else:
            out1 = 0.0

        if val2 > 0.0:
            out2 = 1.0 - val2
        else:
            out2 = 0.0

        out.append("%d %f %f" % (idx, out1, out2))

    if use_file_out:
        with open("%s.data" % output, 'w') as fout:
            fout.write("\n".join(out))

    with open(path, 'w') as fout:
        fout.write("\n".join(out))

    params = "set terminal postscript eps color\n"
#    params += "set arrow 10 from 0,0.045 to 100,0.045 nohead\n"
    params += "set output '%s.eps'\n" % output
    params += "set title '%s'\n" % title
    params += "set xlabel 't'\n"
    params += "set ylabel '(1 - entropy) scores'\n"
    params += "plot '%s' using 1:2 t '%s: %d - %d' lc rgb 'red', " \
        % (path, NOTE_BEGINS[0], start, end)
    params += "'%s' using 1:3 t '%s: %d - %d' lc rgb 'blue'\n" \
        % (path, NOTE_BEGINS[1], start, end)
    params += "q\n"
    
    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)
    
    os.remove(path)

def output_top_model_entropy(results, entropies, output, x, both_required):
    """Go through the entropy values and output the top terms from the models, 
    when the entropy goes low beyond some threshold, or when 1 - H(x) >= x"""
    
    output_model = {}
    
    # entropies[NOTE_BEGINS[0]][start] = basic_entropy()
    # results[note][start] = boringmatrix.BoringMatrix()
    skey = sorted(entropies[NOTE_BEGINS[0]].keys())

    # could probably just do for key in skey... like I do elsewhere. lol.
    for idx in range(0, len(skey)):
        val1 = entropies[NOTE_BEGINS[0]][skey[idx]]
        val2 = entropies[NOTE_BEGINS[1]][skey[idx]]

        if val1 > 0.0:
            out1 = 1.0 - val1
        else:
            out1 = 0.0

        if val2 > 0.0:
            out2 = 1.0 - val2
        else:
            out2 = 0.0

        if both_required:
            if out1 >= x and out2 >= x:
                output_model["%d-%s" % (skey[idx], NOTE_BEGINS[0])] = \
                    vectorspace.top_terms(results[NOTE_BEGINS[0]][skey[idx]].term_weights, 5)
                output_model["%d-%s" % (skey[idx], NOTE_BEGINS[1])] = \
                    vectorspace.top_terms(results[NOTE_BEGINS[1]][skey[idx]].term_weights, 5)
        else:
            if out1 >= x:
                output_model["%d-%s" % (skey[idx], NOTE_BEGINS[0])] = \
                    vectorspace.top_terms(results[NOTE_BEGINS[0]][skey[idx]].term_weights, 5)

            if out2 >= x:
                output_model["%d-%s" % (skey[idx], NOTE_BEGINS[1])] = \
                    vectorspace.top_terms(results[NOTE_BEGINS[1]][skey[idx]].term_weights, 5)

    with open(output, 'w') as fout:
        fout.write(dumps(output_model, indent=4))
    
    print "Intervals Identified: %d" % len(output_model)

#### Unused
def output_renyi_entropy(alpha, entropies, output, use_file_out = False):
    """Output the basic entropy chart."""

    title = "Renyi Entropy of each Vector"
    skey = sorted(entropies[NOTE_BEGINS[0]].keys())
    start = skey[0]
    end = skey[-1]

    out = []
    random.seed()
    
    path = "%d.%d" % (random.getrandbits(random.randint(16, 57)),
                      random.getrandbits(random.randint(16, 57)))

    for idx in range(0, len(skey)):
        out.append("%d %f %f" % (idx,
                                 entropies[NOTE_BEGINS[0]][skey[idx]],
                                 entropies[NOTE_BEGINS[1]][skey[idx]]))

    if use_file_out:
        with open("%s.data" % output, 'w') as fout:
            fout.write("\n".join(out))

    with open(path, 'w') as fout:
        fout.write("\n".join(out))

    params = "set terminal postscript\n"
    params += "set output '%s.eps'\n" % output
    params += "set title '%s'\n" % title
    params += "set xlabel 't'\n"
    params += "set ylabel 'renyi scores - %f'\n" % alpha
    params += "plot '%s' using 1:2 t '%s: %d - %d' lc rgb 'red', " \
        % (path, NOTE_BEGINS[0], start, end)
    params += "'%s' using 1:3 t '%s: %d - %d' lc rgb 'blue'\n" \
        % (path, NOTE_BEGINS[1], start, end)
    params += "q\n"
    
    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)
    
    os.remove(path)
######

def renyi_entropy(boring_a, alpha):
    """Compute the Renyi entropy for the given model."""
    
    entropy = 0.0
    
    if len(boring_a.term_matrix) == 0:
        return 0.0
    
    for term in boring_a.term_matrix:
        entropy += pow(boring_a.term_weights[term], alpha)
    
    entropy = log(entropy, 2)
    
    return (1.0 / (1.0 - alpha)) * entropy

def usage():
    """Print the massive usage information."""

    print "usage: %s -in <model_data> -out <output_file> [-short] [-renyi] [-file] [-json [-both]] [-graphs]" % sys.argv[0]
    print "-short - terms that appear more than once in at least one slice are used for any other things you output."
    print "-file - output as a data file instead of running gnuplot."

def main():
    """."""

    # Did they provide the correct args?
    if len(sys.argv) < 5 or len(sys.argv) > 10:
        usage()
        sys.exit(-1)

    use_short_terms = False
    use_file_out = False
    use_renyi = False
    output_json = False
    output_graphs = False
    both_required = False

    # could use the stdargs parser, but that is meh.
    try:
        for idx in range(1, len(sys.argv)):
            if "-in" == sys.argv[idx]:
                model_file = sys.argv[idx + 1]
            elif "-out" == sys.argv[idx]:
                output_name = sys.argv[idx + 1]
            elif "-renyi" == sys.argv[idx]:
                use_renyi = True
            elif "-short" == sys.argv[idx]:
                use_short_terms = True
            elif "-file" == sys.argv[idx]:
                use_file_out = True
            elif "-json" == sys.argv[idx]:
                output_json = True
            elif "-graphs" == sys.argv[idx]:
                output_graphs = True
            elif "-both" == sys.argv[idx]:
                both_required = True
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

    # compute the basic entropy of each model.
    # this computes the entropy for the model within the windows, which
    # is the maximum timeframe at this point.  I need to check and make sure
    # we don't have an incorrect last segment.
    entropies = {NOTE_BEGINS[0] : {}, NOTE_BEGINS[1] : {}}

    for start in results[NOTE_BEGINS[0]]:
        entropies[NOTE_BEGINS[0]][start] = \
            boringmatrix.basic_entropy(results[NOTE_BEGINS[0]][start])
        entropies[NOTE_BEGINS[1]][start] = \
            boringmatrix.basic_entropy(results[NOTE_BEGINS[1]][start])

    if output_graphs:
        output_basic_entropy(entropies,
                             "%s_entropy" % output_name,
                             use_file_out)
        output_inverse_entropy(entropies,
                               "%s_inv_entropy" % output_name,
                               use_file_out)

    if output_json:
        output_top_model_entropy(results, 
                                 entropies,
                                 "%s_top_models.json" % output_name,
                                 0.045,
                                 both_required)

    if use_renyi:
        for alpha in (0.10, 0.25, 0.5, 0.75):
            renyi = {NOTE_BEGINS[0] : {}, NOTE_BEGINS[1] : {}}

            for start in results[NOTE_BEGINS[0]]:
                renyi[NOTE_BEGINS[0]][start] = \
                    renyi_entropy(results[NOTE_BEGINS[0]][start], alpha)
                renyi[NOTE_BEGINS[1]][start] = \
                    renyi_entropy(results[NOTE_BEGINS[1]][start], alpha)
            output_basic_entropy(renyi,
                                 "%s_renyi-%f" % (output_name, alpha),
                                 use_file_out)

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
    