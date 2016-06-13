#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Spring 2012
#
# This handles all the collect_XXX scripts requests, etc...
#

import sys
import twitter
import urllib2 # for the exception
import httplib # for the exception

CONSUMER_KEY        = 'IoOS13WALONePQbVoq9ePQ'
CONSUMER_SECRET     = 'zjf2HsUqe6FHdwy81lX93BOuk8NFT9jGdBZTprAhY'
ACCESS_TOKEN_KEY    = '187244615-s3gCVJNg9TZJPlIEW7yFKHYPXi2xf3lpQnv9uDNV'
ACCESS_TOKEN_SECRET = 'Hig5HYmDqv7j7cM4LxZExpXKcKfWs1Xb5sWRU24Bg5E'

class RequestTuple:
    """For tracking requests."""
    
    def __init__(self, user_id, since_id=0, max_id=0):
        self.user_id = user_id
        self.since_id = since_id
        self.max_id = max_id
        self.count = 0
    
    def __str__(self):
        return str(self.user_id)

def get_rate_status(api):
    """Given an api object, call GetRateLimitStatus() and if it throws a 
    "Capacity Error" continue calling until it doesn't, with a 2 second pause.  
    
    Any other exceptions are passed up.
    
    Input: api := Twitter.api object
    
    Return: RateLimit dictionary.  See python-twitter docs."""

    success = 0
    rate_status = None
    
    # while the API call fails for capacity error reasons:
    while success == 0:
        try:
            rate_status = api.GetRateLimitStatus()
            success = 1
        except twitter.TwitterError, e:
            if e.message == "Capacity Error":
                print "capacity error on get_rate_status"
                pass
            else:
                break
        except urllib2.URLError, e:
            print "exception: %s" % e.message
        except httplib.BadStatusLine, e:
            print "exception: %s" % e.message
    
    if rate_status == None:
        sys.stderr.write("could not get api rate limit status!\n")
        sys.exit(-1)
    
    return rate_status
