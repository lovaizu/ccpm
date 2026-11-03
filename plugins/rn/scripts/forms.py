"""The forms each role gives its judgments in, each checked against the run's items and the work, so
a slip is named where it is made."""

from __future__ import annotations

import json
import os
import re
from typing import Any, NamedTuple

import parts as work_parts

# Lines of a file, as every form names them: `<path>:<from>-<to>`, or `<path>:<line>` for one.
LINES = re.compile(r"^(.+):(\d+)(?:-(\d+))?$")
# A form given inside a ```json fence, as a model often writes JSON, is the form itself.
FENCE = re.compile(r"^\s*```(?:json)?\s*\n(.*)\n\s*```\s*$", re.DOTALL)
# The roles' form files, each holding the shapes of an item, one choice each, beside the plugin's
# scripts, found from this file as it is, as rn takes it through a link.
FORM_FILES = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "forms")
# The keys every item holds beside its shape, which name it.
NAMING = ("checklist", "item")
# The keys whose value is words, wherever an item holds them.
WORDED = ("need",)


def shapes(path: str) -> tuple[tuple[str, ...], ...]:
    """The shapes of an item the form file at the path takes: the keys each choice of its item
    requires but those that name it, in the order of the choices."""
    with open(path, encoding="utf-8") as f:
        defs = json.load(f)["$defs"]
    choices = [defs[c["$ref"].rpartition("/")[2]] for c in defs["item"]["anyOf"]]
    return tuple(tuple(k for k in c["required"] if k not in NAMING) for c in choices)


class Form(NamedTuple):
    """What an item may hold besides its checklist and ID, one shape of keys each, every item judged
    given; and whether the choices the work rests on are named, as its maker settles points no one
    gave it."""

    shapes: tuple[tuple[str, ...], ...]
    chooses: bool = False


# The generator claims each item it judges, every item or on a mend each item sent to it, at the
# lines that give its Good, and names each choice the work rests on.
CLAIM = Form(shapes(os.path.join(FORM_FILES, "claim.json")), chooses=True)
# The first user gives every item the lines that give its Good, or what the receiver would need to
# get it.
FIRST_READING = Form(shapes(os.path.join(FORM_FILES, "reading.json")))


def named(item: dict[str, Any]) -> dict[str, Any]:
    """The checklist and ID that name an item."""
    return {"checklist": item["checklist"], "item": item["item"]}


def key_of(item: dict[str, Any]) -> tuple[str, Any]:
    """The checklist and ID that name an item, the checklist as the file it is, so a role given the
    checklists' whole paths names the item the CCS names by another."""
    return (os.path.realpath(item["checklist"]), item.get("item"))


def worded(value: Any) -> bool:
    """Whether the value is words, not empty."""
    return isinstance(value, str) and bool(value.strip())


def span(line: Any) -> tuple[str, int, int] | None:
    """The file, as the file it is, and the first and last line that lines name; None where they
    are not written as `<path>:<from>-<to>` or `<path>:<line>`."""
    found = LINES.match(line) if isinstance(line, str) else None
    if not found:
        return None
    first = int(found.group(2))
    return (os.path.realpath(found.group(1)), first, int(found.group(3) or first))


def unfenced(text: str) -> str:
    """The text without the ```json fence around it, if it has one."""
    fenced = FENCE.match(text)
    return fenced.group(1) if fenced else text


def parsed(text: str, lists: tuple[str, ...]) -> dict[str, Any] | None:
    """The reply as JSON, or None when it is not an object of the lists it takes."""
    try:
        data = json.loads(unfenced(text))
    except ValueError:
        return None
    if not isinstance(data, dict) or not all(isinstance(data.get(k), list) for k in lists):
        return None
    return data


def check(
    text: str,
    items: list[dict[str, Any]],
    work: list[str],
    form: Form,
    each: list[dict[str, Any]],
) -> list[str]:
    """What is wrong with a reply of items in the form, each said with what to give instead; empty
    when it is filled. The items are those the form judges, those of them asked of each part of the
    work in `each`."""
    lists = ("items",) + ("chosen",) * form.chooses
    data = parsed(text, lists)
    if data is None:
        return ["give it as JSON: {" + ", ".join(f'"{k}": [...]' for k in lists) + "}"]
    said = item_problems(data["items"], items, work, form, each)
    if form.chooses:
        said += choice_problems(data["chosen"])
    return said


