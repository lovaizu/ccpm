"""The call checked and each kind it names taken from the CCS, so that no AI copies a value and a run
starts only on what it can make the work from."""

from __future__ import annotations

import json
import os
import re
from typing import Any

import forms
import template

SHAPE = (
    '{"ccs": "<path>", "kind": {"work": "<kind>", "checklist": "<kind>", "receiver": "<kind>",'
    ' "use": "<kind>", "has": "<kind>"}, "result": "<path>"}'
)
# The call's keys whose value is a path.
PLACES = ("ccs", "result")
# The kinds whose entries are paths, kept without a trailing slash or a `./`, so a file inside a
# folder named `docs/` is found within `docs`.
PATHS = ("work", "checklist", "has")
KINDS = ("work", "checklist", "receiver", "use", "has")
# An item of a checklist is a heading of the form `### B-1: <title>`, outside a fence, with the
# line under it saying where in the work it is answered.
LEVEL = 3
ITEM = re.compile(r"([A-Z]+-\d+): ")
SCOPES = ("its part", "each part", "whole")


class Stop(Exception):
    """What was wrong, and what to give instead."""


def parse(text: str) -> dict[str, Any]:
    """The call as JSON; stops when it is not a JSON object."""
    try:
        given = json.loads(text)
    except ValueError:
        given = None
    if not isinstance(given, dict):
        raise Stop(f"turn: the call is not JSON; give it as {SHAPE}")
    return given


def checked(given: dict[str, Any]) -> dict[str, Any]:
    """The call, its keys and kinds as turn takes them, each path and kind a name; stops at the
    first thing turn cannot take."""
    unknown = sorted(set(given) - {"ccs", "kind", "result"})
    if unknown:
        raise Stop(
            f'turn: the call holds "{unknown[0]}", which turn does not take; it takes'
            f' "ccs", "kind" and "result": {SHAPE}'
        )
    for key in ("ccs", "kind", "result"):
        if key not in given:
            raise Stop(f'turn: the call has no "{key}"; give it as {SHAPE}')
    for key in PLACES:
        if not forms.worded(given[key]):
            raise Stop(f'turn: the call\'s "{key}" is not a path; give it as {SHAPE}')
    kind = given["kind"]
    if not isinstance(kind, dict):
        raise Stop(f'turn: the call\'s "kind" is not an object; give it as {SHAPE}')
    unknown = sorted(set(kind) - set(KINDS))
    if unknown:
        raise Stop(
            f'turn: the call names the kind of "{unknown[0]}", which turn does not take; it takes'
            ' "work", "checklist", "receiver", "use" and "has"'
        )
    for name in KINDS:
        if name not in kind:
            raise Stop(f'turn: the call names no kind for "{name}"; give it as {SHAPE}')
    for name, value in kind.items():
        if not isinstance(value, str):
            raise Stop(f'turn: the kind for "{name}" is not a name; give the kind as a string')
    return given


def laid_out(given: dict[str, Any]) -> dict[str, Any]:
    """The run the call asks for, laid out from the CCS as it is now: the call, each kind's
    entries, the checklists' items, those asked of each part, the files the orchestrator and the
    generator are given, and those the first user may read, as the receiver has them; stops at the
    first thing turn cannot take."""
    asked = checked(given)
    ccs = read_ccs(asked["ccs"])
    run: dict[str, Any] = {"call": asked}
    for name in KINDS:
        values = entries(ccs, asked["kind"][name])
        if name in PATHS:
            values = [os.path.normpath(v) for v in values]
        if not values:
            raise Stop(
                f'turn: {asked["ccs"]} has no entry of the kind "{asked["kind"][name]}", which the'
                f' call names for "{name}"; add one to the CCS, or name the kind it uses'
            )
        run[name] = values
    for path in run["checklist"]:
        if not os.path.isfile(path):
            raise Stop(f"turn: {path}, named in {asked['ccs']}, is not there; fix its entry")
    for path in run["has"]:
        if not os.path.exists(path):
            raise Stop(f"turn: {path}, named in {asked['ccs']}, is not there; fix its entry")
    found = [item for path in run["checklist"] for item in items(path)]
    run["items"] = [forms.named(i) for i in found]
    run["each"] = [
        forms.named(i)
        for i in found
        if i["scope"] == "each part"  # pragma: no mutate
    ]
    run["given"] = given_of(asked["ccs"], ccs, run["work"])
    run["readable"] = run["work"] + run["has"] + run["checklist"]
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


def items(path: str) -> list[dict[str, str]]:
    """Every item of a checklist, by its path, ID and scope; stops when it holds none, or at an
    item whose scope is not said."""
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    found: list[dict[str, str]] = []
    for number, level, text in template.headings(lines, template.body(lines)):
        heading = ITEM.match(text)
        if (
            level != LEVEL  # pragma: no mutate
            or heading is None
        ):
            continue
        below = lines[number : number + 2]
        scope = next((s for s in SCOPES if below == ["", f"Scope: {s}"]), None)
        if scope is None:
            raise Stop(
                f"turn: {path} {heading.group(1)} does not say where it is answered; put the line"
                " `Scope: its part`, `Scope: each part` or `Scope: whole` after a blank line"
                " under its heading"
            )
        found.append({"checklist": path, "item": heading.group(1), "scope": scope})
    if not found:
        raise Stop(f"turn: {path} holds no item, a heading such as `### B-1: <title>`")
    return found


def given_of(ccs_path: str, ccs: dict[str, list[dict[str, str]]], work: list[str]) -> list[str]:
    """What the roles may read: the CCS, the work and each file or folder an entry names."""
    named = [
        os.path.normpath(v)
        for part in ccs.values()
        for e in part
        for v in e.values()
        if os.path.exists(v)
    ]
    return list(dict.fromkeys([ccs_path, *work, *named]))
