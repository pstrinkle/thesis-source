#!/usr/bin/env python

##
# @author: Patrick Trinkle
# Date:    May 20, 2010
# Purpose: Convert basic wiki pages to LateX.
#
# If strikethrough: \usepackage{ulem}
#
# Implemented the following:
# '' ''' '''' '''''
# <b><i><s><strike><math><u><tt><code>
# == === ==== =====
# some images
#
# Future support:
# tables, <small>, <sub>, <sup>
#
# if strikethrough: \usepackage{ulem}
# if images: \usepackage{graphicx}

import sys
import re

# Nice beginning strings
dbg = "% debug: "

# LaTeX Strings
enum = "enumerate"
items = "itemize"
verbatim = "verbatim"
it = "\\item"
end = "\\end{"
begin = "\\begin{"
endl = "}\n"

# Regex for Finding Stuff
find_headers = re.compile("=")
find_list = re.compile("(#|\*)")

# Useful Global Level Variables
leveltype = list()
inlist = False
inCode = False
listlevel = 0
lasttype = ""

def handleCode(input):
    global inCode

    # Code either has pre in front of it.  or a space.
    # let's only handle space

    if inCode:
        # Are we still in a code section?
        if re.match(r" ", input):
            # Yes, we are.
            return input
        else:
            # No, we're not.
            input = end + verbatim + endl + input
            inCode = False
    elif re.match(r" ", input):
        # Now we're in a code section
        input = begin + verbatim + endl + input
        inCode = True

    return input

