"""The design tree, as only rn's code reads and writes it: its file held to the plan best
practice's template, the order of its deliverables held to that best practice's rules, a tree edit
applied to it, the nodes a change touches, and the tree shown with the ID of each node.

A node's ID is its place in the tree as it stands: `goal`; `D2`, the second deliverable; `D2Q3`,
the intent Q3 of it; and `D2Q3-1`, the first decision of that intent. Lane's every_item counts an
ID answered where it stands as a word of its own, so no ID stands inside another as one: `D2` is no
word of `D2Q3`, and `D2Q3` is none of `D2Q3-1`. rn finds a change against the tree as the work's
branch last committed it, each node by what names it there: the goal, a deliverable by its path,
an intent by its ID, and a decision by what it's about. So a change keeps its nodes apart however
the IDs shift."""

from __future__ import annotations

import copy
import os
import re
from typing import Any, Callable

import files

# The tree's form: the template of the plan best practice.
FORM = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "best-practices", "plan", "design-tree.schema.json"
)
NAME = "design-tree.json"
GOAL = "goal"
ID = re.compile(r"D(?P<n>[1-9][0-9]*)(?:(?P<intent>[A-Za-z][A-Za-z0-9]*)(?:-(?P<k>[1-9][0-9]*))?)?")
# The fields of a deliverable not yet done that an edit may set, and those a done one keeps.
FIELDS = ("name", "path", "kind", "inputs", "preconditions", "status")
KEPT = ("name", "path", "kind", "status")
DONE = "done"
META = "meta"
RESEARCH = "research"
# What finds a kind's best practice for a run: the kind, then the path of its best practice or
# None, and the IDs of its intents where it's found.
Finder = Callable[[str], "list[str] | None"]


class Refused(Exception):
    """A tree edit or a tree that doesn't hold. The message says each fault, a line each."""


def load(path: str) -> dict[str, Any]:
    """The design tree at the path, held to its form. Refuses, by Unreadable, one that's missing,
    holds no JSON, or is out of the form."""
    return files.held(path, files.read(path), files.read(FORM))


def deliverables(tree: dict[str, Any]) -> list[dict[str, Any]]:
    """The tree's deliverables, in the order of the work."""
    return tree["deliverables"]


def at_hand(tree: dict[str, Any]) -> int | None:
    """The number of the first deliverable not done, from 1; None where the work has none left."""
    for n, d in enumerate(deliverables(tree), 1):
        if not done(d):
            return n
    return None


def done(d: dict[str, Any]) -> bool:
    """Whether the deliverable meets every intent and its turns are over."""
    return d["status"] == DONE  # pragma: no mutate


def confirmed(tree: dict[str, Any]) -> bool:
    """Whether the user settled the tree's goal."""
    return tree["goal"]["by"] == "user"  # pragma: no mutate


def numbered(tree: dict[str, Any], n: int) -> dict[str, Any]:
    """The deliverable of the number, from 1."""
    return deliverables(tree)[n - 1]


def nodes(tree: dict[str, Any]) -> list[tuple[str, tuple[str, ...]]]:
    """Each node of the tree in its order, its ID and its key, the name that holds across a change:
    the goal, then each deliverable, each of its intents, and each decision under it."""
    found: list[tuple[str, tuple[str, ...]]] = [(GOAL, (GOAL,))]
    for n, d in enumerate(deliverables(tree), 1):
        found.append((f"D{n}", ("d", d["path"])))
        for intent in d.get("intents", []):
            found.append((f"D{n}{intent['id']}", ("i", d["path"], intent["id"])))
            for k, decision in enumerate(intent["decisions"], 1):
                key = ("x", d["path"], intent["id"], decision["about"])
                found.append((f"D{n}{intent['id']}-{k}", key))
    return found


def content(tree: dict[str, Any]) -> dict[tuple[str, ...], Any]:
    """What each node holds of its own, by its key: what a change to it changes."""
    held: dict[tuple[str, ...], Any] = {(GOAL,): tree["goal"]}
    for d in deliverables(tree):
        held[("d", d["path"])] = {k: d.get(k) for k in FIELDS}
        for intent in d.get("intents", []):
            held[("i", d["path"], intent["id"])] = intent["good"]
            for decision in intent["decisions"]:
                key = ("x", d["path"], intent["id"], decision["about"])
                held[key] = (decision["decided"], decision.get("by"))
    return held


