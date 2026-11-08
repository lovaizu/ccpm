"""What tree.py does for the planner's edits: a tree edit written into the design tree, held to the
tree's form and order, with each node it touches listed; the change committed on the work's branch
once the planner has answered each node touched, with the result the planner gives; a deliverable
done committed with its files, its branch pushed and its draft pull request kept; and the report of
what rn decided without asking the user, read from the run's commits. And what anyone runs on a
design tree: its form and its order checked."""

from __future__ import annotations

import os
from typing import Any

import files
import repository
import runs
import starts
import trees
from starts import Stop

DECIDED = "Decided: "


def empty() -> dict[str, Any]:
    """A tree with no goal yet, which a run's first edit gives one."""
    return {"goal": None, "deliverables": []}


def exists(path: str) -> bool:
    """Whether the repository holds a file or a folder at the path."""
    return os.path.exists(path)


def held(run: str, tree: dict[str, Any]) -> None:
    """Refuses, by Stop, a tree out of its form, or whose order breaks the plan's rules."""
    if tree["goal"] is None:
        raise Stop("the tree has no goal yet: give it one at goal")
    try:
        files.held(runs.tree_path(run), tree, files.read(trees.FORM))
    except files.Unreadable as why:
        raise Stop(str(why)) from None
    found = trees.faults(tree, exists, starts.finder(run), starts.example(run))
    if found:
        raise Stop("\n".join(found))


def answered(run: str) -> set[tuple[str, ...]]:
    """The keys of the nodes the planner answered since its last change."""
    return {tuple(k) for k in runs.kept(run, runs.ANSWERED) or []}


def unanswered(run: str, tree: dict[str, Any]) -> list[str]:
    """The ID of each node the run's change since its last commit touches that the planner hasn't
    answered since."""
    before = starts.committed_tree(run)
    keys = trees.changed(before, tree)
    ids = dict(trees.nodes(tree))
    done = answered(run)
    return [n for n in trees.touched(before, tree, keys) if ids[n] not in done]


def write(run: str, path: str) -> str:
    """Writes the tree edit at the path into the run's design tree: what the planner reads.
    Refuses, by Stop, an edit or a tree that doesn't hold, the tree left as it was."""
    try:
        edit = files.load(path, "tree-edit")
    except files.Unreadable as why:
        raise Stop(str(why)) from None
    tree = starts.tree_of(run) or empty()
    try:
        after = trees.apply(tree, edit, starts.finder(run))
    except trees.Refused as why:
        raise Stop(str(why)) from None
    held(run, after)
    keys = {n: trees.where(tree, n) for n in [a["id"] for a in edit.get("answers", [])]}
    given = {k for k in keys.values() if k is not None}
    change = trees.content(after) != (trees.content(tree) if tree["goal"] is not None else None)
    runs.keep(run, runs.ANSWERED, sorted(given | (set() if change else answered(run))))
    log = runs.kept(run, starts.EDITS) or []
    lines = [
        f"{DECIDED}{n['decided']} ({n.get('grounds') or n['by']})"
        for n in edit["nodes"]
        if n.get("decided")
        and n.get("by") not in (None, "user")
        and n.get("id") != trees.GOAL  # pragma: no mutate
    ]
    runs.keep(run, starts.EDITS, [*log, {"grounds": edit["grounds"], "decided": lines}])
    files.save(runs.tree_path(run), after)
    left = unanswered(run, after)
    if left:
        return (
            "rn: the tree holds. Answer each node the change touches in your next edit, as"
            f" holding or not: {', '.join(left)}."
        )
    return "rn: the tree holds, and each node it touches is answered. Now commit."


def result(run: str, tree: dict[str, Any]) -> str:
    """The result the planner gives once it commits the tree: asks while a point is open for the
    main conversation, ready once the deliverable at hand has none and is doing, done once each
    deliverable is. Refuses, by Stop, a deliverable left open with no point."""
    if not trees.confirmed(tree):
        return "asks"
    n = trees.at_hand(tree)
    if n is None:
        return "done"
    if starts.open_points(run, tree, n):
        return "asks"
    if trees.numbered(tree, n)["status"] != "doing":  # pragma: no mutate
        raise Stop(f"D{n} has no point open: set its status to doing")
    return "ready"


def ready(run: str, tree: dict[str, Any]) -> None:
    """Refuses, by Stop, a change not yet ready to commit: a node it touches unanswered, a
    decision of the change handed that the tree doesn't hold as handed, or a turn come back good
    whose intents the tree doesn't hold good."""
    left = unanswered(run, tree)
    if left:
        raise Stop(f"answer each node the change touches first: {', '.join(left)}")
    kept = runs.pending(run) or {}
    for d in kept.get("decisions", []):
        if not starts.stands(tree, d):
            raise Stop(f"the tree doesn't hold the decision handed at {d['at']}: {d['decided']}")
    cut = runs.kept(run, starts.CUT) or {}
    if cut.get("kind") == "turn" and not cut["reading"]:
        d = trees.deliverable(tree, cut["path"])
        short = [i["id"] for i in d.get("intents", []) if not i["good"]]
        if short:
            raise Stop(f"the turn met each intent of {cut['path']}: make {', '.join(short)} good")


