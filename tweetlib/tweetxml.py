#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

##
# @author: Patrick Trinkle
# Summer 2011
#
# @summary: This handles building XML data for me.
#

import re
import sys
import string

import tweetdate

# I convert these characters to nothing--I just remove them.  Strangely they 
# are crap and somehow show up.
INVALID_CHARS = ('\x00', '\x01', '\x02', '\x03', '\x04',
                                  '\x05', '\x06', '\x07', '\x08', '\x0b',
                                  '\x0c', '\x0e', '\x0f', '\x10', '\x11',
                                  '\x12', '\x13', '\x14', '\x15', '\x16',
                                  '\x17', '\x18', '\x19', '\x1a', '\x1b',
                                  '\x1c', '\x1d', '\x1e', '\x1f') # , '\x85'

# I convert these characters to a single space character.
SPACE_CHARS = ('\n', '\r')

# oldest_id is min(id), since_id is max(id)
def output(current_id, oldest_id, since_id):
    """This is the same as the output function in filter_tweets.py"""

    return \
        "<id>%d</id><last_since_id>%d</last_since_id><oldest_id>%d</oldest_id>"\
        % (current_id, since_id, oldest_id)

def double_unescape(value):
    """SQL is all single-quotes, so I have to unescape the double quotes.
    
    My XML files are all double-escaped, this isn't the case in the database 
    entries."""
    
    return value.replace(r'\"', '"')

def xml_out(tag, value, quotes=True):
    """Build an appropriate xml tagged data unit string.
    
    Input: tag := the name of the tags for wrapping this data
           value := what to place inside the tags, not necessarily a 
                  string -- we handle some conversion
           quotes := would you like the data inside to be wrapped in quotes?"""
    
    xml_str = u""
    xml_strval = u""

    #print "tag: '%s' value: '%s' type: '%s'" % (tag, str(value), type(value))

    if isinstance(value, basestring):
        if isinstance(value, unicode):
            #print "tag: '%s' type: '%s'" % (tag, type(value))
            #xml_strval += value.encode('utf-8')
            xml_strval += value
        elif isinstance(value, str):
            #print "tag: '%s' type: '%s'" % (tag, type(value))
            u = unicode(value, 'utf-8')
            xml_strval += u
    else:
        xml_strval += str(value)

    xml_strval = xml_strval.replace("\n", ' ')  # newline character
    # newline string (yes, there are those)
    xml_strval = xml_strval.replace(r"\n", ' ')

    xml_strval = xml_strval.replace("\r", ' ')  # carriage return character
    # carriage return string (yes, there are those)
    xml_strval = xml_strval.replace(r"\r", ' ')

    # quotes MUST ONLY be escaped if the value is quote surrounded.
    if quotes:
        xml_strval = xml_strval.replace(r'"', r'\"')  # quotes must be escaped
        # this isn't perfect and can get messy.

    if len(xml_strval) > 0:
        xml_str += '<' + tag + '>'
    
        if quotes == True:
            xml_str += '"'
    
        xml_str += xml_strval
    
        if quotes == True:
            xml_str += '"'

        xml_str += '</' + tag + '>'
    else:
        xml_str += '<' + tag + ' />'

    return xml_str

def status_str_from_dict(status):
    """Given a dictionary status thing, created a simple string."""

    status_str = u"<user_id>%d</user_id>" % status["user"]["id"]

    status_str += "<tweet>"

    status_str += xml_out("created", status["created_at"], False)
    status_str += xml_out("id", status["id"], False)

    #if status["in_reply_to_screen_name"] is not None: 
    #  status_str += \
    #    tx.xml_out("in_reply_to_screen_name", status["in_reply_to_screen_name"], True)
        
    if status["in_reply_to_status_id"] is not None:
        status_str += \
            xml_out(
                    "in_reply_to_status_id",
                    status["in_reply_to_status_id"],
                    False)
        
    if status["in_reply_to_user_id"] is not None:
        status_str += \
            xml_out("in_reply_to_user_id", status["in_reply_to_user_id"], False)

    if status["geo"] is not None:
        coordinates = status["geo"]["coordinates"]
        pointStr = "%f, %f" % (coordinates[0], coordinates[1])
        # I copied and pasted the list in order into maps.google.com and it worked perfectly!
        status_str += xml_out("geo", pointStr, False)
    
    if status["place"] is not None:
        if "full_name" in status["place"].keys():
            fname = "%s" % status["place"]["full_name"]
            status_str += xml_out("place_name", fname, False)
        
        if "bounding_box" in status["place"].keys() \
            and status["place"]["bounding_box"] is not None:
            if "coordinates" in status["place"]["bounding_box"].keys():
                bbox = "%s" % status["place"]["bounding_box"]["coordinates"]
                status_str += xml_out("place_box", bbox, False)

    status_str += xml_out("source", status["source"], False)
    status_str += xml_out("text", status["text"], False)
    
    status_str += "</tweet>"
    
    for c in INVALID_CHARS:
        status_str = status_str.replace(c, "")
    for c in SPACE_CHARS:
        status_str = status_str.replace(c, " ")

    return status_str