# This function attempts to handle all in-line changes
# May not work properly if broken by new lines
# Fix formatting
# Doesn't handle arbitrary excessive single-quoting
# ''''' => \textbf{textit{}}
# '''' => '\textbf{}'
# ''' => \textbf{}
# '' => \textit{}
# ' => '
# <tt> => \texttt{}
# <s|strike|del> => \sout{}
# <b> => \textbf{}
# <i> => \textit{}
# <u> => \underline{}
# " & " => " \& "
# <math>\chi^2</math> => $\chi^2$
# Remove links
# [[a|b]] => b
# Fix Images - only one per line
# Also, I center all images, although unnecessary as I could pull their 
# information from their wiki tag.
# Really this just does a lot of the leg work, you will want to skim it for 
# correctness and make changes as necessary.
# Because LaTeX doesn't support special formatting in verbatim output you
# need to check to make sure your wiki doesn't have bolding or links in the
# code display, or remove them from the tex before compiling.
def withinline(input):
    find_boldits = re.compile("'{2,5}")
    find_braces = re.compile("\[\[.*?\|.*?\]\]")
    find_html = re.compile("\<(u|b|i|tt|math|s|strike|del|code)\>.*?\</(u|b|i|tt|math|s|strike|del|code)\>", re.IGNORECASE)
    find_strikes = re.compile(r"(.*?)<(s|strike|del|)>(.*?)</(s|strike|del)>(.*?\n)", re.IGNORECASE)
    find_tt = re.compile(r"(.*?)<tt>(.*?)</tt>(.*?\n)", re.IGNORECASE)
    find_code = re.compile(r"(.*?)<code>(.*?)</code>(.*?\n)", re.IGNORECASE)
    find_bf = re.compile(r"(.*?)<b>(.*?)</b>(.*?\n)", re.IGNORECASE)
    find_it = re.compile(r"(.*?)<i>(.*?)</i>(.*?\n)", re.IGNORECASE)
    find_un = re.compile(r"(.*?)<u>(.*?)</u>(.*?\n)", re.IGNORECASE)
    find_math = re.compile(r"(.*?)<math>(.*?)</math>(.*?\n)", re.IGNORECASE)

    # We only remove this special character from non-verbatim lines.
    if re.match(r" ", input):
        return input

    while re.search(r"[^\\]_", input):
        m_und = re.search(r"(.*?[^\\])_(.*?\n)", input)
        if m_und:
            input = m_und.group(1) + "\_" + m_und.group(2)

    while re.search(r" & ", input):
        m_amp = re.search(r"(.*?)&(.*?\n)", input)
        if m_amp:
            input = m_amp.group(1) + "\&" + m_amp.group(2)

    while re.search(r"[^\\]%", input):
        m_per = re.search(r"(.*?[^\\])%(.*?\n)", input)
        if m_per:
            input = m_per.group(1) + "\%" + m_per.group(2)

    # We also cannot embed nice stuff into headers.
    # But we do have to clean them.
    if re.match(r"=", input):
        return input

    while find_html.search(input):
        m_s = find_strikes.search(input)
        m_tt = find_tt.search(input)
        m_c = find_code.search(input)
        m_bf = find_bf.search(input)
        m_it = find_it.search(input)
        m_un = find_un.search(input)
        m_m = find_math.search(input)

        if m_s:
            input = m_s.group(1) + "\\sout{" + m_s.group(3) + "}" + m_s.group(5)
        elif m_tt:
            input = m_tt.group(1) + "\\texttt{" + m_tt.group(2) + "}" + m_tt.group(3)
        elif m_bf:
            input = m_bf.group(1) + "\\textbf{" + m_bf.group(2) + "}" + m_bf.group(3)
        elif m_it:
            input = m_it.group(1) + "\\textit{" + m_it.group(2) + "}" + m_it.group(3)
        elif m_un:
            input = m_un.group(1) + "\\underline{" + m_un.group(2) + "}" + m_un.group(3)
        elif m_m:
            input = m_m.group(1) + "$" + m_m.group(2) + "$" + m_m.group(3)
        elif m_c:
            input = m_c.group(1) + "\\texttt{" + m_c.group(2) + "}" + m_c.group(3)

    while find_boldits.search(input):
        m_bi = re.search("(.*?)'''''(.*?)'''''(.*?\n)", input)
        m_bb = re.search("(.*?)''''(.*?)''''(.*?\n)", input)
        m_b = re.search("(.*?)'''(.*?)'''(.*?\n)", input)
        m_i = re.search("(.*?)''(.*?)''(.*?\n)", input)

        if m_bi:
            input = m_bi.group(1) + "\\textbf{\\textit{" + m_bi.group(2) + "}}" + m_bi.group(3)
        elif m_bb:
            input = m_bb.group(1) + "'\\textbf{" + m_bb.group(2) + "}'" + m_bb.group(3)
        elif m_b:
            input = m_b.group(1) + "\\textbf{" + m_b.group(2) + "}" + m_b.group(3)
        elif m_i:
            input = m_i.group(1) + "\\textit{" + m_i.group(2) + "}" + m_i.group(3)

    m_img = re.match(r"\[\[Image:(.*?)\|(.*?)\.*?\n", input)
    if m_img:
        input = begin + "center}\n"
        input += "\includegraphics[keepaspectratio=true,scale=0.75]{" + m_img.group(1) + endl
        input += end + "center}\n"

    while find_braces.search(input):
        m_b = re.search("(.*?)\[\[.*?\|(.*?)\]\](.*?\n)", input)
        if m_b:
            input = m_b.group(1) + m_b.group(2) + m_b.group(3)

    return input

