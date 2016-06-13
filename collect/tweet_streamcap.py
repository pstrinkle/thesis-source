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
import tweetstream

sys.path.append(os.path.join("..", "tweetlib"))
import tweetxml as tx

def usage():
    print "usage: %s <count> <output file> <kill_file>" % sys.argv[0]

def main():
    
    socket._fileobject.default_bufsize = 0

    # Did they provide the correct args?
    if len(sys.argv) != 4:
        usage()
        sys.exit(-1)

    max = int(sys.argv[1])
    output = sys.argv[2]
    file_kill = sys.argv[3]

    # --------------------------------------------------------------------------
    # Grab sample stream of tweets, likely only 1% of all tweets.

    count = 0

    try:
        with codecs.open(output, "w", 'utf-8') as f:
            with tweetstream.TweetStream("profoundalias", "tschusisgerman1") as stream:
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
                            f.write(tx.status_str_from_dict(tweet) + u"\n")
                            f.flush()
                            count += 1

                        if count > max:
                            break

    except tweetstream.ConnectionError, e:
        print "Disconnected from twitter. Reason:", e.reason

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
