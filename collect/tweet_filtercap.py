#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Fall 2011
#
# 
#

import os
import sys
import codecs
import socket
from tweetstream import FilterStream, ConnectionError

sys.path.append(os.path.join("..", "tweetlib"))
import tweetxml as tx

def usage():
    """Usage function."""
    
    print "usage: %s <count> <output file> <kill_file>" % sys.argv[0]

def main():
    """Main code."""
    
    socket._fileobject.default_bufsize = 0

    # Did they provide the correct args?
    if len(sys.argv) != 4:
        usage()
        sys.exit(-1)

    max_val = int(sys.argv[1])
    output = sys.argv[2]
    file_kill = sys.argv[3]

    # --------------------------------------------------------------------------
    # Grab sample stream of tweets, likely only 1% of all tweets.

    #"left,bottom", "right,top"
    locations = {
        "I-495" : ["-77.296,38.71", "-76.643,39.133"],
        "Boston" : ["-71.366,42.158", "-70.714,42.551"],
        "Alaska" : ["-173.5,57.4", "-131.8,71.7"],
        "Middle East" : ["38.4,20.4", "80.1,48"],
        "North America" : ["-133.5,17.8", "-50,64.9"],
        "North America 2" : ["-133.5,24.7", "-50,64.9"], # (less Mexico, etc)
        "Some of Western Europe" : ["-4.43,40.91", "16.44,52.51"],
        "Bay Area" : ["-122.75,36.8", "-121.75,37.8"],
        "Europe" : ["-19.1,19.1", "109.6,64.9"],
        "S. America, S. Africa" : ["-83.4,-43.8", "45.3,17.5"],
        "US and Canada" : ["-198.4,-2.4", "-22.1,77.5"],
        "Most of the World" : ["-184,-63", "169,85"],
        "entire world" : ["-180,-90", "180,90"],
        "Eastern Europe" : ["22.7,21.8", "151.4,65.3"]
                 }

    userpass = [{"user" : "profoundalias", "pass" : "tschusisgerman1"},
                {"user" : "umanyannya", "pass" : "happyluckyboomfuck9"}]

    count = 0

    try:
        with codecs.open(output, "w", 'utf-8') as fout:
            with FilterStream("profoundalias", "tschusisgerman1", locations=locations["Boston"]) as stream:
                for tweet in stream:
                    if os.path.exists(file_kill):
                        print "prematurely killing"
                        break
                    if "user" in tweet:
                        print "Got tweet from %-16s\t(tweet %d, rate %.1f tweets/sec)" \
                            % (tweet["user"]["screen_name"], stream.count, stream.rate)          
                        if "retweeted_status" in tweet:
                            pass
                        else:
                            fout.write(tx.status_str_from_dict(tweet) + u"\n")
                            fout.flush()
                            count += 1

                        if count > max_val:
                            break

    except ConnectionError, exp:
        print "Disconnected from twitter. Reason:", exp.reason

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
