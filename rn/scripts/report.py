"""The report: what was decided for the user, each item as turn judged it, with its lines as they
stand in the document handed back, and the document."""

import difflib
import json
import os
import re


def load(path):
    with open(path, encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            raise ValueError(f"{path} is not JSON; give the file as turn or the conductor wrote it")


def entries(part, kind):
    return [entry[kind] for entry in part if kind in entry]


def decided(ccs, judgments, titles):
    gist = ccs["semantic_gist"]
    lines = [f"{d['point']}: {d['ground']}" for d in judgments.get("decided", [])]
    questions = {q["question"]: q["judged"] for q in judgments.get("questions", [])}
    for question in entries(gist, "question"):
        if question not in questions:
            raise ValueError(f"judge the question first: {question}")
        lines.append(f"Question: {question}: {questions[question]}")
    items = {u["item"]: u["judged"] for u in judgments.get("unmet", [])}
    for unmet in entries(gist, "unmet"):
        item = unmet.split(" (", 1)[0]
        if item not in items:
            raise ValueError(f"judge the item first: {item}")
        lines.append(f"Not met: {item} {titles[item]}: {items[item]}")
        lines.append(f"  turn: {unmet.split('): ', 1)[1]}")
    lines += [f"Rule from turn: {rule}" for rule in entries(gist, "rule")]
    lines += [f"Changed after turn: {c['lines']}: {c['why']}" for c in judgments.get("changed", [])]
    return lines


def mapping(kept, now):
    """Each line number of the document as turn kept it, to its number as the document stands now,
    or None where the line is gone."""
    with open(kept, encoding="utf-8") as f:
        old = f.read().splitlines()
    with open(now, encoding="utf-8") as f:
        new = f.read().splitlines()
    moved = {}
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, old, new).get_opcodes():
        for k in range(i2 - i1):
            moved[i1 + k + 1] = j1 + k + 1 if tag == "equal" else None
    return moved


def ranges(numbers):
    """Line numbers as turn writes them, such as `3-5, 12`."""
    found = []
    for n in numbers:
        if found and found[-1][1] == n - 1:
            found[-1][1] = n
        else:
            found.append([n, n])
    return ", ".join(str(a) if a == b else f"{a}-{b}" for a, b in found)


def as_they_stand(lines, maps, only):
    """The lines an item names, each file's ranges mapped to where they now stand; `changed after
    turn` where none of them survive."""
    segments = []
    for segment in lines.split(";"):
        path, colon, spans = segment.strip().rpartition(":")
        path = path.strip() if colon else only
        numbers = [
            n
            for a, b in re.findall(r"(\d+)(?:\s*-\s*(\d+))?", spans)
            for n in range(int(a), int(b or a) + 1)
        ]
        if path not in maps:
            segments.append(segment.strip())
            continue
        kept = [maps[path].get(n) for n in numbers]
        survived = ranges(n for n in kept if n)
        segments.append((f"{path}:" if colon else "") + survived if survived else "")
    return "; ".join(s for s in segments if s) or "changed after turn"


def make(ccs_path, judgments_path):
    ccs = load(ccs_path)
    judgments = load(judgments_path)
    evidence = entries(ccs["episodic_trace"], "evidence")
    lists = [path for path in evidence if path.endswith("list.json")]
    if not lists:
        raise ValueError(
            f"{ccs_path} names no evidence; turn was stopped, so there is no report to make; "
            "call turn again to get one"
        )
    folder = os.path.dirname(lists[0])
    list_ = load(lists[0])
    orchestrator = load(os.path.join(folder, "orchestrator.json"))
    titles = {item["id"]: item["title"] for item in list_["items"]}
    goes = entries(ccs["focal_entities"], "deliverable")
    maps = {
        d: mapping(os.path.join(folder, "kept", d), d)
        for d in goes
        if os.path.isfile(os.path.join(folder, "kept", d)) and os.path.isfile(d)
    }
    lines = ["Decided for you"]
    lines += [f"  {line}" for line in decided(ccs, judgments, titles)] or ["  Nothing."]
    if len(maps) < len(goes):
        lines.append("  Lines are as turn read the document.")
    for checklist in list_["checklists"]:
        lines += ["", f"{checklist['checklist']} {checklist['version']}"]
        for item in list_["items"]:
            name, _, short = item["id"].partition(" ")
            if name == checklist["checklist"]:
                met = orchestrator[item["id"]]
                lines.append(
                    f"  ✅ {short} {item['title']}: "
                    f"{as_they_stand(met['lines'], maps, goes[0] if len(goes) == 1 else '')}"
                    if met["met"]
                    else f"  ⬜ {short} {item['title']}"
                )
    lines += [
        "",
        "The document: " + ", ".join(goes),
        "What it says, item by item: " + ", ".join(entries(ccs["retrieved_artifacts"], "content")),
    ]
    return "\n".join(lines)
