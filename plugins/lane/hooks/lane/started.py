"""What a subagent is given, for a lane taking a thing given for each run, written `{<name>}` in its
step, such as `{work}`: the texts it started from, its prompt and what each script laid by
start_with printed, and each message sent to it after its start, whose values the values port
reads, as ports.py says; those values put in the places of a lane's sentence, and told. A plugin
hands a subagent the files of its run in the JSON it starts from, and in a message sent to it
after where they grow while it works, as when an answer adds a file; so a lane reads them there,
the same way in every plugin, and the subagent goes on rather than being started again, spending
again what it had read."""

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
    """The texts a subagent was given, read from the entries found of its record, made in the
    folder, in the order the record holds them: its prompt and each message sent to it after, as
    record.message reads them, and what each call the runs function holds to run a script laid by
    start_with gave back, at the entry it was used in; None where its record is not found, as what
    it was given is then not known."""
    if found is None:
        return None
    sent = [(n, m) for n, entry in enumerate(found) for m in record.message(entry)]
    printed = [(n, d.result) for n, d in record.done_at(found, cwd) if runs(call.made(d))]
    # Sorted by the entry alone, so the prints of tools used in one entry keep their order; no entry
    # both brings a message, a user entry of text, and uses a tool, an assistant entry.
    return [t for _, t in sorted([*sent, *printed], key=lambda placed: placed[0])]


def held(named: list[str], run: dict[str, list[str] | None]) -> dict[str, list[str]] | None:
    """The run's texts of each name a lane takes, an empty text left out; None where the run gives
    one of them as null, the caller saying there is none, so the lane lets the call or the end
    through on that run, as every lane taking that name does."""
    if any(n in run and run[n] is None for n in named):
        return None
    return {n: [t for t in v if t] for n in named if (v := run.get(n)) is not None}


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
