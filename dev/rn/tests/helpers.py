"""What rn's tests stand on beside what every plugin's tests do: rn's code on sys.path, its modules
taken by each test from here, so each test finds them whichever runs first; and a test that stands
in a repository of tidy, the README's walkthrough's tool, made once a run and copied into each
test's folder, with the system's temporary folder in the test's folder, so the run's folder there
goes with the test."""

from __future__ import annotations

import contextlib
import copy
import io
import json
import os
import sys
import tempfile
from typing import Any
from unittest import mock

RN = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "plugins", "rn")
)
DOMAIN = os.path.join(RN, "domain")
SCRIPTS = os.path.join(RN, "scripts")
ADAPTERS = os.path.join(RN, "hooks", "adapters")
sys.path[:0] = [DOMAIN, SCRIPTS, os.path.join(RN, "..", "..", "dev", "lane")]

import edits
import files
import practices
import records
import repository
import runs
import starts
import testing
import throwaway
import tree
import trees
import tries

__all__ = [
    "edits",
    "files",
    "practices",
    "records",
    "repository",
    "runs",
    "starts",
    "testing",
    "throwaway",
    "tree",
    "trees",
    "tries",
]

# The run of the README's walkthrough, and its goal as the planner drafts it.
RUN = os.path.join(".rn", "20261108-tidy-dry-run")
GOAL = "Someone about to sort their Downloads folder with tidy sees what it would move."
# tidy's repository as the walkthrough finds it.
TIDY = {
    "README.md": "# tidy\n\ntidy sorts a Downloads folder into folders by type.\n",
    "tidy/cli.py": "def main():\n    pass\n",
    "dev/product-vision.md": "# tidy\n\nSomeone sorts their Downloads folder.\n",
}


def deliverable(path: str, kind: str, **given: Any) -> dict[str, Any]:
    """A deliverable not done of the path and kind, each intent of its kind's best practice not
    good, as tree.py lays it, the fields given put in."""
    intents = practices.intents(
        practices.read(os.path.join(practices.OWN, kind, "best-practice.json"))
    )
    made = {
        "name": f"the {kind} of tidy",
        "path": path,
        "kind": kind,
        "inputs": [],
        "preconditions": [],
        "status": "open",
        "intents": [{"id": i, "good": False, "decisions": []} for i in intents],
    }
    made.update(given)
    return made


def done(path: str, name: str, kind: str = "readme") -> dict[str, Any]:
    """A deliverable done, in the one line the tree keeps of it."""
    return {"name": name, "path": path, "kind": kind, "status": "done"}


def walkthrough(by: str = "user") -> dict[str, Any]:
    """The walkthrough's tree once the planner lays the plan: the goal settled by whom, the README,
    which takes from the product vision, and tidy/cli.py, which takes from the README."""
    return {
        "goal": {"decided": GOAL, "by": by},
        "deliverables": [
            deliverable("README.md", "readme", inputs=["dev/product-vision.md"]),
            deliverable("tidy/cli.py", "code", inputs=["README.md"]),
        ],
    }


def decided(tree: dict[str, Any], n: int, intent: str, about: str, what: Any, by: str = "user"):
    """The tree with a decision about the point under the intent of the deliverable of the
    number, open where what's None."""
    made = copy.deepcopy(tree)
    for i in made["deliverables"][n - 1]["intents"]:
        if i["id"] == intent:
            decision = {"about": about, "decided": what}
            if what is not None:
                decision["by"] = by
            i["decisions"].append(decision)
    return made


def ran(module: Any, *argv: str, stdin: str = "") -> tuple[int, str, str]:
    """What the script module's main gives on the arguments, the text on its standard input: its
    exit code, what it printed, and its errors."""
    out, err = io.StringIO(), io.StringIO()
    stdin_ = mock.patch("sys.stdin", io.StringIO(stdin))
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), stdin_:
        code = module.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class RunTest(testing.GitTest):
    """A test standing in tidy's repository, `repo` in `base`, committed on main, with the system's
    temporary folder in `base`."""

    def setUp(self) -> None:
        super().setUp()
        self.repo = self.copied("tidy", self.make)
        self.tmp = os.path.join(self.base, "tmp")
        os.makedirs(self.tmp)
        patched = mock.patch.object(tempfile, "tempdir", self.tmp)
        patched.start()
        self.addCleanup(patched.stop)

    def make(self) -> None:
        """tidy's repository, its files committed on main."""
        self.git("init", "-q", "-b", "main")
        for name, text in TIDY.items():
            self.write(name, text)
        self.commit()

    def lays(self, data: dict[str, Any], run: str = RUN) -> None:
        """The run's tree written, as tree.py writes it."""
        files.save(runs.tree_path(run), data)

    def commits(self, data: dict[str, Any], run: str = RUN) -> None:
        """The run's tree written and committed on its branch, as the planner's last commit left
        it."""
        self.lays(data, run)
        repository.commit(run, [run], "rn: laid")

    def edit(self, data: dict[str, Any], run: str = RUN) -> str:
        """The planner's tree edit written at its path: the path."""
        path = os.path.join(runs.temporary(run), runs.EDIT)
        self.write_json(path, data)
        return path

    def tree_now(self, run: str = RUN) -> dict[str, Any]:
        """The run's tree on disk."""
        return self.read_json(runs.tree_path(run))

    def handed(self, data: dict[str, Any]) -> str:
        """The change handed by tree.py change: what it printed."""
        return starts.change(json.dumps(data))
