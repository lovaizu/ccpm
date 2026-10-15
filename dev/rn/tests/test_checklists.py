import json
import os
import subprocess
import sys
import unittest

from helpers import CHECKLISTS, NOTES, SCRIPTS, Repo, run


def found(repo, kind):
    code, out = run(repo, "checklists", kind)
    assert code == 0, out
    return [(c["path"], c["name"], c["version"]) for c in json.loads(out)]


class Checklists(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()

    def tearDown(self):
        self.repo.close()

    def test_a_kind_rn_has_a_checklist_for_gets_it_with_the_ones_its_opening_says_apply(self):
        # Given: a kind rn keeps a checklist for, whose opening says the one for every document
        # applies
        # When: the checklists for the kind are asked for
        got = found(self.repo, "readme")
        # Then: the one for every document comes first, then the kind's, each with name and version
        self.assertEqual(
            [(os.path.basename(p), n) for p, n, _ in got],
            [("doc.md", "doc"), ("readme.md", "readme")],
        )
        self.assertEqual(got[0][0], os.path.join(CHECKLISTS, "doc.md"))
        self.assertTrue(all(v for _, _, v in got))

    def test_each_kind_rn_keeps_is_found_by_its_name(self):
        for kind in ("plan", "proposal", "verification", "design", "prompt", "code", "checklist"):
            with self.subTest(kind):
                # Given: a kind of work rn keeps a checklist for
                # When: the checklists for the kind are asked for
                got = found(self.repo, kind)
                # Then: the kind's own is among them, named as the kind
                self.assertIn(kind, [n for _, n, _ in got])
                self.assertEqual(got[-1][0], os.path.join(CHECKLISTS, f"{kind}.md"))

    def test_a_kind_whose_checklist_names_no_other_gets_it_alone(self):
        # Given: the kind code, whose checklist's opening names no other checklist
        # When: the checklists for the kind are asked for
        got = found(self.repo, "code")
        # Then: it is the only one
        self.assertEqual([n for _, n, _ in got], ["code"])

    def test_a_checklist_the_user_made_is_found_for_its_kind(self):
        # Given: a checklist the user made for release notes, whose opening says doc applies
        self.repo.write(".rn/checklists/release-notes.md", NOTES)
        # When: the checklists for the kind are asked for
        got = found(self.repo, "release-notes")
        # Then: the one for every document and the user's are found
        self.assertEqual(
            [(os.path.basename(p), n, v) for p, n, v in got],
            [("doc.md", "doc", got[0][2]), ("release-notes.md", "release-notes", "1.0.0")],
        )
        self.assertEqual(got[1][0], os.path.join(".rn", "checklists", "release-notes.md"))

    def test_a_kind_with_no_checklist_gets_none(self):
        # Given: a kind neither rn nor the user has a checklist for
        # When: the checklists for the kind are asked for
        got = found(self.repo, "release-notes")
        # Then: none are found, and the command does not fail
        self.assertEqual(got, [])

    def test_a_kind_that_is_not_a_name_is_stopped(self):
        # Given: a kind with a path in it
        # When: the checklists for it are asked for
        code, out = run(self.repo, "checklists", "../etc")
        # Then: it is stopped, saying what a kind is
        self.assertEqual(code, 1)
        self.assertIn("a kind is a word or words joined by hyphens", out)

    def test_a_user_s_checklist_without_a_name_or_version_is_stopped(self):
        cases = [
            ("without its version", "---\nname: release-notes\n---\n# R\n"),
            ("without front matter", "# R\n"),
        ]
        for name, text in cases:
            with self.subTest(name):
                # Given: a checklist the user made that opens so
                self.repo.write(".rn/checklists/release-notes.md", text)
                # When: the checklists for the kind are asked for
                code, out = run(self.repo, "checklists", "release-notes")
                # Then: it is stopped, naming the file and what it must open with
                self.assertEqual(code, 1)
                self.assertIn(
                    ".rn/checklists/release-notes.md: open the checklist with front matter "
                    "giving its name and version",
                    out,
                )

    def test_an_unknown_command_says_how_to_call(self):
        # Given: a call with no command rn knows
        # When: it is run
        code, out = run(self.repo, "fly")
        # Then: it ends with how to call it
        self.assertEqual(code, 1)
        self.assertIn("usage:", out)

    def test_the_script_run_on_its_own_says_how_to_call(self):
        # Given: the script, as the skill runs it
        script = os.path.join(SCRIPTS, "up.py")
        # When: it is run with no command
        done = subprocess.run([sys.executable, script], check=False, capture_output=True, text=True)
        # Then: it ends with how to call it
        self.assertEqual(done.returncode, 1)
        self.assertIn("usage:", done.stdout)


if __name__ == "__main__":
    unittest.main()
