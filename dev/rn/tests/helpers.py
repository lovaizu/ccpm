"""What rn's tests stand on beside what every plugin's tests do: the repository a session is kept in,
made once a run and copied into each test's folder."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "common"))

import testing


class MainAndWork(testing.GitTest):
    """A test in a git repository whose remote's default branch is `main`, with `work` checked
    out."""

    def main_and_work(self) -> None:
        """Makes where the test stands the repository: `main` with a README, as origin has it, and
        `work` checked out from it."""
        self.git("init", "-q")
        self.git("checkout", "-q", "-b", "main")
        self.write("README.md", "# app\n")
        self.commit()
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")
        self.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
        self.git("checkout", "-q", "-b", "work")
