"""Code for building a vectorspace model."""

__author__ = 'tri1@umbc.edu'

##
# @author: Patrick Trinkle
# Summer 2011
# Spring 2012
#
# @summary: This handles the vector space model stuff.
#

from math import log10
from operator import itemgetter

def build_dictionary(docs, stopwords):
    """docs is a dictionary of documents."""
    
    words = []
    
    for doc_id in docs:
        pruned = \
            set([w for w in docs[doc_id].split(' ') \
                    if w not in stopwords and len(w) > 1])
        
        words.extend([w for w in pruned if w not in words])
    
    return words

def top_terms_tuples(vector, num):
    """Returns the num-highest tf-idf terms in the vector.

    This is an array of tuples [0] - term, [1] -- value.

    num := the number of terms to get.

    This is not identical to the similarly named function in the vectorspace
    module.  It is however, identical to this exact function there."""

    sorted_tokens = sorted(
                           vector.items(),
                           key=itemgetter(1), # (1) is value
                           reverse=True)

    # count to index 
    top = []

    for i in xrange(0, min(num, len(sorted_tokens))):
        top.append(sorted_tokens[i])

    return top

def top_terms(vector, num):
    """Returns the num-highest tf-idf terms in the vector.
    
    This returns the array of terms, not the values.
    
    num := the number of terms to get."""

    # This doesn't seem to work right when I used it here.  It works fine
    # in manual python testing and in the centroid library (i'm assuming).
    sorted_tokens = sorted(
                           vector.items(),
                           key=itemgetter(1), # (1) is value
                           reverse=True)

    # count to index
    terms = []

    # terms = \
    #     [sorted_tokens[i][0] for i in xrange(0, min(num, len(sorted_tokens))]
  
    for i in xrange(0, min(num, len(sorted_tokens))):
        terms.append(sorted_tokens[i][0])

    return terms

def top_terms_overall(doc_tfidf, count):
    """Get the top terms overall for the entire set of columns.

    len(terms) is actually count -- taken from frame module."""

    # Interestingly, many columns can have similar top terms -- with 
    # different positions in the list...  So, this will have to be taken 
    # into account.  Build the overall list and then sort it, then get the
    # first count of the unique...
    #
    terms = {}

    for doc_id in doc_tfidf:
        new_tuples = top_terms_tuples(doc_tfidf[doc_id], count)

        # These are the top tuples for doc_id; if they are not new, then 
        # increase their value to the new max.            
        for kvp in new_tuples:
            if kvp[0] in terms:
                terms[kvp[0]] = max(kvp[1], terms[kvp[0]])
            else:
                terms[kvp[0]] = kvp[1]

    # terms is effectively a document now, so we can use this.
    return top_terms(terms, count)

def calculate_invdf(doc_count, doc_freq):
    """Calculate the inverse document frequencies.
  
    The inverse document frequency is how many documents there are divided by 
    in how many documents the term appears.
  
    Input: doc_count := number of documents
        doc_freq := dictionary of document frequencies, key'd by term
  
    Output: invdoc_freq := dictionary of inverse document frequencies, key'd by 
                        term
  
    idf = log(document count / in how many documents)"""
  
    invdoc_freq = {}
  
    for term in doc_freq:
        invdoc_freq[term] = log10(float(doc_count) / doc_freq[term])

    return invdoc_freq

def calculate_tfidf(doc_length, doc_termfreq, invdoc_freq):
    """Calculate the tf-idf values.
  
    Input: doc_length := total frequency (not distinct count), key'd on doc id
         doc_termfreq := dictionary of term frequencies, key'd on document, 
                         then key'd by term.
         invdoc_freq := dictionary of inverse document frequencies, key'd on 
                        term.
         
    Output: doc_tfidf := dictionary of tf-idf values, key'd on document
  
    A high weight in tf-idf is reached by a high term frequency (in the given 
    document) and a low document frequency of the
    # term in the whole collection of documents.
  
    td-idf = 
        (term count / count of all terms in document) 
            * log(document count / in how many documents)"""

    doc_tfidf = {}

    for doc in doc_termfreq.keys():
        doc_tfidf[doc] = {} # Prepare the dictionary for that document.
        
        for word in doc_termfreq[doc]:
            doc_tfidf[doc][word] = \
                (float(doc_termfreq[doc][word]) / doc_length[doc]) \
                    * invdoc_freq[word]

    return doc_tfidf

def cosine_compute(vector_a, vector_b):
    """Compute the cosine similarity of two normalized vectors.
    
    vector_a and vector_b are dictionaries, where the key is the term and the 
    value is the tf-idf."""

    from math import sqrt

    dotproduct = 0.0
    a_squares = 0.0
    b_squares = 0.0

    # dot = sum([vector_a[k] * vector_b[k] for k in vector_a if k in vector_b])

    for k in vector_a.keys():
        a_squares += (vector_a[k] * vector_a[k])

        if k in vector_b.keys():
            dotproduct += vector_a[k] * vector_b[k]

    for k in vector_b.keys():
        b_squares += (vector_b[k] * vector_b[k])

    a_sqrt = sqrt(a_squares)
    b_sqrt = sqrt(b_squares)

    # it should respect float-ness.
    return (dotproduct / (a_sqrt * b_sqrt))

