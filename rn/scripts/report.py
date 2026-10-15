"""The report: what was decided for the user, each item as turn judged it, and the document."""

import json
import os


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
    changed = judgments.get("changed", [])
    lines += [f"Changed after turn: {c['lines']}: {c['why']}" for c in changed]
    if changed:
        lines.append(
            "The lines below are as turn read the document; a change above may have moved them."
        )
    return lines


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
    list_ = load(lists[0])
    orchestrator = load(os.path.join(os.path.dirname(lists[0]), "orchestrator.json"))
    titles = {item["id"]: item["title"] for item in list_["items"]}
    lines = ["Decided for you"]
    lines += [f"  {line}" for line in decided(ccs, judgments, titles)] or ["  Nothing."]
    for checklist in list_["checklists"]:
        lines += ["", f"{checklist['checklist']} {checklist['version']}"]
        for item in list_["items"]:
            name, _, short = item["id"].partition(" ")
            if name == checklist["checklist"]:
                met = orchestrator[item["id"]]
                lines.append(
                    f"  ✅ {short} {item['title']}: {met['lines']}"
                    if met["met"]
                    else f"  ⬜ {short} {item['title']}"
                )
    lines += [
        "",
        "The document: " + ", ".join(entries(ccs["focal_entities"], "deliverable")),
        "What it says, item by item: " + ", ".join(entries(ccs["retrieved_artifacts"], "content")),
    ]
    return "\n".join(lines)
