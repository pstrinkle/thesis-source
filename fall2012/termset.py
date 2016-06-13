

class TermSet():
    
    def __init__(self, boring_a, name):
        
        self.terms = []
        self.label = str(name)
        self.bin = None

        for term in boring_a.term_matrix:
            self.terms.append(term)

def set_resemblance(terms_a, terms_b):
    """How similar are the sets?"""

    intersection = 0
    union = 0

    for term in terms_a.terms:
        if term in terms_b.terms:
            intersection += 1 # in both
        else:
            union += 1 # in A not B

    for term in terms_b.terms:
        if term not in terms_a.terms:
            union += 1 # in B not A

    union += intersection # union includes intersection

    if intersection == 0 or union == 0:
        return 0.0

    return float(intersection) / float(union)
