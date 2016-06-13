#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Summer 2011
#
# This attempts to collate the tweet files and remove duplicates
# given an entire folder of xml files, instead of using sort/uniq
# on a per file basis.
#

import os
import sys
import re
import glob
import codecs

sys.path.append("tweetlib")
import tweetxml

def usage():
    print "usage: %s <folder of xml files> <output_file>" % sys.argv[0]
    print "       the folder of xml files should have been created with the tweet_statuses.py and"
    print "        be filenamed: user_date.xml"
    print "       the output_file is an xml database of the tweets, sadly it is redundant in xml form"

def main():

    # Did they provide the correct args?
    if len(sys.argv) != 3:
        usage()
        sys.exit(-1)

    # Pull Tweet Collection, there could be multiple xml files for the same user.
    xml_files = glob.glob(os.path.join(sys.argv[1], "*.xml"))
    
    users_tweets = {}
    
    for xml_file in xml_files:
        # get userid from filename.
        user = re.search(r"(\d+?)_(\d{8}).xml", xml_file)
        if user:
            user_id = int(user.group(1))

            if user_id not in users_tweets:
                users_tweets[user_id] = tweetxml.TwitterUser(user_id)
            
            tweets = []
            
            print "user id: %d" % user_id
            
            with codecs.open(xml_file, "r", 'utf-8') as fout:
                tweets = fout.readlines()
                # strip off trailing new line characters
                for i in xrange(len(tweets)):
                    tweets[i] = tweets[i].strip()

            users_tweets[user_id].add_tweets(tweets)
            
        else:
            sys.stderr.write("ahh!\n")
            sys.exit(-1)

    counts = 0
    with codecs.open(sys.argv[2], "w", 'utf-8') as fout:
        users_ids = users_tweets.keys()
        users_ids.sort()
        for user in users_ids:
            counts += len(users_tweets[user])
            print "user: %d tweets: %d" % (user, len(users_tweets[user]))
            for tweet_key in users_tweets[user].tweets:
                fout.write("<user_id>%d</user_id>" % user)
                fout.write(users_tweets[user].tweets[tweet_key] + "\n")
        
    print "tweet count: %d" % counts  

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
