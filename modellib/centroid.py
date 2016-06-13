"""This module builds vectorspace centroids, versus geographic ones"""

__author__ = 'tri1@umbc.edu'

##
# @author: Patrick Trinkle
# Spring 2012
#
# @summary: This handles representing/storing document centroids in a vector 
# space model.
#
# Originally I was calling len(centroids) in each function as input to xrange,
# but I honestly have no idea whether that is being re-evaluated each time or
# whether or not it's a constant.  So, I'm saving it as a variable that doesn't
# change.  In theory, hm... no idea whether this will give me speed-up or not.

from math import sqrt
from numpy import std
from operator import itemgetter

def similarity(centroid_a, centroid_b):
    """Compute dot product of vectors A & B"""
    
    vector_a = centroid_a.centroid_vector
    vector_b = centroid_b.centroid_vector
    
    length_a = centroid_a.length
    length_b = centroid_b.length
    
    dotproduct = 0.0

    for key, value in vector_a.iteritems():
        if key in vector_b: # if both vectors have the key
            dotproduct += (value * vector_b[key])

    return float(dotproduct / (length_a * length_b))

def get_sim_matrix(centroids):
    """Given a list of Centroids, compute the similarity score between each and 
    return a matrix, matrix[i][j] = 0.000... as a dictionary of dictionaries.

    This function could easily work on a list of them... except then the list 
    would be const, because any manipulation of the centroid list would 
    invalidate the matrix."""

    matrix = {}
    length = len(centroids)

    for i in xrange(0, length):
        matrix[i] = {}

        for j in xrange(i + 1, length):
            matrix[i][j] = similarity(centroids[i], centroids[j])

    return matrix

def get_sims_from_matrix(matrix):
    """Given a matrix of similarity values, covert to a straight list."""
  
    sims = []
  
    for i in matrix.keys():
        for j in matrix[i].keys():
            sims.append(matrix[i][j])
  
    return sims

def get_sims(centroids):
    """Given a list of Centroids, compute the similarity score between all pairs
    and return the list.  This can be fed into find_avg(), find_std()."""

    sims = []
    length = len(centroids)
  
    for i in xrange(0, length):
        for j in xrange(i + 1, length):
            sims.append(similarity(centroids[i], centroids[j]))
  
    return sims

def find_std(centroids, short_cut=False, sim_scores=None):
    """Given a list of Centroids, compute the standard deviation of the 
    similarities."""
  
    if short_cut:
        return std(sim_scores)
  
    sims = []
    length = len(centroids)
  
    for i in xrange(0, length):
        for j in xrange(i + 1, length):
            sims.append(similarity(centroids[i], centroids[j]))
  
    return std(sims)

def find_avg(centroids, short_cut=False, sim_scores=None):
    """Given a list of Centroids, compute the similarity of each pairing and 
    return the average.
  
    If short_cut is True, it'll use sim_scores as the input instead of 
    calculating the scores.
  
    This can only work on the early perfect version of the centroid list."""
    
    total_sim = 0.0
    total_comparisons = 0
  
    if short_cut:
        total_comparisons = len(sim_scores)
    
        for score in sim_scores:
            total_sim += score
    
        return (total_sim / total_comparisons)

    length = len(centroids)

    for i in xrange(0, length):
        for j in xrange(i + 1, length):
            total_sim += similarity(centroids[i], centroids[j])
            total_comparisons += 1

    return (total_sim / total_comparisons)

def find_max(centroids):
    """Given a list of Centroids, compute the similarity of each pairing and 
    return the pair with the highest similarity, and their similarity score--so
    i don't have to re-compute."""
    
    max_sim = 0.0
    max_i = 0
    max_j = 0
    length = len(centroids)

    for i in xrange(0, length):
        for j in xrange(i + 1, length):
            curr_sim = similarity(centroids[i], centroids[j])
            if curr_sim > max_sim:
                max_sim = curr_sim
                max_i = i
                max_j = j

    return (max_i, max_j, max_sim)

