import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "rn" / "hooks"))

import record


class Fixtures(unittest.TestCase):
    def test_the_record_of_every_trial_fixture_keeps_the_form(self):
        # Given: the record in each fixture's tree the trials start from
        # When: the form checks run on it as the hooks run them
        # Then: none stops it, so a trial is never stopped by its own starting record
        trees = sorted((ROOT / "dev/rn/trials/fixtures").glob("*/tree"))
        self.assertTrue(trees)
        for tree in trees:
            for plan in sorted(tree.glob(".rn/*/steering.md")):
                with self.subTest(plan=str(plan.relative_to(ROOT))):
                    rec = record.build(str(tree), f".rn/{plan.parent.name}")
                    self.assertEqual([] if rec is None else record.form(rec), [])


if __name__ == "__main__":
    unittest.main()
