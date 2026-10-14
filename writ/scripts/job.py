"""A job from start to end: the checklists listed, the form laid and settled, the CCS for turn written
from it, and the job closed on what turn returned."""

import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess

from state import JOB, Stop, read_json, write_json

CHECKLISTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "checklists")
USERS = os.path.join(".writ", "checklists")
PLACES = ("deliverable", "receiver", "acceptance")
ASKED = ("answer", "proposal confirmed")
TURNS = (
    "predictive_cue",
    "uncertainty_signal",
    "semantic_gist",
    "relational_map",
    "episodic_trace",
)


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


def start(session, document=""):
    if shutil.which("jq") is None:
        raise Stop(
            "jq is not installed; install it (https://jqlang.org/download/) and call writ again"
        )
    # Found before the first question, so no answer is lost to a document turn will not write over.
    if document and os.path.isfile(document) and changed(document):
        raise Stop(
            f"{document} has changes git does not hold; commit them first, so that what it was "
            "can be got back once writ makes it again"
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
    stamp = os.path.join(".writ", "jobs", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    folder, n = stamp, 1
    while os.path.exists(folder):
        n += 1
        folder = f"{stamp}-{n}"
    os.makedirs(folder)
    job = {"session": session, "folder": folder}
    # A job started inside another, such as one making a checklist, hands back to it when it ends.
    if os.path.isfile(JOB):
        job["within"] = read_json(JOB, JOB)
    write_json(JOB, job)
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
    laid: dict = {
        p: "" for p in ("deliverable", "receiver", "use", "acceptance", "language", "asking")
    }
    laid.update(sources=[], open=[])
    # Laid again with another checklist, the form keeps every place already settled.
    path = os.path.join(folder, "form.json")
    if os.path.isfile(path):
        before = read_json(path, "the form")
        laid.update((k, v) for k, v in before.items() if k in laid)
        items.update((i, v) for i, v in before["items"].items() if i in items)
    laid.update(checklists=list(checklists), items=items)
    write_json(os.path.join(folder, "form.json"), laid)


def ccs(folder):
    settled = read_json(os.path.join(folder, "form.json"), "the form")
    found = [f"{p} is not settled" for p in PLACES if not settled[p].strip()]
    for i, item in settled["items"].items():
        if not item["decision"].strip():
            found.append(f"{i}: the decision is not settled")
        if item["settled"] not in ASKED and not os.path.isfile(item["settled"].split(":")[0]):
            found.append(f"{i}: say where it is settled: answer, proposal confirmed, or a file")
    found += [f"{o['item']} is open: {o['question']}" for o in settled["open"]]
    if settled["asking"]:
        found.append(f"a question waits on the user: {settled['asking']}")
    if found:
        raise Stop("\n".join(found))
    n = calls(folder) + 1
    by_turn(folder, settled["deliverable"], n - 1)
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
    ours = {
        "focal_entities": [
            {"deliverable": settled["deliverable"]},
            {"receiver": settled["receiver"]},
        ],
        "goal_orientation": [{k: settled[k]} for k in ("use", "acceptance") if settled[k]],
        "retrieved_artifacts": [{"viewpoint": p} for p in settled["checklists"]]
        + [{"source": p} for p in [decisions] + settled["sources"]],
        "constraints": [{"language": settled["language"]}] if settled["language"] else [],
    }
    given = {p: [] for p in TURNS}
    if n > 1:
        # turn is called again with the CCS it returned: its own parts as they are, and writ's
        # parts, which turn keeps first in constraints, taken again from the form.
        before = read_json(os.path.join(folder, f"in-{n - 1}.json"), "the last CCS")
        given = read_json(os.path.join(folder, f"out-{n - 1}.json"), "what turn returned")
        given["constraints"] = given["constraints"][len(before["constraints"]) :]
    ours["constraints"] += given.pop("constraints", [])
    given.update(ours)
    write_json(os.path.join(folder, f"in-{n}.json"), given)
    # The hook on turn's call checks that turn is called with this CCS, as the script wrote it.
    job = read_json(JOB, JOB)
    job["given"] = [
        os.path.join(folder, f"in-{n}.json"),
        digest(os.path.join(folder, f"in-{n}.json")),
    ]
    write_json(JOB, job)
    print(
        f"in: {os.path.join(folder, f'in-{n}.json')}\nout: {os.path.join(folder, f'out-{n}.json')}"
    )


def calls(folder):
    """How many times turn has returned in the job."""
    n = 0
    while os.path.isfile(os.path.join(folder, f"out-{n + 1}.json")):
        n += 1
    return n


def end(folder, out=""):
    n = calls(folder)
    returned = os.path.join(folder, f"out-{max(n, 1)}.json")
    if not n:
        raise Stop(f"{returned} is not there; call turn with the CCS first")
    ccs = read_json(returned, returned)
    deliverable = ccs["focal_entities"][0]["deliverable"]
    by_turn(folder, deliverable, n)
    if ccs["predictive_cue"] != [{"next": "done"}]:
        left = [i for i, d in decisions_of(ccs).items() if not d["met"]]
        if out:
            write_json(out, {"next": "not met", "document": deliverable, "not met": left})
        close()
        print(f"{deliverable} is written; not met: {', '.join(left)}. No report is made.")
        return
    report = made_report(folder, ccs)
    with open(os.path.join(folder, "report.md"), "w") as f:
        f.write(report)
    if out:
        write_json(out, {"next": "done", "document": deliverable, "report": f.name})
    close()
    print(
        f"{deliverable} is written, and every item of the checklists is met. The report, with the "
        f"lines that meet each item:\n\n{report}"
    )


def decisions_of(ccs):
    """turn's decision on each item, from the evidence the CCS it returned points to."""
    evidence = {
        os.path.basename(v): v
        for e in ccs["episodic_trace"]
        for k, v in e.items()
        if k == "evidence"
    }
    return read_json(evidence["orchestrator.json"], "turn's decisions")


def made_report(folder, ccs):
    """Under each checklist, every item with the lines of its Good, as turn's evidence gives them."""
    decided = decisions_of(ccs)
    More = [i for i, d in decided.items() if not d["met"]]
    if More:
        raise Stop(
            "\n".join(f"{i} is not met in turn's evidence, so no report is made" for i in More)
        )
    lines = []
    for path in read_json(os.path.join(folder, "form.json"), "the form")["checklists"]:
        named = front(path)
        title, items = headings(path)
        lines.append(f"{title} {named['version']}")
        name = named["name"]
        lines += [
            f"  ✅ {i} {t}: lines {decided[name + ' ' + i]['lines']}" for i, t in items.items()
        ]
    return "\n".join(lines) + "\n"


def close():
    """Closes the job, opening again the job it was started inside, if any."""
    within = read_json(JOB, JOB).get("within")
    if within:
        write_json(JOB, within)
    else:
        os.remove(JOB)


def back(folder, out):
    """Hands the open points back to the plugin whose step called writ, each with the answer writ
    recommends, for the plugin to decide and call writ again."""
    points = read_json(os.path.join(folder, "form.json"), "the form")["open"]
    if not points:
        raise Stop("no point is open; run ccs and call turn")
    write_json(out, {"next": "decide", "open": points})
    close()


def changed(*paths):
    """The files git does not hold as committed, among the paths given, or anywhere."""
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all", "--", *paths],
        check=False,
        capture_output=True,
        text=True,
    ).stdout
    return [line[3:] for line in status.splitlines()]


def digest(path):
    with open(path, "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()


def by_turn(folder, deliverable, n):
    """Stops when the document is not as turn left it: as git holds it before turn's first return,
    and as the work turn returned last after it."""
    if n:
        ccs = read_json(os.path.join(folder, f"out-{n}.json"), "what turn returned")
        work = next(v for e in ccs["episodic_trace"] for k, v in e.items() if k == "work")
        kept = os.path.isfile(deliverable) and digest(deliverable) == digest(work)
    else:
        kept = not changed(deliverable)
    if not kept:
        raise Stop(
            f"{deliverable} was written outside turn; the document is written by turn alone, so "
            "put it back as turn left it"
        )
