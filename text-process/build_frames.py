#! /usr/bin/python
"""Build frames per day per month."""

__author__ = 'tri1@umbc.edu'

##
# @author: Patrick Trinkle
# Spring 2012
#
# @summary: This program builds a tf-idf matrix for each day of a given YYYYMM.
#
# Currently it builds a list of users from that time period and only includes
# those that appear in each day...
#
# Use a full_date entry that also has a high user similarity count.
#
# 201107 works with the data set I have at present.
#
# select * from tweets where created like '%Jul%2011%';
# select * from tweets where yyyymm = 201107; <-- so much faster. =)
#
# So yeah... just build tf-idf matrix for entire dictionary for the month.
# --- or maybe find the top terms for the month..?
#
# full_users only means user must have a tweet per day in the month.
# otherwise, user must have a tweet in the month.  -- so, there are no full zero
#  frames.
#

import sys
import sqlite3
from os import stat, mkdir, path
from math import floor
from calendar import monthrange
from ConfigParser import SafeConfigParser

sys.path.append(path.join("..", "tweetlib"))
from tweetclean import import_stopwords, cleanup
from tweetdate import TweetTime, MONTHS, str_yearmonth

sys.path.append(path.join("..", "modellib"))
import frame
from vectorspace import dump_raw_matrix
import imageoutput as img # I use all the functions in it. =)

class Output():
    """This holds the run parameters."""
    
    def __init__(self, output_folder, request_value):
        self.output_folder = output_folder # where to store everything
        self.request_value = request_value # the overall terms to pull daily
        self.overall_terms = [] # the terms overall for the month
        self.max_range = 0 # the maximum range over the days in the month.
    
    def add_terms(self, new_terms):
        """Add some new terms for this output level.  The overall terms vary
        depending on how many you want from the top per day over the month.
        
        Also, new_terms is considered a set, I can wrap it in set() if I 
        need."""

        self.overall_terms.extend([term for term in new_terms \
                                   if term not in self.overall_terms])
    
    def get_folder(self):
        """Get the output_folder."""
        
        return self.output_folder
    
    def get_request(self):
        """Get the request_value."""
        
        return self.request_value
    
    def get_terms(self):
        """Get the overall terms."""
        
        return self.overall_terms

def data_pull(database_file, query):
    """Pull the data from the database."""
    
    user_data = {}
    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row
    
    for row in conn.cursor().execute(query):
        if row['text'] is not None:
            data = cleanup(row['text'], True, True)
            twt = TweetTime(row['created'])
            uid = row['owner']
            
            # could probably get away with pushing this up -- like in c++.
            mdv = twt.get_month()["day_val"]

            try:
                user_data[uid].add_data(mdv, data)
            except KeyError:
                user_data[uid] = frame.FrameUser(uid, mdv, data)

    conn.close()

    return user_data

def text_create(text_name, dictionary, data):
    """Dump the matrix as a csv file."""

    with open(text_name + '.csv', "w") as fout:
        fout.write("%s\n" % dump_raw_matrix(dictionary, data))

    with open(text_name + '.tab', "w") as fout:
        fout.write("%s\n" % dump_raw_matrix(dictionary, data, "\t"))

def output_frame_images(out, day, data, dictionary, build_images):
    """Output the data matrix as images, etc."""
    
    max_range = out.max_range
    
    if build_images['grey']:
        fname = path.join(out.get_folder(), "grey")
        pname = path.join(fname, "%d" % day)
                
        try:
            stat(fname)
        except OSError:
            mkdir(fname)
                
        #img.image_create(
        #                 pname,
        #                 dictionary, # dictionary
        #                 data,       # data
        #                 max_range,
        #                 'black')

        img.image_create_rgb2l(pname, dictionary, data, max_range)

    if build_images['rgb']:
        fname = path.join(out.get_folder(), "rgb")
        pname = path.join(fname, "%d" % day)

        try:
            stat(fname)
        except OSError:
            mkdir(fname)

        img.image_create_color(
                               pname,
                               dictionary, # dictionary
                               data,       # data
                               max_range)

        #rows = img.image_detect_important(pname + '.png')

        #upper_count = int(floor(len(rows) * .01))

        #print "important: %s" \
        #    % [dictionary[rows[i][0]] for i in range(upper_count)]

        #rows = img.image_detect_rows(pname + '.png')
                
        #print "busiest: %s" \
        #    % [dictionary[rows[i][0]] for i in range(upper_count)]

def output_matrix(frames, output_set, build_csv_files, build_images):
    """Output the data matrix."""

    for day in frames:
        # Of interest, there should be no rows of zero, and no columns of zero.
        # This only matters for the matrix completion methods, and not the video
        #  stuff, but still.
        
        for output in output_set:
            out = output_set[output]
            dictionary = sorted(out.get_terms())
            data = frames[day].get_tfidf()

            if build_csv_files:
                text_create(
                            path.join(out.get_folder(), "%d" % day),
                            dictionary,
                            frames[day].get_tfidf())

            output_frame_images(out, day, data, dictionary, build_images)

