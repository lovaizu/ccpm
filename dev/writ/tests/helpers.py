import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CHECKLISTS = os.path.join(ROOT, "writ", "checklists")
sys.path.insert(0, os.path.join(ROOT, "writ", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "writ", "hooks"))

import up

NOTES = """---
name: notes
version: 1.0.0
---

# Release notes

Release notes are read by someone updating the tool.

## Benefit

### B-1: What changed

Can the reader tell what changed?

```markdown
### X-9: not an item
```
"""


class Repo:
    """A git repository with notes committed, as a user's repository."""

    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.realpath(self.tmp.name)
        self.write("docs/notes.md", "Tidies CSV files.\n")
        self.commit()

    def commit(self):
        for args in (
            ["init", "-q"],
            ["add", "."],
            ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "c"],
        ):
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


def started(repo, session="s1"):
    """Starts a job; returns what start printed."""
    code, out = run(repo, "start", session)
    assert code == 0, out
    return json.loads(out)


def laid(repo, *checklists):
    """Starts a job and lays its form for the checklists given by name; returns the job's folder."""
    folder = started(repo)["folder"]
    paths = [os.path.join(CHECKLISTS, f"{c}.md") for c in checklists]
    code, out = run(repo, "form", folder, *paths)
    assert code == 0, out
    return folder


def settle(repo, folder, **places):
    """Fills every place of the form, as writ's skill does once each is settled."""
    path = f"{folder}/form.json"
    form = repo.json(path)
    form.update(
        deliverable="README.md",
        receiver="developers with messy CSV files",
        use="to decide on the tool and start",
        acceptance="they tidy their first folder",
    )
    for item in form["items"].values():
        item.update(decision="Says it plainly.", settled="docs/notes.md:1")
    form.update(places)
    repo.write(path, json.dumps(form))
    return form


def returned(repo, folder, nxt, More, n=1):
    """Writes what turn returns on the job's n-th CCS: next, and its evidence deciding every item
    Good on line 1 but those given as More, each with a way."""
    ccs = repo.json(f"{folder}/in-{n}.json")
    items = list(repo.json(f"{folder}/form.json")["items"])
    work = f".turn/out-{n}"
    repo.write(
        f"{work}/list.json",
        json.dumps(
            {"checklists": [], "items": [{"id": i, "title": "", "text": ""} for i in items]}
        ),
    )
    repo.write(
        f"{work}/orchestrator.json",
        json.dumps(
            {
                i: {"met": False, "lines": "", "note": ""}
                if i in More
                else {"met": True, "lines": "1", "note": "given"}
                for i in items
            }
        ),
    )
    ccs["predictive_cue"] = [{"next": nxt}]
    ccs["semantic_gist"] = [{"difference": f"{i} (its question): a way"} for i in More]
    ccs["episodic_trace"] = [
        {"work": f"{work}/README.md"},
        {"evidence": f"{work}/list.json"},
        {"evidence": f"{work}/orchestrator.json"},
    ]
    repo.write(f"{folder}/out-{n}.json", json.dumps(ccs))
    return ccs
