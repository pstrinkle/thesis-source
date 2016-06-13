#! /usr/bin/python
"""Module developed for outputing data as an image."""

__author__ = 'tri1@umbc.edu'

##
# @author: Patrick Trinkle
# Spring 2012
#
# @summary: This module is meant to represent output of data.
#

import sys
from math import ceil
from PIL import Image
from operator import itemgetter

MAX_COLOR = 256**3
MAX_GREYSCALE = 256

def image_detect_rows(file_name):
    """Given a file, open it, and then walk the rows looking for ones with the
    highest non-zero values.
    
    Returns a sorted list of the row sums, largest to smallest.
    
    Only works on rgb images."""
    
    img = Image.open(file_name)
    pix = img.load()
    width, height = img.size
    
    rows = {}
    
    for i in range(height):
        rows[i] = sum(\
                      [int("".join(["%x" % val for val in pix[j, i]]), 16) \
                        for j in range(width) if pix[j, i] != (0, 0, 0)])

    return sorted(rows.items(), key=itemgetter(1), reverse=True)

def image_detect_important(file_name):
    """Given a file, open it, and then walk the rows looking for ones with the
    highest sums.
    
    Returns a sorted list of the row sums, largest to smallest.
    
    Only works on rgb images."""
    
    img = Image.open(file_name)
    pix = img.load()
    width, height = img.size
    
    rows = {}
    
    for i in range(height):
        rows[i] = sum(\
                      [int("".join(["%x" % val for val in pix[j, i]]), 16) \
                        for j in range(width)])

    return sorted(rows.items(), key=itemgetter(1), reverse=True)

def data_to_color(dictionary, data, val_range):
    """Return the matrix as a color image.
    
    dictionary is the dictionary of terms.
    data       is the document-weight dictionary.
    val_range  is the value range, max - min.
    
    Please pre-sort dictionary"""

    # Each column is a document within data
    # Each row is a term.

    # for greyscale.
    img = Image.new('RGB', (len(data), len(dictionary)))
    pix = img.load()
    
    #print "\twidth: %d; height: %d" % (len(data), len(dictionary)) 

    # This code is identical to the method used to create the text file.
    # Except because it's building bitmaps, I think it will be flipped. lol.
    sorted_docs = sorted(data.keys())
    
    # val_range value is how far the minimum value and maximum value are apart 
    # from each other.
    # so val_range / color_range gives us a way of representing the values with 
    # shading. --> divisible.
    #
    # math.floor(val / divisible) -> shade.
    #
    # the lower the value, the closer to black -- so this will create images
    # that are black with light spots.
    shade_range = float(val_range / MAX_COLOR)

    if shade_range == 0:
        sys.stderr.write("invalid shade_range\n")
        sys.exit(-3)
    
    #print "%f" % shade_range
    # my pictures really hm... maybe, I should halve the scale.

    # Print Term Rows
    # with L the pixel value is from 0 - 255 (black -> white)
    #
    # pix[x, y] -- x is column, y is row. y is i.
    for i in range(len(dictionary)):
        for j in range(len(sorted_docs)):
            # for each row, for each column
            if dictionary[i] in data[sorted_docs[j]]:
                val = data[sorted_docs[j]][dictionary[i]]

                color = ceil(val / shade_range)

                # not bloodly likely (until i switched to ceil)                
                if color > MAX_COLOR-1:
                    color = MAX_COLOR-1
                
                tmp = "%06x" % color
                
                pix[j, i] = \
                    (int(tmp[0:2], 16), int(tmp[2:4], 16), int(tmp[4:6], 16))
            else:
                pix[j, i] = 0 # (white) i is row, j is column.
    
    return img

def image_create_rgb2l(file_name, dictionary, data, val_range):
    """Dump the matrix as a color png file.

    file_name  is the file to create.
    dictionary is the dictionary of terms.
    data       is the document-weight dictionary.
    val_range  is the value range, max - min.
    
    Please pre-sort dictionary"""
    
    img = data_to_color(dictionary, data, val_range)
    img = img.convert("L")
    img.save(file_name + '.png')

def image_create_color(file_name, dictionary, data, val_range):
    """Dump the matrix as a color png file.

    file_name  is the file to create.
    dictionary is the dictionary of terms.
    data       is the document-weight dictionary.
    val_range  is the value range, max - min.
    
    Please pre-sort dictionary"""
    
    img = data_to_color(dictionary, data, val_range)
    img.save(file_name + '.png')

def image_create(file_name, dictionary, data, val_range, background):
    """Dump the matrix as a grey-scale png file.
    
    file_name  is the file to create.
    dictionary is the dictionary of terms.
    data       is the document-weight dictionary.
    val_range  is the value range, max - min.
    background is either 'white' or 'black'.
    
    Please pre-sort dictionary."""

    # Each column is a document within data
    # Each row is a term.

    # for greyscale.
    img = Image.new('L', (len(data), len(dictionary)))
    pix = img.load()
    
    if background == "white":
        backcolor = 255
    elif background == "black":
        backcolor = 0
    else:
        sys.stderr.write("invalid parameter\n")
        sys.exit(-3)
    
    #print "\twidth: %d; height: %d" % (len(data), len(dictionary)) 

    # This code is identical to the method used to create the text file.
    # Except because it's building bitmaps, I think it will be flipped. lol.
    sorted_docs = sorted(data.keys())
    
    # val_range value is how far the minimum value and maximum value are apart 
    # from each other.
    # so val_range / color_range gives us a way of representing the values with 
    # shading. --> divisible.
    #
    # math.floor(val / divisible) -> shade.
    #
    # the lower the value, the closer to black -- so this will create images
    # that are black with light spots.
    shade_range = float(val_range / MAX_GREYSCALE)

    if shade_range == 0:
        sys.stderr.write("invalid shade_range\n")
        sys.exit(-3)
    
    #print "%f" % shade_range
    # my pictures really hm... maybe, I should halve the scale.

    # Print Term Rows
    # with L the pixel value is from 0 - 255 (black -> white)
    for i in range(len(dictionary)):
        for j in range(len(sorted_docs)):
            # for each row, for each column
            if dictionary[i] in data[sorted_docs[j]]:
                val = data[sorted_docs[j]][dictionary[i]]
                
                #print "%f" % val
                #print "%d" % math.floor(val / shade_range)
                
                # with floor and most values of mine very small; maybe it'll
                # set most to just 0 instead of a value when they shouldn't
                # really be zero.
                #color = math.floor(val / shade_range)
                
                # doing math.floor means you will have 0s for your low data --
                # which means there was no data point -- not what we want.
                #
                # could do pix[] = 255 - color to switch to white background.
                
                color = ceil(val / shade_range)
                
                # not bloodly likely (until i switched to ceil)
                if color > MAX_GREYSCALE-1:
                    color = MAX_GREYSCALE-1
                
                #print "color: %d" % color
                if backcolor == 0:
                    pix[j, i] = color
                else:
                    pix[j, i] = 255 - color
            else:
                pix[j, i] = backcolor # (white) i is row, j is column.

    img.save(file_name + '.png')
