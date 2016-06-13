#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Spring 2011
#
# The goal of this simple script is to run various queries against Twitter 
# through the published API, using the python-twitter open source library.
#
# TODO: Note, this doesn't really seem to do anything useful yet as each call 
# seems to retrieve the same 20 tweets... whereas I would imagine each call 
# would have many things.

import os
import sys
import datetime
import time
import calendar
#import glob
import twitter

sys.path.append(os.path.join("..", "tweetlib"))
import tweetrequest

def usage():
    """Parameters."""
    
    print "usage: %s <public requests>" % sys.argv[0]

def main():
    """Main execution path."""

    if len(sys.argv) != 2:
        usage()
        sys.exit(-1)
    
    public_request = int(sys.argv[1])
    
    start_time = datetime.datetime.now()
    
    # Looks like I need to update the library or figure out how to get to the 
    # oauth stuff from it; I built my own application thing and have my own 
    # oauth stuff.
    #
    api = twitter.Api(
                      consumer_key=tweetrequest.CONSUMER_KEY,
                      consumer_secret=tweetrequest.CONSUMER_SECRET,
                      access_token_key=tweetrequest.ACCESS_TOKEN_KEY,
                      access_token_secret=tweetrequest.ACCESS_TOKEN_SECRET)


    # --------------------------------------------------------------------------
    # Collect Tweets.

    tweets_collected = []    
    public_cnt = 0
    
    while public_cnt < public_request:
        rate_status = tweetrequest.get_rate_status(api)
        remains = rate_status['remaining_hits']

        print "public_cnt: %d" % public_cnt
        print "remains: %d" % remains
        
        if remains < 2:
            # this is seconds since the epoch.
            reset_time = int(rate_status['reset_time_in_seconds'])
            my_time = calendar.timegm(time.gmtime())
            min_wait = (reset_time - my_time) / 60
            sec_wait = (reset_time - my_time) - (min_wait * 60)
            
            print "forced sleep: %dm:%ds" % (min_wait, sec_wait)
            time.sleep((reset_time - my_time) + 60)
        else:
            time.sleep(3)

        # Okay, try to get the UserTimeline and the Friends for user in users.
        try:
            statuses = api.GetPublicTimeline(include_entities='true')
            
            print "retrieved: %d" % len(statuses)

            tweets_collected.extend([s for s in statuses \
                                     if s not in tweets_collected])

        except twitter.TwitterError, e:
            if e.message == "Capacity Error":
                pass

        public_cnt += 1

    # --------------------------------------------------------------------------
    # Process Tweets.

    for tweet in tweets_collected:
        print "%s" % tweet.text.encode('utf-8')


    # --------------------------------------------------------------------------
    # Done.
    
    print "total runtime: ",
    print (datetime.datetime.now() - start_time)

if __name__ == "__main__":
    main()

