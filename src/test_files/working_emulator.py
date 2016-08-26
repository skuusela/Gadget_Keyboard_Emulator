# coding=utf-8
# Copyright (c) 2013-2016 Intel, Inc.
# Author Simo Kuusela <simo.kuusela@intel.com>
# Author Igor Stoppa <igor.stoppa@intel.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; version 2 of the License
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.

from time import sleep
import os.path
#from aft import Logger

class KeyboardEmulator(object):
    '''
    Keyboard emulator class which has methods for sending key strokes through
    usb port. HID keyboard message length is 8 bytes and format being:

    [modifier, reserved, Key1, Key2, Key3, Key4, Key6, Key7]

    So first byte is for modifier key and all bytes after third one are for
    normal keys. After sending a key stroke, empty message with zeroes has to be
    sent to stop the key being pressed. Messages are sent by writing to the
    emulated HID usb port in /dev/. This emulator uses US HID keyboard hex codes
    for translating keys.
    '''

    # Empty message which will be sent to stop any keys being pressed
    empty = "\x00\x00\x00\x00\x00\x00\x00\x00"

    # Hex codes for modifier keys
    modifiers = {
        "CONTROL_L":  0x01, "SHIFT_L":    0x02, "ALT_L":            0x04,
        "SUPER_L":    0x08, "MULTI":      0x08, "CONTROL_R":        0x10,
        "SHIFT_R":    0x20, "MENU":       0x80, "ISO_LEVEL3_SHIFT": 0x40,
        }

    hid_table = {
        # Function keys
        'F1': 0x3A,  'F2': 0x3B,  'F3': 0x3C,  'F4': 0x3D,
        'F5': 0x3E,  'F6': 0x3F,  'F7': 0x40,  'F8': 0x41,
        'F9': 0x42, 'F10': 0x43, 'F11': 0x44, 'F12': 0x45,

        # Symbols above the row of numbers
        '!':  0x1E, '@':  0x1F, '#':  0x20, '$':  0x21, '%':  0x22, '^':  0x23,
        '&':  0x24, '*':  0x25, '(':  0x26, ')':  0x27,

        # Row of numbers
        '1': 0x1E, '2': 0x1F, '3': 0x20, '4': 0x21, '5': 0x22,
        '6': 0x23, '7': 0x24, '8': 0x25, '9': 0x26, '0': 0x27,

        # Navigation/Editing
        'INSERT': 0x49, 'HOME': 0x4A, 'PRIOR': 0x4B,
        'DELETE': 0x4C, 'END':  0x4D, 'NEXT':  0x4E,

        'ENTER': 0x28, 'ESCAPE': 0x29, 'BACKSPACE': 0x2A,
        'TAB':    0x2B, ' ':  0x2C,

        # Miscellaneous Symbols - grouped by key (one per row)
        '-': 0x2D, '_':  0x2D,
        '=': 0x2E, '+':  0x2E,
        '[': 0x2F, '{':  0x2F,
        ']': 0x30, '}':  0x30,
        '\\':0x31, "|":  0x31,
        ';': 0x33, ':':  0x33,
        "'": 0x34, '"':  0x34,
        '`': 0x35, '~':  0x35,
        ',': 0x36, '<':  0x36,
        '.': 0x37, '>':  0x37,
        '/': 0x38, '?':  0x38,

        #Arrow Keys
        'RIGHT': 0x4f, 'LEFT': 0x50, 'DOWN': 0x51, 'UP': 0x52,
        }

    '''
    Some keys use the same hex code for example '1' and '!'. To get '!', SHIFT
    modifier has to be used. This list contains these keys that need SHIFT.
    '''
    keys_with_shift = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_',
                       '+', '{', '}', '|', ':', '"', '~', '<', '>', '?']


    def __init__(self, emulator_path="/dev/hidg0", write_mode="w"):
        self.emulator = emulator_path # Initialize path to HID keyboard emulator
        self.write_mode = write_mode # Change send_key file write mode
        self.filepath = ""
        self.delay_between_keys = 0 # Delay between each keystroke
        self.modifier = b"\x00" # Default modifier key will be NONE
        self.line_number = 0 # Line number we are parsing from text file

    def send_keystrokes_from_file(self, filepath):
        '''
        Send keystrokes from a file to USB.

        Args:
            filepath: path to the text file

        The text file needs to have special syntax. Example:
            # These lines are comments
            # Do not use empty lines or sending keystrokes is stopped
            # Setting delay between keystrokes to 0.1s
            DELAY=0.1
            # Write text by using ""
            "Hello world!"
            # Writing " is done by \"
            "\"Hello world!\""
            # Write special keys with < >
            <F2> <ENTER> <ESCAPE>
            # Use modifiers with < >, modifiers should have start and end
            <SHIFT_R> "hello world1" <SHIFT_R>
            # Anything outside of "" and <> will be ignored
              this text and spaces are ignored "This will be written to usb"
            # Mix everything on single line
            <ENTER> "Hello world!" <ENTER> <SHIFT_L> "uppercase" <SHIFT_L>
        '''

        self.delay_between_keys = 0
        self.modifier = b"\x00"
        self.filepath = filepath

        with open(filepath, "r") as f:
            line = f.readline().strip()
            self.line_number = 1
            while line:
                self.parse_line(line)
                line = f.readline().strip()
                self.line_number += 1

    def parse_line(self, line):
        # If line starts with 'DELAY=' set the delay
        if line[0:6] == "DELAY=":
            try:
                self.delay_between_keys = float(line[6:].strip())
            except ValueError:
                raise FileError(self.filepath, self.line_number,
                            "'" + line[6:].strip() + "' not a number")

        else:
            # Parse lines keys one at a time
            i = 0
            while i < len(line):
                key = line[i]

                if key == "<":
                    i = self.parse_special(line, i)

                elif key == "\"":
                    i = self.parse_text(line, i)

                elif key == "#":
                    return 0

                # If key is ' ', just ignore it
                elif key == " ":
                    pass

                # If key is anything else, print warning and ignore it
                else:
                    raise FileError(self.filepath, self.line_number,
                                "Found '" + key + "' outside of <> and \"\"")

                i += 1

    def parse_special(self, line, i):
        i += 1
        special = ""
        try:
            while line[i] != ">":
            # Add letters to 'special' until '>' is found
                special += line[i]
                i += 1
        except IndexError:
            raise FileError(self.filepath, self.line_number,
                                "Didn't find closing '>'")

        # If the special key is a modifier, toggle it
        if special in self.modifiers:
            # Set modifier back to None if it's on
            if self.modifiers[special] == self.modifier:
                self.modifier = b"\x00"
            else:
                self.modifier = self.modifiers[special]

        else:
            self.send_a_key(special, self.modifier)
            sleep(self.delay_between_keys)

        return i

    def parse_text(self, line, i):
        i += 1
        try:
            while line[i] != "\"":
                key = line[i]
                # Allow sending ", by using '\'
                if key == "\\":
                    i += 1
                    key = line[i]

                self.send_a_key(key)
                sleep(self.delay_between_keys)
                i += 1
        except IndexError:
            raise FileError(self.filepath, self.line_number,
                                "Didn't find closing \"")

        return i

    def send_a_key(self, key, timeout=20):
        '''
        Send a keystroke. Format for HID keyboard message:
            [modifier, reserved, Key1, Key2, Key3, Key4, Key6, Key7]

        Args:
            key: a key, examples: "a", "3", "F2", "ENTER"
            timeout: how long sending a key will be tried until quitting [s]
        '''
        usb_message = bytearray(self.empty)
        key, _modifier = self.key_to_hex(key) # Translate key to hex code

        # Override given modifier if the key needs a specific one
        if _modifier:
            modifier = _modifier
        else:
            modifier = self.modifier

        usb_message[2] = key
        usb_message[0] = modifier

        time = 0
        while time < timeout:
            try:
                with open(self.emulator, self.write_mode) as emulator:
                    emulator.write(usb_message)
                    emulator.write(self.empty)

            except IOError:
                print("Can't connect")
                time += 1
                sleep(1)

            else:
                return 0

        raise TimeoutError("Keyboard emulator couldn't connect to host")

    def key_to_hex(self, key):
        """
        Returns the given keys (US) HID keyboard hex code and possible modifier
        key
        """
        modifier_key = 0

        if key in list(self.hid_table.keys()):
            hex_key = self.hid_table[key]

            if key in self.keys_with_shift:
                modifier_key = self.modifiers["SHIFT_L"]

        elif len(key) == 1:
            if 'A' <= key and key <= 'Z':
                hex_key = ord(key) - ord('A') + 0x04
                modifier_key = self.modifiers["SHIFT_L"]

            elif 'a' <= key and key <= 'z':
                hex_key = ord(key) - ord('a') + 0x04

            else:
                raise TranslateError(self.filepath, self.line_number,
                                        "Couldn't translate key: '" + key +"'")

        else:
            raise TranslateError(self.filepath, self.line_number,
                                    "Couldn't translate key: <" + key +">")

        return hex_key, modifier_key


class TimeoutError(Exception):
    '''
    Error caused by not getting connection to host device
    '''

class TranslateError(Exception):
    '''
    Error caused when key_to_hex() cant translate a key
    '''
    def __init__(self, _file, line, msg):
        super(TranslateError, self).__init__()
        self._file = _file
        self.line = line
        self.msg = msg

    def __str__(self):
        return ("Error in file " + os.path.abspath(self._file) +
            " on line " + str(self.line) + ": " + self.msg)

class FileError(Exception):
    '''
    Error caused by text file syntax error
    '''
    def __init__(self, _file, line, msg):
        super(FileError, self).__init__()
        self._file = _file
        self.line = line
        self.msg = msg

    def __str__(self):
        return ("Error in file " + os.path.abspath(self._file) +
            " on line " + str(self.line) + ": " + self.msg)