class Centroid:
    """This data structure represents an average of documents in a vector space.
  
    Amusingly, modeled directly after a C# class I wrote for a class I took."""
  
    def __init__(self, name, doc_vec):
        """Representation of a document(s) as a tf-idf vector.
    
        name the name for it."""
        self.name = "" # it's added below
        self.vector_cnt = 0
        self.centroid_vector = {}
        self.length = 0.00
        self.add_vector(name, 1, doc_vec)

    def __len__(self):
        """Get the length of it!"""
        return len(self.centroid_vector)

    def __str__(self):
        """Get the string representation.  In this case, it's the name and the 
        top 25 terms."""

        return "%s:\n%s" % (self.name, self.top_terms_tuples(25))

    def top_terms_tuples(self, num):
        """Returns the num-highest tf-idf terms in the vector.
        
        This is an array of tuples [0] - term, [1] -- value.
    
        num := the number of terms to get.
        
        This is not identical to the similarly named function in the vectorspace
         module.  It is however, identical to this exact function there."""
  
        sorted_tokens = sorted(
                               self.centroid_vector.items(),
                               key=itemgetter(1), # (1) is value
                               reverse=True)

        # count to index
        top_terms = []
  
        for i in xrange(0, min(num, len(sorted_tokens))):
            top_terms.append(sorted_tokens[i])

        return top_terms

    def add_centroid(self, new_cen):
        """This merges in the new centroid.
    
        newCent := the centroid object to add."""
        
        self.add_vector(
                        new_cen.name,
                        new_cen.vector_cnt,
                        new_cen.centroid_vector)

    def add_vector(self, doc_name, add_cnt, new_docvec):
        """This averages in the new vector.
    
        doc_name   := the name of the thing we're adding in.
        add_cnt    := the number of documents represented by newV.
        new_docvec := the vector representing the document(s).
    
        This is copied and translated directly from my c# program."""
    
        # determine the weight of the merging pieces
        old_weight = float(self.vector_cnt) / (self.vector_cnt + add_cnt)
        new_weight = float(add_cnt) / (self.vector_cnt + add_cnt)
    
        if len(self.name) == 0:
            self.name = doc_name
        else:
            self.name += ", %s" % doc_name
    
        # computes magnitude as it goes.
        self.length = 0
    
        # reduce weight of values already in vector
        for key in self.centroid_vector.keys():
            if key in new_docvec: # if is in both vectors!
        
                oldvalue = float(self.centroid_vector[key]) * old_weight
                newvalue = float(new_docvec[key]) * new_weight
                value = oldvalue + newvalue
        
                self.centroid_vector[key] = value
                self.length += (value * value) # magnitude
                
                # so when we go through to add in all the missing ones we won't 
                # have excess.
                del new_docvec[key]
            else: # if it is strictly in the old vector
        
                oldvalue = float(self.centroid_vector[key]) * old_weight
                self.centroid_vector[key] = oldvalue
                self.length += (oldvalue * oldvalue) # magnitude
    
        # add new values to vector
        for key, value in new_docvec.iteritems():
            # we don't so we'll have to create a new value with the weight of 
            # the added vector
            value = float(value) * new_weight
            self.centroid_vector[key] = value
            self.length += (value * value)

        self.vector_cnt += add_cnt

        # calculate magnitude
        self.length = sqrt(self.length)

def find_matrix_max(matrix):
    """This provides the outer and inner key and the value, of the maximum 
    value."""

    max_val = 0.0
    max_i = 0
    max_j = 0

    for i in matrix.keys():
        try:
            kvp = max(matrix[i].iteritems(), key=itemgetter(1))
        except ValueError:
            continue
    
        # Maybe I should store the max value with the array, and then always 
        # store the previous largest, and when i insert or delete...
    
        if kvp[1] > max_val:
            max_val = kvp[1]
            max_i = i
            max_j = kvp[0]

    return (max_i, max_j, max_val)

def remove_matrix_entry(matrix, key):
    """This removes any matrix key entries, outer and inner."""

    try:
        del matrix[key]
    except KeyError:
        print "deleting matrix[%s]" % str(key)
        print "%s" % matrix.keys()
        raise Exception

    for i in matrix.keys():
        try:
            del matrix[i][key]
        except KeyError:
            continue

def add_matrix_entry(matrix, centroids, new_centroid, name):
    """Add this entry and comparisons to the matrix, the key to use is name.
  
    Really just need to matrix[name] = {}, then for i in matrix.keys() where 
    not name, compare and add.
  
    Please remove before you add, otherwise there can be noise in the data."""

    if name in matrix:
        print "enabling matrix[%s] <-- already there!" % str(name)

    matrix[name] = {}

    for i in matrix.keys():
        if i != name:
            matrix[name][i] = similarity(centroids[i], new_centroid)

def cluster_documents(documents, threshold_str="std"):
    """Given a dictionary of documents, where the key is some unique 
    (preferably) id value.  Create a centroid representation of each, and then 
    merge the centroids by their similarity scores.
  
    documents := dictionary of documents in tf-idf vectors.
    threshold_str := either "std" or "avg" to set the threshold."""
  
    centroids = {}
    arbitrary_name = 0

    for doc, vec in documents.iteritems():
        centroids[arbitrary_name] = Centroid(str(doc), vec) 
        arbitrary_name += 1

    # The size of sim_matrix is: (num_centroids^2 / 2) - (num_centroids / 2)
    # -- verified, my code does this correctly. : )

    sim_matrix = get_sim_matrix(centroids)
    initial_similarities = get_sims_from_matrix(sim_matrix)
  
    average_sim = find_avg(centroids, True, initial_similarities)
  
    if threshold_str == "std":
        threshold = \
            average_sim + find_std(centroids, True, initial_similarities)
    elif threshold_str == "avg":
        threshold = average_sim
    else:
        return None

    # --------------------------------------------------------------------------
    # Merge centroids
    while len(centroids) > 1:
        i, j, sim = find_matrix_max(sim_matrix)

        if sim >= threshold:
        
            centroids[i].add_centroid(centroids[j])
            del centroids[j]

            remove_matrix_entry(sim_matrix, i)
            remove_matrix_entry(sim_matrix, j)
            add_matrix_entry(sim_matrix, centroids, centroids[i], i)
        else:
            break
  
    return centroids
