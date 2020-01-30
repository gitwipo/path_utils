#!/usr/env python

# Copyright 2019 Wilfried Pollan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   # http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
file=os_path.py

Two functions that build on top of os.walk. They extend the basic behavior to a
more granually walk and a scan of directory for files containing a given regex.
"""

__author__ = 'Wilfried Pollan'


# Imports
import os
import re


def walk2(top, topdown=True, onerror=None, followlinks=False, level=False,
          excludes=None):
    """
    Add options to os.walk:
        exclusive filtering for dirnames, filenames (list or regex)
        level option

    :param top: <string>; see os.walk
    :param topdown: <boolean>; see os.walk
    :param onerror: <boolean>; see os.walk
    :param followlinks: <boolean>; see os.walk
    :param level: <int>; folder search level depth
    :param excludes: <regex string>|<list>
    :returns: <generator>; dirpath, dirnames, filenames
    """

    # Compile re expression
    try:
        re_excludes = re.compile(excludes)
    except TypeError:
        pass

    # level
    if level:
        top = top.rstrip(os.path.sep)
        assert os.path.isdir(top)
        num_sep = top.count(os.path.sep)

    # loop through os.walk
    for dirpath, dirnames, filenames in os.walk(top, topdown, onerror, followlinks):
        # modify dirnames in place
        try:
            dirnames[:] = [d for d in dirnames if d not in excludes]
            dirnames[:] = [d for d in dirnames if not re_excludes.match(d)]
        except (UnboundLocalError, TypeError, ValueError, AttributeError):
            pass

        # yield result
        yield dirpath, dirnames, filenames

        # level
        if level:
            num_sep_current = dirpath.count(os.path.sep)
            if num_sep + level <= num_sep_current:
                del dirnames[:]


def scan_folder(path, search_pattern, followlinks=False, level=False,
                excludes=None):
    """
    Scan a given root folder and yield all found files

    :param path: <string>; search root path
    :param search_pattern: <regex string>
    :param followlinks: <boolean>; see os.walk
    :param level: <int>; folder search level depth
    :param excludes: <regex string>|<list>
    :return: <generator>; found files else <boolean> False
    """

    # Compile search pattern regex
    try:
        re_search = re.compile(search_pattern, re.IGNORECASE)
    except TypeError:
        raise TypeError('Expected regex search string')

    # Check the path
    if not os.path.isdir(path):
        raise OSError('Path does not exist')

    # Do the scan
    path = os.path.normpath(path)
    walk_gen = walk2(path, followlinks=followlinks, level=level, excludes=excludes)
    for dirpath, dirnames, filenames in walk_gen:
        if filenames:
            for filename in filenames:
                if re_search.search(filename):
                    yield dirpath, filename
