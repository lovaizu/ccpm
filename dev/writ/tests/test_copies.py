"""The hook scripts writ carries are the same files as pith's, so a fix to one reaches both."""

import filecmp
import os
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")


class Copies(unittest.TestCase):
    def test_writ_carries_the_same_hook_scripts_as_pith(self):
        # Given
        names = ["ccs.py", "check_in.py", "facts.py"]
        # When
        match, mismatch, errors = filecmp.cmpfiles(os.path.join(ROOT, "pith", "scripts"),
                                                   os.path.join(ROOT, "writ", "scripts"), names, shallow=False)
        # Then
        self.assertEqual((mismatch, errors), ([], []))
        self.assertEqual(match, names)
