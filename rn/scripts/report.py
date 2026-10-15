"""The report the conductor hands back with the work: first what the caller decides, then each item as
turn decided it, so an item shows met only where turn's evidence shows it."""

import json
import os

from checklists import Stop


def read(path):
    try:
        with open(path) as f:
            return json.load(f)
    except ValueError:
        raise Stop(f"{path} is not JSON")


def entries(ccs, part, kind):
    return [v for e in ccs[part] for k, v in e.items() if k == kind]


def judged(given, key, name, found, what):
    """The judgment given on each thing turn returned, or a stop naming the first left unjudged."""
    said = {j[key]: j["judged"] for j in given.get(name, [])}
    for thing in found:
        if thing not in said:
            raise Stop(f"judge the {what} first: {thing}")
    return said


def report(back, judgments):
    """Prints the report from turn's CCS back, its evidence and the conductor's judgments."""
    ccs, given = read(back), read(judgments)
    evidence = [p for p in entries(ccs, "episodic_trace", "evidence") if p.endswith("list.json")]
    if not evidence:
        raise Stop(f"{back} names no evidence; turn was stopped, so there is no report to make")
    folder = os.path.dirname(evidence[0])
    listed = read(os.path.join(folder, "list.json"))
    decided = read(os.path.join(folder, "orchestrator.json"))
    titles = {i["id"]: i["title"] for i in listed["items"]}
    questions = entries(ccs, "semantic_gist", "question")
    unmet = {
        u.partition(" (")[0]: u.partition("): ")[2] for u in entries(ccs, "semantic_gist", "unmet")
    }
    asked = judged(given, "question", "questions", questions, "question")
    left = judged(given, "item", "unmet", unmet, "item")
    first = [f"  {d['point']}: {d['ground']}" for d in given.get("decided", [])]
    first += [f"  Question: {q}: {asked[q]}" for q in questions]
    for item, way in unmet.items():
        first += [f"  Not met: {item} {titles[item]}: {left[item]}", f"    turn: {way}"]
    first += [f"  Rule from turn: {r}" for r in entries(ccs, "semantic_gist", "rule")]
    first += [f"  Changed after turn: {c['lines']}: {c['why']}" for c in given.get("changed", [])]
    if given.get("changed"):
        first.append(
            "  The lines below are as turn read the document; a change above may have moved them."
        )
    lines = ["Decided for you"] + (first or ["  Nothing."])
    for c in listed["checklists"]:
        lines += ["", f"{c['checklist']} {c['version']}"]
        for i in listed["items"]:
            if i["id"].split()[0] == c["checklist"]:
                short = i["id"].split()[1]
                place = decided.get(i["id"], {})
                lines.append(
                    f"  ✅ {short} {i['title']}: {place['lines']}"
                    if place.get("met")
                    else f"  ⬜ {short} {i['title']}"
                )
    lines += [
        "",
        f"The document: {', '.join(entries(ccs, 'focal_entities', 'deliverable'))}",
        "What it says, item by item: " + ", ".join(entries(ccs, "retrieved_artifacts", "content")),
    ]
    print("\n".join(lines))
