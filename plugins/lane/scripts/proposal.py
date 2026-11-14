"""Decides whether a Proposal can stand against the lane types, the plugin's Steps, and its files,
and keeps each Proposal shown by its ID with the Steps it came from and the conversation that
showed it, in `<temp>/lane/<yyyymmdd>-<plugin>/`, for the Run of up that showed it, if any: until
the caller approves it, the Steps change, or that Run ends without its approval."""

from __future__ import annotations

import datetime
import glob
import json
import os
import re
import secrets
from collections.abc import Sequence
from dataclasses import asdict, dataclass, replace
from typing import Any

from domain.fault import Fault
from domain.laid_set import Lane, Move, Route
from domain.lanes import type_of
from domain.run_record import Run
from steps import Role, Step, fingerprint

# What the skill's step that the Routes lie on says before its end, so that the main conversation
# starts the subagents that the guard names.
_ROUTES_SENTENCE = "Start each subagent you are told to start, until you are told to start no more."
# Each kind of a move, as proposal.schema.json names them.
_KINDS = ("start", "resume", "call", "wait", "no_more")


@dataclass(frozen=True)
class Proposal:
    """The lanes and the routes proposed from the Steps as they read at one time, the data model's
    Proposal, in the form of `domain/proposal.schema.json`: the plugin, each skill whose call begins
    a run of its own, each Lane with its sentence, each Route of each skill, the adapters named, the
    ID, the fingerprint of the Steps, and the ID of the conversation in which `lay.py print` showed
    it, "" for none."""

    plugin: str
    skills: tuple[str, ...]
    lanes: tuple[Lane, ...]
    routes: tuple[Route, ...]
    text_adapter: str = ""
    results_adapter: str = ""
    id: str = ""
    steps: str = ""
    conversation: str = ""


@dataclass(frozen=True)
class Refusal:
    """Why a Proposal can't stand: each fault, and whether up mends it, or the user mends a file of
    the plugin, such as a subagent's file without `background: true`."""

    faults: tuple[str, ...]
    in_files: bool


def parse(given: Any, where: str) -> Proposal:
    """The Proposal of the JSON value that up wrote to the file at `where`, without sentences, ID,
    or fingerprint. Raises Fault, naming the field and what the form takes, with up to mend it,
    where it isn't in the form of `domain/proposal.schema.json`."""
    whole = _object(given, where, ("plugin", "skills", "lanes", "routes"))
    lanes = tuple(_lane(each, f"{where}: lane {n}") for n, each in enumerate(whole["lanes"], 1))
    routes = tuple(_route(each, f"{where}: route {n}") for n, each in enumerate(whole["routes"], 1))
    return Proposal(
        plugin=_text(whole, "plugin", where),
        skills=tuple(_texts(whole, "skills", where)),
        lanes=lanes,
        routes=routes,
        text_adapter=_text(whole, "text_adapter", where, ""),
        results_adapter=_text(whole, "results_adapter", where, ""),
    )


def _wrong(where: str, what: str) -> Fault:
    return Fault(f"{where} {what}, as domain/proposal.schema.json gives the form", "up")


def _object(given: Any, where: str, required: Sequence[str]) -> dict[str, Any]:
    if not isinstance(given, dict):
        raise _wrong(where, "isn't a JSON object")
    missing = [f"`{name}`" for name in required if name not in given]
    if missing:
        raise _wrong(where, "lacks " + ", ".join(missing))
    return given


def _text(given: dict[str, Any], name: str, where: str, default: str | None = None) -> str:
    value = given.get(name, default)
    if not isinstance(value, str):
        raise _wrong(where, f"holds `{name}` that isn't text")
    return value


def _texts(given: dict[str, Any], name: str, where: str) -> list[str]:
    value = given[name]
    if not isinstance(value, list) or not all(isinstance(each, str) for each in value):
        raise _wrong(where, f"holds `{name}` that isn't a list of text")
    return value


def _lane(given: Any, where: str) -> Lane:
    lane = _object(given, where, ("role", "step", "type", "takes"))
    step = lane["step"]
    if not isinstance(step, int) or isinstance(step, bool) or step < 1:
        raise _wrong(where, "holds `step` that isn't a whole number from 1")
    takes = tuple(_texts(lane, "takes", where))
    return Lane(_text(lane, "role", where), step, "", _text(lane, "type", where), takes, "")


def _route(given: Any, where: str) -> Route:
    route = _object(given, where, ("skill", "after", "moves"))
    moves = route["moves"]
    if not isinstance(moves, list) or not moves:
        raise _wrong(where, "holds `moves` that isn't a list of one move or more")
    return Route(
        _text(route, "skill", where),
        _text(route, "after", where),
        tuple(_move(each, f"{where}, move {n}") for n, each in enumerate(moves, 1)),
    )


def _move(given: Any, where: str) -> Move:
    move = _object(given, where, ("kind",))
    kind = _text(move, "kind", where)
    if kind not in _KINDS:
        raise _wrong(where, f"holds the kind `{kind}`, not one of {', '.join(_KINDS)}")
    return Move(kind, _text(move, "role", where, ""), _text(move, "waits_for", where, ""))


