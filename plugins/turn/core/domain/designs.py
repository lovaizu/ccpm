"""What Turn holds of a run's design beside what pin's check.py holds: the design tree asks each
question of the template as the template asks it, each named `<kind>/Q<n>`; the work's parts each
hold every decision joined to their own and paths of the work no other part holds; a remake names
decisions and questions of the tree; and the decisions split into branches, the groups that build
on none in another, each of which a run of builder of its own makes."""

from __future__ import annotations

import os
import re
from typing import Any

import files

# The script each of a work's commands runs inside, as the command its user types, so that none
# reaches the person's own files: Turn's own scripts/throwaway.py, by the path Turn lies at.
THROWAWAY = (
    "python3 "
    + os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "scripts",
        "throwaway.py",
    )
    + " "
)


def asked(tree: dict[str, Any], standard: dict[str, Any], kind: str) -> list[str]:
    """Each way the tree's questions differ from the template's: one left out, one asked in other
    words, in the template's order, then each the template has not."""
    asks = {q["id"]: q["what"] for q in tree["questions"]}
    found = []
    expected = set()
    for q in standard["benefits"]:
        name = f"{kind}/{q['id']}"
        expected.add(name)
        if name not in asks:
            found.append(f"the tree does not ask {name}: {q['what']}")
        elif asks[name] != q["what"]:
            found.append(f"{name} is not asked as the template asks it: {q['what']}")
    found += [f"{name} is no question of the template" for name in asks if name not in expected]
    return found


def joins(tree: dict[str, Any]) -> list[tuple[str, str]]:
    """Each pair of decisions one joins to the other: by building on it, or by serving it."""
    ids = {d["id"] for d in tree["decisions"]}
    return [
        (d["id"], other)
        for d in tree["decisions"]
        for other in d["builds_on"] + d["contributes_to"]
        if other in ids
    ]


def branches(tree: dict[str, Any]) -> list[list[str]]:
    """The decisions in groups, each holding every decision joined to one of its own, the groups
    in the order of their first decision and each decision in the tree's order."""
    order = [d["id"] for d in tree["decisions"]]
    group = {i: {i} for i in order}
    for a, b in joins(tree):
        if b not in group[a]:
            merged = group[a].union(group[b])
            for i in merged:
                group[i] = merged
    found: list[list[str]] = []
    for i in order:
        if not any(i in g for g in found):
            found.append([j for j in order if j in group[i]])
    return found


def parted(work: dict[str, Any], tree: dict[str, Any]) -> dict[str, Any]:
    """The work with its parts made again from the tree's branches: a branch whose decisions a
    part already holds keeps that part's paths, a work of one part gives it every path, and any
    other part's paths are left for designer to give."""
    kept = {frozenset(p["decisions"]): p["paths"] for p in work["parts"]}
    found = branches(tree)
    parts = []
    for n, decisions in enumerate(found, 1):
        paths = kept.get(frozenset(decisions))
        if paths is None:
            paths = [] if found[1:] else list(work["paths"])
        parts.append({"id": f"P{n}", "decisions": decisions, "paths": paths})
    return {**work, "parts": parts}


def under(path: str, paths: list[str]) -> bool:
    """Whether the path is one of the paths, or lies in a folder of them."""
    return any(path == p or path.startswith(p.rstrip("/") + "/") for p in paths)


def work_faults(work: dict[str, Any], tree: dict[str, Any]) -> list[str]:
    """Each way the work's parts fail: a work of no paths; a part naming a decision the tree has
    not, a path none of the work's, or no path; a decision in no part, or in two; a path in two
    parts; a decision joined to one of another part; and a command not run inside Turn's
    scripts/throwaway.py, after its `--`."""
    ids = [d["id"] for d in tree["decisions"]]
    found = [] if work["paths"] else ["the work has no paths"]
    held: dict[str, list[str]] = {}
    placed: dict[str, list[str]] = {}
    for part in work["parts"]:
        for d in part["decisions"]:
            if d not in ids:
                found.append(f"{part['id']} names {d}, which is no decision of the tree")
            held.setdefault(d, []).append(part["id"])
        for path in part["paths"]:
            if not under(path, work["paths"]):
                found.append(f"{part['id']}'s path {path} is none of the work's paths")
            placed.setdefault(path, []).append(part["id"])
        if not part["paths"]:
            found.append(f"{part['id']} has no paths")
    for d in ids:
        if d not in held:
            found.append(f"{d} is in no part")
        elif held[d][1:]:
            found.append(f"{d} is in {' and '.join(held[d])}")
    found += [f"{p} is in {' and '.join(at)}" for p, at in placed.items() if at[1:]]
    found += [
        f"the command {c} is not run by `{THROWAWAY}[--file <path>]... -- <command>`, which keeps"
        " the person's own files out of its reach"
        for c in work["commands"]
        if not re.fullmatch(re.escape(THROWAWAY) + r"(--file \S+ )*-- .+", c, re.DOTALL)
    ]
    for part in work["parts"]:
        mine = set(part["decisions"])
        for a, b in joins(tree):
            if a in mine and b in held and b not in mine:
                found.append(
                    f"{a} of {part['id']} is joined to {b} of {' and '.join(held[b])}: a part"
                    " holds every decision joined to its own"
                )
    return found


def remake_faults(remake: dict[str, Any], tree: dict[str, Any]) -> list[str]:
    """Each decision or question the remake names that the tree has not."""
    decisions = {d["id"] for d in tree["decisions"]}
    questions = {q["id"] for q in tree["questions"]}
    found = []
    for item in remake["decisions"]:
        if item["decision"] not in decisions:
            found.append(f"the remake names {item['decision']}, which is no decision of the tree")
        if item["question"] not in questions:
            found.append(f"the remake names {item['question']}, which is no question of the tree")
    return found


def check(run: str) -> list[str]:
    """Each fault of the run's design: the tree's questions against the standard's, then the
    work's parts and the remake, where designer has written them; refuses, by files.Unreadable, a
    file it cannot read."""
    tree = files.load(os.path.join(run, "design-tree.json"), "design-tree")
    kind = files.load(os.path.join(run, "run.json"), "run")["kind"]
    standard = files.load(os.path.join(run, "standard.json"), "standard")
    found = asked(tree, standard, kind)
    work = os.path.join(run, "work.json")
    if os.path.exists(work):
        found += work_faults(files.load(work, "work"), tree)
    remake = os.path.join(run, "remake.json")
    if os.path.exists(remake):
        found += remake_faults(files.load(remake, "remake"), tree)
    return found
