# coding=utf-8
# Copyright (c) 2016 Intel, Inc.
# Author Simo Kuusela <simo.kuusela@intel.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; version 2 of the License
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.

import unittest
import os
import filecmp
import keyboard_emulator as emulator

class TestKeyboardEmulator(unittest.TestCase):
    '''
    Keyboard emulator test class
    '''

    @classmethod
    def setUpClass(self):
        os.chdir("test_files")

    def setUp(self):
        self.kb_emulator = emulator.KeyboardEmulator(emulator_path="_test_path",
                                                        write_mode="a")
        if os.path.isfile("_test_path"):
            os.remove("_test_path")

    def test_broken_special(self):
        with self.assertRaises(emulator.TranslateError):
            self.kb_emulator.send_keystrokes_from_file("broken_special")

    def test_broken_special2(self):
        with self.assertRaises(emulator.LineSyntaxError):
            self.kb_emulator.send_keystrokes_from_file("broken_special2")

    def test_broken_delay(self):
        with self.assertRaises(emulator.LineSyntaxError):
            self.kb_emulator.send_keystrokes_from_file("broken_delay")

    def test_broken_text(self):
        with self.assertRaises(emulator.LineSyntaxError):
            self.kb_emulator.send_keystrokes_from_file("broken_text")

    def test_broken_text2(self):
        with self.assertRaises(emulator.LineSyntaxError):
            self.kb_emulator.send_keystrokes_from_file("broken_text2")

    def test_text(self):
        self.kb_emulator.send_keystrokes_from_file("text")
        self.assertTrue(filecmp.cmp("_test_path", "successful_text"))

    def test_text_delay(self):
        self.kb_emulator.send_keystrokes_from_file("text_delay")
        self.assertTrue(filecmp.cmp("_test_path", "successful_text_delay"))

    def test_special_keys(self):
        self.kb_emulator.send_keystrokes_from_file("special_keys")
        self.assertTrue(filecmp.cmp("_test_path", "successful_special_keys"))

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestKeyboardEmulator)
    unittest.TextTestRunner(verbosity=2).run(suite)
