"""A kind's best practice, as rn's roles take it: where it lies, read and held to its form; its
intents, in groups that each evaluator of a round judges at once; and the steps of its practices,
in the form of Lane's steps port, each with the lanes its trace calls for.

rn looks for a kind's best practice in the run's own folder of them, where a meta deliverable of
the run makes one, then among rn's own, then in the folders of the repository's earlier runs, the
newest first, as a later run may take what an earlier one made."""

from __future__ import annotations

import glob
import os
from typing import Any

import files

# rn's own best practices, beside this module.
OWN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "best-practices")
PRACTICE = "best-practice.json"
# What an intent's about names where the intent asks of the deliverable as a whole.
WHOLE = "the whole"
# The kinds whose deliverable is code, which a turn of how it reads takes by refactor-code; every
# other kind's deliverable is a document, which a turn of how it reads takes by refactor-doc.
CODE = ("code", "plugin")
READING = {"code": "refactor-code", "document": "refactor-doc"}
# The lane of Lane's that holds each action a step's trace names.
LANES = {"run": "run_step", "read": "read_whole", "write": "write_step"}


def found(kind: str, run: str, top: str = ".") -> str | None:
    """The path of the kind's best practice for the run's folder, under the repository's top: in
    the run's own folder, then among rn's own, then in an earlier run's, the newest first; None
    where none is there."""
    places = [
        os.path.join(run, "best-practices", kind, PRACTICE),
        os.path.join(OWN, kind, PRACTICE),
    ]
    earlier = glob.glob(os.path.join(top, ".rn", "*", "best-practices", kind, PRACTICE))
    places += sorted(earlier, reverse=True)
    return next((p for p in places if os.path.isfile(p)), None)


def read(path: str) -> dict[str, Any]:
    """The best practice at the path, held to rn's form of it. Refuses, by Unreadable, one that's
    missing, holds no JSON, or is out of the form."""
    return files.load(path, "best-practice")


def intents(data: dict[str, Any]) -> list[str]:
    """The ID of each intent of the best practice, in its order."""
    return [i["id"] for i in data["intents"]]


def reading(kind: str) -> str:
    """The kind of the turn of how a deliverable of the kind reads: refactor-code for code,
    refactor-doc for a document."""
    return READING["code" if kind in CODE else "document"]


def abouts(intent: dict[str, Any]) -> set[str]:
    """What the intent asks of, each part or section its about names, or the whole alone where it
    names the whole."""
    named = {a.strip() for a in intent["about"].split(",")}
    return {WHOLE} if WHOLE in named else named


def groups(data: dict[str, Any]) -> list[list[str]]:
    """The best practice's intents in groups, each of the IDs of the intents that ask of a part in
    common, those of the whole in one group of their own; the groups in the order of their first
    intent, the IDs of each in the best practice's order. An evaluator judges a group fresh, and
    the evaluators of a round judge theirs at once."""
    made: list[tuple[set[str], list[str]]] = []
    for intent in data["intents"]:
        named = abouts(intent)
        joined = [g for g in made if g[0] & named]
        kept = (named, [intent["id"]])
        for group in joined:
            kept[0].update(group[0])  # pragma: no mutate
            kept[1].extend(group[1])
            made.remove(group)
        made.append(kept)
    order = intents(data)
    return sorted((sorted(g[1], key=order.index) for g in made), key=lambda g: order.index(g[0]))


def steps(data: dict[str, Any], chosen: list[str] | None) -> list[dict[str, Any]]:
    """The step lists of the practices of the intents chosen, all where None, in the form of Lane's
    steps port: one list for each practice that has steps, named by its intent, each step its text
    and a lane of the trace kind for its trace, none where it has no trace."""
    made = []
    for practice in data["practices"]:
        if chosen is not None and practice["intent"] not in chosen:
            continue
        listed = [
            {
                "says": step["text"],
                "lanes": [{"lane": LANES[step["trace"]["action"]], "takes": step["trace"]["takes"]}]
                if "trace" in step
                else [],
            }
            for step in practice["steps"]
        ]
        if listed:
            made.append({"list": practice["intent"], "steps": listed})
    return made
