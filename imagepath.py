#!/usr/bin/env python

"""
imagepath.py

Seperate image into parts.
Get image values

Get/Set frame
Get/Set version
"""

__version__ = '3.0.0'
__author__ = 'Wilfried Pollan'


# MODULES
import os.path
import re


class Image(object):
    """
    Manipulates vfx image values
    """

    IMAGE = None
    IMAGE_DICT = None

    def __init__(self, image=None):
        """
        Init the inage class.

        It sets up all basic variables for the input image.

        :params image: path to an image file
        :type image: str
        """
        # Init internal vars
        self.image_path = None
        self.image_name = None
        self.name = None
        self.ext = None

        # Assign init parm
        self.IMAGE = image

        # Assign internal vars
        self._get_basic_parts()

        # private vars
        self._name_list = self._split_name()

        # Assign global class vars
        self.IMAGE_DICT = self.get_image_values()

    # REGEX FUNCTIONS
    def _regex_version(self):
        """
        Create version regex string.

        :return: re_major_version, re_prefix_major_version, re_prefix_major_minor_version
        :rtype: tuple(str)
        """

        re_major_version = r'^([v|V])(\d+)'
        re_prefix_major_version = r'([.|_|-])([v|V])(\d+)*'
        re_prefix_major_minor_version = r'([.|_|-])([v|V])(\d+)([.|_|-])(\d+)'
        return re_major_version, re_prefix_major_version, re_prefix_major_minor_version

    def _regex_frame(self):
        """
        Create frame regex string

        :return: re_frame, re_frame_only
        :rtype: tuple(str)
        """

        re_frame = r'([.|_|-])((\d+)|(%0\dd)|(#+))\Z'
        re_frame_only = r'^((\d+)|(%0\dd)|(#+))\Z'
        return re_frame, re_frame_only

    def _re_compile_version(self):
        """
        Compile re version object.

        :return: re_major_version, re_prefix_major_version, re_prefix_major_minor_version
        :rtype: tuple(re object)
        """

        re_major_version = re.compile(self._regex_version()[0])
        re_prefix_major_version = re.compile(self._regex_version()[1])
        re_prefix_major_minor_version = re.compile(self._regex_version()[2])
        return re_major_version, re_prefix_major_version, re_prefix_major_minor_version

    def _re_compile_frame(self):
        """
        Compile re frame object.

        :return: re_frame, re_frame_only
        :rtype: tuple(re object)
        """

        re_frame = re.compile(self._regex_frame()[0])
        re_frame_only = re.compile(self._regex_frame()[1])
        return re_frame, re_frame_only

    # HELPER FUNCTIONS
    def _set_padded_number(self, number, padding):
        """
        Set padded number.

        :params number:
        :type number: int
        :params padding:
        :type padding: int
        :return: padded number string
        :rtype: str
        """
        return '%0{}d'.format(padding) % number

    # FUNCTIONS
    def _get_basic_parts(self):
        """
        Get path, name, ext

        :return: [dirname, name, ext]
        :rtype: list(str)
        """

        self.image_path = os.path.dirname(self.IMAGE)
        self.image_name = os.path.basename(self.IMAGE)
        self.name, self.ext = os.path.splitext(self.image_name)

    def _split_name(self):
        """
        Split image into base name, prefix & frame part

        :return: [basename, frame_prefix, frame]
                 or if frame_parts=True:
                 [basename, frame_prefix, frame,
                 frame_digit, frame_notation, frame_hash]
        :rtype: list
        """

        re_frame, re_frame_only = self._re_compile_frame()
        self._get_basic_parts()

        name_list = []
        try:
            name_list = re_frame.split(self.name)
            if len(name_list) == 1:
                name_list = re_frame_only.split(self.name)
                if len(name_list) > 1:
                    name_list.insert(0, None)
                else:
                    name_list.extend([None, None])

            name_list = name_list[:6]
        except IndexError: pass

        name_list = [None if v is '' else v for v in name_list]

        return name_list

    def get_b_name(self):
        """
        Get image base name.

        :return: base name
        :rtype: str
        """

        return self._name_list[0]

    def set_b_name(self, new_name):
        """
        Set image base name.

        :params new_name: base name to use for the rename
        :type new_name: str
        :return: image
        :rtype: str
        """

        name_list = self._name_list
        name_list = ['' if v is None else v for v in name_list]
        new_name = new_name + ''.join(name_list[1:3])

        self.IMAGE = os.path.join(self.image_path, new_name) + self.ext
        self._name_list = self._split_name()

        return self.IMAGE

    def get_frame(self):
        """
        Get image frame values.

        Option name=True adds name value pair to dict.

        :return: frame_dict = {'frame_prefix':  frame_prefix,
                               'frame':         frame,
                               'frame_padding': padding,
                               'frame_digit':   frame_digit,
                               'frame_notation':frame_notation,
                               'frame_hash':    frame_hash
                              }
        :rtype: dict
        """

        frame_prefix, frame, frame_digit, frame_notation, frame_hash = None, None, None, None, None
        if self._name_list[2]:
            frame_prefix, frame, frame_digit, frame_notation, frame_hash = self._name_list[1:]

        # GET FRAME PADDING
        padding = None
        if frame_digit:
            padding = len(frame)
        elif frame_notation:
            padding = int(frame_notation[2])
        elif frame_hash:
            padding = len(frame_hash)

        # FRAME NOTATION, HASH
        if padding:
            if frame:
                frame_notation = '%0' + str(padding) + 'd'
                frame_hash = '#' * padding
            elif frame_notation:
                frame_hash = '#' * padding
            elif frame_hash:
                frame_notation = '%0' + str(padding) + 'd'

        frame_dict = {'frame_prefix':  frame_prefix,
                      'frame':         frame,
                      'frame_padding': padding,
                      'frame_digit':   frame_digit,
                      'frame_notation':frame_notation,
                      'frame_hash':    frame_hash
                     }

        return frame_dict

    def set_frame(self, new_frame, prefix=None):
        """
        Set image frame value. Can also set the prefix if given.

        :params new_frame: new frame number
        :type new_frame: str
        :params prefix: character to use before the frame e.g. _
        :type prefix: str
        :return: image
        :rtype: str
        """

        new_frame = str(new_frame)
        re_frame, re_frame_only = self._re_compile_frame()

        name_list = self._name_list

        # Check input values
        parm = None
        value = None
        if not re_frame_only.search(new_frame):
            parm = 'new_frame'
            value = new_frame
            error_msg = '{} \"{}\" must be given as frame hash/frame notation/digit.'.format(parm, value)
            raise ValueError(error_msg)
        elif prefix and not isinstance(prefix, str):
            parm = 'prefix'
            value = str(prefix)
            error_msg = '{} \"{}\" must be given as string.'.format(parm, value)
            raise ValueError(error_msg)

        # CONVERT NONE TO EMPTY STRING
        name_list = ['' if v is None else v for v in name_list]

        frame_prefix = None
        if name_list[1]:
            frame_prefix = name_list[1]
        elif prefix:
            frame_prefix = prefix
        else:
            frame_prefix = ''

        # Assign with existing frame
        self.name = name_list[0] + frame_prefix + new_frame
        self.IMAGE = os.path.join(self.image_path, self.name) + self.ext

        # Replace values in internal var
        self._name_list = self._split_name()
        self.IMAGE_DICT = self.get_image_values()

        return self.IMAGE

    def get_version(self, major_minor=False):
        """
        Get all version strings.

        :params major_minor: Set to True if the image is using two style version
                             convention; default to False
        :type major_minor: bool
        :return: version_dict = {'version_folder_level':  version_folder_level,
                                 'version_folder_prefix': version_folder_prefix,
                                 'version_folder':        version_folder,
                                 'version_prefix':        version_prefix,
                                 'version':               version,
                                 'version_sep':           version_sep
                                }
        :rtype: dict
        """

        re_version_all = self._re_compile_version()
        re_version_only = re_version_all[0]
        re_version = re_version_all[1]
        re_major_minor_version = re_version_all[2]

        version_folder_prefix = None
        version_folder = None
        version_prefix = None
        version = None
        version_sep = None

        def version_result(value):
            """
            Inside method fetching version from input value.

            :param value: image base name
            :type value: str
            :return: version_prefix, version
            :rtype: tuple(str)
            """
            re_version_result = re_version.search(value)
            version_prefix = ''.join(re_version_result.group(1, 2))
            version = re_version_result.group(3)
            return version_prefix, version

        def version_only_result(value):
            """
            Inside method fetching version from input value
            if the name may only consist of the version.

            :param value: image base name
            :type value: str
            :return: version_prefix, version
            :rtype: tuple(str)
            """
            re_version_result = re_version_only.search(value)
            version_prefix = re_version_result.group(1)
            version = re_version_result.group(2)
            return version_prefix, version

        # Get file version
        if major_minor:
            try:
                re_version_result_image = re_major_minor_version.search(self.name)
                version_prefix = ''.join(re_version_result_image.group(1, 2))
                version = re_version_result_image.group(3, 5)
                version_sep = re_version_result_image.group(4)
            except AttributeError: pass
        else:
            try:
                version_prefix, version = version_result(self.name)
            except AttributeError:
                try:
                    version_prefix, version = version_only_result(self.name)
                except AttributeError: pass

        # Get folder version
        level = 1
        while level < len(self.image_path.split(os.sep))-1:
            image_folder = self.image_path.split(os.sep)[-level]
            try:
                version_folder_prefix, version_folder = version_result(image_folder)
            except AttributeError:
                try:
                    version_folder_prefix, version_folder = version_only_result(image_folder)
                except AttributeError: pass

            if version_folder: break
            level += 1

        if not version_folder: level = None

        version_dict = {'version_folder_level':  level,
                        'version_folder_prefix': version_folder_prefix,
                        'version_folder':        version_folder,
                        'version_prefix':        version_prefix,
                        'version':               version,
                        'version_sep':           version_sep
                       }

        return version_dict

    def set_version(self, new_version, set_folder=True, major_minor=False,
                    prefix=None, sep=None):
        """
        Set the given version.

        :params new_version: version as a string without the prefix
        :type new_version: str
        :params set_folder: Set the version in the folder
        :type set_folder: bool
        :params major_minor: Set to True if the version is using
                             major, minor version style
        :type major_minor: bool
        :params prefix: character to use before the version
        :type prefix: str
        :params sep: separator to use for major, minor version style
        :type sep: str
        :return: image
        :rtype: str
        """

        # Init self.regex
        re_version_all = self._re_compile_version()
        re_version_only = re_version_all[0]
        re_version = re_version_all[1]
        re_major_minor_version = re_version_all[2]

        # Get current version
        version_dict = self.get_version(major_minor)
        version_folder_level = version_dict['version_folder_level']
        version_folder_prefix = version_dict['version_folder_prefix']
        version_folder = version_dict['version_folder']
        version_prefix = version_dict['version_prefix']
        version = version_dict['version']
        version_sep = version_dict['version_sep']

        if version_folder_level > 1:
            image_root = os.sep.join(self.image_path.split(os.sep)[:-(version_folder_level)])
            image_folder = self.image_path.split(os.sep)[-version_folder_level]
            sub_folder = os.sep.join(self.image_path.split(os.sep)[-(version_folder_level-1):])
        else:
            image_root = os.path.dirname(self.image_path)
            image_folder = os.path.basename(self.image_path)
            sub_folder = ''

        # Assign input parameter
        if prefix:
            version_prefix = prefix
            if version_folder_prefix:
                version_folder_prefix = prefix
        if sep:
            version_sep = sep

        # Set version
        try:
            # Set version in file
            if version:
                if major_minor:
                    if isinstance(new_version, (list, tuple)):
                        self.name = re_major_minor_version.sub(version_prefix + str(new_version[0]) + version_sep + str(new_version[1]), self.name)
                    else:
                        self.name = re_major_minor_version.sub(version_prefix + str(new_version), self.name)
                else:
                    if re_version.search(self.name):
                        self.name = re_version.sub(version_prefix + str(new_version), self.name)
                    elif re_version_only.search(self.name):
                        self.name = re_version_only.sub(version_prefix + str(new_version), self.name)

            # Set version in folder
            if set_folder:
                if isinstance(new_version, (list, tuple)):
                    new_version = new_version[0]
                if version_folder:
                    if re_version.search(image_folder):
                        image_folder = re_version.sub(version_folder_prefix + str(new_version), image_folder)
                    elif re_version_only.search(image_folder):
                        image_folder = re_version_only.sub(version_folder_prefix + str(new_version), image_folder)

            # Generate image string
            self.image_path = os.path.join(image_root, image_folder, sub_folder)
            self.IMAGE = os.path.join(self.image_path, self.name) + self.ext
            self._name_list = self._split_name()

            return self.IMAGE

        except (AttributeError, TypeError) as err:
            error_msg = 'Wrong input. Error: {}'.format(err)
            raise ValueError(error_msg)

    def get_image_values(self, major_minor=False):
        """
        Get all image part values.

        :params major_minor: Set to True if the version is using
                             major, minor version style
        :type major_minor: bool
        :return: image_dict = {'path':                  image_path,
                               'name':                  b_name,
                               'ext':                   ext,
                               'version_folder_level':  version_folder_level,
                               'version_folder_prefix': version_folder_prefix,
                               'version_folder':        version_folder,
                               'version_prefix':        version_prefix,
                               'version':               version,
                               'version_sep':           version_sep,
                               'frame_prefix':          frame_prefix,
                               'frame':                 frame,
                               'frame_padding':         padding,
                               'frame_notation':        frame_notation,
                               'frame_hash':            frame_hash
                              }
        :rtype: dict
        """

        # FRAME
        frame_dict = self.get_frame()

        # VERSION
        version_dict = self.get_version(major_minor)

        # GENERATE IMAGE DICT
        image_dict = {'path':                  self.image_path,
                      'name':                  self._name_list[0],
                      'ext':                   self.ext,
                      'version_folder_level':  version_dict['version_folder_level'],
                      'version_folder_prefix': version_dict['version_folder_prefix'],
                      'version_folder':        version_dict['version_folder'],
                      'version_prefix':        version_dict['version_prefix'],
                      'version':               version_dict['version'],
                      'version_sep':           version_dict['version_sep'],
                      'frame_prefix':          frame_dict['frame_prefix'],
                      'frame':                 frame_dict['frame'],
                      'frame_padding':         frame_dict['frame_padding'],
                      'frame_notation':        frame_dict['frame_notation'],
                      'frame_hash':            frame_dict['frame_hash']
                     }

        return image_dict
