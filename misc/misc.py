"""Library for miscellaneous crap."""

import os

PATH_DISQUALIFIERS = (".jpg", ".db", ".gif", ".png", ".bmp", "jpeg")

# This returns hidden files as well.
def get_file(folder):
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file[0] != ".":
                yield os.path.join(root, file)
