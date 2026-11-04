"""Properties of throwaway.py over many paths: a path names a file under the home exactly where,
joined to the home, it lands below it, so a file the work names never lies out of the throwaway
home, and none is refused that lies in it."""

import os
import unittest

import helpers
from helpers import throwaway

hypothesis = helpers.testing.hypothesis()
given, st = hypothesis.given, hypothesis.strategies

HOME = os.path.join(os.sep, "home")


class TestUnderHome(unittest.TestCase):
    @given(st.text("a./", max_size=10))
    def test_a_path_is_under_the_home_exactly_where_it_lands_below_it(self, path):
        lands = os.path.normpath(os.path.join(HOME, path))
        self.assertEqual(throwaway.under_home(path), lands.startswith(HOME + os.sep), path)


if __name__ == "__main__":
    unittest.main()
