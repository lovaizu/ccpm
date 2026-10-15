import os
import sys
import unittest

from test_form import HOOKS

sys.path.insert(0, HOOKS)

import record
import stop

FIXTURES = os.path.join(os.path.dirname(os.path.dirname(HOOKS)), "dev", "rn", "trials", "fixtures")


class FixturesTest(unittest.TestCase):
    def test_every_fixture_passes_the_form_checks_at_the_end_of_a_turn(self):
        # Given: each record the trials start from, as its fixture's tree holds it
        # When: the turn ends on it
        # Then: nothing is stopped
        for name in sorted(os.listdir(FIXTURES)):
            tree = os.path.join(FIXTURES, name, "tree")
            for session in os.listdir(os.path.join(tree, ".rn")):
                with self.subTest(fixture=name):
                    found = record.build(tree, os.path.join(".rn", session))
                    self.assertEqual(stop.at_turn_end(found), [])


if __name__ == "__main__":
    unittest.main()
