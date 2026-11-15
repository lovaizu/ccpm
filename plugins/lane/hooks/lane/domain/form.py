"""The form of Lanes, Routes, adapters, and the Laid, as lanes.json and a Proposal hold them, which
lanes.schema.json beside this file states."""

from __future__ import annotations

import functools
import json
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal, Union

# The values a Lane's type takes, by the names that its type's module gives as `ARGS`, such as the
# `commands` that a run_only Lane allows.
Args = Mapping[str, Union[str, Sequence[str]]]


SCHEMA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lanes.schema.json")


class OutOfForm(Exception):
    """A lanes.json or a Proposal that lanes.schema.json doesn't take, with each place that's out of
    form and what the form takes there."""

    def __init__(self, problems: Sequence[str]) -> None:
        super().__init__("\n".join(problems))
        self.problems = tuple(problems)


@dataclass(frozen=True)
class Lane:
    """A rule of one lane type on one Step: the role whose Step it is, the file and the number of
    the Step, the lane type by its name, and the values its type takes."""

    role: str
    file: str
    step: int
    type: str
    args: Args


@dataclass(frozen=True)
class After:
    """What a Route goes after: the skill's start (`first`), a Result that a role gave (`result`), a
    command that the person types (`command`), or another plugin's run that a move called, once it
    hands its work back (`returned`)."""

    kind: Literal["first", "result", "command", "returned"]
    role: str | None = None
    result: str | None = None
    command: str | None = None
    skill: str | None = None


# Each kind of Move.
MoveKind = Literal["start", "resume", "wait", "no_more", "call"]


@dataclass(frozen=True)
class Move:
    """One move that a Route makes due: start a subagent, resume one by SendMessage, wait for the
    person's reply or the command they type, start no more by the skill's own Result, or call
    another plugin's skill."""

    kind: MoveKind
    role: str | None = None
    command: str | None = None
    result: str | None = None
    skill: str | None = None


@dataclass(frozen=True)
class Route:
    """The moves of one skill after what the Route goes after."""

    skill: str
    after: After
    moves: tuple[Move, ...]


@dataclass(frozen=True)
class Adapters:
    """The adapters that lanes.json names, each a path under the plugin's hooks/adapters/: the one
    that gives a start's text, and the one that gives the Kept results."""

    text: str | None
    records: str | None


@dataclass(frozen=True)
class LaidSentence:
    """One sentence that Lane added to a Step, by the Step's file and number."""

    file: str
    step: int
    text: str


@dataclass(frozen=True)
class Laid:
    """What Lane added to the plugin: the version of the Lane that laid it, and each sentence it
    added to a Step. Every version keeps these fields and those of LaidSentence, as a later
    lay.py reads them through the copy of this code that laid them."""

    version: str
    sentences: tuple[LaidSentence, ...]


@dataclass(frozen=True)
class Proposal:
    """The Lanes, the Routes, and the adapters that up proposes for one plugin."""

    lanes: tuple[Lane, ...]
    routes: tuple[Route, ...]
    adapters: Adapters


@dataclass(frozen=True)
class LanesFile:
    """lanes.json: the approved Proposal as laid, and the Laid."""

    proposal: Proposal
    laid: Laid


def proposal_form() -> dict[str, Any]:
    """The form of a Proposal, as a JSON Schema, which lay.py types gives up.

    Takes: nothing.
    Gives: the JSON Schema of a Proposal, taken from lanes.schema.json.
    Changes: nothing.
    Refuses: nothing; a lanes.schema.json that can't be read is a fault of Lane's own folder.
    Carries: S1 `L-->>UP: the types, and the form of a Proposal`.
    """
    schema = _schema()
    return {**schema["definitions"]["proposal"], "definitions": schema["definitions"]}


def read_proposal(text: str) -> Proposal:
    """The Proposal that up wrote, read from its JSON.

    Takes: the JSON text of a Proposal, as up hands it to lay.py print.
    Gives: the Proposal.
    Changes: nothing.
    Refuses: OutOfForm, where the text isn't JSON or lanes.schema.json doesn't take it, so that up
    mends the Proposal.
    Carries: S1 `UP->>L: print (Proposal)`.
    """
    held = _held(text, "the Proposal")
    _check(held, _schema()["definitions"]["proposal"])
    return _proposal(held)


