"""A job from start to end: the checklists listed, the form laid and settled, the CCS for turn written
from it, and the job closed on what turn returned."""

import datetime
import json
import os
import re
import shutil

from state import JOB, Stop, read_json, write_json

CHECKLISTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "checklists")
USERS = os.path.join(".writ", "checklists")
PLACES = ("deliverable", "receiver", "acceptance")
ASKED = ("answer", "proposal confirmed")


def front(path):
    """The fields of the front matter the file opens with."""
    with open(path) as f:
        lines = f.read().splitlines()
    if lines[:1] != ["---"] or "---" not in lines[1:]:
        return {}
    fields = (re.match(r"(\w+):\s*(.*)", line) for line in lines[1 : lines.index("---", 1)])
    return dict(m.groups() for m in fields if m)


def headings(path):
    """The checklist's title and each item's ID and title, leaving out fenced examples."""
    title, items, fence = "", {}, False
    with open(path) as f:
        for line in f:
            if line.startswith("```"):
                fence = not fence
            elif not fence:
                item = re.match(r"### ([A-Z]-\d+): (.+)", line)
                if item:
                    items[item.group(1)] = item.group(2).strip()
                elif line.startswith("# ") and not title:
                    title = line[2:].strip()
    return title, items


def start(session):
    if shutil.which("jq") is None:
        raise Stop(
            "jq is not installed; install it (https://jqlang.org/download/) and call writ again"
        )
    listed = []
    for whose, place in (("writ", CHECKLISTS), ("the user", USERS)):
        names = sorted(os.listdir(place)) if os.path.isdir(place) else []
        for name in names:
            path = os.path.join(place, name)
            named = front(path)
            listed.append(
                {
                    "path": path,
                    "name": named.get("name", ""),
                    "version": named.get("version", ""),
                    "title": headings(path)[0],
                    "whose": whose,
                }
            )
    folder = os.path.join(".writ", "jobs", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    os.makedirs(folder, exist_ok=True)
    write_json(JOB, {"session": session, "folder": folder})
    print(json.dumps({"folder": folder, "checklists": listed}, indent=1, ensure_ascii=False))


def form(folder, *checklists):
    found = [f"{p} is not there" for p in checklists if not os.path.isfile(p)]
    found += [
        f"{p} does not open with a name and a version"
        for p in checklists
        if os.path.isfile(p) and not {"name", "version"} <= front(p).keys()
    ]
    if found:
        raise Stop("\n".join(found))
    items = {
        f"{front(p)['name']} {i}": {"title": t, "decision": "", "settled": ""}
        for p in checklists
        for i, t in headings(p)[1].items()
    }
    laid: dict = {p: "" for p in ("deliverable", "receiver", "use", "acceptance", "language")}
    laid.update(sources=[], checklists=list(checklists), items=items)
    write_json(os.path.join(folder, "form.json"), laid)


def ccs(folder):
    settled = read_json(os.path.join(folder, "form.json"), "the form")
    found = [f"{p} is not settled" for p in PLACES if not settled[p].strip()]
    for i, item in settled["items"].items():
        if not item["decision"].strip():
            found.append(f"{i}: the decision is not settled")
        if item["settled"] not in ASKED and not os.path.isfile(item["settled"].split(":")[0]):
            found.append(f"{i}: say where it is settled: answer, proposal confirmed, or a file")
    if found:
        raise Stop("\n".join(found))
    decisions = os.path.join(folder, "decisions.md")
    with open(decisions, "w") as f:
        f.write(
            f"# What {settled['deliverable']} gives its reader\n\n"
            "For each item of the checklists, what the document gives, settled before it is "
            "written, and where it was settled.\n"
        )
        for i, item in settled["items"].items():
            f.write(
                f"\n## {i}: {item['title']}\n\n{item['decision']}\n\nSettled by: {item['settled']}\n"
            )
    given = os.path.join(folder, "in-1.json")
    write_json(
        given,
        {
            "focal_entities": [
                {"deliverable": settled["deliverable"]},
                {"receiver": settled["receiver"]},
            ],
            "goal_orientation": [{k: settled[k]} for k in ("use", "acceptance") if settled[k]],
            "retrieved_artifacts": [{"viewpoint": p} for p in settled["checklists"]]
            + [{"source": p} for p in [decisions] + settled["sources"]],
            "constraints": [{"language": settled["language"]}] if settled["language"] else [],
            "predictive_cue": [],
            "uncertainty_signal": [],
            "semantic_gist": [],
            "relational_map": [],
            "episodic_trace": [],
        },
    )
    print(f"in: {given}\nout: {os.path.join(folder, 'out-1.json')}")


def end(folder):
    returned = os.path.join(folder, "out-1.json")
    if not os.path.isfile(returned):
        raise Stop(f"{returned} is not there; call turn with the CCS first")
    ccs = read_json(returned, returned)
    deliverable = ccs["focal_entities"][0]["deliverable"]
    os.remove(JOB)
    print(f"{deliverable} is written.")
