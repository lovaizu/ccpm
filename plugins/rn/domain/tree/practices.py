"""Decides how tree.py reads a best practice, `best-practice.json` in its kind's folder, as
dev/scripts/forms/best-practice.schema.json gives its form: each necessary condition with its
group, its critical success factor, and each practice with the phase it's carried out in. A best
practice made on a run, in the run's worktree under `.rn/best-practices/<kind>/`, is taken over
rn's own of the same kind, and which refactor best practice finishes a deliverable."""

from __future__ import annotations

from dataclasses import dataclass

BEST_PRACTICE = "best-practice.json"
# The kinds of the best practices that finish a deliverable: one of code, and one of a document.
REFACTOR_CODE, REFACTOR_DOC = "refactor-code", "refactor-doc"
# The phase of a practice, as its mark *While deciding* or *While making* names it.
DECIDE, MAKE = "decide", "make"


@dataclass(frozen=True)
class Practice:
    """One practice: its ID, such as `N3.2`, the phase it's carried out in, and its words."""

    id: str
    at: str
    text: str


@dataclass(frozen=True)
class NecessaryCondition:
    """One necessary condition of a best practice: its ID, its group, the ID of its critical
    success factor, its question, and its practices."""

    id: str
    group: str
    what: str
    practices: tuple[Practice, ...] = ()


@dataclass(frozen=True)
class BestPractice:
    """A best practice: its kind, the name of its folder, and its necessary conditions in its
    order."""

    kind: str
    conditions: tuple[NecessaryCondition, ...] = ()


def loads(text: str, kind: str, where: str) -> BestPractice:
    """The best practice of the kind in the JSON text read from the file at `where`. Raises Wrong,
    naming the file and the field, where the text isn't in the form of a best practice."""
    raise NotImplementedError("practices.loads")


def find(worktree: str, plugin_root: str, kind: str) -> str:
    """The path of the kind's `best-practice.json`: the one made on a run in the worktree's
    `.rn/best-practices/<kind>/` where there is one, else rn's own in its folder. Raises Wrong
    where neither holds the kind."""
    raise NotImplementedError("practices.find")


def load(worktree: str, plugin_root: str, kind: str) -> BestPractice:
    """The best practice of the kind, from where `find` gives. Raises Wrong as `loads` does."""
    raise NotImplementedError("practices.load")


def finisher(kind: str, path: str) -> str:
    """The kind of the refactor best practice that finishes a deliverable of the kind at the path:
    refactor-code for code, which a deliverable of the kind code is, and one of the kind specific
    whose path names a source file of a programming language, such as `.py`; refactor-doc for
    every other, as a document."""
    raise NotImplementedError("practices.finisher")


def groups(best_practice: BestPractice) -> tuple[str, ...]:
    """The ID of each group of the best practice's necessary conditions, in its order."""
    raise NotImplementedError("practices.groups")
