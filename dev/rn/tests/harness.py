"""A repository with an rn session in it, and a way to run rn's hooks on it with the JSON Claude
Code sends, through their entry files."""
import json
import os
import subprocess
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.join(HERE, "..", "..", "..", "rn")
HOOKS = os.path.join(PLUGIN, "hooks")

STEERING = """---
rn: 0.9.0
pr: https://github.com/you/repo/pull/1
status: running
artifact-language: English
conversation-language: Japanese
readme: README.md
design: docs/design.md
verification: docs/verification.md
---

# Goal

A wrong type fails the build.

# Acceptance criteria

## Attractive quality

- A1: Code reproducing each bug fails the build

## Must-be quality

- M1: The app builds as before

# Assumptions

# Rules

# Tasks

### [ ] #1: Plan sign-off
### [ ] #2: Design sign-off
"""

SDIR = ".rn/20261003-typescript"


def sh(cwd, *args):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=True).stdout


class Repo:
    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = os.path.join(self.tmp.name, "work")
        self.data = os.path.join(self.tmp.name, "data")
        sh(self.tmp.name, "git", "init", "-q", "-b", "main", self.dir)
        sh(self.dir, "git", "config", "user.name", "t")
        sh(self.dir, "git", "config", "user.email", "t@example.com")
        self.write("README.md", "app\n")
        sh(self.dir, "git", "add", "-A")
        sh(self.dir, "git", "commit", "-qm", "init")
        sh(self.dir, "git", "switch", "-qc", "session")
        self.write(f"{SDIR}/steering.md", STEERING)
        self.commit("rn: start\n\n● plan ── started → working out the plan")

    def write(self, rel, text):
        p = os.path.join(self.dir, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(text)
        return p

    def commit(self, msg):
        sh(self.dir, "git", "add", "-A")
        sh(self.dir, "git", "commit", "-qm", msg)

    def hook(self, entry, **data):
        data.setdefault("cwd", self.dir)
        data.setdefault("session_id", "s1")
        env = dict(os.environ, CLAUDE_PLUGIN_DATA=self.data)
        r = subprocess.run(["python3", os.path.join(HOOKS, entry + ".py")], input=json.dumps(data),
                           cwd=self.dir, capture_output=True, text=True, env=env)
        return r.returncode, r.stdout + r.stderr


class Session(unittest.TestCase):
    """A repository with an rn session, and a conversation (s1) where the user typed /rn:on."""

    def setUp(self):
        self.r = Repo()
        self.r.hook("userpromptexpansion", command_name="rn:on")

    def tearDown(self):
        self.r.tmp.cleanup()
