#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

##
# @author: Patrick Trinkle
# Summer 2011
#
# @summary: This handles the date string parsing my tweets use.
#
# @todo: Make one function just parse the string and return a structure of
# everything -- maybe just use the class and then access what you want 
# specifically each time.

import re

MONTHS = {
    'Jan': '01',
    'Feb': '02',
    'Mar': '03',
    'Apr': '04',
    'May': '05',
    'Jun': '06',
    'Jul': '07',
    'Aug': '08',
    'Sep': '09',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12'}

WEEKDAYS = {
    'Mon': '00',
    'Tue': '01',
    'Wed': '02',
    'Thu': '03',
    'Fri': '04',
    'Sat': '05',
    'Sun': '06'}

def str_yearmonth(year, month):
    """Convert a year int and month int into an int YYYYMM."""
    
    return "%4d%02d" % (year, month)

def str_yearmonthday(year, month, day):
    """Convert a year int, month int, and day int into an int YYYYMMDD."""
    
    return "%4d02%d%02d" % (year, month, day)

def get_monthfromint(date_val):
    """Grab the year from a date integer, the first four digits.
        Input: YYYYMMHH...
        Output: MM or -1 on error"""
  
    monre = re.search('^\d{4}(\d{2})', str(date_val))
    if monre == None:
        return -1
    else:
        return int(monre.group(1))

def get_yearfromint(date_val):
    """Grab the year from a date integer, the first four digits.
        Input: YYYYMMHH...
        Output: YYYY or 0 on error"""
  
    yearre = re.search('^(\d{4})', str(date_val))
    if yearre == None:
        return 0
    else:
        return int(yearre.group(1))

def get_dayofweek(date_str):
    """Get the day of the week from the string.
        Input: Fri Jan 21 09:28:12 +0000 2011
        Output: Fri (see above)"""
  
    # ----------------Fri     Jan     21    09  : 28  :  12   +0000   2011
    day = re.search('(\w{3}) \w{3} \d{1,2} \d{2}:\d{2}:\d{2} \+\d{4} \d{4}', date_str)
  
    if day:
        return day.group(1)
  
    return ""

def get_fulltimeint(date_str):
    """Build a date integer from the string.
        Input: Fri Jan 21 09:28:12 +0000 2011
        Output: YYYYMMDDHHMMSS"""

    # ----------------Fri   Jan       21        09  : 28    :  12     +0000   2011
    # ----------------        1        2        3       4       5               6
    day = re.search('\w{3} (\w{3}) (\d{1,2}) (\d{2}):(\d{2}):(\d{2}) \+\d{4} (\d{4})', date_str)

    if day == None:
        print "regex doesn't match anything"
        date = -1
    else:
        date = int(day.group(6) + MONTHS[day.group(1)] + day.group(2) + day.group(3) + day.group(4) + day.group(5))

    return date

def get_dateint(date_str):
    """Build a date integer from the string.
        Input: Fri Jan 21 09:28:12 +0000 2011
        Output: YYYYMMDDHH"""

    # ----------------Fri   Jan       21        09  : 28  :  12   +0000   2011
    # ----------------        1        2        3                           4
    day = re.search('\w{3} (\w{3}) (\d{1,2}) (\d{2}):\d{2}:\d{2} \+\d{4} (\d{4})', date_str)

    if day == None:
        print "regex doesn't match anything"
        date = -1
    else:
        date = int(day.group(4) + MONTHS[day.group(1)] + day.group(2) + day.group(3))

    return date

def get_yearmondayint(date_str):
    """Build a date integer from the string.
        Input: Fri Jan 21 09:28:12 +0000 2011
        Output: YYYYMMDD"""

    day = re.search('\w{3} (\w{3}) (\d{1,2}) \d{2}:\d{2}:\d{2} \+\d{4} (\d{4})', date_str)

    if day == None:
        print "regex doesn't match anything"
        date = -1
    else:
        date = int(day.group(3) + MONTHS[day.group(1)] + day.group(2))

    return date

def get_yearmonint(date_str):
    """Build a date integer from the string.
        Input: Fri Jan 21 09:28:12 +0000 2011
        Output: YYYYMM"""

    day = re.search('\w{3} (\w{3}) (\d{1,2}) \d{2}:\d{2}:\d{2} \+\d{4} (\d{4})', date_str)

    if day == None:
        print "regex doesn't match anything"
        date = -1
    else:
        date = int(day.group(3) + MONTHS[day.group(1)])

    return date

def get_monthint(date_str):
    """Build a date integer from the string.
        Input: Fri Jan 21 09:28:12 +0000 2011
        Output: MM"""

    # ----------------Fri   Jan       21        09  : 28  :  12   +0000   2011
    # ----------------        1        2        3                           4
    day = re.search('\w{3} (\w{3}) (\d{1,2}) (\d{2}):\d{2}:\d{2} \+\d{4} (\d{4})', date_str)

    if day == None:
        print "regex doesn't match anything"
        date = -1
    else:
        date = int(MONTHS[day.group(1)])

    return date

def get_yearint(date_str):
    """Build a date integer from the string.
        Input: Fri Jan 21 09:28:12 +0000 2011
        Output: YYYY"""

    # ----------------Fri   Jan       21        09  : 28  :  12   +0000   2011
    # ----------------        1        2        3                           4
    day = re.search('\w{3} (\w{3}) (\d{1,2}) (\d{2}):\d{2}:\d{2} \+\d{4} (\d{4})', date_str)

    if day == None:
        print "regex doesn't match anything"
        date = -1
    else:
        date = int(day.group(4))

    return date

class TweetTime:
    """Stores the datetime string in pieces."""

    def __init__(self, datetime=""):
        """Input: datetime := "Fri Jan 21 09:28:12 +0000 2011" """
        
        self.strrep = datetime
        self.valid = False
        
        self.weekday = {}
        self.weekday["val"] = 0
        self.weekday["str"] = ""

        self.month = {}
        self.month["val"] = 0
        self.month["str"] = ""
        self.month["day_val"] = 0
        
        self.time = {}
        self.time["hour"] = 0
        self.time["minute"] = 0
        self.time["second"] = 0
        
        self.year = 0
        
        self.yearmonday = 0

        # ----------------Fri     Jan       21        09  : 28  :  12      +0000    2011
        # ---------------- 1        2        3         4     5      6                7
        day = re.search('(\w{3}) (\w{3}) (\d{1,2}) (\d{2}):(\d{2}):(\d{2}) \+\d{4} (\d{4})', datetime)
    
        if day == None:
            print "regex fails"
        else:
            self.valid = True
            
            self.weekday["str"] = day.group(1)
            self.weekday["val"] = WEEKDAYS[day.group(1)]
            
            self.month["str"] = day.group(2)
            self.month["val"] = int(MONTHS[day.group(2)])
            
            self.month["day_val"] = int(day.group(3))
            
            self.time["hour"] = int(day.group(4))
            self.time["minute"] = int(day.group(5))
            self.time["second"] = int(day.group(6))
            
            self.year = int(day.group(7))
            
            self.yearmonday = get_yearmondayint(datetime)

    def __str__(self):
        return self.strrep

    def get_weekday(self):
        """Get the weekday dictionary."""
        
        return self.weekday
      
    def get_month(self):
        """Get the month dictionary."""
        
        return self.month