def xml_user(user):
    """Given a user object, build a string from their more immediate details.
    
    Input: user := a user object
    
    Output: a string holding the user id, name, language, and location."""
    
    output_str = ""
    
    if user is None:
        return output_str
    
    if user.protected == True:
        return output_str
    
    uid = user.id
    name = user.name.encode('utf-8')
    lang = user.lang.encode('utf-8')
    sn = user.screen_name.encode('utf-8')
    total_tweets = str(user.statuses_count)
    location = ""

    if user.location is not None:
        location = \
            user.location.encode('utf-8').replace("\n", "").replace("\r", "").strip()

    output_str = "<id>%d</id><screen_name>%s</screen_name><name>%s</name><total_tweets>%s</total_tweets><lang>%s</lang><location>%s</location>" \
        % (uid, sn, name, total_tweets, lang, location)
    
    for c in INVALID_CHARS:
        output_str = output_str.replace(c, "")
    for c in SPACE_CHARS:
        output_str = output_str.replace(c, " ")
    
    return output_str

def xml_status(status):
    """Given a twitter status object, build an XML representation.
    
    Input: status := the status object
    
    Output: a string holding the XML representation.
    
    Current python-twitter-0.8.2:
      |    status.created_at
      |    status.created_at_in_seconds # read only
      |    status.favorited
      |    status.in_reply_to_screen_name
      |    status.in_reply_to_user_id
      |    status.in_reply_to_status_id
      |    status.truncated
      |    status.source
      |    status.id
      |    status.text
      |    status.location
      |    status.relative_created_at # read only
      |    status.user
      |    status.urls
      |    status.user_mentions
      |    status.hashtags
      |    status.geo
      |    status.place
      |    status.coordinates
      |    status.contributors"""

    # if I end up wanting to not need to collate, this line need to be added.
    #status_str = "<user_id>%d</user_id>" % status.user.id

    status_str = "<tweet>"

    status_str += xml_out("created", status.created_at, False)
    status_str += xml_out("id", status.id, False)

    # used to also dump reply_to_screen_name here.
    
    if status.in_reply_to_status_id is not None:
        status_str += \
            xml_out(
                    "in_reply_to_status_id",
                    status.in_reply_to_status_id,
                    False)
        
    if status.in_reply_to_user_id is not None:
        status_str += \
            xml_out("in_reply_to_user_id", status.in_reply_to_user_id, False)

    # TODO: add the hashtag stuff in.
    #if status.hashtags is not None:
    #  status_str += xml_out("hashtags", status.hashtags, False)

    if status.geo is not None:
        coordinates = status.geo["coordinates"]
        pointStr = "%f, %f" % (coordinates[0], coordinates[1])
        # I copied and pasted the list in order into maps.google.com and it 
        # worked perfectly!
        status_str += xml_out("geo", pointStr, False)
    
    if status.place is not None:
        if "full_name" in status.place.keys():
            fname = "%s" % status.place["full_name"]
            status_str += xml_out("place_name", fname, False)
        
        if "bounding_box" in status.place.keys() \
            and status.place["bounding_box"] is not None:
            if "coordinates" in status.place["bounding_box"].keys():
                bbox = "%s" % status.place["bounding_box"]["coordinates"]
                status_str += xml_out("place_box", bbox, False)

    status_str += xml_out("source", status.source, False)
    status_str += xml_out("text", status.text, False)
    
    status_str += "</tweet>"
    
    for c in INVALID_CHARS:
        status_str = status_str.replace(c, "")
    for c in SPACE_CHARS:
        status_str = status_str.replace(c, " ")
    
    return status_str

