"""Decides the form of a plugin's laid set, `hooks/lanes.json`: the Lanes, the Routes, the adapters,
and the Laid, as `lay.py write` writes it and the guard reads it on each hook event."""

from __future__ import annotations

from dataclasses import dataclass, field

# The kinds of a move after the start of a Run, a Result, or a command the person types.
START, RESUME, WAIT, NO_MORE = "start", "resume", "wait", "no_more"


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
    """One move of a Route: `kind` is START, RESUME, WAIT, or NO_MORE, `role` the role that a start
    or a resume names, and `waits_for` the command, such as `/changelog:approve`, that the person
    types before the move is due, or "" for a move due at once. A WAIT waits for no command."""

    kind: str
    role: str = ""
    waits_for: str = ""


@dataclass(frozen=True)
class Route:
    """The moves of one skill after one moment: `skill` is the skill whose Run the Route moves,
    `after` is `first` for the start of its Run, `<role> <result>` for a Result, or the command the
    person types, such as `/changelog:pause`. One move is the move due, and several are those among
    which the skill's steps choose."""

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
    raise NotImplementedError("laid_set.dumps")


def loads(text: str, path: str) -> LaidSet:
    """The laid set of the JSON text read from the file at `path`. Raises Fault, naming the path and
    what isn't in the form, with `the plugin's maker` to fix it by running `/lane:up` again, where
    the text isn't a laid set."""
    raise NotImplementedError("laid_set.loads")


def load(plugin_root: str) -> LaidSet | None:
    """The laid set of the plugin in the folder, or None where it has no `hooks/lanes.json`. Raises
    Fault as `loads` does."""
    raise NotImplementedError("laid_set.load")


def routes_of(laid_set: LaidSet, skill: str) -> tuple[Route, ...]:
    """Each Route of the skill, in their order; none for a name that isn't a skill of the laid
    set."""
    raise NotImplementedError("laid_set.routes_of")


def lanes_of(laid_set: LaidSet, role: str) -> tuple[Lane, ...]:
    """Each Lane of the role, in the order of its steps; none for a role that no Lane names."""
    raise NotImplementedError("laid_set.lanes_of")
