"""What a design tree is and when it holds: its file, a Markdown nested list that shows the tree as
a tree, read into the form the checks take, or refused with why, a line for each fault; a tree in
that form written as the Markdown; each way it fails to hold, as pin's architecture names them, its
problems; and the open decisions that can be decided now, each it builds on being decided.

The file, design-tree.md, is in one form. Its first line is `# Design tree`, then an empty line,
then `Goal: <one sentence>` and a line `- Grounds: <text>` for each of the goal's grounds; then an
empty line and the list. A question stands at the top of the list, `- **<ID>** <intent>`. A
decision stands under the first question it serves, else under the first decision it builds on,
else at the top of the list: `- **<ID> <what is decided>**: <what was decided, or open>
(<who settled it>)`, who settled it left out where no one has. Under a decision stand, in this
order, a line `- Grounds: <text>` for each ground, `- Also serves: <IDs>` naming what else it
serves, `- Also builds on: <IDs>` naming what else it builds on, and the decisions under it. Each
item stands two spaces deeper than the one it is under. So the nesting is the tree, and an AI that
changes a node with Read and Edit sees the path from it to the goal and every branch under it."""

from __future__ import annotations

import os
import re
from typing import Any

# Who settles a decision: the person, a fact found and confirmed, what follows from the goal and the
# decisions before it, or the maker AI that handed the tree over, whose points the pinner keeps.
SETTLED_BY = ("user", "research", "reasoning", "maker")
# The tree's form, said once for each message that names a part of it.
TREE = "the tree must be an object with goal, questions and decisions"
TEXT = "must be one line of text, not empty"
TEXTS = "must be a list of texts, each one line and not empty"
IDS = "must be a list of IDs"
AN_ID = "must be an ID: a word with no `*` or `,`"
# The lines of the Markdown, each as it stands, the indent left out.
HEADING = "# Design tree"
GOAL = "Goal: "
GROUNDS = "- Grounds: "
SERVES = "- Also serves: "
BUILDS = "- Also builds on: "
# What a decision's line says where it is not decided.
OPEN = "open"
# An ID: a word with no `*` or `,`, as a question's or a decision's line and an Also line hold it.
ID = re.compile(r"[^\s*,]+")
QUESTION = re.compile(rf"- \*\*(?P<id>{ID.pattern})\*\* (?P<what>\S.*)")
DECISION = re.compile(
    rf"- \*\*(?P<id>{ID.pattern}) (?P<what>(?:(?!\*\*).)+)\*\*: (?P<decided>\S.*?)"
    rf"(?: \((?P<by>{'|'.join(SETTLED_BY)})\))?"
)
# Each Also line, by the key of the decision it adds to.
ALSO = {SERVES: "contributes_to", BUILDS: "builds_on"}
# The lines under a decision, in the order they stand, by the rank of each.
RANK = {GROUNDS: 0, SERVES: 1, BUILDS: 2}
UNDER = 3
# An item a line stands under: whether it is a question or a decision, the item, and the rank of the
# last line under it.
Item = tuple[str, dict[str, Any], list[int]]
FORMS = (
    "a question `- **<ID>** <intent>`, a decision `- **<ID> <what is decided>**: <what was decided,"
    " or open> (<user, research, reasoning or maker>)`, `- Grounds: <text>`, `- Also serves: <IDs>`"
    " or `- Also builds on: <IDs>`"
)


class Unreadable(Exception):
    """The tree cannot be checked: its file is missing, is not text or is out of form. The message
    says why, a line for each fault."""


def load(path: str) -> dict[str, Any]:
    """The design tree in the file at the path; refuses, by Unreadable, a file that is missing, is
    not text in UTF-8 or is out of the tree's form."""
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        raise Unreadable(f"there is no file {path}") from None
    except UnicodeDecodeError:
        raise Unreadable("it is not text in UTF-8") from None
    return read(text)


