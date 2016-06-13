"""This module lets you feed in documents and it attempts to use cosine 
similarity for k-means clustering.

This isn't in the modellib because it's tailored to work with the fall 2012
work itself and not my general data model.

Really don't want to re-do what is done correctly in the centroid module..."""

class KMeans():
    """Represents a set of clusters.
    
    Each document will be grouped given a cosine similarity comparison, that
    takes the term frequencies over the document sizes."""

    def __init__(self):
        """Initializes the variables."""

        self.documents = {} # 'named' documents

    def add_doc(self, name, boring):
        """Add a BoringMatrix; we're going to just store them at this point."""

        self.documents[name] = boring