class Tweet:
    """The Tweet class is how I represent a tweet.
    
    xml here is what is between <tweet>...</tweet>"""

    def __init__(self, owner_id, tweet=""):
        """Given what we so far have in the database this works.
    
        Input:
        <created>"Sun Sep 04 22:16:36 +0000 2011"</created>                       <-- double-quoted
        <id>110476379149185024</id>
        <in_reply_to_screen_name>"FirstLadi_Lyles"</in_reply_to_screen_name>      <-- double-quoted, but don't care
        <in_reply_to_status_id>110475524261949440</in_reply_to_status_id>
        <in_reply_to_user_id>318206268</in_reply_to_user_id>
        <geo>33.711488, -80.217898</geo>
        <place_name>"South Carolina, US"</place_name>                             <-- double-quoted
        <place_box>[[[-83.353928, 32.033454], [-78.499301, 32.033454], [-78.499301, 35.21554], [-83.353928, 35.21554]]]</place_box>
        <source>"<a href=\"http://www.tweetcaster.com\" rel=\"nofollow\">TweetCaster for Android</a>"</source>  <-- double-quoted
        <text>"@FirstLadi_Lyles ya...."</text> <-- double-quoted
    
        It unescapes the double-quotes and does completely unpack (if you will) the XML."""
        
        self.owner = owner_id
        self.reply_to_tweet = None
        self.reply_to_user = None
        self.geo = None
        self.place_name = None
        self.place_box = None
        self.source = None
        # some of my tweets seem to have no-text... which is weird.
        self.text = None
        self.created = None
        self.tweet_id = None
        self.yyyymm = 0 # weirdly set to 0 on init.
    
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
            self.created = re_created.group(1)
            self.yyyymm = tweetdate.get_yearmonint(self.created)

        if re_tweet_id:
            self.tweet_id = int(re_tweet_id.group(1))
    
        if re_reply_tweet_id:
            self.reply_to_tweet = int(re_reply_tweet_id.group(1))
    
        if re_reply_user_id:
            self.reply_to_user = int(re_reply_user_id.group(1))
    
        if re_geo:
            self.geo = re_geo.group(1)
    
        if re_place_name:
            self.place_name = re_place_name.group(1)
    
        if re_place_box:
            self.place_box = re_place_box.group(1)
    
        if re_source:
            self.source = re_source.group(1)
    
        if re_text:
            self.text = re_text.group(1)


