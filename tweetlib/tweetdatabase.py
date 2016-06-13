#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

##
# @author: Patrick Trinkle
# Summer 2011
#
# @summary: This handles building XML data for me.
#
#c.execute('''create table users (id integer primary key, screen_name text, name text, lang text, location text, friends text, private integer)''')
#c.execute('''create table tweets (id integer primary key, owner integer, created text, reply_to_user integer, reply_to_tweet integer, geo text, place_name text, place_box text, source text, contents text, yyyymm integer)''')
#c.execute('''create table s_users (id integer primary key, screen_name text, name text, lang text, location text, friends text)''')
#c.execute('''create table s_tweets (id integer primary key, owner integer, created text, reply_to_user integer, reply_to_tweet integer, geo text, place_name text, place_box text, source text, contents text, yyyymm integer)''')

import re
import sys

import tweetdate

def tweet_insert(user_id, tweet):
    """Build the tweet insert parameters."""

    owner = int(user_id)
    
    reply_to_tweet = None
    reply_to_user = None
    geo = None
    place_name = None
    place_box = None
    source = None
    text = None # some of my tweets seem to have no-text... which is weird.
    created = None
    tweet_id = None
    yyyymm = None

    # Pull the parts from the tweet
    re_created = re.search("<created>(.+?)</created>", tweet)
    re_tweet_id = re.search("<id>(.+?)</id>", tweet)
    # reply_to_screen_name we don't care about.
    re_reply_tweet_id = \
        re.search("<in_reply_to_status_id>(.+?)</in_reply_to_status_id>", tweet)
    re_reply_user_id = \
        re.search("<in_reply_to_user_id>(.+?)</in_reply_to_user_id>", tweet)
    re_geo = re.search("<geo>(.+?)</geo>", tweet)
    re_place_name = re.search("<place_name>(.+?)</place_name>", tweet)
    re_place_box = re.search("<place_box>(.+?)</place_box>", tweet)
    re_source = re.search("<source>(.+?)</source>", tweet)
    re_text = re.search("<text>(.+?)</text>", tweet)
    
    # All tweets have this crap or else.
    if re_created is None or re_tweet_id is None:
        sys.stderr.write("evil abort!\n")
        sys.exit(-1)
    
    if re_created:
        created = re_created.group(1)
        yyyymm = tweetdate.get_yearmonint(created)

    if re_tweet_id:
        tweet_id = int(re_tweet_id.group(1))
    
    if re_reply_tweet_id:
        reply_to_tweet = int(re_reply_tweet_id.group(1))
    
    if re_reply_user_id:
        reply_to_user = int(re_reply_user_id.group(1))
    
    if re_geo:
        geo = re_geo.group(1)
    
    if re_place_name:
        place_name = re_place_name.group(1)
    
    if re_place_box:
        place_box = re_place_box.group(1)
    
    if re_source:
        source = re_source.group(1)
    
    if re_text:
        text = re_text.group(1)
    
    # c.execute('''create table tweets (
    #                                   id integer primary key,
    #                                   owner integer,
    #                                   created text,
    #                                   reply_to_user integer,
    #                                   reply_to_tweet integer,
    #                                   geo text,
    #                                   place_name text,
    #                                   place_box text,
    #                                   source text,
    #                                   contents text,
    #                                   yyyymm integer)''')
    
    ins = (tweet_id, owner, created, reply_to_user, reply_to_tweet, geo, 
           place_name, place_box, source, text, yyyymm,)
    
    # c.execute('insert into tweets values (?,?,?,?,?,?,?,?,?,?,?)', ins)
        
    return ins

def user_insert(user):
    """Build the user insert list from the tweetxml User."""
    
    friend_list = None
    screen_name = None
    name = None
    lang = None
    location = None
    private = None

    if len(user.friends) > 0:
        x = ["%d" % y for y in user.friends]
        friend_list = ",".join(x)

    if len(user.screen_name) > 0:
        screen_name = user.screen_name

    if len(user.name) > 0:
        name = user.name

    # lang here is always like 'en' or something...
    if len(user.lang) > 0:
        lang = user.lang

    if len(user.location) > 0:
        location = user.location

    # c.execute('''create table users (
    #                                  id integer primary key,
    #                                  screen_name text,
    #                                  name text,
    #                                  lang text,
    #                                  location text,
    #                                  friends text,
    #                                  private integer)''')
    
    ins = (user.user_id, screen_name, name, lang, location, friend_list, 
           private,)

    # c.execute('insert into users values (?,?,?,?,?,?,?)', ins)

    return ins