def changed(before: dict[str, Any] | None, after: dict[str, Any]) -> set[tuple[str, ...]]:
    """The key of each node the change from the tree before to the tree after added, changed or
    removed; every node where there was no tree before."""
    was = content(before) if before is not None else {}
    now = content(after)
    return {k for k in set(was) | set(now) if was.get(k, None) != now.get(k, None) or k not in was}


def touched(
    before: dict[str, Any] | None, after: dict[str, Any], keys: set[tuple[str, ...]]
) -> list[str]:
    """The ID of each node of the tree after that the change of the keys touches, in the tree's
    order, as Q9 of the plan best practice lists them: up to the goal, the later decisions of the
    deliverable, and the deliverables it takes from or gives to. The list leaves out the nodes
    changed, as their change is what the edit answers for."""
    order = nodes(after)
    places = {key: at for at, (_, key) in enumerate(order)}
    paths = [d["path"] for d in deliverables(after)]
    found: set[tuple[str, ...]] = set()
    for key in keys:
        if key == (GOAL,):
            found.update(("d", p) for p in paths)
            continue
        path = key[1]
        found.add((GOAL,))
        found.update(neighbours(after, path))
        if key not in places:
            # A node removed: the nodes over it that the tree still holds.
            found.update(k for k in over(key) if k in places)
            continue
        found.update(over(key))
        # Each decision of the deliverable after the node, as a deliverable's own come after it.
        found.update(k for k in order_keys(order, places[key]) if decides(k) and k[1] == path)
    left = [k for k in found - keys if k in places]
    return [order[places[k]][0] for k in sorted(left, key=places.__getitem__)]


def decides(key: tuple[str, ...]) -> bool:
    """Whether the key is a decision's, the last kind of node in a key's order."""
    return key[0] == "x"  # pragma: no mutate


def order_keys(order: list[tuple[str, tuple[str, ...]]], at: int) -> list[tuple[str, ...]]:
    """The key of each node after the place in the order."""
    # The node's own key, were it taken in too, is among the keys changed, which touched leaves out.
    return [key for _, key in order[at + 1 :]]


def over(key: tuple[str, ...]) -> list[tuple[str, ...]]:
    """The keys of the nodes the node of the key stands under, up to the goal's child."""
    if key[0] == "x":  # pragma: no mutate
        return [("i", key[1], key[2]), ("d", key[1])]
    if key[0] == "i":  # pragma: no mutate
        return [("d", key[1])]
    return []


def neighbours(tree: dict[str, Any], path: str) -> list[tuple[str, ...]]:
    """The keys of the deliverables the deliverable at the path takes from, by its inputs and
    preconditions, and of those that take from it."""
    paths = {d["path"] for d in deliverables(tree)}
    found = []
    for d in deliverables(tree):
        named = d.get("inputs", []) + d.get("preconditions", [])
        if d["path"] == path:
            found += [("d", p) for p in named if p in paths]
        elif path in named:
            found.append(("d", d["path"]))
    return found


def where(tree: dict[str, Any], node: str) -> tuple[str, ...] | None:
    """The key of the node of the ID in the tree; None where no node has it."""
    return dict(nodes(tree)).get(node)


def deliverable(tree: dict[str, Any], path: str) -> dict[str, Any]:
    """The deliverable at the path."""
    return next(d for d in deliverables(tree) if d["path"] == path)


def intent_of(tree: dict[str, Any], key: tuple[str, ...]) -> dict[str, Any]:
    """The intent of the key of an intent or of a decision under it."""
    intents = deliverable(tree, key[1])["intents"]
    return next(i for i in intents if i["id"] == key[2])  # pragma: no mutate


def decision_of(tree: dict[str, Any], key: tuple[str, ...]) -> dict[str, Any]:
    """The decision of the key."""
    return next(x for x in intent_of(tree, key)["decisions"] if x["about"] == key[3])


def made(given: dict[str, Any], finder: Finder) -> dict[str, Any]:
    """A deliverable of the fields given, not yet begun, with an intent for each of its kind's best
    practice where that's found, none good yet."""
    fresh = {k: given[k] for k in FIELDS if k in given and k != "status"}  # pragma: no mutate
    fresh["status"] = given.get("status", "open")
    fresh["intents"] = [
        {"id": i, "good": False, "decisions": []} for i in finder(fresh["kind"]) or []
    ]
    return fresh


