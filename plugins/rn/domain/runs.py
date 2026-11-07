"""A run's files: its folder `.rn/<yyyymmdd>-<goal>/` at the top of the repository, with the design
tree and each turn's rounds, which git keeps; and its folder in the system's temporary folder,
`rn/<yyyymmdd>-<goal>/`, with what rn uses only while the run goes on: the change handed for the
planner's next start, the planner's tree edit, its answers since the last change, and the groups
of a round already cut.

A turn of a deliverable lies in `turns/<nn>-<deliverable>/`, its number in the run, then the
deliverable's path in a few words, and `-reading` after them for its turn of how it reads. Its
rounds lie in `01/`, `02/` and on, each holding the Making record, `generator.json`, the try
record, `throwaway.txt`, and the Answers of each group, `evaluator-G<n>.json`. rn reads where the
run stands from the tree's statuses and these records alone, as a second record of it would drift
from them."""

from __future__ import annotations

import datetime
import glob
import os
import re
import tempfile
from typing import Any

import files

TOP = ".rn"
TURNS = "turns"
READING = "-reading"
CHANGE = "change.json"
EDIT = "edit.json"
ANSWERED = "answered.json"
CUTS = "cuts.json"
MADE = "generator.json"
TRY = "throwaway.txt"
# A round's Answers, by its group.
ANSWERS = re.compile(r"evaluator-(G[1-9][0-9]*)\.json")
# What a run's name and a turn's take of the words they come from: a few words, each of letters
# and digits.
WORD = re.compile(r"[a-z0-9]+")
WORDS = 5


def today() -> str:
    """Today's date, as a run's name begins with it."""
    return datetime.date.today().strftime("%Y%m%d")


def words(text: str, count: int = WORDS) -> str:
    """The first words of the text, of letters and digits in lower case, joined by `-`."""
    return "-".join(WORD.findall(text.lower())[:count]) or "work"


def new(request: str) -> str:
    """The folder of a new run of the request: today's date and its first words, with a number
    after them where a run of that name is there already, or its change waits."""
    first = os.path.join(TOP, f"{today()}-{words(request)}")
    name, number = first, 1
    while os.path.exists(name) or pending(name) is not None:
        number += 1
        name = f"{first}-{number}"
    return name


def temporary(run: str) -> str:
    """The run's folder in the system's temporary folder, `rn/<its name>/`."""
    return os.path.join(tempfile.gettempdir(), "rn", os.path.basename(os.path.normpath(run)))


def repository() -> str:
    """The top of the repository the command runs at, with every link in it followed."""
    return os.path.realpath(".")


def kept(run: str, name: str) -> Any:
    """What the run's temporary folder keeps under the name for this repository; None where it
    keeps nothing, or what it keeps is another repository's of the same run name."""
    path = os.path.join(temporary(run), name)
    try:
        data = files.read(path)
    except files.Unreadable:
        return None
    return data["data"] if isinstance(data, dict) and data.get("repo") == repository() else None


def keep(run: str, name: str, data: Any) -> None:
    """Keeps the data under the name in the run's temporary folder, for this repository."""
    files.save(os.path.join(temporary(run), name), {"repo": repository(), "data": data})


def drop(run: str, *names: str) -> None:
    """Removes what the run's temporary folder keeps under each name, where it keeps it."""
    for name in names:
        path = os.path.join(temporary(run), name)
        if os.path.exists(path):
            os.remove(path)


def pending(run: str) -> dict[str, Any] | None:
    """The change handed for the run's planner, not yet committed; None where none is."""
    return kept(run, CHANGE)


def handed() -> str | None:
    """The run of this repository whose change waits for the planner, the one handed last where
    more than one does; None where none does."""
    places = glob.glob(os.path.join(tempfile.gettempdir(), "rn", "*", CHANGE))
    found = [p for p in places if pending(os.path.dirname(p)) is not None]
    if not found:
        return None
    return os.path.join(TOP, os.path.basename(os.path.dirname(max(found, key=os.path.getmtime))))


