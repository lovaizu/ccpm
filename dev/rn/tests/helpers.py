"""A user's repository, and a way to run rn's scripts in it, as the conductor does."""

import contextlib
import io
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CHECKLISTS = os.path.join(ROOT, "rn", "checklists")
SCRIPTS = os.path.join(ROOT, "rn", "scripts")
sys.path.insert(0, SCRIPTS)

import up

SESSION = ".rn/20261003-typescript"

NOTES = """---
name: release-notes
version: 1.0.0
---

# Release notes

Release notes are read by someone updating the tool. Each item of `doc.md` applies to them.

## Benefit

### B-1: What changed

Can the reader tell what changed?

```markdown
### X-9: not an item
```
"""


class Repo:
    """A user's repository: a folder with notes in it."""

    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.realpath(self.tmp.name)
        self.write("docs/notes.md", "Tidies CSV files.\n")

    def write(self, rel, text):
        full = os.path.join(self.path, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(text if isinstance(text, str) else json.dumps(text))

    def read(self, rel):
        with open(os.path.join(self.path, rel)) as f:
            return f.read()

    def json(self, rel):
        return json.loads(self.read(rel))

    def exists(self, rel):
        return os.path.exists(os.path.join(self.path, rel))

    def close(self):
        self.tmp.cleanup()


def run(repo, *args):
    """Runs up.py with args from the repository; returns its exit code and what it printed."""
    out = io.StringIO()
    here = os.getcwd()
    os.chdir(repo.path)
    try:
        with contextlib.redirect_stdout(out):
            code = up.main(list(args))
    finally:
        os.chdir(here)
    return code, out.getvalue()
