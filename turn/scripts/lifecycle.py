"""A run from start to end: started on a CCS, and ended or stopped with the work and a CCS written
back."""

import filecmp
import json
import os
import shutil

from ccs import checklist, entries, faults
from forms import PLACES, forms, lay, learned, ways_in
from questions import left_open, question_faults
from repo import changed, drop, elsewhere, git
from state import CLOSING, RUN, Stop, read_json, the_work, write_json


def start(src, out, session, work=None, before=None):
    """Starts a run on a CCS; a run's second reading starts in a folder of the first's, with what the
    repository held before the first."""
    if os.path.exists(out):
        raise Stop(f"{out} already exists; turn never writes over a file, so name a new out")
    if shutil.which("jq") is None:
        raise Stop(
            "jq is not installed; install it (https://jqlang.org/download/) and run turn again"
        )
    ccs = read_json(src, src)
    found = faults(ccs)
    if found:
        raise Stop("\n".join(found))
    deliverable = entries(ccs, "focal_entities", "deliverable")[0]
    begun = entries(ccs, "episodic_trace", "work")
    # A run called again on what a run returned makes the work again on the ways that lie in it.
    taken = [e for e in entries(ccs, "episodic_trace", "evidence") if e.endswith("learner.json")]
    for path in begun + taken:
        if not os.path.isfile(path):
            raise Stop(f"{path} is not there, so the run cannot start from it")
    ways = [
        {k: v for k, v in w.items() if k != "in"}
        for path in taken
        for w in ways_in(path)[0]
        if w["in"] == PLACES[0]
    ]
    # What is there is written over only when git holds it, or when it is the work a run returned
    # with this CCS, unchanged since, which that run's evidence keeps.
    if (
        git("status", "--porcelain", "--ignored", "--", deliverable)
        and os.path.isfile(deliverable)
        and not any(filecmp.cmp(path, deliverable, shallow=False) for path in begun)
    ):
        raise Stop(
            f"{deliverable} has changes git does not hold; commit or remove them, so that what was "
            "there can be got back once turn writes the work there"
        )
    second = work is not None
    before = changed() if before is None else before
    work = work or os.path.join(".turn", os.path.splitext(os.path.basename(out))[0])
    lists = [checklist(p) for p in entries(ccs, "retrieved_artifacts", "viewpoint")]
    listed = {
        "checklists": [c for c, _ in lists],
        "items": [i for _, items in lists for i in items],
    }
    write_json(os.path.join(work, "list.json"), listed)
    laid = forms([i["id"] for i in listed["items"]])
    lay(work, laid)
    write_json(os.path.join(work, "questions.json"), [])
    run = {"session": session, "work": work, "in": src, "out": out, "ways": ways, "before": before}
    if second:
        run["second"] = True
    for path in begun:
        shutil.copyfile(path, os.path.join(work, os.path.basename(deliverable)))
        run["from"] = path
    write_json(RUN, run)
    print(
        json.dumps(
            {
                "folder": work,
                "list": os.path.join(work, "list.json"),
                "work": os.path.join(work, os.path.basename(deliverable)),
                "hand-on": os.path.join(work, "hand-on.json"),
                "orchestrator": os.path.join(work, "orchestrator.json"),
                "questions": os.path.join(work, "questions.json"),
                "receiver": "; ".join(entries(ccs, "focal_entities", "receiver")),
                "use": "; ".join(entries(ccs, "goal_orientation", "use")),
                "acceptance": entries(ccs, "goal_orientation", "acceptance"),
                "sources": entries(ccs, "retrieved_artifacts", "source"),
                "constraints": [f"{k}: {v}" for e in ccs["constraints"] for k, v in e.items()],
            },
            indent=1,
            ensure_ascii=False,
        )
    )


def end(work):
    left, rules = learned(work)
    found = question_faults(work, decided=True)
    if found:
        raise Stop("\n".join(found))
    run, ccs, deliverable, path = the_work(work)
    items = {i["id"]: i for i in read_json(os.path.join(work, "list.json"), "the list")["items"]}
    questions = left_open(work)
    differences = [{"difference": q} for q in questions] + [
        {"difference": f"{i} ({items[i]['text'].splitlines()[0]}): {w['way']}"}
        for w in left
        for i in w["items"]
    ]
    caller = [f"{i}: {w['way']}" for w in left if w["in"] == PLACES[1] for i in w["items"]]
    if not differences:
        nxt = "done"
    elif caller and not questions:
        nxt = f"to the caller: {'; '.join(caller)}"
    else:
        nxt = "ask the user"
    for rule in rules:
        if {"rule": rule} not in ccs["constraints"]:
            ccs["constraints"].append({"rule": rule})
    evidence = ["orchestrator.json"] + (["learner.json"] if left else [])
    os.makedirs(os.path.dirname(deliverable) or ".", exist_ok=True)
    shutil.copyfile(path, deliverable)
    ccs.update(
        predictive_cue=[{"next": nxt}],
        semantic_gist=differences,
        episodic_trace=[{"work": path}]
        + [{"evidence": os.path.join(work, e)} for e in ["list.json"] + evidence],
    )
    if nxt == "ask the user" and not questions and not run.get("second"):
        # The first reading left ways only in the work: the run reads the work a second time, as
        # the caller would call turn again on what the first returned.
        again = os.path.join(work, "again.json")
        write_json(again, ccs)
        os.remove(RUN)
        start(again, run["out"], run["session"], os.path.join(work, "2"), run["before"])
        return
    write_json(run["out"], ccs)
    if questions:
        points = "one point" if len(questions) == 1 else f"{len(questions)} points"
        said = [f"The work is at {deliverable}, waiting on you for {points}."]
        said += [f"❓ {q}" for q in questions]
    elif nxt == "ask the user":
        said = [f"The work is at {deliverable}; running again can give what is not yet there."]
    else:
        said = [nxt, f"The work is at {deliverable}."]
    close(work, said + elsewhere(run, deliverable))


def close(work, lines):
    """Closes the run, keeping its last lines for the console to show once."""
    with open(os.path.join(work, CLOSING), "w") as f:
        f.write("\n".join(lines))
    os.remove(RUN)
    print("\n".join(lines))


def stop(work):
    """Ends a run the user stopped, with a CCS saying where it was and the work as it stands."""
    if not os.path.isfile(RUN):
        raise Stop("no run is open, so there is nothing to stop")
    run, ccs, deliverable, path = the_work(work, written=False)
    step = (
        "check"
        if os.path.isfile(os.path.join(work, "evaluator-brief.json"))
        else "read"
        if os.path.isfile(os.path.join(work, "first-user-brief.json"))
        else "write"
    )
    begun = run.get("from") if step == "write" else path
    first = os.path.join(work, "first-user-brief.json")
    if os.path.isfile(first) and os.path.exists(read_json(first, "the first user's brief")["copy"]):
        drop(read_json(first, "the first user's brief")["copy"])
    ccs.update(
        predictive_cue=[{"next": f"stopped: {step}"}],
        semantic_gist=[],
        episodic_trace=[{"work": begun}] if begun else [],
    )
    write_json(run["out"], ccs)
    close(work, [f"stopped: {step} — CCS: {run['out']}"] + elsewhere(run, deliverable))
