#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Spring 2011/Summer 2011
#
# The goal of this simple script is to run various queries against Twitter through
# the published API, using the python-twitter open source library.
#

import os
import sys
import re
import datetime
import time
import calendar
import twitter
import codecs
from urllib2 import URLError
from httplib import BadStatusLine

sys.path.append(os.path.join("..", "tweetlib"))
import tweetxml
import tweetrequest

def usage():
    usageStr = \
    """
    usage: %s -ts <users_input_filename> <output_folder> <error_log> <kill_file> <success_log>
    
            -ts := pull tweets
            users_input_filename := this is a file of the following format: "<id>id</id>..."
            output_folder := where you want the paired files created:
                    the statuses are placed in files, id_date.xml
                    the friends are placed in files, id_friends.txt
            error_log := this will hold the exceptions that we catch during processing.
            kill_file := if this file suddenly exists the program will cleaning stop executing.
    """
    print usageStr % sys.argv[0]

def main():

    if len(sys.argv) != 7:
        usage()
        sys.exit(-1)
    
    startTime = datetime.datetime.now()
    
    # Looks like I need to update the library or figure out how to get to the oauth stuff from it;
    # I built my own application thing and have my own oauth stuff.
    #
    api = twitter.Api(
                      consumer_key=tweetrequest.CONSUMER_KEY,
                      consumer_secret=tweetrequest.CONSUMER_SECRET,
                      access_token_key=tweetrequest.ACCESS_TOKEN_KEY,
                      access_token_secret=tweetrequest.ACCESS_TOKEN_SECRET)

    users = []
    
    paramaters = sys.argv[1]
    file_input = sys.argv[2]
    folder_output = sys.argv[3]
    file_errors = sys.argv[4]
    file_kill = sys.argv[5]
    file_fin = sys.argv[6]
    
    pull_statuses = 0
    pull_friends = 0
    
    if paramaters == "-ts":
        pull_statuses = 1
    else:
        usage()
        sys.exit(-1)

    # --------------------------------------------------------------------------
    # Read in user list file.
    with open(file_input, "r") as f:
        users_raw = f.readlines()
        for i in users_raw:
            urs = re.search(r"<id>(\d+?)</id><last_since_id>(\d+?)</last_since_id><oldest_id>(\d+?)</oldest_id>", i)
            onlyid = re.search("<id>(\d+?)</id>", i)
            if urs and urs.group(1) not in users:
                # since_id is 0 here because we want to start at a point in the past and walk backwards.
                users.append(tweetrequest.RequestTuple(int(urs.group(1)), 0, int(urs.group(3))))
            elif onlyid and onlyid.group(1) not in users:
                users.append(tweetrequest.RequestTuple(int(onlyid.group(1))))
    
    print "users to pull: %d" % len(users)
    
    # open error log:
    err = open(file_errors, "w")
    
    # open success log:
    fin = open(file_fin, "w")

    # --------------------------------------------------------------------------
    # For each user in the users input file.
    users.sort(key=lambda request: request.user_id)
    
    # For each user:
    for user in users:
        
        print "\nprocessing: %d" % user.user_id
        
        # FYI, this API can only get me 3500 tweets back--that being said, I want to hit each user
        # repeatedly until no more come out, even if the last one is a wasted call.
        done = False
        
        while done == False:
            # short-cut out!
            if os.path.exists(file_kill):
                print "prematurely killing"
                break
        
            # Do we need to wait?
            rate_status = tweetrequest.get_rate_status(api)
            remains = rate_status['remaining_hits']
        
            if remains < 1:
                # this is seconds since the epoch.
                reset_time = int(rate_status['reset_time_in_seconds'])
                my_time = calendar.timegm(time.gmtime())
            
                min_wait = (reset_time - my_time) / 60
                sec_wait = (reset_time - my_time) - (min_wait * 60)
                print "forced sleep: %dm:%ds" % (min_wait, sec_wait)
                sys.stdout.flush()
                time.sleep((reset_time - my_time))
            else:
                time.sleep(6) # 3600 / 350 ~ 10, so 6.
        
            # If this runs overnight, then the pulls will be from the date I kicked off the script.
            ext = "_%s.xml" % datetime.date.today().isoformat().replace("-", "")

            # Given a since_id we know where to start pulling the future.
            # Given a max_id we know where to start pulling the past. 
            try:
                print "\tprocessing: %d, since: %d, max: %d" % (user.user_id, user.since_id, user.max_id)
            
                # Get the timeline (and an updated user information view, sans friends)
                statuses = \
                    api.GetUserTimeline(
                                        user_id=user.user_id,
                                        since_id=user.since_id,
                                        max_id=user.max_id,
                                        count=200,
                                        include_entities='true')

                if len(statuses) > 0:
                    with codecs.open(os.path.join(folder_output, str(user) + ext), "a", 'utf-8') as f:
                        for s in statuses:
                            f.write(tweetxml.xmlStatus(s))
                            # originally the newline was added, but I think this was inadvertently converting it to a string..?
                            f.write("\n")
                    user.max_id = statuses[len(statuses) - 1].id
                    user.count += len(statuses)
                    print "\ttotal: %d retrieved: %d, new max_id: %d" \
                        % (statuses[0].user.statuses_count, len(statuses), user.max_id)
                
                # what if this is a valid new tweet?... I'm fairly certain this tends to be the
                # tweet with max_id == id or something.
                # originally this was only checking for == 1, but the it ran all night and did nothing
                # with user 13, and I'm assuming this was because it returned 0.
                if len(statuses) == 1 or len(statuses) == 0:
                    print "len(statuses) == %d, done with user" % len(statuses)
                    fin.write("<id>%s</id>\n" % str(user))
                    fin.flush()
                    done = True

            except twitter.TwitterError, e:
                if e.message == "Capacity Error":
                    print "capacity error caught on api.GetUserTimeline(%s) added back in." % str(user)
                    users.append(user)
                    done = True
                    pass
                else:
                    print "other error caught, not adding back in: %s" % e.message
                    err.write("%s on <id>%d</id>\n" % (e.message, user.user_id))
                    err.flush()
                    done = True
            except URLError, e:
                print "exception: %s" % e.message
            except BadStatusLine, e:
                print "exception: %s" % e.message

    fin.close()
    err.close()

    # --------------------------------------------------------------------------
    # Done.

    print "total runtime: ",
    print (datetime.datetime.now() - startTime)

if __name__ == "__main__":
    main()

