"""The tests of dev/scripts/quality.sh: given the commit a push started from, it checks only the
code whose lines changed since it, and given nothing, the whole; it runs the property-based tests
and mutation testing of each plugin that dev/<plugin>/cosmic-ray.toml names, and fails on any mutant
under which every test passes. Each test runs the script in a repository of its own, with stand-ins
for pytest and cosmic-ray's commands, so that it checks what the script decides and not the tools it
runs."""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest

from helpers import GIT_ENV, TOP, executable, git_in, ran_in

# Each stand-in writes the command it ran, and, for pytest, the profile of the property-based tests.
LOGGED = '#!/bin/sh\necho "$(basename "$0") $* ${HYPOTHESIS_PROFILE:-}" >> "$LOG"\n'
# cr-filter-git writes the configuration it read, where the branch it compares with lies.
FILTER_GIT = LOGGED + 'cat "$2" >> "$LOG"\n'
# cr-rate gives the share of mutants that survived, as RATE sets it.
RATE = LOGGED + 'echo "${RATE:-0.00}"\n'
TOOLS = {
    "pytest": LOGGED,
    "cosmic-ray": LOGGED,
    "cr-filter-pragma": LOGGED,
    "cr-filter-operators": LOGGED,
    "cr-filter-git": FILTER_GIT,
    "cr-report": LOGGED,
    "cr-rate": RATE,
}


class QualityTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="quality-")
        self.addCleanup(shutil.rmtree, self.dir)
        self.repo = os.path.join(self.dir, "repo")
        self.log = os.path.join(self.dir, "log")
        bin_ = os.path.join(self.dir, "bin")
        os.makedirs(bin_)
        for name, text in TOOLS.items():
            executable(os.path.join(bin_, name), text)
        self.env = dict(os.environ, **GIT_ENV, LOG=self.log)
        self.env["PATH"] = bin_ + os.pathsep + self.env["PATH"]
        git_in(self.dir, self.env, "init", "-q", "-b", "main", self.repo)
        for script in ("quality.sh", "findings.sh"):
            self.put(f"dev/scripts/{script}", self.source(script))
        # Plugin a has property-based tests, and plugin b none.
        for plugin in ("a", "b"):
            self.put(f"dev/{plugin}/cosmic-ray.toml", f"[cosmic-ray]\nmodule-path = '{plugin}'\n")
            self.put(f"plugins/{plugin}/code.py", "")
        self.put("dev/a/tests/properties/test_a.py", "")
        self.base = self.commit()

    def source(self, script):
        with open(os.path.join(TOP, "dev", "scripts", script)) as file:
            return file.read()

    def put(self, path, text):
        full = os.path.join(self.repo, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        executable(full, text)

    def commit(self):
        git_in(self.repo, self.env, "add", "-A")
        git_in(self.repo, self.env, "commit", "-q", "--allow-empty", "-m", "change")
        return git_in(self.repo, self.env, "rev-parse", "HEAD")

    def quality(self, *args, rate="0.00"):
        return ran_in(self.repo, dict(self.env, RATE=rate), "sh", "dev/scripts/quality.sh", *args)

    def ran(self):
        if not os.path.exists(self.log):
            return ""
        with open(self.log) as file:
            return file.read()

    def test_with_no_base_the_whole_is_checked_with_the_most_inputs(self):
        # When: quality.sh runs with no commit given.
        done = self.quality()
        # Then: it passes, runs the property-based tests at the nightly profile, and runs the
        # mutants of each plugin's code, filtered by no commit.
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("pytest -q -p no:cacheprovider dev/a/tests/properties night", self.ran())
        self.assertEqual(self.ran().count("pytest"), 1, "only plugin a has property-based tests")
        self.assertEqual(self.ran().count("cosmic-ray exec"), 2, "a's mutants and b's")
        self.assertNotIn("cr-filter-git", self.ran())

    def test_with_a_base_it_names_the_base_on_the_line_ci_fix_reads(self):
        # Given: a change to plugin a's code after the base.
        self.put("plugins/a/code.py", "x = 1\n")
        self.commit()
        # When: quality.sh runs from the base.
        done = self.quality(self.base)
        # Then: it says which lines it checks, in the words ci-fix.sh finds the base by.
        self.assertIn(f"quality.sh: the lines changed since {self.base}\n", done.stdout)

    def test_with_a_base_only_the_lines_changed_since_it_are_mutated(self):
        # Given: a change to plugin a's code after the base.
        self.put("plugins/a/code.py", "x = 1\n")
        self.commit()
        # When: quality.sh runs from the base.
        done = self.quality(self.base)
        # Then: it runs the property-based tests at the push profile, and filters the mutants by
        # the lines changed since the base.
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("dev/a/tests/properties push", self.ran())
        self.assertIn(f'branch = "{self.base}"', self.ran())

    def test_code_with_no_line_changed_since_the_base_is_left_unchecked_and_said(self):
        # Given: a change to plugin a's code alone after the base.
        self.put("plugins/a/code.py", "x = 1\n")
        self.commit()
        # When: quality.sh runs from the base.
        done = self.quality(self.base)
        # Then: it mutates plugin a's code alone, and says that no line of b's changed.
        self.assertEqual(self.ran().count("cosmic-ray exec"), 1, "a's mutants alone")
        self.assertIn(
            "quality.sh: no line of b's code or of its property-based tests changed since"
            f" {self.base}",
            done.stdout,
        )

    def test_a_base_that_is_no_commit_here_checks_the_whole_and_says_so(self):
        # When: quality.sh runs from a commit the repository doesn't hold, as after a push that
        # rewrote history.
        done = self.quality("0123456789abcdef0123456789abcdef01234567")
        # Then: it says so, and checks the whole.
        self.assertIn("isn't a commit here, so the whole is checked", done.stdout)
        self.assertEqual(self.ran().count("cosmic-ray exec"), 2, "a's mutants and b's")

    def test_with_no_plugin_to_mutate_it_passes_and_says_so(self):
        # Given: no dev/<plugin>/cosmic-ray.toml.
        for plugin in ("a", "b"):
            git_in(self.repo, self.env, "rm", "-q", f"dev/{plugin}/cosmic-ray.toml")
        self.commit()
        # When: quality.sh runs.
        done = self.quality()
        # Then: it passes, runs nothing, and says that nothing names code to mutate.
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(self.ran(), "")
        self.assertIn("no dev/<plugin>/cosmic-ray.toml names code to mutate", done.stdout)

    def test_a_mutant_that_every_test_passes_under_fails_the_check(self):
        # When: quality.sh runs, and a share of the mutants survives.
        done = self.quality(rate="1.50")
        # Then: it fails, and reports the survivors' diffs with what the check is for.
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("cr-report --surviving-only --show-diff", self.ran())
        self.assertIn("Don't add a test only to clear a finding.", done.stdout)


if __name__ == "__main__":
    unittest.main()