def read_lanes(path: str) -> LanesFile:
    """lanes.json, read in the form of this Lane's code.

    Takes: the path of a plugin's hooks/lanes.json.
    Gives: the Lanes, Routes, adapters, and Laid it holds.
    Changes: nothing.
    Refuses: OutOfForm, where the file isn't in the form, and FileNotFoundError, where it isn't
    there, so that the guard says it can't check and who must fix it.
    Carries: the guard's reading of the Lanes and Routes on each event of S1 to S7, and S4 `L->>LS:
    reads the Laid by the guard's code in its hooks/lane/`, as the plugin's copy of this code
    reads it for a later lay.py.
    """
    with open(path, encoding="utf-8") as f:
        held = _held(f.read(), path)
    _check(held, _schema())
    return LanesFile(_proposal(held), _laid(held["laid"]))


def write_lanes(path: str, lanes: LanesFile) -> None:
    """Writes lanes.json whole, in the form of this Lane's code.

    Takes: the path of the plugin's hooks/lanes.json, and what it is to hold.
    Gives: nothing.
    Changes: the file, replaced at once.
    Refuses: OSError, where the file can't be written, so that lay.py write puts back each file it
    changed.
    Carries: S2 `L->>G: writes lanes.json through the guard's code`.
    """
    held = {**_proposal_json(lanes.proposal), "laid": _laid_json(lanes.laid)}
    staged = f"{path}.{os.getpid()}"
    try:
        with open(staged, "w", encoding="utf-8") as f:
            f.write(json.dumps(held, indent=2) + "\n")
        os.replace(staged, path)
    finally:
        if os.path.exists(staged):
            os.remove(staged)


def proposal_text(proposal: Proposal) -> str:
    """The Proposal as JSON, in the form that read_proposal reads back.

    Takes: a Proposal.
    Gives: its JSON text.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `L->>P: keeps the Proposal by its ID`, as proposals.py keeps it.
    """
    return json.dumps(_proposal_json(proposal))


# How the JSON of lanes.json and a Proposal is read and held to lanes.schema.json: the keywords
# that the schema uses, $ref to its definitions, oneOf, anyOf, type, const, required, properties,
# additionalProperties, items, minLength, minimum, and minItems, as a laid plugin runs on Python's
# standard library alone.

_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
}


@functools.cache
def _schema() -> dict[str, Any]:
    with open(SCHEMA, encoding="utf-8") as f:
        return json.load(f)


def _held(text: str, what: str) -> Any:
    try:
        return json.loads(text)
    except ValueError as e:
        raise OutOfForm([f"{what} isn't JSON: {e}"]) from e


def _check(value: Any, schema: Mapping[str, Any]) -> None:
    problems = _problems(value, schema, "$")
    if problems:
        raise OutOfForm(problems)


def _problems(value: Any, schema: Mapping[str, Any], where: str) -> list[str]:
    """Each place where the value falls out of the schema, with what the form takes there."""
    if "$ref" in schema:
        schema = _schema()["definitions"][schema["$ref"].rsplit("/", 1)[-1]]
    for key, fitting in (("oneOf", lambda n: n == 1), ("anyOf", lambda n: n >= 1)):
        if key in schema:
            fits = [s for s in schema[key] if not _problems(value, s, where)]
            return [] if fitting(len(fits)) else [f"{where}: takes one of {_shapes(schema[key])}"]
    problem = _scalar_problem(value, schema)
    if problem:
        return [f"{where}: {problem}, not {json.dumps(value)[:40]}"]
    if isinstance(value, dict):
        return _object_problems(value, schema, where)
    if isinstance(value, list) and "items" in schema:
        return [
            p for i, v in enumerate(value) for p in _problems(v, schema["items"], f"{where}[{i}]")
        ]
    return []


