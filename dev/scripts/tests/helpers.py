"""What the tests of dev/scripts stand on: the top of the repository, a git that reads no setting
of the machine the tests run on, a PATH with one command left out, and a temporary folder for each
test."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from typing import Any

TOP = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

GIT_ENV = {
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
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

    def read_json(self, path: str) -> Any:
        """The JSON at the path."""
        with open(path, encoding="utf-8") as f:
            return json.load(f)