def tree_path(run: str) -> str:
    """The path of the run's design tree."""
    return os.path.join(run, "design-tree.json")


def listed() -> list[str]:
    """Each run of the repository that has a design tree, by its folder, in order."""
    return sorted(os.path.dirname(p) for p in glob.glob(os.path.join(TOP, "*", "design-tree.json")))


def turn_folders(run: str) -> list[str]:
    """Each turn folder of the run, in the order of the turns."""
    return sorted(glob.glob(os.path.join(run, TURNS, "[0-9][0-9]-*")))


def turn_name(path: str, reading: bool) -> str:
    """The name a turn of the deliverable at the path takes after its number."""
    return words(path, 8) + (READING if reading else "")


def turn_of(run: str, path: str, reading: bool) -> str | None:
    """The folder of the turn of the deliverable at the path, of how it reads where `reading`, of
    what it says otherwise; None where it has none yet."""
    name = turn_name(path, reading)
    found = [t for t in turn_folders(run) if os.path.basename(t)[3:] == name]
    # rn makes a turn of each kind of a deliverable once, so it finds one at most.
    return found[-1] if found else None  # pragma: no mutate


def new_turn(run: str, path: str, reading: bool) -> str:
    """The folder of a new turn of the deliverable at the path, numbered after the run's last."""
    number = len(turn_folders(run)) + 1
    return os.path.join(run, TURNS, f"{number:02d}-{turn_name(path, reading)}")


def rounds(turn: str | None) -> list[str]:
    """Each round folder of the turn, in order; none where there's no turn."""
    if turn is None:
        return []
    return sorted(glob.glob(os.path.join(turn, "[0-9][0-9]")))


def last(turn: str | None) -> str | None:
    """The folder of the turn's last round; None where it has none."""
    found = rounds(turn)
    return found[-1] if found else None


def next_round(turn: str) -> str:
    """The folder of the turn's next round."""
    return os.path.join(turn, f"{len(rounds(turn)) + 1:02d}")


def answers_of(round_: str) -> dict[str, Any]:
    """The Answers the round holds, by their group, each as its file holds it."""
    found = {}
    for path in glob.glob(os.path.join(round_, "evaluator-G*.json")):
        matched = ANSWERS.fullmatch(os.path.basename(path))
        if matched:
            found[matched[1]] = files.read(path)
    return found


def made_of(round_: str) -> dict[str, Any] | None:
    """The round's Making record; None where the generator hasn't written it."""
    path = os.path.join(round_, MADE)
    return files.read(path) if os.path.isfile(path) else None


def outcome(round_: str, groups: list[str]) -> str:
    """Where the round stands: `making` while it has no Making record, `open` where the generator
    or an evaluator found a point open, `judging` while a group has no Answers, `more` where an
    intent isn't met, and `good` where each one is."""
    made = made_of(round_)
    if made is None:
        return "making"
    if made["open"]:
        return "open"
    given = answers_of(round_)
    if any(g not in given for g in groups):
        return "judging"
    each = [given[g] for g in groups]
    if any(a["open"] for a in each):
        return "open"
    return "more" if any(a["not_met"] for a in each) else "good"


def shortfalls(round_: str) -> list[tuple[str, str]]:
    """Each intent the round's evaluators found not met, with what the people still lack."""
    return [
        (s["question"], s["lacks"])
        for _, a in sorted(answers_of(round_).items())
        for s in a["not_met"]
    ]


def points(round_: str) -> list[dict[str, str]]:
    """Each point the round found open, the generator's then each evaluator's: its intent, what
    it's about, and the point itself."""
    made = made_of(round_) or {"open": []}
    found = [{"intent": p["intent"], "about": p["about"], "what": p["what"]} for p in made["open"]]
    for _, a in sorted(answers_of(round_).items()):
        found += [
            {"intent": p["question"], "about": p["about"], "what": p["what"]} for p in a["open"]
        ]
    return found