def usage():
    """Standard usage message."""

    print "%s <config_file>" % sys.argv[0]

def main():
    """Main."""

    if len(sys.argv) != 2:
        usage()
        sys.exit(-1)

    # --------------------------------------------------------------------------
    # Parse the parameters.
    config = SafeConfigParser()
    config.read(sys.argv[1])

    database_file = config.get('input', 'database_file')
    year_val = config.getint('input', 'year')
    month_str = config.get('input', 'month')
    stop_file = config.get('input', 'stopwords')
    remove_singletons = config.getboolean('input', 'remove_singletons')
    build_images = {}
    build_images['rgb'] = config.getboolean('input', 'build_rgb_images')
    build_images['grey'] = config.getboolean('input', 'build_grey_images')
    build_csv_files = config.getboolean('input', 'build_csv_files')
    full_users_only = config.getboolean('input', 'full_users')
    
    # XXX: If full_users_only is not set to True, the images and such have 
    # varying dimensions... which is bad.  So, there is a bug here and I have
    # yet to fully investigate it.

    if month_str not in MONTHS:
        usage()
        sys.exit(-2)

    output_set = {}
    
    for section in config.sections():
        if section.startswith("run"):
            output_folder = config.get(section, 'output_folder')
            
            output_set[section] = \
                Output(
                       output_folder,
                       config.getint(section, 'request_value'))

            try:
                stat(output_folder)
            except OSError:
                mkdir(output_folder)

    # --------------------------------------------------------------------------
    # Pull stop words
    stopwords = import_stopwords(stop_file)

    kickoff = \
"""
-------------------------------------------------------------------
parameters  :
  database  : %s
  date      : %s
  output    : %s
  stop      : %s
  count     : %s
  remove    : %s
  output    : %s
  full only : %s
-------------------------------------------------------------------
"""

    print kickoff % \
        (database_file, 
         (month_str, year_val),
         str([output_set[output].get_folder() for output in output_set]),
         stop_file,
         str([output_set[output].get_request() for output in output_set]),
         remove_singletons,
         build_images,
         full_users_only)

    # now that it's an integer lookup that can be more readily searched and 
    # indexed versus a text field search with like.
    query_prefetch = \
    "select owner, created, contents as text from tweets where yyyymm = %d;"

    # --------------------------------------------------------------------------
    # Build a set of documents, per user, per day.
    num_days = monthrange(year_val, int(MONTHS[month_str]))[1]
    user_data = \
        data_pull(
                  database_file,
                  query_prefetch % \
                    int(str_yearmonth(year_val, int(MONTHS[month_str]))))
    
    if len(user_data) < 2:
        print "empty dataset."
        sys.exit(-3)
    
    # you want full users only if you're running matrix completion stuff.
    if full_users_only:
        users = frame.find_full_users(user_data, stopwords, num_days)
    else:
        users = frame.find_valid_users(user_data, stopwords)

    print "data pulled"
    print "user count: %d\tframe users: %d" % (len(user_data), len(users))

    # this is only an issue at present. mind you, because for the video 
    # analysis code the users don't have to be full. 
    if len(users) < 2:
        print "no full users"
        sys.exit(-4)

    # --------------------------------------------------------------------------
    # I don't build a master tf-idf set because the tf-idf values should... 
    # evolve.  albeit, I don't think I'm correctly adjusting them -- I'm just 
    # recalculating then.
    #
    # Calculate daily tf-idf; then build frame from top terms over the period
    # of days.
    frames = {}

    for day in range(1, num_days + 1):
        # This is run once per day overall.
        frames[day] = frame.build_full_frame(users, user_data, day)
        frames[day].calculate_tfidf(stopwords, remove_singletons)

        if frames[day].tfidf_len() == 0:
            print "weird data error."
            sys.exit(-5)

        # This is run once per day per output.
        for output in output_set:
            out = output_set[output]
            out.add_terms(frames[day].top_terms_overall(out.get_request()))
        
            # get_range() is just whatever the last time you ran 
            # top_terms_overall
            new_range = frames[day].get_range()
        
            # This way the images are created with the correct range to cover 
            # all of them.
            if out.max_range < new_range:
                out.max_range = new_range
        
        #break
        #if day == 3:
            #break # just do first day.

    print "Frames created"

    # len(overall_terms) should be at most 250 * num_users * num_days -- if
    # there is no overlap of high value terms over the period of days between
    # the users.  If there is literally no overlap then each user will have 
    # their own 250 terms each day.

    # --------------------------------------------------------------------------
    # Dump the matrix.
    output_matrix(frames, output_set, build_csv_files, build_images)

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