def save(path: str, tree: dict[str, Any]) -> None:
    """Writes the tree, in form, at the path as its Markdown, making its folder where it is not
    there."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(markdown(tree))


def read(text: str) -> dict[str, Any]:
    """The design tree the Markdown text holds; refuses, by Unreadable, a text out of the tree's
    form, or whose IDs do not hold, with a line for each fault."""
    lines = text.split("\n")
    if lines[-1] == "":
        lines.pop()
    lines += [""] * (3 - len(lines))
    faults = []
    if lines[0] != HEADING:
        faults.append(f"line 1 must be `{HEADING}`")
    if lines[1] != "":
        faults.append("line 2 must be empty")
    if not lines[2].startswith(GOAL) or lines[2] == GOAL:
        faults.append("line 3 must be `Goal: <one sentence>`")
    goal = {"what": lines[2][len(GOAL) :], "grounds": []}
    at = 3
    while at < len(lines) and lines[at].startswith(GROUNDS) and lines[at] != GROUNDS:
        goal["grounds"].append(lines[at][len(GROUNDS) :])
        at += 1
    if at < len(lines) and lines[at] != "":
        faults.append(f"line {at + 1} must be empty, between the goal and its questions")
    found = {"goal": goal, "questions": [], "decisions": []}
    faults += list_faults(lines[at + 1 :], at + 2, found)
    faults = faults or id_faults(found["questions"], found["decisions"])
    if faults:
        raise Unreadable("\n".join(faults))
    return found


def list_faults(lines: list[str], first: int, found: dict[str, Any]) -> list[str]:
    """Reads the list's lines, the first of them at the line number first, into the tree found;
    gives each fault of their form. An item out of form is left out, and the items under it are
    read under the item it stands under."""
    faults = []
    # The items each line stands under, the top first, each with the rank of its last line under;
    # an item out of form stands for the one it is under, or None at the top.
    above: list[Item | None] = []
    for n, line in enumerate(lines, first):
        item = line.lstrip(" ")
        depth, rest = divmod(len(line) - len(item), 2)
        if not line:
            faults.append(f"line {n} is empty, inside the list")
            continue
        if rest or depth > len(above):
            faults.append(f"line {n} must be indented by two spaces for each item it stands under")
            continue
        del above[depth:]
        parent = above[-1] if above else None
        fault = taken(n, item, parent, above, found)
        if fault:
            faults.append(fault)
            above.append(parent)
    return faults


def taken(
    n: int, item: str, parent: Item | None, above: list[Item | None], found: dict[str, Any]
) -> str:
    """Takes the item of the line numbered n, under the parent, into the tree found and, a question
    or a decision, onto the items above; gives its fault, "" where it has none, and then takes
    nothing."""
    kind = next((k for k in RANK if item.startswith(k)), None)
    question, decision = QUESTION.fullmatch(item), DECISION.fullmatch(item)
    if decision:
        d = {
            "id": decision["id"],
            "what": decision["what"],
            "contributes_to": [parent[1]["id"]] if parent and parent[0] == "question" else [],
            "builds_on": [parent[1]["id"]] if parent and parent[0] == "decision" else [],
            "decided": None if decision["decided"] == OPEN else decision["decided"],
            "settled_by": decision["by"],
            "grounds": [],
        }
        found["decisions"].append(d)
        if parent and parent[0] == "decision":
            parent[2][0] = UNDER
        above.append(("decision", d, [0]))
        return ""
    if question:
        if parent:
            return f"line {n}: a question stands at the top of the list, under the goal alone"
        q = {"id": question["id"], "what": question["what"]}
        found["questions"].append(q)
        above.append(("question", q, [UNDER]))
        return ""
    if kind is None or item == GROUNDS:
        return f"line {n} is none of the tree's lines: {FORMS}"
    name = kind[2:-2]
    if not parent or parent[0] != "decision":
        return f"line {n}: a{'n' if kind in ALSO else ''} {name} line stands under a decision"
    d, rank = parent[1], parent[2]
    if rank[0] > RANK[kind] or (kind in ALSO and rank[0] == RANK[kind]):
        return (
            f"line {n}: the lines under {d['id']} go in the order Grounds, Also serves, Also builds"
            " on, then the decisions under it, each Also line once"
        )
    rank[0] = RANK[kind]
    said = item[len(kind) :]
    if kind == GROUNDS:
        d["grounds"].append(said)
        return ""
    ids = said.split(", ")
    if not all(ID.fullmatch(i) for i in ids):
        return f"line {n}: an {name} line takes IDs joined by `, `"
    d[ALSO[kind]] += ids
    return ""


def markdown(tree: dict[str, Any]) -> str:
    """The tree, in form, as its Markdown: each decision under the first question it serves, else
    under the first decision it builds on where that leads to no loop, else at the top of the list
    after the questions; each in the tree's order among those beside it."""
    questions = {q["id"] for q in tree["questions"]}
    decisions = {d["id"]: d for d in tree["decisions"]}

    def first(d: dict[str, Any]) -> str | None:
        serves = [i for i in d["contributes_to"] if i in questions]
        on = [i for i in d["builds_on"] if i in decisions]
        return (serves or on or [None])[0]

    def place(d: dict[str, Any]) -> str | None:
        at, seen = first(d), set()
        while at in decisions and at not in questions and at not in seen:
            if at == d["id"]:
                return None
            seen.add(at)
            at = first(decisions[at])
        return first(d)

    placed = {d["id"]: place(d) for d in tree["decisions"]}
    goal = tree["goal"]
    lines = [HEADING, "", GOAL + goal["what"]] + [GROUNDS + g for g in goal["grounds"]] + [""]

    def under(parent: str | None, depth: int) -> None:
        for d in tree["decisions"]:
            if placed[d["id"]] == parent:
                key = "contributes_to" if parent in questions else "builds_on"
                lines.extend(decision_lines(d, (key, parent), depth))
                under(d["id"], depth + 1)

    for q in tree["questions"]:
        lines.append(f"- **{q['id']}** {q['what']}")
        under(q["id"], 1)
    under(None, 0)
    return "\n".join(lines) + "\n"