def choice_problems(chosen: list[Any]) -> list[str]:
    """What is wrong with the choices named, each to hold what was chosen and why, in words."""
    return [
        f'choice {n} must hold "chosen" and "why", what was chosen and why, in words'
        for n, choice in enumerate(chosen, 1)
        if not isinstance(choice, dict)
        or set(choice) != {"chosen", "why"}
        or not all(worded(v) for v in choice.values())
    ]


def item_problems(
    given: list[Any],
    items: list[dict[str, Any]],
    work: list[str],
    form: Form,
    each: list[dict[str, Any]],
) -> list[str]:
    """What is wrong with the items given, against the items judged, every one of which is to be
    given."""
    keys = [key_of(i) for i in items]
    of_each = [key_of(i) for i in each]
    said: list[str] = []
    seen: list[tuple[str, Any]] = []
    for item in given:
        known = isinstance(item, dict) and isinstance(item.get("checklist"), str)
        key = key_of(item) if known else None
        name = f"{item['checklist']} {item.get('item')}" if known else json.dumps(item)
        if key not in keys:
            said.append(f"{name} is not an item judged here; give each item by its checklist")
            continue
        if key in seen:
            said.append(f"{name} is given twice; give each item once")
            continue
        seen.append(key)
        held = [s for s in form.shapes if all(k in item for k in s)]
        shaped = [k for s in held for k in s]
        rest = [k for k in item if k not in NAMING and k not in shaped]
        if len(held) != 1 or rest:
            said.append(f"{name} must hold {allowed(form.shapes)}")
            continue
        said += value_problems(name, item, work, key in of_each)
    return said + [
        f"{i['checklist']} {i['item']} is left out; give every item judged here"
        for i in items
        if key_of(i) not in seen
    ]


def allowed(shapes: tuple[tuple[str, ...], ...]) -> str:
    """The shapes an item may take, in words."""
    each = [" with ".join(f'"{k}"' for k in shape) for shape in shapes]
    *others, last = each
    return f"one of {', '.join(others)} or {last}" if others else last


def value_problems(name: str, item: dict[str, Any], work: list[str], each: bool) -> list[str]:
    """What is wrong with the values of an item of its shape, the item asked of each part of the
    work where `each` says."""
    said = [
        f'{name} has an empty "{key}"; say it in words'
        for key in WORDED
        if key in item and not worded(item[key])
    ]
    if "lines" in item:
        inside = lines_problems(name, item["lines"], work)
        said += inside or (parts_problems(name, item["lines"], work) if each else [])
    return said


def lines_problems(name: str, lines: Any, work: list[str]) -> list[str]:
    """What is wrong with the lines an item names, each to be lines there in a file of the work."""
    if not isinstance(lines, list) or not lines:
        return [f"{name} names no lines; give the lines, each as <path>:<from>-<to>"]
    return [
        f"{name}: {line} is not lines of the work; give each as <path>:<from>-<to>"
        for line in lines
        if not in_files(line, work)
    ]


def parts_problems(name: str, lines: list[str], work: list[str]) -> list[str]:
    """An item asked of each part has its Good only where every part of the work holds one of its
    lines, each range inside one part; the lines are already lines of the work."""
    whole = work_parts.parts(work)
    spans = [span(p) for p in whole]
    held = [[at for at in spans if within(span(line), at)] for line in lines]
    said = [
        f"{name}: {line} is not inside one part of the work; give each range inside one of"
        f" {', '.join(f'`{p}`' for p in whole)}"
        for line, parts in zip(lines, held)
        if not parts
    ]
    # A part holding none of the lines has no Good, said once each range lies inside a part.
    return said or [
        f"{name}: {p} holds none of its lines; give lines in every part, as the item has its Good"
        " only where every part holds it"
        for p, at in zip(whole, spans)
        if not any(at in parts for parts in held)
    ]


def within(lines: Any, part: Any) -> bool:
    """Whether the lines, as span gives them, lie inside the part, in its own file."""
    return lines[0] == part[0] and part[1] <= lines[1] and lines[2] <= part[2]


def in_files(line: Any, paths: list[str]) -> bool:
    """Whether the line names lines that are there in one of the files at the paths, a folder's
    files among them."""
    at = span(line)
    if at is None or at[0] not in {os.path.realpath(p) for p in work_parts.files(paths)}:
        return False
    held = work_parts.lines(at[0])
    return held is not None and 1 <= at[1] <= at[2] <= len(held)
