#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

##
# @author: Patrick Trinkle
# Spring 2012
#
# @summary: Given a CSV, it'll build a .tex file for the invoice.
#

import sys

class Expense:
    """Container for holding an expense."""

    def __init__(self, details):
        self.name = details[0].replace("#", "\#").replace("&", "\&").strip()
        self.date = details[1].strip()
        self.cat = details[2].strip()
        self.total = details[3].replace("$", "").strip()
        self.effective = details[4].replace("$", "").strip()
    
    def __str__(self):
        return "%s & %s & %s &  %s & %s" % \
            (self.name, self.date, self.cat, self.total, self.effective)

    def get_value(self):
        return float(self.effective)

def usage():
    """Parameters."""

    sys.stderr.write("usage: %s <in.csv> number <out.tex>\n" % sys.argv[0])

def main():

    if len(sys.argv) != 4:
        usage()
        sys.exit(-1)

    input_file = sys.argv[1]  
    num_val = int(sys.argv[2])
    output_file = sys.argv[3]
    
    # --------------------------------------------------------------------------
    
    # (num_val)
    header = \
    """
\\documentclass[11pt]{article}
\\usepackage{amssymb,amsmath}
\\usepackage{dsfont}
\\usepackage{times}
\\usepackage[left=1in, right=1in, top=1in, bottom=0.5in, includefoot]{geometry}
\\setlength\\parindent{0.25in}
\\setlength\\parskip{1mm}

% This package is for including our graph
\\usepackage{graphicx}
    """
    
    inv = \
    """
\\title{Invoice \#%d}
\\author{Patrick Trinkle}
\\date{\\today}

\\begin{document}

\\maketitle

\\section{Introduction}
    """
    
    # fill with (shared, house, bills)
    intro = \
    """
This invoice covers the following expenses. In this table, ``shared'' expenses at %d\\%% and ``house'' at %d\\%% and ``bills'' at %d\\%%.
    """
    
    table_top = \
    """
\section{Expenses}

% Items  Date  Type  Value  Net Value
\\begin{tabular}{| l | r | l | r | r |}
\\hline
\\textbf{Item} & \\textbf{Date} & \\textbf{Type} & \\textbf{Value (\$)} & \\textbf{Net Value (\$)}\\\\
\\hline
"""
    
    # (expense, date, total_cost, percentage_cost)
    item = """%s\\\\ \n"""
    
    # (sum)
    bottom = \
    """
\\hline
\\multicolumn{4}{|l|}{\\textbf{Total:}} & %s \\\\
\\hline
\\end{tabular}
\\end{document}
    """

    # --------------------------------------------------------------------------
    # Pull invoice entries from csv file.
    with open(input_file, "r") as f:
        entries = f.readlines()

    # --------------------------------------------------------------------------
    
    shared = 12
    house = 50
    bills = 40
    
    output = header
    output += inv % num_val
    output += intro % (shared, house, bills)
    output += table_top
    
    total = 0.0

    for entry in entries:
        exp = Expense(entry.strip().split(","))

        output += item % exp
        total += exp.get_value()    
    
    output += bottom % total
    
    with open(output_file, "w") as f:
        f.write(output)

if __name__ == "__main__":
    main()