def decision_lines(d: dict[str, Any], parent: tuple[str, str | None], depth: int) -> list[str]:
    """The decision's line at the depth, under the parent, which it serves or builds on by the key
    given, and its lines under it but the decisions: its grounds, then what else it serves and
    builds on."""
    indent = "  " * depth
    by = f" ({d['settled_by']})" if d["settled_by"] else ""
    lines = [f"{indent}- **{d['id']} {d['what']}**: {d['decided'] or OPEN}{by}"]
    lines += [f"{indent}  {GROUNDS}{g}" for g in d["grounds"]]
    for kind, key in ALSO.items():
        also = list(d[key])
        if key == parent[0] and parent[1] in also:
            also.remove(parent[1])
        if also:
            lines.append(f"{indent}  {kind}{', '.join(also)}")
    return lines


def is_text(value: Any) -> bool:
    """Whether the value is a text that is not empty, on one line."""
    return isinstance(value, str) and bool(value) and "\n" not in value


def is_texts(value: Any) -> bool:
    """Whether the value is a list of texts, each not empty and on one line."""
    return isinstance(value, list) and all(is_text(v) for v in value)


def is_id(value: Any) -> bool:
    """Whether the value is an ID: a word with no `*` or `,`."""
    return isinstance(value, str) and ID.fullmatch(value) is not None


def form_faults(data: Any) -> list[str]:
    """Each way the data is out of the tree's form, in the order of its parts, so it cannot be
    written as the Markdown; then each fault of its IDs; none where it is in form, so the checks of
    problems can read it."""
    if not isinstance(data, dict):
        return [TREE]
    faults = goal_faults(data.get("goal"))
    questions, decisions = data.get("questions"), data.get("decisions")
    if not isinstance(questions, list):
        faults.append("questions must be a list")
        questions = []
    for n, q in enumerate(questions):
        faults += question_faults(n, q)
    if not isinstance(decisions, list):
        faults.append("decisions must be a list")
        decisions = []
    for n, d in enumerate(decisions):
        faults += decision_faults(n, d)
    return faults or id_faults(questions, decisions)


def goal_faults(goal: Any) -> list[str]:
    """Each way the goal is out of form."""
    if not isinstance(goal, dict):
        return ["goal must be an object with what and grounds"]
    faults = [] if is_text(goal.get("what")) else [f"goal.what {TEXT}"]
    return faults + ([] if is_texts(goal.get("grounds")) else [f"goal.grounds {TEXTS}"])


def question_faults(n: int, question: Any) -> list[str]:
    """Each way the question at the place n of the questions is out of form."""
    if not isinstance(question, dict):
        return [f"questions[{n}] must be an object with id and what"]
    faults = [] if is_id(question.get("id")) else [f"questions[{n}].id {AN_ID}"]
    return faults + ([] if is_text(question.get("what")) else [f"questions[{n}].what {TEXT}"])


def decision_faults(n: int, decision: Any) -> list[str]:
    """Each way the decision at the place n of the decisions is out of form."""
    at = f"decisions[{n}]"
    if not isinstance(decision, dict):
        return [f"{at} must be an object"]
    checks = [
        ("id", is_id, AN_ID),
        ("what", lambda v: is_text(v) and "**" not in v, f"{TEXT}, with no `**`"),
        ("contributes_to", lambda v: isinstance(v, list) and all(map(is_id, v)), IDS),
        ("builds_on", lambda v: isinstance(v, list) and all(map(is_id, v)), IDS),
        (
            "decided",
            lambda v: v is None or (is_text(v) and v != OPEN),
            f"{TEXT} and not `{OPEN}`, or null",
        ),
        (
            "settled_by",
            lambda v: v is None or v in SETTLED_BY,
            "must be user, research, reasoning or maker, or null",
        ),
        ("grounds", is_texts, TEXTS),
    ]
    return [f"{at}.{key} {rule}" for key, ok, rule in checks if not ok(decision.get(key))]


