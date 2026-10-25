"""What a subagent started from, for a lane taking a thing given for each run, written
`{<name>}` in its step, such as `{work}`: the texts the subagent started from, its prompt and what
each script laid by start_with printed, whose values the values port reads, as ports.py says; those
values put in the places of a lane's sentence, and told. The JSON a subagent starts from is the one place a plugin hands it the
files of its run, so a lane reads them there, the same way in every plugin."""

from __future__ import annotations

import itertools
import re
from typing import Any, Callable

import call
import record

# A take given for each run: a name in braces, the braces wrapping the whole take.
NAMED = re.compile(r"\{(?P<name>[^{}]+)\}")


def names(takes: list[str]) -> list[str]:
    """The name of each take given for each run, once each, in the order taken."""
    found = (NAMED.fullmatch(t) for t in takes)
    return list(dict.fromkeys(m["name"] for m in found if m))


def texts(
    found: list[dict[str, Any]] | None, cwd: str, runs: Callable[[call.Call], bool]
) -> list[str] | None:
    """The texts a subagent started from, in order, read from the entries found of its record, made
    in the folder: its prompt, then what each call the runs function holds to run a script laid by
    start_with gave back; None where its record is not found, as what it was given is then not
    known."""
    if found is None:
        return None
    made = [d for d in record.done(found, cwd) if runs(call.made(d))]
    return [record.prompt(found), *(d.result for d in made)]


def put(places: list[list[str]], run: dict[str, list[str]]) -> list[list[str] | None]:
    """The texts in each place of a lane's sentence, the run's texts put in for each take given for
    each run, beside the takes fixed in the step, in the order taken; None for a place where a take
    given for each run is not given."""
    found: list[list[str] | None] = []
    for takes in places:
        named = [NAMED.fullmatch(t) for t in takes]
        given = [run.get(m["name"]) if m else [t] for m, t in zip(named, takes)]
        texts = [t for g in given if g is not None for t in g]
        found.append(None if None in given else texts)
    return found


def resolved(places: list[list[str]], alone: int) -> list[list[str]]:
    """Each list of things the lane is checked on, of the texts in each place: in one of the first
    `alone` places, each of which takes one thing, the lane is checked once for each text, so an
    output given as a list is held one by one; in a place taking the rest, the texts stand side by
    side."""
    each = [*([[t] for t in p] for p in places[:alone]), *([p] for p in places[alone:])]
    return [list(itertools.chain(*e)) for e in itertools.product(*each)]


def told(name: str, texts: list[str]) -> str:
    """The line telling the subagent the run's value of the name, after the sentence that shows the
    name as its step says it."""
    listed = ", ".join(f"`{t}`" for t in texts)
    return f"`{{{name}}}` is {listed}."
