#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

##
# @author: Patrick Trinkle
# Summer 2011
#
# @summary: This handles the Earth coordinate stuff.
#
# Currently implemented to only support the degree decimal system.

import math

def kms_to_smi(kilos_squared):
    """
    Given an area in kilometers squared, calculate the square mileage.
  
    1 (kilometer squared) = 0.386102159 square miles
  
    Input: kilos_squared := area
  
    Returns: square miles
    """
    return kilos_squared * 0.386102159

def km_to_mi(kilos):
    """
    Given a distance in kilometers, calculate the mileage.
  
    1 kilometer = 0.621371192 miles
  
    Input: kilos := distance
  
    Returns: miles
    """
    return kilos * 0.621371192

def haversin(theta):
    """
    Given a theta, return the haversin value.
  
    See: http://en.wikipedia.org/wiki/Haversine_formula
  
    Input: theta := angle in radians
  
    Return: haversin(theta)
    """

    return math.sin(theta / 2) * math.sin(theta / 2)

def calculate_distance(coord_a, coord_b):
    """
  Given two points on Earth, calculate the distance between them in kilometers.

  haversin(rad) = sin**2(rad * 0.5) = (1-cos(rad)) * 0.5
  haversin(d / R) = \
      haversin(lat2 - lat1) + cos(lat1)cos(lat2)haversin(lon2-lon1)
  haver = haversin(d / R)
  d = 2*R*arcsin(sqrt(haver)
  
  haver = haversin(lat2 - lat1) + cos(lat1)cos(lat2)haversin(lon2-lon1)
  d = 2*R*arcsin(sqrt(haver)
  
  Input: coord_a := point A as a coordinate tuple [lat, long]
         coord_b := point B as a coordinate tuple
  
  Return: floating point value distance between points on Earth.
    """

    if len(coord_a) != 2 or len(coord_b) != 2:
        return 0

    lat1, long1 = coord_a
    lat2, long2 = coord_b

    dynlat = math.radians(lat2 - lat1)
    dynlong = math.radians(long2 - long1)

    rlat1 = math.radians(lat1)
    rlat2 = math.radians(lat2)

    # radius of Earth in kilometers
    radius = 6371

    haver = \
        haversin(dynlat) + \
            (math.cos(rlat1) * math.cos(rlat2) * haversin(dynlong))

    return (2 * radius * math.asin(math.sqrt(haver)))

def calculate_area(box, lat=0, longitude=1):
    """
    Given a rectangle of GPS coordinates in the Twitter format used with all
    other box functions.  Calculate the area in square kilometers.
  
    Input: box  := rectangle for area calculation.
           lat  := index of the latitude value within a coordinate
           longitude := index of the longitude value within a coordinate
  
    Return: area in square kilometers.
    """

    #print "%f,%f  --- %f,%f  " % (upper_left[1], upper_left[0], upper_right[1], upper_right[0])
    #print "|              |  "
    #print "%f,%f  --- %f,%f  " % (lower_left[1], lower_left[0], lower_right[1], lower_right[0])
  
    lower_left = box[0]
    #lower_right = box[1]
    upper_right = box[2]
    upper_left = box[3]
  
    vert = calculate_distance(
                              (upper_left[lat], upper_left[longitude]),
                              (lower_left[lat], lower_left[longitude]))

    horz = calculate_distance(
                              (upper_left[lat], upper_left[longitude]),
                              (upper_right[lat], upper_right[longitude]))
  
    return vert * horz

def merge_box(box_a, box_b, latitude=0, longitude=1):
    """Given two rectangles of Twitter GPS coordinates, merge the boxes into the
    encompassing rectangle.
  
  Input: box_a := rectangle of GPS coordinates.
         box_b := rectangle of GPS coordinates.
         latitude  := index of the latitude value within a coordinate
         longitude := index of the longitude value within a coordinate
  
  Return: Encompassing box."""
  
    if len(box_a) != 4 or len(box_b) != 4:
        return None
  
    lower_left_a = box_a[0]
    #lower_rightA = box_a[1]
    upper_right_a = box_a[2]
    upper_left_a = box_a[3]

    lower_left_b = box_b[0]
    #lower_rightB = box_b[1]
    upper_right_b = box_b[2]
    upper_left_b = box_b[3]
  
    maxlat = upper_left_a[latitude]
    minlat = lower_left_a[latitude]
    left_long = upper_left_a[long]
    right_long = upper_right_a[long]
  
    if maxlat < upper_left_b[latitude]:
        maxlat = upper_left_b[latitude]

    if minlat > lower_left_b[latitude]:
        minlat = lower_left_b[latitude]
  
    if left_long > upper_left_b[long]:
        left_long = upper_left_b[long]
  
    if right_long < upper_right_b[long]:
        right_long = upper_right_b[long]
  
    # long, latitude
    lower_left = [left_long, minlat]
    lower_right = [right_long, minlat]
    upper_right = [right_long, maxlat]
    upper_left = [left_long, maxlat]
  
    #print "box a:"
    #print "%f,%f  --- %f,%f  " % (upper_left_a[latitude], upper_left_a[longitude], upper_right_a[latitude], upper_right_a[longitude])
    #print "|              |  "
    #print "%f,%f  --- %f,%f  " % (lower_left_a[latitude], lower_left_a[longitude], lower_rightA[latitude], lower_rightA[longitude])
  
    #print "box b:"
    #print "%f,%f  --- %f,%f  " % (upper_left_b[latitude], upper_left_b[longitude], upper_right_b[latitude], upper_right_b[longitude])
    #print "|              |  "
    #print "%f,%f  --- %f,%f  " % (lower_left_b[latitude], lower_left_b[longitude], lower_rightB[latitude], lower_rightB[longitude])
  
    #print "merged:"
    #print "%f,%f  --- %f,%f  " % (upper_left[latitude], upper_left[longitude], upper_right[latitude], upper_right[longitude])
    #print "|              |  "
    #print "%f,%f  --- %f,%f  " % (lower_left[latitude], lower_left[longitude], lower_right[latitude], lower_right[longitude])
    
    return lower_left, lower_right, upper_right, upper_left

def within_box(box, point):
    """Given a bounding box on Earth, determine whether the specified point is 
    within the box.
  
    Twitter weirdly stores the place coordinates in [long, lat]
  
    [[[-121.794055, 38.534883], [-121.675465, 38.534883],
        [-121.675465, 38.578737], [-121.794055, 38.578737]]]

    38.546354, -121.758611
  
    Input: box := four point box describing a piece of Earth [weird format]:
         [long, lat], [long, lat], (lower_left, lower_right),
         [long, lat], [long, lat]  (upper_right, upper_left)
         point := a coordinate tuple [lat, long]
  
    Return: True if the point is within the box; False otherwise."""
  
    if len(box) != 4 or len(point) != 2:
        return False
  
    # These are long, lat
    lower_left = box[0]
    #lower_right = box[1]
    upper_right = box[2]
    upper_left = box[3]
  
    # These are lat, long
    lat = point[0]
    longitude = point[1]
  
    #print "%f,%f  --- %f,%f  " % (upper_left[1], upper_left[0], upper_right[1], upper_right[0])
    #print "|              |  "
    #print "%f,%f  --- %f,%f  " % (lower_left[1], lower_left[0], lower_right[1], lower_right[0])
  
    if lat > upper_left[1] or lat < lower_left[1]:
        return False
  
    if longitude > upper_right[0] or longitude < upper_left[0]:
        return False
  
    return True
