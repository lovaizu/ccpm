import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, "turn", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "turn", "hooks"))

import up  # noqa: E402

CHECKLIST = """# Note

A note is read by a teammate. It lets them act on it.

## Benefit

### B-1: What to do

Can the reader tell what to do?

Why: a note is for acting.

## Format

### F-1: Short

Is it short?

```markdown
### X-9: not an item
```
"""

PARTS = ["focal_entities", "goal_orientation", "retrieved_artifacts", "constraints",
         "predictive_cue", "uncertainty_signal", "semantic_gist", "relational_map", "episodic_trace"]


def ccs(**parts):
    c = {p: [] for p in PARTS}
    c["focal_entities"] = [{"deliverable": "docs/note.md"}, {"receiver": "a new teammate"}]
    c["goal_orientation"] = [{"use": "to start work"}, {"acceptance": "they can start alone"}]
    c["retrieved_artifacts"] = [{"viewpoint": "checklists/note.md"}, {"source": "notes.md"}]
    c.update(parts)
    return c


class Repo:
    """A git repository with a checklist and a source committed, as a user's repository."""

    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.realpath(self.tmp.name)
        self.write("checklists/note.md", CHECKLIST)
        self.write("notes.md", "Run make.\n")
        for args in (["init", "-q"], ["add", "."],
                     ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "first"]):
            subprocess.run(["git", "-C", self.path, *args], check=True)

    def write(self, rel, text):
        full = os.path.join(self.path, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(text)

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


def started(repo, c=None):
    """Starts a run from a CCS written to in.json; returns what start printed."""
    repo.write("in.json", json.dumps(c or ccs()))
    code, out = run(repo, "start", "in.json", "out.json", "s1")
    assert code == 0, out
    return json.loads(out)


def fill(repo, form, items):
    """Writes a role's form, as the role fills it."""
    repo.write(form, json.dumps(items))


def form(role, n=1):
    """Where a role's form is in round n of the run the tests start."""
    return f".turn/out/{n}/{role}.json"
