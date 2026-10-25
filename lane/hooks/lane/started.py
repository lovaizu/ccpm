"""What a subagent started from, for a lane taking a thing given for each run, written
`{<name>}` in its step, such as `{work}`: the value under that name in the JSON the subagent starts
from, its prompt where it is a JSON object and each JSON object a script laid by start_with prints,
the later over the earlier. A list stands for each of its texts, a text for itself; a value of
another kind gives nothing. The JSON a subagent starts from is the one place a plugin hands it the
files of its run, so a lane reads them there, the same way in every plugin."""

from __future__ import annotations

import itertools
import json
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


def values(texts: list[str]) -> dict[str, list[str]]:
    """The run's value of each name the JSON objects in the texts give, the later over the earlier,
    as the texts it stands for."""
    merged: dict[str, Any] = {}
    for text in texts:
        for given in objects(text):
            merged.update(given)
    found = {name: texts_of(value) for name, value in merged.items()}
    return {name: value for name, value in found.items() if value is not None}


def objects(text: str) -> list[dict[str, Any]]:
    """The JSON objects the text holds: the text itself where it is one JSON value, however many
    lines it is printed over; otherwise each line that is one, as a script may print lines of its
    own before it."""
    try:
        each = [json.loads(text)]
    except ValueError:
        each = [loaded(line) for line in text.splitlines()]
    return [o for o in each if isinstance(o, dict)]


def loaded(line: str) -> Any:
    """The JSON value the line is; None where it is none."""
    try:
        return json.loads(line)
    except ValueError:
        return None


def texts_of(value: Any) -> list[str] | None:
    """The texts a value stands for: a text itself, a list its texts; None for a value of another
    kind, which gives a lane nothing to hold to."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [v for v in value if isinstance(v, str)]
    return None


def resolved(takes: list[str], run: dict[str, list[str]], alone: int) -> list[list[str]]:
    """Each list of things the lane is checked on, the run's texts put in for each take given for
    each run: in one of the first `alone` places, each of which takes one thing, the lane is checked
    once for each text, so an output given as a list is held one by one; in a place taking the rest,
    the texts stand side by side."""
    places = []
    for at, take in enumerate(takes):
        named = NAMED.fullmatch(take)
        texts = run[named["name"]] if named else [take]
        places.append([[t] for t in texts] if at < alone else [texts])
    return [list(itertools.chain(*each)) for each in itertools.product(*places)]


def told(name: str, texts: list[str]) -> str:
    """The line telling the subagent the run's value of the name, after the sentence that shows the
    name as its step says it."""
    listed = ", ".join(f"`{t}`" for t in texts) or "an empty list"
    return f"`{{{name}}}` is {listed}."
