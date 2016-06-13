#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

##
# @author: Patrick Trinkle
# Summer 2011
#
# @summary: This handles cleaning tweets.  These things have a very specific 
# format.
#

import re

def import_stopwords(location):
    """Given a file location, read in the stop words."""
    with open(location, "r") as ifo:
        stopwords = ifo.readlines()

        # clean them up!
        for i in xrange(0, len(stopwords)):
            stopwords[i] = stopwords[i].strip()
  
    return stopwords

def extract_id(tweet):
    """
    Given a line from my XML file of tweets, return a tuple 
    (tweet_id, tweet_contents)
    """
    twtid = re.search('<id>(.*?)</id>', tweet)
    text = re.search('<text>(.*?)</text>', tweet)
  
    if twtid == None or text == None:
        print "you have a formatting error"
        return None
  
    return (twtid.group(1), text.group(1))

def extract(tweet):
    """
    Given a line from my XML file of tweets, return a tuple 
    (date string, tweet contents)
  
    The date string is a string in this, and the tweet is not cleaned.
    """
    created = re.search('<created>"(.*?)"</created>', tweet)
    text = re.search('<text>"(.*?)"</text>', tweet)
  
    if created == None or text == None:
        print "you have a formatting error"
        return None
  
    return (created.group(1), text.group(1))

def cleanup(tweet, lowercase=True, to_ascii=False):
    """
    Clean up the string in all the pretty ways.
  
    Input: tweet := the text body of the tweet, so far I've been trying to 
                    process these as utf-8 and let python handle the stuff... 
                    but that may not work if I leave the English base.
           lowercase := defaults to True, would you like the tweet moved 
                        entirely into lowercase?
         
           to_ascii := defaults to False, would you like only the valid ascii 
                       characters used?
         
    Only set to_ascii as true if you read the file in with codecs.open()!
  
    Output: Cleaned tweet string.
  
    This currently removes any @username mentions, extraneous newlines, 
    parentheses, and most if not all punctuation.  It does leave in 
    apostrophies.
    """

    if to_ascii:
        tweet = tweet.encode('ascii', errors='ignore')
  
    new_tweet = tweet.replace("\n", ' ')     # newline character
    # newline string (yes, there are those)
    new_tweet = new_tweet.replace(r"\n", ' ')
    new_tweet = new_tweet.replace(',', ' ')   # commas provide nothing to us
    # tab string (yes, there are those)
    new_tweet = new_tweet.replace(r"\t", ' ')

    if lowercase:
        new_tweet = new_tweet.lower()

    url = re.search(r'(http://\S+)', new_tweet, flags=re.IGNORECASE)

    if url != None:
        new_tweet = new_tweet.replace(url.group(1), '')
    
    url2 = re.search(r'(https://\S+)', new_tweet, flags=re.IGNORECASE)

    if url2 != None:
        new_tweet = new_tweet.replace(url2.group(1), '')

    # Could for the most part just use ascii char available.
    new_tweet = new_tweet.replace("&gt;", ">") # html to character
    new_tweet = new_tweet.replace("&lt;", "<") # html to character
    new_tweet = new_tweet.replace("&amp;", "&") # html to character

    # excessive backslashing
    # periods.  Safe to remove only after you've cleared out the URLs
    # excessive forward-slashing
    # emphasis dashes
    # topic tag TODO: Removing this unweighs the term. <-- leaving in place for 
    # now.
    replacements = [
                  '.', '/', '(', ')', '!', '?', '"', ':', ";", "&", "*", '^',
                  '>', '<', '+', '=', '_', ',', '[', ']', '{', '}', '|', '~',
                  '\\', "--"]

    for rep in replacements:
        new_tweet = new_tweet.replace(rep, ' ')
  
    # There could be a few usernames in the tweet...
    user = re.search('(@\S+)', new_tweet)

    while user != None:
        new_tweet = new_tweet.replace(user.group(1), '')
        user = re.search('(@\S+)', new_tweet)
  
    new_tweet = new_tweet.replace("@", '')   # at sign
    #new_tweet = new_tweet.replace('-', ' ')  # hyphen (us-1, i-95)
    # XXX: I would like to however, remove -x or x-... can use regex... 
    new_tweet = new_tweet.replace("'", '') # makes don't -> dont
  
    extra_space = re.search('(\s{2})', new_tweet)
  
    while extra_space != None:
        new_tweet = new_tweet.replace(extra_space.group(1), ' ')
        extra_space = re.search('(\s{2})', new_tweet)

    new_tweet = new_tweet.strip()

    return new_tweet
