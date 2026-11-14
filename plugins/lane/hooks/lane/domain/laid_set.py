"""Decides the form of a plugin's laid set, `hooks/lanes.json`: the Lanes, the Routes, the adapters,
and the Laid, as `lay.py write` writes it and the guard reads it on each hook event."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from typing import Any

from domain.fault import Fault

# The kinds of a move after the start of a Run, a Result, a command the person types, or the end of
# another plugin's run that a move called.
START, RESUME, CALL, WAIT, NO_MORE = "start", "resume", "call", "wait", "no_more"


@dataclass(frozen=True)
class Lane:
    """A rule on one step of one role, in the file that holds the step, of one lane type: `role` is
    the skill's or a subagent's name, `step` the step's number, `file` the path of the file in the
    plugin's folder, `type` the lane type's name, `takes` what the type takes, such as commands or
    paths, each name in braces standing for a run value, and `sentence` what the role reads."""

    role: str
    step: int
    file: str
    type: str
    takes: tuple[str, ...]
    sentence: str


@dataclass(frozen=True)
class Move:
    """One move of a Route: `kind` is START, RESUME, CALL, WAIT, or NO_MORE, `role` the role that a
    start or a resume names, or the skill of another plugin, as `<plugin>:<skill>`, that a CALL
    calls, as the plugin guide's A plugin that uses another says, and `waits_for` the command, such
    as `/changelog:approve`, that the person types before the move is due, or "" for a move due at
    once. A WAIT waits for no command."""

    kind: str
    role: str = ""
    waits_for: str = ""


@dataclass(frozen=True)
class Route:
    """The moves of one skill after one moment: `skill` is the skill whose Run the Route moves,
    `after` is `first` for the start of its Run, `<role> <result>` for a Result, the command the
    person types, such as `/changelog:pause`, or the skill `<plugin>:<skill>` that a CALL called,
    for the moves once the main conversation goes back to its own steps. One move is the move due,
    and several are those among which the skill's steps choose."""

    skill: str
    after: str
    moves: tuple[Move, ...]


@dataclass(frozen=True)
class LaidSentence:
    """A sentence that Lane added to a step: the file it lies in, the words of the step it follows,
    and the sentence."""

    file: str
    follows: str
    sentence: str


@dataclass(frozen=True)
class Laid:
    """What Lane laid in the plugin, so that the next `/lane:up` takes Lane's text apart from the
    user's: each sentence added to a step, and each hook entry of `hooks/hooks.json` that is
    Lane's, as its event and command."""

    sentences: tuple[LaidSentence, ...] = ()
    hooks: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class LaidSet:
    """What `hooks/lanes.json` holds: the plugin's name, each skill whose call begins a Run of its
    own, its roles, the Lanes, the Routes of each skill, the program in `hooks/adapters/` that gives
    a start's text and the one that gives the Kept results, each "" where the plugin has none, the
    Laid, and `proposes`, true only for Lane's own up, whose Run waits for the caller's Approval of
    a Proposal."""

    plugin: str
    skills: tuple[str, ...]
    roles: tuple[str, ...]
    lanes: tuple[Lane, ...]
    routes: tuple[Route, ...]
    text_adapter: str = ""
    results_adapter: str = ""
    laid: Laid = field(default_factory=Laid)
    proposes: bool = False


def dumps(laid_set: LaidSet) -> str:
    """The laid set as the JSON text of `hooks/lanes.json`, which `loads` reads back as it was."""
    return json.dumps(asdict(laid_set), indent=2) + "\n"


# Each field of a laid set's JSON, in its order.
_FIELDS = (
    "plugin",
    "skills",
    "roles",
    "lanes",
    "routes",
    "text_adapter",
    "results_adapter",
    "laid",
    "proposes",
)


def _wrong(path: str, what: str) -> Fault:
    return Fault(f"{path} {what}, so run `/lane:up` again to lay it anew", "the plugin's maker")


def loads(text: str, path: str) -> LaidSet:
    """The laid set of the JSON text read from the file at `path`. Raises Fault, naming the path and
    what isn't in the form, with `the plugin's maker` to fix it by running `/lane:up` again, where
    the text isn't a laid set."""
    try:
        given = json.loads(text)
    except ValueError as e:
        raise _wrong(path, f"isn't JSON ({e})") from None
    if not isinstance(given, dict):
        raise _wrong(path, "isn't a JSON object")
    missing = [name for name in _FIELDS if name not in given]
    if missing:
        raise _wrong(path, "lacks " + ", ".join(f"`{name}`" for name in missing))
    try:
        return _laid_set(given)
    except (KeyError, TypeError, AttributeError) as e:
        raise _wrong(path, f"holds a field out of form ({e!r})") from None


def _laid_set(given: dict[str, Any]) -> LaidSet:
    laid = given["laid"]
    return LaidSet(
        plugin=str(given["plugin"]),
        skills=tuple(given["skills"]),
        roles=tuple(given["roles"]),
        lanes=tuple(
            Lane(
                str(each["role"]),
                int(each["step"]),
                str(each["file"]),
                str(each["type"]),
                tuple(each["takes"]),
                str(each["sentence"]),
            )
            for each in given["lanes"]
        ),
        routes=tuple(
            Route(
                str(each["skill"]),
                str(each["after"]),
                tuple(
                    Move(str(m["kind"]), str(m["role"]), str(m["waits_for"])) for m in each["moves"]
                ),
            )
            for each in given["routes"]
        ),
        text_adapter=str(given["text_adapter"]),
        results_adapter=str(given["results_adapter"]),
        laid=Laid(
            tuple(
                LaidSentence(str(each["file"]), str(each["follows"]), str(each["sentence"]))
                for each in laid["sentences"]
            ),
            tuple((str(event), str(command)) for event, command in laid["hooks"]),
        ),
        proposes=bool(given["proposes"]),
    )


def load(plugin_root: str) -> LaidSet | None:
    """The laid set of the plugin in the folder, or None where it has no `hooks/lanes.json`. Raises
    Fault as `loads` does."""
    path = os.path.join(plugin_root, "hooks", "lanes.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return loads(f.read(), path)


def routes_of(laid_set: LaidSet, skill: str) -> tuple[Route, ...]:
    """Each Route of the skill, in their order; none for a name that isn't a skill of the laid
    set."""
    return tuple(route for route in laid_set.routes if route.skill == skill)


def lanes_of(laid_set: LaidSet, role: str) -> tuple[Lane, ...]:
    """Each Lane of the role, in the order of its steps; none for a role that no Lane names."""
    return tuple(sorted((lane for lane in laid_set.lanes if lane.role == role), key=_step))


def _step(lane: Lane) -> int:
    return lane.step
