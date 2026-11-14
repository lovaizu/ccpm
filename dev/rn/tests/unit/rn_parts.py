"""What the unit cases of rn's parts build their inputs from: the walkthrough's design tree in the
parts' own form, a run's folder written as tree.py keeps it, and a git repository of the test's own
with a bare remote, each in the words of rn's README walkthrough, which is the parts'
specification."""

from __future__ import annotations

import dataclasses
import json
import os
from typing import Any

from rn_example import ANSWER, GOAL, HINTS, HINTS_NAME, POINT, TYPED, TYPED_NAME, git, write
from tree.design import DOING, DONE, Decision, Deliverable, DesignTree, NecessaryCondition
from tree.sign_offs import PLAN, SIGNED, WAITING, SignOff

RUN = ".rn/20261114-type-hints-for-invoicer"
NAME = "20261114-type-hints-for-invoicer"
ANSWERED = Decision(POINT, ANSWER, "user")
OPEN_POINT = Decision(POINT, None)


def hints(*decisions: Decision, status: str = "open") -> Deliverable:
    """The walkthrough's hints, of the kind code, with the decisions under N3."""
    return Deliverable(
        HINTS_NAME,
        HINTS,
        "code",
        status,
        conditions=(NecessaryCondition("N3", decisions=decisions),),
    )


def typed(*decisions: Decision, status: str = "open") -> Deliverable:
    """The walkthrough's typed marker, which takes from the hints and waits for them."""
    return Deliverable(
        TYPED_NAME,
        TYPED,
        "code",
        status,
        inputs=(HINTS,),
        preconditions=(HINTS,),
        conditions=(NecessaryCondition("N1", decisions=decisions),),
    )


def walkthrough(*deliverables: Deliverable) -> DesignTree:
    """The walkthrough's design tree, with its plan, or with the deliverables given."""
    return DesignTree(GOAL, "user", deliverables or (hints(ANSWERED), typed()))


def done(item: Deliverable) -> Deliverable:
    """The deliverable done, which keeps only its name, path, kind, and status."""
    return Deliverable(item.name, item.path, item.kind, DONE)


def doing(item: Deliverable) -> Deliverable:
    """The deliverable marked doing."""
    return dataclasses.replace(item, status=DOING)


PLAN_SIGNED = (SignOff(PLAN, "", state=SIGNED),)
PLAN_WAITING = (SignOff(PLAN, "", state=WAITING),)


def schema_tree(**fields: Any) -> dict[str, Any]:
    """The walkthrough's design tree as design-tree.schema.json gives it, with the fields given."""
    given: dict[str, Any] = {
        "goal": {"decided": GOAL, "by": "user"},
        "deliverables": [
            {
                "name": HINTS_NAME,
                "path": HINTS,
                "kind": "code",
                "inputs": [],
                "preconditions": [],
                "status": "open",
                "necessary_conditions": [
                    {
                        "id": "N3",
                        "good": False,
                        "decisions": [{"about": POINT, "decided": ANSWER, "by": "user"}],
                    }
                ],
            },
            {"name": TYPED_NAME, "path": TYPED, "kind": "code", "status": "done"},
        ],
    }
    given.update(fields)
    return given


def repository(base: str) -> tuple[str, str]:
    """A git repository with one commit of invoicer/__init__.py, and a bare repository as its
    `origin`, each in the folder; gives the repository's root and the remote's."""
    root, remote = os.path.join(base, "invoicer"), os.path.join(base, "origin.git")
    git(base, "init", "-q", "--bare", "-b", "main", remote)
    git(base, "init", "-q", "-b", "main", root)
    write(root, "invoicer/__init__.py", '"""invoicer."""\n')
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "invoicer")
    git(root, "remote", "add", "origin", remote)
    return root, remote


def environ(base: str) -> dict[str, str]:
    """The environment of a part's git and gh: no setting of the machine's own, and the double of
    gh first on the PATH, logged in, with what GitHub holds in the folder."""
    from rn_example import GH

    state = os.path.join(base, "github.json")
    if not os.path.exists(state):
        write(base, "github.json", json.dumps({"logged_in": True, "pulls": {}, "issues": []}))
    return dict(
        os.environ,
        PATH=GH + os.pathsep + os.environ.get("PATH", os.defpath),
        RN_GH_STATE=state,
        GIT_CONFIG_GLOBAL=os.devnull,
        GIT_CONFIG_NOSYSTEM="1",
        GIT_AUTHOR_NAME="u",
        GIT_AUTHOR_EMAIL="u@example.com",
        GIT_COMMITTER_NAME="u",
        GIT_COMMITTER_EMAIL="u@example.com",
        TMPDIR=base,
    )
