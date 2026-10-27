"""The forms the orchestrator and each role give their judgments in, each checked against the run's
items and the work, so a slip is named where it is made."""

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
# The key of a Good given at its lines, which an item asked of each part does not take, and of the
# Goods given for each part, which no other item takes.
ONE_GOOD = "lines"
EACH_GOOD = "parts"
# What a role that stops for what lies outside the work gives: what it tried, what it confirmed and
# what not, and what it needs to go on.
BLOCKED = ("tried", "confirmed", "not_confirmed", "needs")
# The keys whose value is words, wherever an item holds them.
WORDED = ("good", "evidence", "outside", "did", "lacking", "hinders")


def shapes(path: str) -> tuple[tuple[str, ...], ...]:
    """The shapes of an item the form file at the path takes: the keys each choice of its item
    requires but those that name it, in the order of the choices."""
    with open(path, encoding="utf-8") as f:
        defs = json.load(f)["$defs"]
    choices = [defs[c["$ref"].rpartition("/")[2]] for c in defs["item"]["anyOf"]]
    return tuple(tuple(k for k in c["required"] if k not in NAMING) for c in choices)


class Form(NamedTuple):
    """What an item may hold besides its checklist and ID, one shape of keys each, every item judged
    given; whether questions are asked; whether a reply asking questions gives only the items
    waiting on them, as one asked before the work is made has no Good to give yet; whether the
    choices the work rests on are named, as its maker settles points no one gave it; and whether a
    role may stop for what lies outside the work, its items then left as they stood."""

    shapes: tuple[tuple[str, ...], ...]
    asks: bool = False
    asks_first: bool = False
    chooses: bool = False
    blocks: bool = False


# On a remake the generator claims each item sent back, mended with its evidence or lying outside
# the purpose with why, or the question it waits on; asking before it makes anything, it gives only
# the items waiting; and it names each choice the work rests on.
REMADE = Form(
    shapes(os.path.join(FORM_FILES, "claim.json")),
    asks=True,
    asks_first=True,
    chooses=True,
    blocks=True,
)
# On its first making it claims every item, passing with its evidence or waiting on a question, as
# no gap has been sent back that could lie outside the purpose.
CLAIM = REMADE._replace(shapes=tuple(s for s in REMADE.shapes if "outside" not in s))
# The first user gives every item the Good it found, or where it stopped.
FIRST_READING = Form(shapes(os.path.join(FORM_FILES, "reading.json")), blocks=True)
# Each item two rounds leave without Good waits on a question the orchestrator words, in a form set
# in its steps, not in a form file as the roles' are: it hands it on standard input, which no lane
# holds.
LEFT = Form((("question",),), asks=True)


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
    lists = ("items",) + ("questions",) * form.asks + ("chosen",) * form.chooses
    data = parsed(text, lists)
    if data is None:
        return ["give it as JSON: {" + ", ".join(f'"{k}": [...]' for k in lists) + "}"]
    if form.blocks and data.get("blocked") is not None:
        return blocked_problems(data["blocked"])
    every = not (form.asks_first and data["questions"])
    said = item_problems(data["items"], items, work, form, each, every)
    if form.asks:
        said += question_problems(data)
    if form.chooses:
        said += choice_problems(data["chosen"])
    return said


def blocked_problems(blocked: Any) -> list[str]:
    """What is wrong with a stop for what lies outside the work, to hold what was tried, what was
    confirmed and what was not, and what is needed, in words."""
    if (
        isinstance(blocked, dict)
        and set(blocked) == set(BLOCKED)
        and all(worded(v) for v in blocked.values())
    ):
        return []
    keys = ", ".join(f'"{k}"' for k in BLOCKED)
    return [f'"blocked" must hold {keys}, what you tried, confirmed and not, and need, in words']


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
    every: bool,
) -> list[str]:
    """What is wrong with the items given, against the items judged; every one of them is to be
    given where `every` says."""
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
        # An item asked of each part gives a Good for every part, and any other one Good.
        barred = ONE_GOOD if key in of_each else EACH_GOOD
        taken = [s for s in form.shapes if barred not in s]
        held = [s for s in taken if all(k in item for k in s)]
        shaped = [k for s in held for k in s]
        rest = [k for k in item if k not in NAMING and k not in shaped]
        if len(held) != 1 or rest:
            asked = ", as it is asked of each part" if key in of_each else ""
            said.append(f"{name} must hold {allowed(taken)}{asked}")
            continue
        said += value_problems(name, item, work)
    if every:
        said += [
            f"{i['checklist']} {i['item']} is left out; give every item judged here"
            for i in items
            if key_of(i) not in seen
        ]
    return said


