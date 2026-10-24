"""What rn's tests stand on beside what every plugin's tests do: the repository a session is kept in,
with the remote it is pushed to, made once a run and copied into each test's folder."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lane"))

import testing

# The folder of the copy holding the user's repository, beside `origin.git`, its remote.
REPO = "repo"


class MainAndWork(testing.GitTest):
    """A test in a git repository whose remote's default branch is `main`, with `work` checked
    out, both pushed to the remote, a bare repository beside it."""

    def main_and_work(self) -> None:
        """Makes where the test stands `origin.git`, a bare repository standing for the remote, and
        the repository `repo`: `main` with a README and `work` checked out from it, each pushed and
        tracking the remote's. The remote is named by a path from the repository, so a copy pushes
        to its own."""
        self.git("init", "-q", "--bare", "origin.git")
        os.makedirs(REPO)
        os.chdir(REPO)
        self.git("init", "-q")
        self.git("checkout", "-q", "-b", "main")
        self.write("README.md", "# app\n")
        self.commit()
        self.git("remote", "add", "origin", "../origin.git")
        self.git("push", "-q", "-u", "origin", "main")
        self.git("remote", "set-head", "origin", "main")
        self.git("checkout", "-q", "-b", "work")
        self.git("push", "-q", "-u", "origin", "work")