class TwitterUser:
    """The TwitterUser class really needs to converge at some point.
    I use it for a few different things and as such it has many
    different structures, each with a specific goal in mind.
    
    I really should try to just get my data to come out in the final
    format."""
    
    def __init__(self, user_id, name="", lang="", location="", friends="", 
                 screen_name="", totaltweets=0, private=False):
        """Input: 
            user_id is an int
            name is a utf-8 string
            lang is a utf-8 string (i think)
            location is a utf-8 string
            friends is a comma separated string as input."""
        
        # the user id of this user
        self.user_id = user_id
        self.screen_name = screen_name
        self.name = name
        self.lang = lang
        self.location = location
        self.friends = []
        self.tweets = {}
        self.total_retrieved = 0
        self.total_tweets = totaltweets
        self.private = private
        
        # not yet doing anything with this, but in the future
        # it will be required so I don't pull someone daily
        # if they rarely tweet.
        self.last_pulled = None
        self.last_date = ""
        self.last_since_id = 0
        self.oldest_id = 0
        
        # were we given any friends?
        if len(friends) > 0:
            fids = friends.split(", ")
            for fid in fids:
                if len(fid) > 0:
                    if int(fid) not in self.friends:
                        self.friends.append(int(fid))

    def __len__(self):
        return len(self.tweets)

    def unicode_tweets(self):
        """."""
        
        out_str = u''
        for tweet_id in self.tweets:
            out_str += "<user_id>%s</user_id>" % str(self.user_id)
            out_str += unicode(self.tweets[tweet_id], 'utf-8')
            out_str += "\n"
            
        return out_str

    def to_unicodestr(self):
        """Output the TwitterUser in the XML format:
        
        <user>
            <id></id>
            <screen_name></screen_name>
            <name></name>
            <lang></lang>
            <location></location>
            <friends></friends>
            <total_retrieved></total_retrieved>
            <total_tweets></total_tweets>
            <last_pulled></last_pulled> <-- useful, but hm...
            <last_date></last_date>
            <last_since_id></last_since_id>
            <oldest_id></oldest_id>
            <tweets>
                <tweet>....</tweet>
            </tweets>
        </user>
        
        The geo, place_name, and place_box are optional.  It will always have a source, text, created, and id.
        <tweet><created>""</created><id></id><geo></geo>
            <place_name>""</place_name><place_box></place_box><source>""</source><text>""</text></tweet>
        
        Implementing this as __str__ didn't work once the unicode strings were involved."""

        # these tweets cannot quite be sorted like this.
        #
        # Maybe I should make them a dictionary key'd by id and then just use the id to sort... 
        # but really if I recall Twitter announced the ids were no longer going to be necessarily
        # sequential.
        tweet_ids = sorted(self.tweets.keys())
        
        if len(tweet_ids) > 0:
            # If the created stops being quoted, this will need to be updated.
            t_info = re.search("<created>(.+?)</created><id>(\d+?)</id>", self.tweets[tweet_ids[len(tweet_ids) - 1]])
            if t_info:
                t_created = t_info.group(1)
                t_id = int(t_info.group(2))
                
            t_old_info = re.search("<created>(.+?)</created><id>(\d+?)</id>", self.tweets[tweet_ids[0]])
            if t_old_info:
                t_old_id = int(t_old_info.group(2))
        else:
            t_created = ""
            t_id = ""
            t_old_id = ""
        
        out_str = unicode("<user>\n", 'utf-8')
        out_str += "\t%s\n" % xml_out("id", self.user_id, False)
        out_str += "\t%s\n" % xml_out("screen_name", self.screen_name, False)
        out_str += "\t%s\n" % xml_out("name", self.name, False)
        out_str += "\t%s\n" % xml_out("lang", self.lang, False)
        out_str += "\t%s\n" % xml_out("location", self.location, False)

        # need to sort and print friends list appropriately
        if len(self.friends) > 0:
            out_str += "\t<friends>"
            self.friends.sort()
            for i in range(len(self.friends)):
                out_str += str(self.friends[i])
                if i != len(self.friends) - 1:
                    out_str += ", "
            out_str += "</friends>\n"
        else:
            out_str += "\t<friends />\n"
    
        out_str += "\t%s\n" % xml_out("total_retrieved", len(self.tweets), False)
        out_str += "\t%s\n" % xml_out("total_tweets", self.total_tweets, False)
        out_str += "\t%s\n" % xml_out("last_pulled", "", False)
        out_str += "\t%s\n" % xml_out("last_date", t_created, False)
        out_str += "\t%s\n" % xml_out("last_since_id", t_id, False)
        out_str += "\t%s\n" % xml_out("oldest_id", t_old_id, False)

        if len(self.tweets) > 0:
            out_str += "\t<tweets>\n"
            for tid in tweet_ids:
                if isinstance(self.tweets[tid], unicode): # should be utf-8...
                    out_str += "\t\t<tweet>%s</tweet>\n" % self.tweets[tid]
                else: # should be str type
                    out_str += "\t\t<tweet>%s</tweet>\n" % unicode(self.tweets[tid], 'utf-8')
            out_str += "\t</tweets>\n"
        else:
            out_str += "\t<tweets />\n"
        
        out_str += "</user>\n"
        
        return out_str
    
    def add_tweets(self, new_tweets=[]):
        """Tweets in xml format."""
        
        for new_tweet in new_tweets:
            #print new_tweet
            self.add_tweet(new_tweet)

    def add_tweet(self, new_tweet):
        """Tweet in xml format."""
        
        t_info = re.search("<id>(\d+?)</id>", new_tweet)
        if t_info:
            tid = int(t_info.group(1))
            if tid not in self.tweets:
                self.tweets[tid] = new_tweet
        else:
            sys.stderr.write("invalid tweet!\n")
            sys.stderr.write(new_tweet)
            sys.stderr.write("\n")
            sys.exit(-1)

    def add_friends(self, new_friends=[]):
        for friend in new_friends:
            if friend not in self.friends:
                self.friends.append(friend)
    
    def addFriendsStr(self, new_friends=""):
        """id1, id2, id3, id4, ..., idn string!"""
        
        if len(new_friends) > 0:
            fids = new_friends.split(", ")
            for fid in fids:
                if len(fid) > 0:
                    if int(fid) not in self.friends:
                        self.friends.append(int(fid))