def dump_raw_matrix(term_dict, tfidf_dict, delimiter = ","):
    """Dump a complete term space matrix of tf-idf values.

    The printout should look something like:

    w1,  w2,  w3,  wN
    w1,  w2,  w3,  wN
    w1,  w2,  w3,  wN
  
    Which is an NxM matrix.  It will be a sparse matrix for most cases."""

    output = ""
  
    sorted_docs = sorted(tfidf_dict.keys())  
    sorted_terms = sorted(term_dict)
  
    # Print Term Rows
    for term in sorted_terms:
        row = []
        for doc in sorted_docs:

            if term in tfidf_dict[doc]:
                row.append(str(tfidf_dict[doc][term]))
            else:
                row.append(str(0.0))

        output += delimiter.join(row)
        output += "\n"

    return output

def dump_matrix(term_dict, tfidf_dict):
    """Dump a complete term space matrix of tf-idf values.
  
    The printout should look something like:
    terms,day1,day2,day3,...,dayN
    t1,   w1,  w2,  w3,  wN
    t2,   w1,  w2,  w3,  wN
    tM,   w1,  w2,  w3,  wN
  
    Which is an NxM matrix.  It will be a sparse matrix for most cases."""

    output = ""

    sorted_docs = sorted(tfidf_dict.keys())  
    sorted_terms = sorted(term_dict)
  
    # Print Matrix!
    output += "term weight space matrix!\n"

    # Print Header Row
    output += "terms,"
    output += ",".join([str(doc) for doc in sorted_docs])
    output += "\n"
  
    # Print Term Rows
    for term in sorted_terms:
        output += term + ","
        for doc in sorted_docs:
            
            if term in tfidf_dict[doc]:
                output += str(tfidf_dict[doc][term]) + ","
            else:
                output += str(0.0) + ","
        output += "\n"

    return output

def build_singletons(doc_freq):
    """Note: this builds the list of singletons.  doc_freq comes out of
    build_termfreqs."""

    return [word for word in doc_freq.keys() if doc_freq[word] == 1]

def build_termfreqs(documents, stopwords):
    """Build doc_length, doc_freq, doc_termfreq dictionaries.
    
    Returns: doc_length, doc_freq, doc_termfreq
    """
    
    doc_length = {}   # total count of all terms, keyed on document
    doc_freq = {}     # dictionary of in how many documents the "word" appears
    doc_termfreq = {} # dictionary of term frequencies by date as integer

    #print "documents in: %d" % len(documents)

    for doc_id in documents:
        # Calculate Term Frequencies for this doc_id/document.
        # let's make a short list of the words we'll accept.

        # only words that are greater than one letter and not in the stopword 
        # list.
        pruned = [w for w in documents[doc_id].split(' ') \
                    if w not in stopwords and len(w) > 1]

        # skip documents that only have one word.
        if len(pruned) < 2:
            continue

        doc_termfreq[doc_id] = {} # Prepare the dictionary for that document.

        try:
            doc_length[doc_id] += len(pruned)
        except KeyError:
            doc_length[doc_id] = len(pruned)

        for word in pruned:
            try:
                doc_termfreq[doc_id][word] += 1
            except KeyError:
                doc_termfreq[doc_id][word] = 1

        # Contribute to the document frequencies.
        for word in doc_termfreq[doc_id]:
            try:
                doc_freq[word] += 1
            except KeyError:
                doc_freq[word] = 1
                
    return doc_length, doc_freq, doc_termfreq

def build_doc_tfidf(documents, stopwords = [], remove_singletons=False):
    """Note: This doesn't remove singletons from the dictionary of terms, unless 
    you say otherwise.  With tweets there is certain value in not removing 
    singletons.
  
    Input:
        documents := a dictionary of documents, by an doc_id value.
        stopwords := a list of stopwords.
        remove_singletons := boolean value of whether we should remove 
                             singletons.

    Returns:
        document tf-idf vectors.
        term counts"""
    
    if len(documents) == 1:
        print "WARNING: Computing on 1 document means all will be singletons."

    doc_length, doc_freq, doc_termfreq = build_termfreqs(documents, stopwords)

    if remove_singletons:
        singles = [word for word in doc_freq.keys() if doc_freq[word] == 1]
        # could use map() function to delete terms from singles
        for doc_id in doc_termfreq:
            for single in singles:
                try:
                    del doc_termfreq[doc_id][single]
                    # only subtracts if the deletion worked
                    doc_length[doc_id] -= 1
                except KeyError:
                    pass

    #print "document frequency: %s" % doc_freq
    #print "term frequency per document: %s" % doc_termfreq
    #print "term frequency per document: %d" % len(doc_termfreq)
      
    # Calculate the inverse document frequencies.
    # dictionary of the inverse document frequencies
    invdoc_freq = calculate_invdf(len(doc_termfreq), doc_freq)
    
    #print "inverse document frequency: %s" % invdoc_freq
    #print "inverse document frequency: %d" % len(invdoc_freq)

    # Calculate the tf-idf values.
    # similar to doc_termfreq, but holds the tf-idf values
    doc_tfidf = calculate_tfidf(doc_length, doc_termfreq, invdoc_freq)
    
    #print "tf-idf per document: %s" % doc_tfidf
    #print "tf-idf per document: %d" % len(doc_tfidf)

    return doc_tfidf, doc_freq
