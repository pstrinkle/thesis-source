#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

##
# @author: Patrick Trinkle
# Summer 2011
# Spring 2012
#
# @summary: This handles the language model stuff.
#
# Currently implemented for words, Bigram model.

def build_matrix(document, invalids=""):
    """Given a string, build a matrix of occurrences of pairs of terms.
  
    Input: document := string you want to parse
           invalids := string pieces to remove, as single characters in a string
    Output: matrix of occurrences {'termA + "_" + termB' => int}
    
    XXX: Switch to use (termA, termB, int) ... 
  
    The matrix is built as a dictionary, key'd by the paired terms. """
    
    term_matrix = {}
    words = document.split(' ')
  
    while ' ' in words:
        words.remove(' ')
  
    while '' in words:
        words.remove('')
  
    for word in words:
        if word in invalids:
            words.remove(word)
  
    # -1 here because we extend each step by +1
    for i in xrange(0, len(words) - 1):
        term = words[i] + "_" + words[i + 1]

        try:
            term_matrix[term] += 1
        except KeyError:
            term_matrix[term] = 1
  
    return term_matrix

def update_matrix(current_matrix, update_matrix):
    """Given a current matrix and an update matrix, update it!
  
    Input: current_matrix := current matrix of occurrences
           update_matrix := update matrix of occurrences

    Output: updated matrix
  
    This should be used in tandem with build_matrix()"""
    
    for k, v in update_matrix.items():
        try:
            current_matrix[k] += v
        except KeyError:
            current_matrix[k] = v

    return current_matrix

class LanguageStore:
    """Store the language model, this includes raw data and stats to allow for
    updating.
  
    Currently only works on Bigrams. (pairs of words)"""

    def __init__(self, initial_document=None, invalids=None):
        self.matrix = None
        self.stats = None
        self.invalids = invalids
    
        if initial_document is not None:
            self.matrix = build_matrix(initial_document, invalids)
      
            # build statistics.
  
    def get_probability(self, seq_bow=""):
        """Given a document as a list of words in sequence, return the 
        probability of such a sentence given the current state of the model."""

        return None

    def update_model(self, seq_bow=""):
        """Add this document to the data used by the model to blah, blah, 
        blah"""
    
        return
    