def _scalar_problem(value: Any, schema: Mapping[str, Any]) -> str | None:
    """What the value lacks of the schema's type and bounds, the first found, or None."""
    kind = schema.get("type")
    whole = isinstance(value, int) and not isinstance(value, bool)
    checks = (
        (kind == "integer" and not whole, "must be a whole number"),
        (
            kind in _TYPES and not isinstance(value, _TYPES.get(str(kind), object)),
            f"must be of the type {kind}",
        ),
        (
            "const" in schema and value != schema.get("const"),
            f"must be {json.dumps(schema.get('const'))}",
        ),
        (isinstance(value, str) and len(value) < schema.get("minLength", 0), "must not be empty"),
        (isinstance(value, list) and len(value) < schema.get("minItems", 0), "must hold an item"),
        (
            whole and value < schema.get("minimum", value),
            f"must be at least {schema.get('minimum')}",
        ),
    )
    return next((said for broken, said in checks if broken), None)


def _object_problems(value: dict[str, Any], schema: Mapping[str, Any], where: str) -> list[str]:
    found = [f"{where}: lacks `{key}`" for key in schema.get("required", []) if key not in value]
    properties = schema.get("properties", {})
    extra = schema.get("additionalProperties", True)
    for key, each in value.items():
        if key in properties:
            found += _problems(each, properties[key], f"{where}.{key}")
        elif extra is False:
            found.append(f"{where}: takes no `{key}`, only {', '.join(properties) or 'nothing'}")
        elif isinstance(extra, dict):
            found += _problems(each, extra, f"{where}.{key}")
    return found


def _shapes(schemas: Sequence[Mapping[str, Any]]) -> str:
    """The forms of oneOf or anyOf, each by its required keys or its type, as a message names
    them."""
    return " or ".join(
        "{" + ", ".join(s["required"]) + "}" if "required" in s else str(s.get("type"))
        for s in schemas
    )


# Lanes, Routes, and adapters, from their JSON and back.

# Each kind of Move, by its key in JSON, with the field of Move that its value fills.
_MOVES: dict[MoveKind, str] = {
    "start": "role",
    "resume": "role",
    "wait": "command",
    "no_more": "result",
    "call": "skill",
}


def _proposal(held: Mapping[str, Any]) -> Proposal:
    lanes = tuple(
        Lane(x["role"], x["file"], x["step"], x["type"], dict(x["args"])) for x in held["lanes"]
    )
    routes = tuple(
        Route(x["skill"], _after(x["after"]), tuple(_move(m) for m in x["moves"]))
        for x in held["routes"]
    )
    adapters = held["adapters"]
    return Proposal(lanes, routes, Adapters(adapters.get("text"), adapters.get("records")))


def _after(held: Mapping[str, Any]) -> After:
    if "first" in held:
        return After("first")
    if "command" in held:
        return After("command", command=held["command"])
    if "returned" in held:
        return After("returned", skill=held["returned"])
    return After("result", role=held["role"], result=held["result"])


def _move(held: Mapping[str, str]) -> Move:
    ((key, value),) = held.items()
    kind = next(each for each in _MOVES if each == key)
    return Move(kind, **{_MOVES[kind]: value})


def _laid(held: Mapping[str, Any]) -> Laid:
    sentences = tuple(LaidSentence(x["file"], x["step"], x["text"]) for x in held["sentences"])
    return Laid(held["version"], sentences)


def _proposal_json(proposal: Proposal) -> dict[str, Any]:
    adapters = {"text": proposal.adapters.text, "records": proposal.adapters.records}
    return {
        "lanes": [
            {"role": x.role, "file": x.file, "step": x.step, "type": x.type, "args": dict(x.args)}
            for x in proposal.lanes
        ],
        "routes": [
            {
                "skill": x.skill,
                "after": _after_json(x.after),
                "moves": [{m.kind: getattr(m, _MOVES[m.kind])} for m in x.moves],
            }
            for x in proposal.routes
        ],
        "adapters": {k: v for k, v in adapters.items() if v is not None},
    }


def _after_json(after: After) -> dict[str, Any]:
    if after.kind == "first":
        return {"first": True}
    if after.kind == "command":
        return {"command": after.command}
    if after.kind == "returned":
        return {"returned": after.skill}
    return {"role": after.role, "result": after.result}


def _laid_json(laid: Laid) -> dict[str, Any]:
    sentences = [{"file": x.file, "step": x.step, "text": x.text} for x in laid.sentences]
    return {"version": laid.version, "sentences": sentences}