def handleLists(input):
    global inlist
    global lasttype
    global listlevel
    global leveltype

    # are we still in a list.
    if find_list.match(input):
        # we are still in a list.
        depth = input.find(" ")
        thistype = input[depth - 1]

        # if depth is 1 and type has changed it's a new list, dump and start over
        if depth == 1 and lasttype != thistype:
            pre = ""
            while (len(leveltype) > 0):
                lvl = leveltype.pop()
                pre += end + lvl + endl

            listlevel = 1

            if thistype == "#":
                leveltype.append(enum)
                pre += begin + enum + endl
            elif thistype == "*":
                leveltype.append(items)
                pre += begin + items + endl
            else:
                sys.stderr.write("invalid list character on line: " + input)
                sys.exit()

            # write out first line of the new list type
            input = pre + it + input[depth:]
            lasttype = thistype
        elif depth > (listlevel + 1):
            sys.stderr.write("trying to jump too many levels at once: " + input)
            sys.exit()
        # if depth is greater than listlevel, increase listlevel and add pre for
        # the ending type
        elif depth > listlevel:
            pre = ""
            listlevel += 1

            if thistype == "#":
                leveltype.append(enum)
                pre = begin + enum + endl
            elif thistype == "*":
                leveltype.append(items)
                pre = begin + items + endl
            else:
                sys.stderr.write("invalid list character on line: " + input)
                sys.exit()

            input = pre + it + input[depth:]
            lasttype = thistype
        # if the depth is the same as listlevel, check the type with the last type
        #   if the types are different, this won't work in LaTeX -- warn and ignore
        elif depth == listlevel:
            pre = ""
            if lasttype != thistype:
                pre = "% LaTeX does not support switching midstream\n"

            input = pre + it + input[depth:]
        # if depth < listlevel we need to add end's for how much less it is.
        elif depth < listlevel:
            pre = ""
            i = listlevel - depth

            while i > 0:
                listlevel -= 1
                lvl = leveltype.pop()
                pre += end + lvl + endl
                i -= 1

            input = pre + it + input[depth:]
            lasttype = thistype
        else:
            sys.stderr.write("a case I hadn't thought of!!!")
            sys.exit()
    else:
        pre = ""
        # we are no longer in the list all!
        while (len(leveltype) > 0):
            lvl = leveltype.pop()
            pre += end + lvl + endl

        input = pre + input
        inlist = False

    return input

def newList(input):
    global inlist
    global lasttype
    global listlevel
    global leveltype
    
    inlist = True
    listlevel = 1
    depth = 0
    pre = ""

    m_star = re.match("\*+", input)
    m_enum = re.match("#+", input)
    if m_enum:
        depth = len(m_enum.group(0))
        pre = begin + enum + endl
        leveltype.append(enum)
        lasttype = "#"
    elif m_star:
        depth = len(m_star.group(0))
        pre = begin + items + endl
        leveltype.append(items)
        lasttype = "*"

    if depth != 1:
        sys.stderr.write("error on line: " + input)
        sys.exit()
    else:
        input = pre + it + input[depth:]

    return input

def fixHeader(input):
    x = find_headers.findall(input)
    # We know it's divisible by two because they are on both sides
    header_lvl = (len(x) / 2) - 1

    header = re.search(r"=+(.*?)=+", input)
    if header:
        if header_lvl == 1:
            input = "\section{" + header.group(1) + endl
        else:
            i = 1
            full = "\\"
            while i < header_lvl:
                full += "sub"
                i += 1
            input = full + "section{" + header.group(1) + endl
    else:
        sys.stderr.write("error with line: " + input)
        sys.exit()

    return input

def main():

    # check for correct # of arguments
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        sys.stderr.write("Usage: " + sys.argv[0] + " <input.wiki> <output.tex> [header.tex]\n")
        sys.stderr.write("\n")
        sys.stderr.write("This script will by default add " + begin)
        sys.stderr.write("document} and the " + end + "document}")
        sys.exit()

    ifp = open(sys.argv[1], "r")
    ofp = open(sys.argv[2], "w")

    content = ifp.readlines()
    ifp.close()

    if len(sys.argv) == 4:
        ifp = open(sys.argv[3], "r")
        header = ifp.readlines()
        ifp.close()
        for line in header:
            ofp.write(line)

    ofp.write(begin + "document" + endl)

    cnt = 0
    for line in content:
        cnt += 1
        # Handle all changes within a line
        line = withinline(line)
        line = handleCode(line)

        # Process list items.
        # In wiki you can start two lists without a space between them
        # by just using different types, but I may not support that.
        # 
        # Also, you cannot start a list somewhat deep.
        # Currently this doesn't support : indent characters.
        if inlist:
            line = handleLists(line)
        elif find_list.match(line):
            # We weren't in a list, but we are now.
            line = newList(line)

        # Fix Headers
        if find_headers.match(line):
            line = fixHeader(line)

        ofp.write(line)

    if len(leveltype) > 0:
        pre = ""
        while (len(leveltype) > 0):
            lvl = leveltype.pop()
            pre += end + lvl + endl

        line = pre
        ofp.write(line)

    ofp.write(end + "document" + endl)
    ofp.close()

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()