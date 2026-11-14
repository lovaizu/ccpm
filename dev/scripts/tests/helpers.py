"""What the tests of dev/scripts stand on: the top of the repository, a git that reads no setting
of the machine the tests run on, a PATH with one command left out, and a temporary folder for each
test."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from typing import Any

TOP = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# git reads no setting of the machine, and starts no maintenance of its own in the background, which
# would write in a test's repository while the test removes it.
GIT_ENV = {
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_COUNT": "2",
    "GIT_CONFIG_KEY_0": "maintenance.auto",
    "GIT_CONFIG_VALUE_0": "false",
    "GIT_CONFIG_KEY_1": "gc.auto",
    "GIT_CONFIG_VALUE_1": "0",
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@t",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@t",
}


def without(path: str, tool: str, folder: str) -> str:
    """Makes folder, which links each command of path, the first of each name, but the tool, and
    returns it as a PATH."""
    os.makedirs(folder)
    for each in path.split(os.pathsep):
        if not os.path.isdir(each):
            continue
        for name in os.listdir(each):
            command = os.path.join(each, name)
            link = os.path.join(folder, name)
            if name != tool and not os.path.lexists(link) and os.access(command, os.X_OK):
                os.symlink(command, link)
    return folder


class FolderTest(unittest.TestCase):
    """Each test runs in a temporary folder of its own, `base`, removed after it."""

    def setUp(self) -> None:
        self.base = os.path.realpath(tempfile.mkdtemp(prefix="dev-scripts-"))
        self.addCleanup(shutil.rmtree, self.base)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.base)

    def write(self, path: str, text: str) -> None:
        """Writes the text at the path, making its folder where it isn't there."""
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def write_json(self, path: str, data: Any) -> None:
        """Writes the data at the path as JSON on one line."""
        self.write(path, json.dumps(data))

    def read(self, path: str) -> str:
        """The text at the path."""
        with open(path, encoding="utf-8") as f:
            return f.read()


def executable(path: str, text: str) -> None:
    """Writes the text at the path as a file that runs, such as a script or a stand-in for a
    command."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    os.chmod(path, 0o755)


def git_in(repo: str, env: dict[str, str], *args: str) -> str:
    """What the git command prints, run in the folder; it stops the test where git fails."""
    return subprocess.run(
        ["git", *args], cwd=repo, env=env, check=True, capture_output=True, text=True
    ).stdout.strip()


def ran_in(repo: str, env: dict[str, str], *command: str) -> subprocess.CompletedProcess[str]:
    """What the command gives, run in the repository: its exit code and its output, which a test
    reads in place of an exception."""
    return subprocess.run(
        list(command), cwd=repo, env=env, capture_output=True, text=True, check=False
    )
