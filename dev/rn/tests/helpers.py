import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

SCRIPTS = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "rn", "scripts")
)
sys.path.insert(0, SCRIPTS)

import up


def rn_checklist(name):
    return os.path.join(os.path.dirname(SCRIPTS), "checklists", name + ".md")


class RepoTest(unittest.TestCase):
    """Each test runs rn from a temporary folder standing for the user's repository."""

    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.repo)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.repo)

    def rn(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = up.main(list(argv))
        return code, out.getvalue()

    def write(self, path, text):
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def write_json(self, path, data):
        self.write(path, json.dumps(data))

    def read_text(self, path):
        with open(path, encoding="utf-8") as f:
            return f.read()

    def read_json(self, path):
        return json.loads(self.read_text(path))