def message(run: str, subject: str, extra: list[str]) -> str:
    """The commit's message: the subject, then each decision taken without asking the user."""
    log = runs.kept(run, starts.EDITS) or []
    grounds = " ".join(e["grounds"] for e in log)
    lines = [*extra, *(x for e in log for x in e["decided"])]
    said = [grounds] if subject and grounds else []
    body = "\n\n".join([*said, "\n".join(lines)] if lines else said)
    return f"rn: {subject or grounds}" + (f"\n\n{body}" if body else "")


def forget(run: str) -> None:
    """Drops what the run's temporary folder kept for the change now committed."""
    runs.drop(run, runs.CHANGE, runs.EDIT, runs.ANSWERED, starts.EDITS, starts.CUT)


def commit(run: str) -> str:
    """Commits the run's folder on its branch, once the change is ready: what the planner gives."""
    tree = starts.the_tree(run)
    ready(run, tree)
    cut = runs.kept(run, starts.CUT) or {}
    if cut.get("kind") == "turn" and cut["reading"]:
        raise Stop(f"{cut['path']} reads well: set it done, and run tree.py deliver")
    given = result(run, tree)
    repository.commit(run, [run], message(run, "", []))
    forget(run)
    return (
        f"rn: committed on {repository.branch(run)}. {starts.GIVE.format(result=given)}: the"
        f" tree of {run} is committed."
    )


def done_now(run: str, tree: dict[str, Any]) -> dict[str, Any]:
    """The deliverable the change set done, which the branch doesn't hold done yet; refuses, by
    Stop, a change that sets none done."""
    before = starts.committed_tree(run) or {"deliverables": []}
    was = {d["path"] for d in before["deliverables"] if trees.done(d)}
    now = [d for d in trees.deliverables(tree) if trees.done(d) and d["path"] not in was]
    if len(now) != 1:
        raise Stop("set the one deliverable whose turn of how it reads came back good done")
    (only,) = now
    return only


def made_by(run: str, path: str) -> tuple[list[str], list[str]]:
    """The files the turns of the deliverable at the path made, and each small point their last
    rounds decided, as a line of the commit."""
    made: list[str] = [path]
    decided: list[str] = []
    for reading in (False, True):
        last = runs.last(runs.turn_of(run, path, reading))
        record = runs.made_of(last) if last else None
        if record is None:
            continue
        made += [p for p in record["made"] if p not in made]
        decided += [f"{DECIDED}{x['decided']} ({x['grounds']})" for x in record["decided"]]
    return made, decided


def deliver(run: str) -> str:
    """Commits the deliverable done with its files and the run's folder, pushes the branch, and
    keeps the draft pull request: what the planner gives, and the report once the run has no work
    left."""
    tree = starts.the_tree(run)
    ready(run, tree)
    d = done_now(run, tree)
    made, decided = made_by(run, d["path"])
    given = result(run, tree)
    paths = [run, *(p for p in made if os.path.exists(p))]
    repository.commit(run, paths, message(run, f"{d['path']}: {d['name']}", decided))
    forget(run)
    plan = "\n".join(f"- {e['path']}: {e['name']}" for e in trees.deliverables(tree))
    try:
        url = repository.push(run, tree["goal"]["decided"], f"{tree['goal']['decided']}\n\n{plan}")
        said = f"rn: committed {d['path']} on {repository.branch(run)}, and pushed: {url}."
    except repository.Failed as why:
        said = (
            f"rn: committed {d['path']} on {repository.branch(run)}, which isn't pushed: {why}."
            " Name what's missing in your message for the user."
        )
    if given == "done":
        return f"{said} {starts.GIVE.format(result='done')}:\n{report(run)}"
    return f"{said} {starts.GIVE.format(result=given)}: {d['path']} is done."


def report(run: str) -> str:
    """The message the user gets once the run has no work left: each deliverable, the files made
    with them, and each decision taken without asking, with its grounds, read from the run's
    commits."""
    tree = starts.the_tree(run)
    paths = [d["path"] for d in trees.deliverables(tree)]
    extra = []
    for path in paths:
        extra += [p for p in made_by(run, path)[0] if p not in paths and p not in extra]
    *rest, last = paths
    named = f"{', '.join(rest)} and {last}" if rest else last
    head = f"Done: {named} {'are' if rest else 'is'} changed"
    head += f", with {', '.join(extra)}." if extra else "."
    out = [
        head + " Each was tried as its people would use it, and meets every question of its kind's"
        " best practice."
    ]
    decided = [
        line[len(DECIDED) :]
        for m in repository.messages(run)
        for line in m.splitlines()
        if line.startswith(DECIDED)
    ]
    if decided:
        out += ["", "Decided without asking you:", *(f"- {x}" for x in decided)]
    return "\n".join(out)


def check(path: str) -> list[str]:
    """Each fault of the design tree at the path: of its form, or of its order."""
    tree = trees.load(path)
    run = os.path.dirname(path)
    return trees.faults(tree, exists, starts.finder(run), starts.example(run))