def user_from_xml(xml=""):
    """Given what we so far have in the database this works.
    
    Input:
        <user>
            <id></id>
            <screen_name></screen_name>
            <name></name>
            <lang></lang>
            <location></location>
            <friends></friends>
            <total_retrieved></total_retrieved>
            <total_tweets></total_tweets>
            <last_pulled></last_pulled> <-- useful, but hm...
            <last_date></last_date>
            <last_since_id></last_since_id>
            <oldest_id></oldest_id>
            <tweets>
                <tweet>....</tweet>
            </tweets>
        </user>"""

    idr = re.search("<id>(\d+?)</id>\n", xml)
    if idr:
        user = TwitterUser(int(idr.group(1)))

        # Things that went out to XML and then are read in and then go back out through the toXml
        # need to have their escaped characters unescaped.

        # screen_name might not be known
        snr = re.search("<screen_name>(.+?)</screen_name>", xml)
        if snr:
            user.screen_name = snr.group(1)

        # name is not optional
        namer = re.search("<name>(.+?)</name>", xml)
        if namer:
            user.name = namer.group(1)

        # lang is not optional
        langr = re.search("<lang>(.+?)</lang>", xml)
        if langr:
            user.lang = langr.group(1)

        # location is optional
        locr = re.search("<location>(.+?)</location>", xml)
        if locr:
            user.location = locr.group(1)

        # friends are optional, lol.
        frnr = re.search("<friends>(.+?)</friends>", xml)
        if frnr:
            friend_string = frnr.group(1)
            # there is more than one friend
            if "," in friend_string:
                friends_list = friend_string.split(", ")
                for f in friends_list:
                    if len(f) > 0:
                        user.friends.append(int(f))
            else:
                user.friends.append(int(frnr.group(1)))

        # this is something we should always know, albeit not always update
        trr = re.search("<total_retrieved>(.*?)</total_retrieved>", xml)
        if trr:
            user.total_retrieved = int(trr.group(1))

        # total tweets is required eventually
        ttr = re.search("<total_tweets>(.*?)</total_tweets>", xml)
        if ttr:
            if ttr.group(1) is not None and len(ttr.group(1)) > 0:
                user.total_tweets = int(ttr.group(1))

        # date we last pulled their tweets
        lpr = re.search("<last_pulled>(.*?)</last_pulled>", xml)
        if lpr:
            user.last_pulled = lpr.group(1)

        # date of their last tweet
        ldr = re.search("<last_date>(.*?)</last_date>", xml)
        if ldr:
            user.last_date = ldr.group(1)

        # since id of their last tweet
        lsr = re.search("<last_since_id>(\d+)</last_since_id>", xml)
        if lsr:
            user.last_since_id = int(lsr.group(1))
            
        lor = re.search("<oldest_id>(\d+)</oldest_id>", xml)
        if lor:
            user.oldest_id = int(lor.group(1))
        
        twrl = re.search("<tweets />", xml)
        if twrl:
            pass
        else:
            tweets_start = string.find(xml, "<tweets>")
            tweets_end = string.find(xml, "</tweets")
            tweets_list = xml[tweets_start:tweets_end]
            tweets = tweets_list.split("\n")
            for tweet in tweets:
                twr = re.search("<tweet>(.+?)</tweet>", tweet)
                if twr:
                    contents = twr.group(1)
                    tidr = re.search("<id>(\d+?)</id>", contents)
                    if tidr:
                        user.tweets[int(tidr.group(1))] = contents
        
        return user
    else:
        return None

