"""How a start's text and the Kept results come from the user's plugin: the adapter that lanes.json
names, run in the hook event's cwd, what it's handed, and how its output is read, with Lane's own
text where the plugin names no adapter of a start's text."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

# The text a start goes with where the plugin names no adapter of a start's text.
TEXT = "Carry out your steps"


class AdapterFailed(Exception):
    """An adapter that exited other than 0, printed what isn't in its form, or couldn't run, with
    why, so that the guard says who must fix it."""


@dataclass(frozen=True)
class StartText:
    """A start's text, and the run values that the role's Lanes hold it to."""

    text: str
    values: Mapping[str, str]


@dataclass(frozen=True)
class Running:
    """A Start of the Run that runs, as the adapter is handed it."""

    role: str
    text: str
    values: Mapping[str, str]


@dataclass(frozen=True)
class KeptResult:
    """One Result that the user's plugin keeps in its own records, by the role that gave it."""

    role: str
    result: str


def start_text(
    program: str | None, role: str, running: Sequence[Running], words: str, cwd: str
) -> StartText:
    """The text and run values of one start due.

    Takes: the adapter of a start's text that lanes.json names, or None; the role due; the text and
    values of each Start of the Run that runs; the words typed after the skill's command; and the
    hook event's cwd.
    Gives: what the adapter prints, `{"text": ..., "values": {<name>: <value>}}`, its values
    optional, given the role as its one argument and `{"running": [{"role": ..., "text": ...,
    "values": {...}}]}` on standard input; or, with no adapter, Lane's text, `Carry out your
    steps`, and the words typed, with no values.
    Changes: nothing of Lane's; the adapter may read the plugin's files.
    Refuses: AdapterFailed.
    Carries: S5 `G->>A: asks for the text of each start due, with each Start that runs`, and its
    `A-->>G` answers.
    """
    if program is None:
        return StartText(f"{TEXT}: {words}" if words else TEXT, {})
    raise NotImplementedError("adapters.start_text, of an adapter")


def kept_results(program: str, words: str, cwd: str) -> tuple[KeptResult, ...]:
    """The Results that the user's plugin keeps, in the order the run gave them.

    Takes: the adapter of the plugin's records that lanes.json names, the words typed after the
    skill's command, and the hook event's cwd.
    Gives: the Results of what the adapter prints, `{"results": [{"role": ..., "result": ...}]}`,
    given no argument and `{"words": <the words>}` on standard input, as words that begin with `-`
    would read as an option where they came as an argument; none where it gives none.
    Changes: nothing of Lane's.
    Refuses: AdapterFailed.
    Carries: S7 `G->>A: asks for the Kept results, with those words`.
    """
    raise NotImplementedError("adapters.kept_results")