def id_faults(questions: list[dict[str, Any]], decisions: list[dict[str, Any]]) -> list[str]:
    """Each ID used twice, and each ID a decision names that the tree does not hold where it is
    named, or that is the decision's own."""
    ids = [q["id"] for q in questions] + [d["id"] for d in decisions]
    seen: set[str] = set()
    twice: set[str] = set()
    for i in ids:
        (twice if i in seen else seen).add(i)
    faults = [f"the ID {i} is used twice" for i in sorted(twice)]
    decided_ids = {d["id"] for d in decisions}
    for d in decisions:
        for i in d["contributes_to"]:
            if i == d["id"]:
                faults.append(f"{i} contributes to itself")
            elif i not in ids:
                faults.append(f"{d['id']} contributes to {i}, which is not in the tree")
        for i in d["builds_on"]:
            if i == d["id"]:
                faults.append(f"{i} builds on itself")
            elif i not in decided_ids:
                faults.append(f"{d['id']} builds on {i}, which is not a decision of the tree")
    return faults


def problems(tree: dict[str, Any]) -> list[str]:
    """Each way a tree in form fails to hold, a sentence each, in the order of the checks: a goal or
    a question nothing serves; a decision that reaches no question; decisions out of the order
    builds_on gives; and a decision settled with what it rests on missing. None where it holds."""
    return gaps(tree) + unreached(tree) + out_of_order(tree) + unsettled(tree)


def gaps(tree: dict[str, Any]) -> list[str]:
    """The goal with no question under it, and each question no decision contributes to."""
    if not tree["questions"]:
        return ["The goal has no question that must hold for it."]
    served = {i for d in tree["decisions"] for i in d["contributes_to"]}
    return [
        f"{q['id']} is served by no decision." for q in tree["questions"] if q["id"] not in served
    ]


def unreached(tree: dict[str, Any]) -> list[str]:
    """Each decision from which no chain of contributes_to reaches a question."""
    questions = {q["id"] for q in tree["questions"]}
    serves = {d["id"]: d["contributes_to"] for d in tree["decisions"]}
    found = []
    for d in tree["decisions"]:
        seen, left = set(), list(d["contributes_to"])
        while left and not questions & set(left):
            seen.update(left)
            left = [i for j in left for i in serves[j] if i not in seen]
        if not left:
            found.append(f"{d['id']} reaches no question, so it serves nothing.")
    return found


def out_of_order(tree: dict[str, Any]) -> list[str]:
    """Each loop of builds_on, named once from its first decision in the tree, and each decision
    decided while one it builds on is open."""
    by_id = {d["id"]: d for d in tree["decisions"]}
    found, looped = [], set()
    for d in tree["decisions"]:
        loop = loop_from(d["id"], by_id)
        if loop and not looped & set(loop):
            looped.update(loop)
            found.append(
                f"{listed(loop)} build on one another in a loop, so none can be decided first."
            )
    for d in tree["decisions"]:
        for i in d["builds_on"]:
            if d["decided"] is not None and by_id[i]["decided"] is None:
                found.append(
                    f"{d['id']} is decided before {i}, which it builds on and which is still open."
                )
    return found


def loop_from(start: str, by_id: dict[str, dict[str, Any]]) -> list[str]:
    """The decisions of the shortest loop of builds_on that leads from start back to it, in the
    order the chain meets them, start first; none where no chain from start comes back to it. The
    chains are followed breadth first, so the first to come back is the shortest."""
    paths = [[start]]
    seen = {start}
    while paths:
        path = paths.pop(0)
        for i in by_id[path[-1]]["builds_on"]:
            if i == start:
                return path
            if i not in seen:
                seen.add(i)
                paths.append(path + [i])
    return []


def listed(ids: list[str]) -> str:
    """The IDs in words, as "D1, D2 and D3"."""
    return ", ".join(ids[:-1]) + " and " + ids[-1]


def unsettled(tree: dict[str, Any]) -> list[str]:
    """Each decision whose decided, settled_by and grounds do not go together: a decision decided
    by no one named, named as settled while not decided, or decided on no ground."""
    found = []
    for d in tree["decisions"]:
        if d["decided"] is not None and d["settled_by"] is None:
            found.append(f"{d['id']} is decided, but not by whom or what: give its settled_by.")
        elif d["decided"] is None and d["settled_by"] is not None:
            found.append(f"{d['id']} has a settled_by, but is not decided: give what was decided.")
        elif d["decided"] is not None and not d["grounds"]:
            found.append(f"{d['id']} is decided on no ground: give what it rests on.")
    return found


def ready(tree: dict[str, Any]) -> list[str]:
    """The IDs of the open decisions each of whose builds_on is decided, in the order the tree
    lists them: those that can be decided now."""
    decided = {d["id"] for d in tree["decisions"] if d["decided"] is not None}
    return [
        d["id"]
        for d in tree["decisions"]
        if d["decided"] is None and set(d["builds_on"]) <= decided
    ]
