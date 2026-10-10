import unittest

import harness  # noqa: F401
import ccs
from checks import handed, order


class Record(unittest.TestCase):
    def test_a_record_written_back_keeps_every_line_and_kind_it_does_not_know(self):
        # Given
        text = '# note\n\nfocal_entities:\n  - work: "a \\"b\\""\n  - other: plain\n'
        # When
        back = ccs.dump(ccs.load(text))
        # Then
        self.assertEqual(back, 'focal_entities:\n  - work: "a \\"b\\""\n  - other: "plain"\n')

    def test_a_line_out_of_form_is_refused(self):
        for text in ("  - work: \"x\"\n", "focal_entities:\n  work\n", 'p:\n  - k: "open\n'):
            with self.subTest(text=text):
                # Given / When / Then
                with self.assertRaises(ccs.Bad):
                    ccs.load(text)

    def test_what_turn_cannot_start_without_is_named(self):
        # Given
        parts = ccs.load(harness.RECORD.replace('  - use: "follow it from the top"\n', ""))
        # When
        missing = ccs.missing(parts)
        # Then
        self.assertEqual(missing, ["goal_orientation.use"])


class Order(unittest.TestCase):
    def test_each_call_waits_for_the_use_and_the_learning_before_it(self):
        cases = [
            ([], "maker", []),
            ([], "learner", ["nothing to learn"]),
            (["maker", "made"], "maker", ["use what was made"]),
            (["maker", "made"], "done", ["use what was made"]),
            (["maker", "made"], "first-user", []),
            (["maker", "made", "first-user"], "maker", ["learn from the last use"]),
            (["maker", "made", "first-user"], "made", ["learn from the last use"]),
            (["maker", "made", "first-user"], "learner", []),
            (["maker", "made", "first-user", "learner"], "done", []),
            (["maker"], "done", ["has not been used"]),
        ]
        for done, now, want in cases:
            with self.subTest(done=done, now=now):
                # Given / When
                got = order.check(done, now)
                # Then
                self.assertEqual(len(got), len(want))
                for w, g in zip(want, got):
                    self.assertIn(w, g)


class Handed(unittest.TestCase):
    def setUp(self):
        self.repo = harness.Repo()

    def tearDown(self):
        self.repo.close()

    def check(self, **args):
        return handed.check(dict({"in": ".caller/1.yaml", "out": ".caller/2.yaml"}, **args),
                            self.repo.work)

    def test_a_whole_record_and_a_new_out_pass(self):
        self.assertEqual(self.check(), [])

    def test_what_is_wrong_with_the_record_handed_in_is_said(self):
        cases = [({"in": ""}, "no record"), ({"in": "none.yaml"}, "no record"),
                 ({"out": ""}, "needs `out:`"), ({"out": ".caller/1.yaml"}, "never rewritten")]
        for args, want in cases:
            with self.subTest(args=args):
                # Given / When
                got = self.check(**args)
                # Then
                self.assertIn(want, " ".join(got))

    def test_a_record_out_of_form_or_short_is_sent_back(self):
        for text, want in (("x\n", "neither"), ("focal_entities:\n", "is missing")):
            with self.subTest(text=text):
                # Given
                self.repo.write(".caller/1.yaml", text)
                # When
                got = self.check()
                # Then
                self.assertIn(want, " ".join(got))


if __name__ == "__main__":
    unittest.main()