def settled(decision: dict[str, Any], given: dict[str, Any]) -> None:
    """Sets the decision to what the node given says of it: open where its decided is null, else
    settled by whom it names."""
    decision.update({k: given[k] for k in ("about", "decided") if k in given})
    if decision["decided"] is None:
        decision.pop("by", None)
    elif "by" in given:
        decision["by"] = given["by"]


def apply(tree: dict[str, Any], edit: dict[str, Any], finder: Finder) -> dict[str, Any]:
    """The tree the edit makes of the tree, the IDs of its nodes and answers read against the tree
    as it stands before it; refuses, by Refused, an edit that names a node no tree holds, sets
    what its node doesn't hold, or leaves a decision settled with no one who settled it."""
    after = copy.deepcopy(tree)
    faults: list[str] = []
    named = [n.get("id", n.get("after", "")) for n in edit.get("nodes", [])]
    keys = {node: where(tree, node) for node in named + [a["id"] for a in edit.get("answers", [])]}
    for node in edit.get("nodes", []):
        named = node.get("id", node.get("after"))
        key = keys.get(named)
        if key is None and "after" in node and named in [d["path"] for d in deliverables(after)]:
            # A deliverable added after one the edit added before it, by that one's path.
            key = ("d", named)
        if key is None:
            faults.append(f"{named} is no node of the tree")
            continue
        try:
            put(after, key, node, finder)
        except Refused as why:
            faults.append(f"{named}: {why}")
    for answer in edit.get("answers", []):
        key = keys[answer["id"]]
        if key is None:
            faults.append(f"{answer['id']} is no node of the tree")
        elif not answer["holds"]:
            if key[0] != "x":  # pragma: no mutate
                faults.append(f"{answer['id']} is no decision: change it among the nodes instead")
            elif key in content(after):
                settled(decision_of(after, key), {"decided": None})
    if faults:
        raise Refused("\n".join(faults))
    return after


def put(tree: dict[str, Any], key: tuple[str, ...], node: dict[str, Any], finder: Finder) -> None:
    """Puts the node of the edit at the node of the key: the goal set, a deliverable added after
    the node, set or removed, an intent made good or not, a decision added under an intent or set
    by what it's about, or a decision set or removed."""
    if "after" in node:
        if key[0] not in (GOAL, "d"):
            raise Refused("a deliverable goes after the goal or a deliverable")
        missing = [f for f in ("name", "path", "kind", "inputs", "preconditions") if f not in node]
        if missing:
            raise Refused(f"a deliverable added needs {', '.join(missing)}")
        at_goal = key == (GOAL,)  # pragma: no mutate
        place = 0 if at_goal else deliverables(tree).index(deliverable(tree, key[1])) + 1
        deliverables(tree).insert(place, made(node, finder))
        return
    if key == (GOAL,):
        tree["goal"] = {"decided": node["decided"], "by": node["by"]}
        return
    if key[0] == "d":  # pragma: no mutate
        found = deliverable(tree, key[1])
        if node.get("remove"):
            deliverables(tree).remove(found)
            return
        set_deliverable(found, node, finder)
        return
    if key[0] == "i":  # pragma: no mutate
        intent = intent_of(tree, key)
        if "good" in node:
            intent["good"] = node["good"]
        if "about" in node:
            same = [x for x in intent["decisions"] if x["about"] == node["about"]]
            # Each decision of an intent has an about of its own, so one is the same at most.
            fresh = {"about": node["about"], "decided": None}
            decision = same[0] if same else fresh  # pragma: no mutate
            if not same:
                intent["decisions"].append(decision)
            settled(decision, node)
            unsettled(decision)
        return
    intent = intent_of(tree, key)
    decision = decision_of(tree, key)
    if node.get("remove"):
        intent["decisions"].remove(decision)
        return
    settled(decision, node)
    unsettled(decision)


def unsettled(decision: dict[str, Any]) -> None:
    """Refuses, by Refused, a decision settled with no one who settled it."""
    if decision["decided"] is not None and "by" not in decision:
        raise Refused(f"the decision {decision['about']} is settled by no one: name its by")