def check(proposal: Proposal, found: Sequence[Role], plugin_root: str) -> Refusal | None:
    """Why the Proposal can't stand, or None where it can: each Lane of a type there is, on a Step
    there is, taking what its type takes; each skill a skill of the plugin, with a Route `first`,
    and each Route of a skill of the Proposal; each Role reached by the Routes and each Result named
    by a Route; each subagent's file setting `background: true`; each command that a Route waits for
    or goes after setting `disable-model-invocation: true`; each program in `hooks/adapters/` named;
    and no two Roles taking their Steps from one file."""
    faults = [fault for lane in proposal.lanes for fault in _lane_faults(proposal, lane, found)]
    return Refusal(tuple(faults), False) if faults else None


def _step(found: Sequence[Role], lane: Lane) -> Step | None:
    steps = [step for role in found if role.name == lane.role for step in role.steps]
    return next((step for step in steps if step.number == lane.step), None)


def _lane_faults(proposal: Proposal, lane: Lane, found: Sequence[Role]) -> list[str]:
    try:
        lane_type = type_of(lane.type)
    except Fault as fault:
        return [fault.why]
    if _step(found, lane) is None:
        return [f"the lane of {lane.role} on step {lane.step} lies on a step that isn't there"]
    faults = lane_type.faults(lane.role, lane.takes, lane.role in proposal.skills)
    return [f"the lane of {lane.role} on step {lane.step}: {fault}" for fault in faults]


def moves_of(proposal: Proposal, skill: str, after: str) -> tuple[Move, ...]:
    """The moves of the skill's Route after the moment, none where no Route of it goes after it."""
    raise NotImplementedError("proposal.moves_of")


def keep(proposal: Proposal, found: Sequence[Role], temp: str, conversation: str = "") -> Proposal:
    """Keeps the Proposal, with the sentence of each Lane made by its type, the fingerprint of the
    Roles' Steps it came from, and the ID of the conversation that showed it, "" for none, under a
    new ID of 8 hex digits, and gives it with its ID."""
    lanes = tuple(
        replace(lane, file=_file(found, lane), sentence=_sentence(proposal, lane))
        for lane in proposal.lanes
    )
    given = replace(
        proposal,
        lanes=lanes,
        id=secrets.token_hex(4),
        steps=fingerprint(found),
        conversation=conversation,
    )
    day = datetime.date.today().strftime("%Y%m%d")
    path = os.path.join(temp, "lane", f"{day}-{given.plugin}", f"{given.id}.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(asdict(given), f)
    return given


def _file(found: Sequence[Role], lane: Lane) -> str:
    step = _step(found, lane)
    if step is None:
        raise Fault(f"{lane.role} has no step {lane.step}", "up")
    return step.file


def _sentence(proposal: Proposal, lane: Lane) -> str:
    sentence = type_of(lane.type).sentence(lane.role, lane.takes)
    if lane.role in proposal.skills and lane.type == "gives_result":
        return f"{_ROUTES_SENTENCE} {sentence}"
    return sentence


def kept(temp: str, plugin: str, id: str) -> Proposal | None:
    """The Proposal kept for the plugin under the ID, or None where none is."""
    folder = os.path.join(glob.escape(temp), "lane", f"*-{glob.escape(plugin)}")
    found = sorted(glob.glob(os.path.join(folder, f"{glob.escape(id)}.json")))
    if not found:
        return None
    with open(found[-1], encoding="utf-8") as f:
        given = json.load(f)
    return Proposal(
        plugin=given["plugin"],
        skills=tuple(given["skills"]),
        lanes=tuple(
            Lane(l["role"], l["step"], l["file"], l["type"], tuple(l["takes"]), l["sentence"])
            for l in given["lanes"]
        ),
        routes=tuple(
            Route(each["skill"], each["after"], tuple(Move(**m) for m in each["moves"]))
            for each in given["routes"]
        ),
        text_adapter=given["text_adapter"],
        results_adapter=given["results_adapter"],
        id=given["id"],
        steps=given["steps"],
        conversation=given["conversation"],
    )


def role_order(proposal: Proposal) -> list[str]:
    """Each role of the Proposal in the order that `lay.py` shows and lays them: each skill, then
    each subagent that a Lane names, in the order of its first Lane."""
    named = [lane.role for lane in proposal.lanes if lane.role not in proposal.skills]
    return [*proposal.skills, *dict.fromkeys(named)]


def waits(proposal: Proposal, run: Run | None) -> bool:
    """Whether the Proposal can still be laid as far as the Run of up that showed it goes, given
    the Run of up of the conversation that showed it, None where that conversation has none: true
    where it has none, as no Run of up showed the Proposal, or where its Run goes on and showed this
    Proposal last; false where that Run ended, or showed another Proposal since, as a later Run of
    up in the same conversation does."""
    if run is None:
        return True
    shown = re.search(rf"^ID: {re.escape(proposal.id)}$", run.shown, re.MULTILINE)
    return not run.ended and shown is not None
