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
import re
import sys
import glob
import codecs

sys.path.append("tweetlib")
import tweetxml

def usage():
    ustr = \
"""
usage: %s <starting_file> <folder of friend files> <output_file>
\tthe folder of xml files should have been created with the tweet_statuses.py 
\tand be filenamed: user_date.xml

\tthe output_file is an xml database of the tweets, sadly it is redundant in 
\txml form.
"""
    print ustr % sys.argv[0]

def main():

    # Did they provide the correct args?
    if len(sys.argv) != 4:
        usage()
        sys.exit(-1)

    # dictionary of TwitterUsers key'd by int(id)
    users_list = {}
    start_file = sys.argv[1]
    output_file = sys.argv[3]

    # --------------------------------------------------------------------------
    # Parse the starting file, because the _friends.txt files only have the 
    # user id in the names and no other details -- so this should have the 
    # user's details.
    with codecs.open(start_file, "r", 'utf-8') as fout:
        users = fout.readlines()
    
    for user in users:
        usr = \
            re.search(
                      "<id>(\d+?)</id><name>(.*?)</name>"
                      "<lang>(.*?)</lang><location>(.*?)</location>",
                      user)
        if usr:
            uid = int(usr.group(1))
            name = usr.group(2)
            lang = usr.group(3)
            location = usr.group(4)
            
            if uid not in users_list:
                users_list[uid] = \
                    tweetxml.TwitterUser(uid, name, lang, location)
        else:
            print "invalid line!"

    print "users: %d" % len(users)

    # --------------------------------------------------------------------------
    # Pull Tweet Collection, there could be multiple xml files for the same 
    # user.
    xml_files = glob.glob(os.path.join(sys.argv[2], "*_friends.txt"))

    for xml_file in xml_files:
        # get userid from filename.
        usr = re.search("(\d+?)_friends.txt", xml_file)
        if usr:
            uid = int(usr.group(1))
            
            if uid not in users_list:
                users_list[uid] = tweetxml.TwitterUser(uid)
            
            sub_list = []
            
            # use id here to get to the user's friends.
            with codecs.open(xml_file, "r", 'utf-8') as f:
                friends = f.readlines()
                for friend in friends:
                    nusr = \
                        re.search(
                                  "<id>(\d+?)</id><screen_name>(.*?)"
                                  "</screen_name><name>(.*?)</name>"
                                  "<total_tweets>(.*?)</total_tweets>"
                                  "<lang>(.*?)</lang>"
                                  "<location>(.*?)</location>",
                                  friend)
                    if nusr:
                        fid = int(nusr.group(1))
                        screen_name = nusr.group(2)
                        name = nusr.group(3)
                        totaltweets = nusr.group(4)
                        lang = nusr.group(5)
                        location = nusr.group(6)
                        
                        if fid not in users_list:
                            users_list[fid] = \
                                tweetxml.TwitterUser(
                                                     nusr.group(1),
                                                     name,
                                                     lang,
                                                     location, 
                                                     "",
                                                     screen_name,
                                                     totaltweets)
                        
                        if fid not in sub_list:
                            sub_list.append(fid)

                users_list[uid].add_friends(sub_list)

    # --------------------------------------------------------------------------
    # users_list should now have all the users from the starting point and 
    # each _friends.txt file.
    
    with codecs.open(output_file, "w", 'utf-8') as out:
        for u in users_list:
            
            output = u''
            output += tweetxml.xmlOut("id", users_list[u].user_id, False)
            output += \
                tweetxml.xmlOut(
                                "screen_name",
                                users_list[u].screen_name,
                                False)
            output += tweetxml.xmlOut("name", users_list[u].name, False)
            output += \
                tweetxml.xmlOut(
                                "total_tweets",
                                users_list[u].total_tweets,
                                False)
            output += tweetxml.xmlOut("lang", users_list[u].lang, False)
            output += \
                tweetxml.xmlOut("location", users_list[u].location, False)        
            output += "<friends>"
            
            users_list[u].friends.sort()
            
            for i in range(len(users_list[u].friends)):
                output += "%d" % users_list[u].friends[i]
                if i != len(users_list[u].friends) - 1:
                    output += ", "
            output += "</friends>\n"

            out.write(output)

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
