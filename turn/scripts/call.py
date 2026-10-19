"""The call checked and each kind it names taken from the CCS, so that no AI copies a value and a run
starts only on what it can make the work from."""

import json
import os
import re
from typing import Any

SHAPE = (
    '{"ccs": "<path>", "kind": {"work": "<kind>", "checklist": "<kind>", "receiver": "<kind>",'
    ' "use": "<kind>", "opens": "<kind>"}, "result": "<path>"}'
)
REQUIRED = ("work", "checklist", "receiver")
KINDS = REQUIRED + ("use", "opens")
# An item of a checklist is a heading of the form `### B-1: <title>`, outside a fence, with the
# line under it saying where in the work it is answered.
ITEM = re.compile(r"^### ([A-Z]+-\d+): ")
SCOPES = ("its part", "each part", "whole")
EACH = "each part"


class Stop(Exception):
    """What was wrong, and what to give instead."""


def parse(text: str) -> dict[str, Any]:
    """The call as JSON; stops when it is not a JSON object."""
    try:
        call = json.loads(text)
    except ValueError:
        call = None
    if not isinstance(call, dict):
        raise Stop(f"turn: the call is not JSON; give it as {SHAPE}, the last two kinds optional")
    return call


def check(call: dict[str, Any]) -> dict[str, Any]:
    """The run the call asks for: the call, each kind's entries, the checklists' items, the files
    the orchestrator and the generator are given, and those the first user and the evaluator are
    shown, as the receiver has them; stops at the first thing turn cannot take."""
    unknown = sorted(set(call) - {"ccs", "kind", "result"})
    if unknown:
        raise Stop(
            f'turn: the call holds "{unknown[0]}", which turn does not take; it takes'
            f' "ccs", "kind" and "result": {SHAPE}'
        )
    for key in ("ccs", "kind", "result"):
        if key not in call:
            raise Stop(f'turn: the call has no "{key}"; give it as {SHAPE}')
    kind = call["kind"]
    if not isinstance(kind, dict):
        raise Stop(f'turn: the call\'s "kind" is not an object; give it as {SHAPE}')
    for name in sorted(set(kind) - set(KINDS)):
        raise Stop(
            f'turn: the call names the kind of "{name}", which turn does not take; it takes'
            ' "work", "checklist" and "receiver", and may take "use" and "opens"'
        )
    for name in REQUIRED:
        if name not in kind:
            raise Stop(f'turn: the call names no kind for "{name}"; give it as {SHAPE}')
    for name, value in kind.items():
        if not isinstance(value, str):
            raise Stop(f'turn: the kind for "{name}" is not a name; give the kind as a string')
    ccs = read_ccs(call["ccs"])
    run: dict[str, Any] = {"call": call}
    for name in KINDS:
        values = entries(ccs, kind[name]) if name in kind else []
        if name in REQUIRED and not values:
            raise Stop(
                f'turn: {call["ccs"]} has no entry of the kind "{kind[name]}", which the call'
                f' names for "{name}"; add one to the CCS, or name the kind it uses'
            )
        run[name] = values
    for path in run["checklist"] + run["opens"]:
        if not os.path.isfile(path):
            raise Stop(f"turn: {path}, named in {call['ccs']}, is not there; fix its entry")
    scoped = [item for path in run["checklist"] for item in items(path)]
    run["items"] = [{"checklist": c, "item": i} for c, i, _ in scoped]
    run["each"] = [{"checklist": c, "item": i} for c, i, scope in scoped if scope in (EACH,)]
    run["given"] = given(call["ccs"], ccs, run["work"])
    run["shown"] = run["work"] + run["opens"] + run["checklist"]
    return run


def read_ccs(path: str) -> dict[str, list[dict[str, str]]]:
    """The CCS at the path; stops when it is not parts, each a list of entries, each one kind and
    its value."""
    form = (
        f"turn: {path} is not a CCS; a CCS is a JSON object of parts, each a list of entries,"
        ' each one kind and its value as text, such as {"focal_entities": [{"deliverable":'
        ' "README.md"}]}'
    )
    if not os.path.isfile(path):
        raise Stop(f"turn: the CCS {path} is not there; give the path of the CCS")
    try:
        with open(path, encoding="utf-8") as f:
            ccs = json.load(f)
    except ValueError:
        raise Stop(form) from None
    entries_ok = isinstance(ccs, dict) and all(
        isinstance(part, list)
        and all(
            isinstance(e, dict) and len(e) == 1 and isinstance(next(iter(e.values())), str)
            for e in part
        )
        for part in ccs.values()
    )
    if not entries_ok:
        raise Stop(form)
    return ccs


def entries(ccs: dict[str, list[dict[str, str]]], kind: str) -> list[str]:
    """Every value of the kind, in the order of the CCS."""
    return [e[kind] for part in ccs.values() for e in part if kind in e]


def items(path: str) -> list[tuple[str, str, str]]:
    """Every item of a checklist, by its path, ID and scope; stops when it holds none, or at an
    item whose scope is not said."""
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    found: list[tuple[str, str, str]] = []
    fenced = False
    for n, line in enumerate(lines):
        if line.startswith("```"):
            fenced = not fenced
        heading = None if fenced else ITEM.match(line)
        if heading is None:
            continue
        below = lines[n + 1 : n + 3]
        scope = next((s for s in SCOPES if below == ["", f"Scope: {s}"]), None)
        if scope is None:
            raise Stop(
                f"turn: {path} {heading.group(1)} does not say where it is answered; put the line"
                " `Scope: its part`, `Scope: each part` or `Scope: whole` after a blank line"
                " under its heading"
            )
        found.append((path, heading.group(1), scope))
    if not found:
        raise Stop(f"turn: {path} holds no item, a heading such as `### B-1: <title>`")
    return found


def given(ccs_path: str, ccs: dict[str, list[dict[str, str]]], work: list[str]) -> list[str]:
    """What the roles may read: the CCS, the work and each file or folder an entry names."""
    named = [v for part in ccs.values() for e in part for v in e.values() if os.path.exists(v)]
    found: list[str] = []
    for path in [ccs_path] + work + named:
        if path not in found:
            found.append(path)
    return found