def set_deliverable(found: dict[str, Any], node: dict[str, Any], finder: Finder) -> None:
    """Sets the fields of the deliverable that the node names: its intents those of its new kind
    where the kind changes, and the deliverable kept in one line once it's done, where each
    intent is good."""
    if node.get("status") == DONE:
        short = [i["id"] for i in found.get("intents", []) if not i["good"]]
        if short:
            raise Refused(f"it isn't done while {', '.join(short)} isn't good")
        for k in list(found):
            if k not in KEPT:
                del found[k]
    elif done(found):
        raise Refused("a deliverable done stays done")
    kind = found["kind"]
    found.update({k: node[k] for k in FIELDS if k in node})
    if found["kind"] != kind and not done(found):
        found["intents"] = made(found, finder)["intents"]


def faults(tree: dict[str, Any], exists: Callable[[str], bool], finder: Finder) -> list[str]:
    """Each way the tree's order breaks the plan best practice's rules, in words: a path two
    deliverables hold, a deliverable before what it takes from, an input or precondition that
    names neither a deliverable nor a file, a kind with neither a best practice nor a meta
    deliverable before it, a meta deliverable whose kind no later deliverable takes, a research
    deliverable no later one takes from, and the intents of a deliverable unlike its kind's."""
    found = []
    listed = deliverables(tree)
    paths = [d["path"] for d in listed]
    for path in sorted({p for p in paths if paths.count(p) > 1}):  # pragma: no mutate
        found.append(f"two deliverables are at {path}")
    for n, d in enumerate(listed, 1):
        for field in ("inputs", "preconditions"):
            for p in d.get(field, []):
                if p in paths and paths.index(p) >= n - 1:
                    found.append(f"D{n} takes {p} in its {field}, which comes later")
                elif p not in paths and not exists(p):
                    found.append(f"D{n} names {p} in its {field}, neither a deliverable nor a file")
        if done(d):
            continue
        practiced = finder(d["kind"])
        made_before = any(
            e["kind"] == META and os.path.basename(e["path"].rstrip("/")) == d["kind"]
            for e in listed[: n - 1]
        )
        if practiced is None and not made_before:
            found.append(f"D{n}'s kind {d['kind']} has no best practice, nor a meta one before it")
        elif practiced is not None and [i["id"] for i in d["intents"]] != practiced:
            found.append(f"D{n}'s intents aren't those of its kind {d['kind']}, in their order")
        later = listed[n:]
        if d["kind"] == META:
            made_kind = os.path.basename(d["path"].rstrip("/"))
            if not any(e["kind"] == made_kind for e in later):
                found.append(f"D{n} makes the kind {made_kind}, which no later deliverable takes")
        if d["kind"] == RESEARCH and not any(
            d["path"] in e.get("inputs", []) + e.get("preconditions", []) for e in later
        ):
            found.append(f"D{n} is research that no later deliverable takes from")
    return found


def open_decisions(tree: dict[str, Any], n: int) -> list[tuple[str, dict[str, Any]]]:
    """Each decision of the deliverable of the number still open, by its ID."""
    found = []
    for intent in numbered(tree, n).get("intents", []):
        for k, decision in enumerate(intent["decisions"], 1):
            if decision["decided"] is None:
                found.append((f"D{n}{intent['id']}-{k}", decision))
    return found


def view(tree: dict[str, Any], questions: Callable[[str], dict[str, str]]) -> str:
    """The tree as a reader reads it, each node with its ID: the goal, then each deliverable, and
    under one not done, each intent with its question, as the kind's best practice gives it, and
    the decisions under it."""
    goal = tree["goal"]
    lines = [f"- {GOAL}: {goal['decided']} ({goal['by']})"]
    for n, d in enumerate(deliverables(tree), 1):
        line = f"- D{n} {d['path']}: {d['name']} (kind {d['kind']}, {d['status']})"
        if not done(d):
            taken = [f"{f} {', '.join(d[f])}" for f in ("inputs", "preconditions") if d[f]]
            line += "".join(f"; {t}" for t in taken)
        lines.append(line)
        asked = {} if done(d) else questions(d["kind"])
        for intent in d.get("intents", []):
            good = "good" if intent["good"] else "not good yet"
            said = asked.get(intent["id"], "")
            lines.append(f"  - D{n}{intent['id']}, {good}: {said}".rstrip())
            for k, x in enumerate(intent["decisions"], 1):
                decided = "open" if x["decided"] is None else f"{x['decided']} ({x['by']})"
                lines.append(f"    - D{n}{intent['id']}-{k} {x['about']}: {decided}")
    return "\n".join(lines)