def allowed(shapes: list[tuple[str, ...]]) -> str:
    """The shapes an item may take, in words."""
    each = [" with ".join(f'"{k}"' for k in shape) for shape in shapes]
    *others, last = each
    return f"one of {', '.join(others)} or {last}" if others else last


def value_problems(name: str, item: dict[str, Any], work: list[str]) -> list[str]:
    """What is wrong with the values of an item of its shape."""
    said = [
        f'{name} has an empty "{key}"; say it in words'
        for key in WORDED
        if key in item and not worded(item[key])
    ]
    if "question" in item and not (
        isinstance(item["question"], int) and not isinstance(item["question"], bool)
    ):
        said.append(f"{name}'s \"question\" is not a number; give the question's, from 1")
    for key in ("lines", "places"):
        if key in item:
            said += lines_problems(name, item[key], work)
    if "parts" in item:
        said += parts_problems(name, item["parts"], work)
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


def parts_problems(name: str, given: Any, work: list[str]) -> list[str]:
    """An item asked of each part gives, for every part of the work, the Good the part gives, at
    lines inside it."""
    if not isinstance(given, list):
        return [f'{name} gives its parts as no list; give [{{"part", "good", "lines"}}, ...]']
    whole = work_parts.parts(work)
    spans = [span(p) for p in whole]
    said: list[str] = []
    seen: list[Any] = []
    for k, part in enumerate(given, 1):
        if (
            not isinstance(part, dict)
            or set(part) != {"part", "good", "lines"}
            or not worded(part["good"])
        ):
            said.append(f'{name}: part {k} must hold "part", "good" and "lines", the Good in words')
            continue
        at = span(part["part"])
        if at not in spans:
            said.append(
                f"{name}: {part['part']} is not a part of the work; give each as one of"
                f" {', '.join(f'`{p}`' for p in whole)}"
            )
        elif at in seen:
            said.append(f"{name}: {part['part']} is given twice; give each part once")
        else:
            seen.append(at)
            inside = lines_problems(name, part["lines"], work)
            said += inside or [
                f"{name}: {line} is not inside its part {part['part']}; name lines of the part"
                for line in part["lines"]
                if not within(span(line), at)
            ]
    # A part left out has no Good, said once the parts given are in their form.
    return said or [
        f"{name}: {p} has no Good; give a Good for every part, as the item has its Good only where"
        " every part gives it"
        for p, at in zip(whole, spans)
        if at not in seen
    ]


def within(lines: Any, part: Any) -> bool:
    """Whether the lines, as span gives them, lie inside the part, in its own file."""
    return lines[0] == part[0] and part[1] <= lines[1] and lines[2] <= part[2]


def in_files(line: Any, paths: list[str]) -> bool:
    """Whether the line names lines that are there in one of the files."""
    at = span(line)
    if at is None or at[0] not in {os.path.realpath(p) for p in paths} or not os.path.isfile(at[0]):
        return False
    with open(at[0], encoding="utf-8") as f:
        count = len(f.read().splitlines())
    return 1 <= at[1] <= at[2] <= count


def question_problems(data: dict[str, Any]) -> list[str]:
    """What is wrong with the questions, each numbered from 1, against the items waiting on them."""
    said: list[str] = []
    questions = data["questions"]
    waiting = [i.get("question") for i in data["items"] if isinstance(i, dict)]
    for n, question in enumerate(questions, 1):
        if not isinstance(question, dict) or not all(
            worded(question.get(k)) for k in ("question", "recommended")
        ):
            said.append(
                f'question {n} must hold "question" and "recommended", the answer you'
                " recommend, each in words"
            )
        elif n not in waiting:
            said.append(f"question {n} has no item waiting on it; name it at the item it settles")
    said += [
        f"question {n} is waited on but not given; add it to the questions"
        for n in waiting
        if isinstance(n, int) and not 1 <= n <= len(questions)
    ]
    return said
