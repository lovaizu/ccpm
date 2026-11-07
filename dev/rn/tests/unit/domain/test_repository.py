"""domain/repository.py, the work's branch and its draft pull request: each commit on the run's
branch, the branch pushed, the pull request opened once and found again, and the run's commits."""

from __future__ import annotations

import os
import subprocess

import helpers
from helpers import RUN, repository


def gh(folder: str, view: bool) -> str:
    """A stand-in for gh on a PATH of its own, in the folder: `pr view` finds a pull request where
    `view`, and `pr create` makes one; each prints what a recorded run of gh printed."""
    os.makedirs(folder, exist_ok=True)
    found = "echo https://github.com/tidy-sort/tidy/pull/7" if view else "exit 1"
    with open(os.path.join(folder, "gh"), "w", encoding="utf-8") as f:
        f.write(
            '#!/bin/sh\ncase "$2" in\n'
            f"view) {found};;\n"
            'create) echo "Creating draft pull request"; echo https://github.com/tidy-sort/tidy/pull/8;;\n'
            "esac\n"
        )
    os.chmod(os.path.join(folder, "gh"), 0o755)
    return folder


class Branch(helpers.RunTest):
    def test_the_first_commit_makes_the_branch_and_each_after_goes_on_it(self):
        self.write(os.path.join(RUN, "a"), "1")
        self.assertTrue(repository.commit(RUN, [RUN], "rn: one"))
        self.assertEqual(
            repository.ran("git", "branch", "--show-current"), "rn/20261108-tidy-dry-run"
        )
        self.git("switch", "-q", "main")
        self.assertFalse(repository.commit(RUN, [RUN], "rn: none"))
        self.write(os.path.join(RUN, "a"), "2")
        self.assertTrue(repository.commit(RUN, [RUN], "rn: two"))
        self.assertEqual(
            repository.ran("git", "branch", "--show-current"), "rn/20261108-tidy-dry-run"
        )
        self.assertFalse(repository.commit(RUN, [RUN], "rn: none"))
        self.assertEqual(
            repository.messages(RUN), [f"rn: one\n\nRn-Run: {RUN}", f"rn: two\n\nRn-Run: {RUN}"]
        )
        self.assertEqual(repository.committed(RUN, os.path.join(RUN, "a")), "2")
        self.assertIsNone(repository.committed(RUN, "gone"))

    def test_a_branch_not_made_yet_has_no_commits(self):
        self.assertEqual(repository.messages(RUN), [])
        self.assertIsNone(repository.committed(RUN, "README.md"))

    def test_a_command_not_there_or_failing_is_refused(self):
        with self.assertRaises(repository.Failed) as stop:
            repository.ran("no-such-command-of-rn")
        self.assertEqual(str(stop.exception), "`no-such-command-of-rn` isn't installed")
        with self.assertRaises(repository.Failed) as stop:
            repository.ran("git", "show", "nowhere")
        self.assertIn("`git show nowhere` gave: fatal: ", str(stop.exception))
        with self.assertRaises(repository.Failed) as stop:
            repository.ran("sh", "-c", "exit 3")
        self.assertEqual(str(stop.exception), "`sh -c exit 3` gave: 3")


class Push(helpers.RunTest):
    def setUp(self) -> None:
        super().setUp()
        subprocess.run(
            ["git", "init", "-q", "--bare", os.path.join(self.base, "origin.git")], check=True
        )
        self.git("remote", "add", "origin", os.path.join(self.base, "origin.git"))
        self.write(os.path.join(RUN, "a"), "1")
        repository.commit(RUN, [RUN], "rn: one")

    def test_a_draft_pull_request_opened_once_and_found_again(self):
        path = os.environ["PATH"]
        os.environ["PATH"] = f"{gh(os.path.join(self.base, 'new'), False)}:{path}"
        self.addCleanup(os.environ.__setitem__, "PATH", path)
        self.assertEqual(repository.push(RUN, "g", "b"), "https://github.com/tidy-sort/tidy/pull/8")
        os.environ["PATH"] = f"{gh(os.path.join(self.base, 'old'), True)}:{path}"
        self.assertEqual(repository.push(RUN, "g", "b"), "https://github.com/tidy-sort/tidy/pull/7")

    def test_a_push_git_cant_make_is_refused_the_commit_kept(self):
        self.git("remote", "remove", "origin")
        with self.assertRaises(repository.Failed):
            repository.push(RUN, "g", "b")
        self.assertEqual(len(repository.messages(RUN)), 1)
