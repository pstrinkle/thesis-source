"""This module was designed to assist in dumping data as a frame."""

from operator import itemgetter
import vectorspace

class Frame():
    """This holds the data for a given day for a set of users."""
    
    def __init__(self, day_val):
        self.day = day_val
        self.data = {}
        self.doc_tfidf = None
        self.doc_freq = None
        self.maximum = 0.0
        self.minimum = float(2**32) # amazingly big value.
        self.val_range = 0.0
    
    def __len__(self):
        return len(self.data)

    def tfidf_len(self):
        """What is the length of the tf-idf matrix."""
        
        return sum([len(self.doc_tfidf[doc_id]) for doc_id in self.doc_tfidf])
    
    def add_data(self, user_id, data):
        """Add data to this frame for a user given an id value and their 
        data."""
        
        if data is not None:
            self.data[user_id] = data
        else: # so that the frames are always the same size.
            self.data[user_id] = ""

    def calculate_tfidf(self, stopwords, rm_singletons=False):
        """Calculate the tf-idf value for the documents involved."""
        
        # does not remove singletons.
        self.doc_tfidf, self.doc_freq = \
            vectorspace.build_doc_tfidf(self.data, stopwords, rm_singletons)
    
    def get_tfidf(self):
        """Run calculate_tfidf first or this'll return None."""
        
        return self.doc_tfidf
    
    def top_terms(self, count):
        """Get the top terms from all the columns within a frame.
        
        len(terms) is at most the number of users for a given frame X count."""
        
        terms = []

        for doc_id in self.doc_tfidf:
            new_terms = vectorspace.top_terms(self.doc_tfidf[doc_id], count)

            # new_terms is always a set.
            terms.extend([term for term in new_terms if term not in terms])

        return terms

    def get_range(self):
        """Get the range from the minimum to the maximum value."""

        return self.val_range

    def top_terms_overall(self, count):
        """Get the top terms overall for the entire set of columns.
        
        len(terms) is actually count."""
        
        # Interestingly, many columns can have similar top terms -- with 
        # different positions in the list...  So, this will have to be taken 
        # into account.  Build the overall list and then sort it, then get the
        # first count of the unique...
        #        
        terms = {}
        
        for doc_id in self.doc_tfidf:
            new_tuples = \
                vectorspace.top_terms_tuples(self.doc_tfidf[doc_id], count)

            # These are the top tuples for doc_id; if they are not new, then 
            # increase their value to the new max.            
            for kvp in new_tuples:
                if kvp[0] in terms:
                    terms[kvp[0]] = max(kvp[1], terms[kvp[0]])
                else:
                    terms[kvp[0]] = kvp[1]

        maxkvp = max(terms.iteritems(), key=itemgetter(1))
        minkvp = min(terms.iteritems(), key=itemgetter(1))

        # these are going to be used to determine the mapping into 256 values
        # for greyscale, or 256**3 for rgb.
        self.maximum = maxkvp[1]
        self.minimum = minkvp[1]
        self.val_range = self.maximum - self.minimum

        # terms is effectively a document now, so we can use this.
        return vectorspace.top_terms(terms, count)

class FrameUser():
    """Given a user, this holds their daily data."""

    def __init__(self, user_id, day_val, text):
        self.data = {} # tweets collected given some day...?
        self.user_id = user_id
        self.add_data(day_val, text)

    def __len__(self):
        return len(self.data)

    def all_valid_data(self, stopwords):
        """Do all the days have real data.
        
        Must run after num_days check."""

        for day in self.data:
            pruned = [word for word in " ".join(self.data[day]).split(' ') \
                      if word not in stopwords and len(word) > 1]

            # skip documents that only have one word.
            # the vectorspace code skips these docs.
            if len(pruned) < 2:
                return False
        
        return True

    def valid_data(self, stopwords):
        """Does at least one day have real data."""

        valid_day = 0

        for day in self.data:
            if len(self.data) == 0:
                continue

            pruned = [word for word in " ".join(self.data[day]).split(' ') \
                      if word not in stopwords and len(word) > 1]

            # skip documents that only have one word.
            # the vectorspace code skips these docs.
            if len(pruned) < 2:
                continue

            valid_day += 1
        
        # Was there at least one day with a good document.
        if valid_day:
            return True
        
        return False

    def add_data(self, day_val, text):
        """Add a data to a user's day."""

        try:
            self.data[day_val].append(text)
        except KeyError:
            self.data[day_val] = []
            self.data[day_val].append(text)

    def has_data(self, day_val):
        """Does this user have tweets for that day."""
        
        if day_val in self.data:
            return True
        return False

    def get_data(self, day_val):
        """Get text for this user from that day."""
        
        if day_val in self.data:
            return " ".join(self.data[day_val])
        return None

    def get_alldata(self):
        """Get all the documents as one."""
        
        data = []
        for day in self.data:
            data.extend(self.data[day])
        
        return " ".join(data)

    def get_id(self):
        """What is the id of the user."""
        
        return self.user_id

def find_full_users(users, stopwords, num_days):
    """Which users have tweets for every day in the month (and year)."""
    
    # users is a dictionary of FrameUsers key'd on their user id.    
    return [user for user in users \
            if len(users[user]) == num_days \
                and users[user].all_valid_data(stopwords)]

def find_valid_users(users, stopwords):
    """Which users have at least some valid tweets.  This is far less 
    restrictive than find_full_users()."""
    
    # users is a dictionary of FrameUsers key'd on their user id.
    return [user for user in users if users[user].valid_data(stopwords)]

def build_full_frame(user_list, user_data, day):
    """Build tf-idf for that day."""

    frm = Frame(day)

    for user in user_list:
        frm.add_data(user, user_data[user].get_data(day))

    print "day: %d; user_list: %d; user_data: %d; frame: %d" \
        % (day, len(user_list), len(user_data), len(frm))

    return frm