class DbUser:
    """Temporary thing until I move away from files forever."""
    
    def __init__(self, row):
        """Custom init, must use sqlite3.Row for row_factory."""
        
        self.id = row['id']
        
        self.screen_name = None
        self.name = None
        self.lang = None
        self.location = None
        self.private = None
        
        if row['screen_name'] != None:
            # I don't think I need the single_unescape here, the python library 
            # handles it; but in theory if I correctly escape thing and unescape
            # things all the time--it should be fine.
            self.screen_name = row['screen_name']

        if row['name'] != None:
            self.name = row['name']

        if row['lang'] != None:
            self.lang = row['lang']

        if row['location'] != None:
            self.location = row['location']

        if row['private'] != None:
            self.private = row['private']

        self.friends = row['friends']

class DbTweet:
    """Temporary thing until I move away from files forever (well, at database 
    side)."""
    
    def __init__(self, row):
        """Custom init, must use sqlite3.Row for row_factory."""

        if row == None:
            return

        self.id = row['id']
        self.owner = row['owner']
        self.created = row['created']
        self.reply_to_user = row['reply_to_user']
        self.reply_to_tweet = row['reply_to_tweet']
        self.geo = row['geo']
        self.place_name = None
        self.source = None
        self.contents = None
        self.yyyymm = 0 # weirdly set to 0 on init.
        
        if row['place_name'] != None:
            self.place_name = row['place_name']

        self.place_box = row['place_box']
        
        if row['source'] != None:
            self.source = row['source']

        if row['contents'] != None:
            self.contents = row['contents']
        
        if row['yyyymm'] != None:
            self.yyyymm = row['yyyymm']

def compare_users(txt_user, db_user):
    """Compare user object built from text and from the database.
    
    This doesn't compare counts or oldest and newest ids, etc."""
    
    if txt_user.user_id != db_user.id:
        print "invalid id"
        return False

    if txt_user.screen_name == '':
        if db_user.screen_name != None:
            print "invalid screen_name"
            return False
    elif txt_user.screen_name != db_user.screen_name:
        print "invalid screen_name"
        return False

    if txt_user.name == '':
        if db_user.name != None:
            print "invalid name"
            return False
    elif txt_user.name != db_user.name:
        print "invalid name"
        return False

    if txt_user.lang == '':
        if db_user.lang != None:
            print "invalid lang"
            return False
    elif txt_user.lang != db_user.lang:
        print "invalid lang"
        return False
    
    if txt_user.location == '':
        if db_user.location != None:
            print "invalid location"
            return False
    elif txt_user.location != db_user.location:
        print "invalid location"
        return False

    txt_friends = ''

    if len(txt_user.friends) > 0:
        x = ["%d" % y for y in txt_user.friends]
        txt_friends = ",".join(x)

    if txt_friends == '':
        if db_user.friends != None:
            print "invalid friends"
            return False
    elif txt_friends != db_user.friends:
        print "invalid friends"
        return False
    
    if txt_user.private != db_user.private:
        print "non-matching privacy"
        return False

    return True

def compare_tweets(txt_tweet, db_tweet):
    """Compare user object built from text and from the database."""

    if txt_tweet.owner != db_tweet.owner:
        print "invalid owner"
        return False
    elif txt_tweet.reply_to_tweet != db_tweet.reply_to_tweet:
        print "invalid reply_to_tweet"
        return False
    elif txt_tweet.reply_to_user != db_tweet.reply_to_user:
        print "invalid reply_to_user"
        return False
    elif txt_tweet.geo != db_tweet.geo:
        print "invalid geo"
        return False
    elif txt_tweet.place_name != db_tweet.place_name:
        print "invalid place_name"
        return False
    elif txt_tweet.place_box != db_tweet.place_box:
        print "invalid place_box:"
        print "text: %s" % txt_tweet.place_box
        print "sql: %s" % db_tweet.place_box
        return False
    elif txt_tweet.source != db_tweet.source:
        print "invalid source: %s != %s" % (txt_tweet.source, db_tweet.source)
        return False
    elif txt_tweet.text != db_tweet.contents:
        print "invalid text"
        return False
    elif txt_tweet.created != db_tweet.created:
        print "invalid created"
        return False
    elif txt_tweet.tweet_id != db_tweet.id:
        print "invalid tweet id.."
        return False
    elif txt_tweet.yyyymm != db_tweet.yyyymm:
        print "invalid yyyymm"
        return False

    return True
