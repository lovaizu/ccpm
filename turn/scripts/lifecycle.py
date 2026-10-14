"""A run from start to end: started on a CCS, taken to its second round, and ended or stopped with
the work and a CCS written back."""

import filecmp
import json
import os
import shutil

from ccs import checklist, entries, faults
from forms import PLACES, forms, lay, learned
from questions import left_open, question_faults
from repo import changed, drop, elsewhere, git
from state import CLOSING, RUN, Stop, read_json, the_work, write_json


def start(src, out, session):
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
    for path in begun:
        if not os.path.isfile(path):
            raise Stop(f"{path} is not there, so the run cannot start from it")
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
    before = changed()
    work = os.path.join(".turn", os.path.splitext(os.path.basename(out))[0])
    lists = [checklist(p) for p in entries(ccs, "retrieved_artifacts", "viewpoint")]
    listed = {
        "checklists": [c for c, _ in lists],
        "items": [i for _, items in lists for i in items],
    }
    write_json(os.path.join(work, "list.json"), listed)
    laid = forms([i["id"] for i in listed["items"]])
    lay(work, 1, laid)
    write_json(os.path.join(work, "questions.json"), [])
    run = {"session": session, "work": work, "in": src, "out": out, "round": 1, "before": before}
    for path in begun:
        shutil.copyfile(path, os.path.join(work, "1", os.path.basename(deliverable)))
        run["from"] = path
    write_json(RUN, run)
    print(
        json.dumps(
            {
                "folder": work,
                "list": os.path.join(work, "list.json"),
                "round": 1,
                "work": os.path.join(work, "1", os.path.basename(deliverable)),
                "hand-on": os.path.join(work, "1", "hand-on.json"),
                "orchestrator": os.path.join(work, "1", "orchestrator.json"),
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


def round_two(work):
    run = read_json(RUN, RUN)
    if run["round"] != 1:
        raise Stop("a run has two rounds at most")
    given, _ = learned(work, 1)
    found = question_faults(work, decided=True)
    if found:
        raise Stop("\n".join(found))
    if not any(w["in"] == PLACES[0] for w in given):
        raise Stop("no way for the generator to take, so the run ends after round 1")
    _, _, _, path = the_work(work, 1)
    lay(
        work,
        2,
        forms([i["id"] for i in read_json(os.path.join(work, "list.json"), "the list")["items"]]),
    )
    made = os.path.join(work, "2", os.path.basename(path))
    shutil.copyfile(path, made)
    run["round"] = 2
    write_json(RUN, run)
    print(json.dumps({"round": 2, "work": made}))


def end(work, n):
    n = int(n)
    left, _ = learned(work, n)
    found = question_faults(work, decided=True)
    if found:
        raise Stop("\n".join(found))
    if n == 1 and any(w["in"] == PLACES[0] for w in left):
        raise Stop("a way lies with the generator: start the second round")
    run, ccs, deliverable, path = the_work(work, n)
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
    for k in range(1, n + 1):
        for rule in learned(work, k)[1]:
            if {"rule": rule} not in ccs["constraints"]:
                ccs["constraints"].append({"rule": rule})
    evidence = [
        os.path.join(str(n), e) for e in ["orchestrator.json"] + (["learner.json"] if left else [])
    ]
    os.makedirs(os.path.dirname(deliverable) or ".", exist_ok=True)
    shutil.copyfile(path, deliverable)
    ccs.update(
        predictive_cue=[{"next": nxt}],
        semantic_gist=differences,
        episodic_trace=[{"work": path}]
        + [{"evidence": os.path.join(work, e)} for e in ["list.json"] + evidence],
    )
    write_json(run["out"], ccs)
    if questions:
        points = "one point" if len(questions) == 1 else f"{len(questions)} points"
        said = [f"The work is at {deliverable}, waiting on you for {points}."]
        said += [f"❓ {q}" for q in questions]
    else:
        said = [nxt, f"The work is at {deliverable}."]
        if nxt == "ask the user":
            said.append("❓ Run turn again on what is still missing, or take the work as it is?")
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
    run, ccs, deliverable, path = the_work(work, read_json(RUN, RUN)["round"], written=False)
    n, here = run["round"], os.path.join(work, str(run["round"]))
    step = (
        "check"
        if os.path.isfile(os.path.join(here, "evaluator-brief.json"))
        else "read"
        if os.path.isfile(os.path.join(here, "first-user-brief.json"))
        else "write"
    )
    if step == "write":
        begun = the_work(work, 1)[3] if n == 2 else run.get("from")
    else:
        begun = path
    first = os.path.join(here, "first-user-brief.json")
    if os.path.isfile(first) and os.path.exists(read_json(first, "the first user's brief")["copy"]):
        drop(read_json(first, "the first user's brief")["copy"])
    ccs.update(
        predictive_cue=[{"next": f"stopped: round {n}, {step}"}],
        semantic_gist=[],
        episodic_trace=[{"work": begun}] if begun else [],
    )
    write_json(run["out"], ccs)
    close(work, [f"stopped: round {n}, {step} — CCS: {run['out']}"] + elsewhere(run, deliverable))
