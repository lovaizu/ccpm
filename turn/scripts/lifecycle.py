"""A run from start to end: started on a CCS, and ended or stopped with the work and a CCS written
back."""

import filecmp
import glob
import json
import os
import shutil

from ccs import checklist, deliverables, entries, faults, should
from forms import PLACES, forms, lay, learned
from questions import left_open, question_faults
from repo import changed, elsewhere, git
from state import CLOSING, RUN, Stop, read_json, the_work, write_json

CALLERS = ("focal_entities", "goal_orientation", "retrieved_artifacts", "constraints")
TURNS = (
    "predictive_cue",
    "uncertainty_signal",
    "semantic_gist",
    "relational_map",
    "episodic_trace",
)


def kept(deliverable):
    """Whether a run's evidence keeps the file where the work goes as it stands, at that very path,
    so writing over it loses nothing."""
    return any(
        filecmp.cmp(path, deliverable, shallow=False)
        for pattern in (("*", "work"), ("*", "2", "work"))
        for path in glob.glob(os.path.join(".turn", *pattern, deliverable))
    )


def start(src, out, session, work=None, before=None, questions=(), begun=None, ways=(), rules=()):
    """Starts a run on a CCS, making the work anew from the caller's inputs; a run's second round
    starts in a folder of the first's, from the work the first made and the ways it found, with what
    the repository held before the first and the questions it left open."""
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
    # What is there is written over only when git holds it, or a run's evidence keeps it as it
    # stands, so what was there can be got back.
    for deliverable in deliverables(ccs):
        if (
            git("status", "--porcelain", "--ignored", "--", deliverable)
            and os.path.isfile(deliverable)
            and not kept(deliverable)
        ):
            raise Stop(
                f"{deliverable} has changes git does not hold; commit or remove them, so that what "
                "was there can be got back once turn writes the work there"
            )
    before = changed() if before is None else before
    work = work or os.path.join(".turn", os.path.splitext(os.path.basename(out))[0])
    paths = [os.path.join(work, "work", d) for d in deliverables(ccs)]
    lists = [checklist(p) for p in entries(ccs, "retrieved_artifacts", "checklist")]
    listed = {
        "checklists": [c for c, _ in lists],
        "items": [i for _, items in lists for i in items],
    }
    write_json(os.path.join(work, "list.json"), listed)
    laid = forms([i["id"] for i in listed["items"]])
    lay(work, laid)
    write_json(
        os.path.join(work, "questions.json"), [{"question": q, "ask": True} for q in questions]
    )
    run = {
        "session": session,
        "work": work,
        "in": src,
        "out": out,
        "ways": list(ways),
        "rules": list(rules),
        "before": before,
    }
    if begun is not None:
        run["second"] = True
        for deliverable, path in zip(deliverables(ccs), paths):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            shutil.copyfile(os.path.join(begun, "work", deliverable), path)
    write_json(RUN, run)
    print(
        json.dumps(
            {
                "folder": work,
                "list": os.path.join(work, "list.json"),
                "work": paths,
                "hand-on": os.path.join(work, "hand-on.json"),
                "orchestrator": os.path.join(work, "orchestrator.json"),
                "questions": os.path.join(work, "questions.json"),
                **should(ccs),
            },
            indent=1,
            ensure_ascii=False,
        )
    )


def end(work):
    left, learnt = learned(work)
    found = question_faults(work, decided=True)
    if found:
        raise Stop("\n".join(found))
    run, ccs, goes, paths = the_work(work)
    rules = list(dict.fromkeys(run.get("rules", []) + learnt))
    items = {i["id"]: i for i in read_json(os.path.join(work, "list.json"), "the list")["items"]}
    questions = left_open(work)
    unmet = [
        {"unmet": f"{i} ({items[i]['text'].splitlines()[0]}): {w['way']}"}
        for w in left
        for i in w["items"]
    ]
    caller = [f"{i}: {w['way']}" for w in left if w["in"] == PLACES[1] for i in w["items"]]
    if not questions and not unmet:
        nxt = "done"
    elif caller and not questions:
        nxt = f"to the caller: {'; '.join(caller)}"
    else:
        nxt = "ask the user"
    evidence = ["orchestrator.json"] + (["learner.json"] if left else [])
    if any(w["in"] == PLACES[0] for w in left) and not run.get("second"):
        # The first round left ways in the work: the run reads the work a second time, made again
        # on those ways from the work as it stands.
        ways = [{k: v for k, v in w.items() if k != "in"} for w in left if w["in"] == PLACES[0]]
        os.remove(RUN)
        start(
            run["in"],
            run["out"],
            run["session"],
            os.path.join(work, "2"),
            run["before"],
            questions,
            work,
            ways,
            rules,
        )
        return
    # The work reaches where it goes only now, as the run returns, so a run stopped or cut off
    # leaves it as it was.
    for deliverable, path in zip(goes, paths):
        os.makedirs(os.path.dirname(deliverable) or ".", exist_ok=True)
        shutil.copyfile(path, deliverable)
    write_json(
        run["out"],
        returned(
            ccs,
            predictive_cue=[{"next": nxt}],
            semantic_gist=[{"question": q} for q in questions]
            + unmet
            + [{"rule": r} for r in rules],
            episodic_trace=[{"evidence": os.path.join(work, e)} for e in ["list.json"] + evidence],
        ),
    )
    where = ", ".join(goes)
    if questions:
        points = "one point" if len(questions) == 1 else f"{len(questions)} points"
        said = [f"The work is at {where}, waiting on you for {points}."]
        said += [f"❓ {q}" for q in questions]
    elif nxt == "ask the user":
        said = [f"The work is at {where}, with what it does not give yet in the CCS."]
    else:
        said = [nxt, f"The work is at {where}."]
    close(work, said + elsewhere(run, goes))


def returned(ccs, **turns):
    """The CCS written back: the caller's four parts as received, and turn's five holding only what
    this run gives."""
    return {
        **{part: ccs[part] for part in CALLERS},
        **{part: turns.get(part, []) for part in TURNS},
    }


def close(work, lines):
    """Closes the run, keeping its last lines for the console to show once."""
    with open(os.path.join(work, CLOSING), "w") as f:
        f.write("\n".join(lines))
    os.remove(RUN)
    print("\n".join(lines))


def stop(work):
    """Ends a run the user stopped, with a CCS saying where it was."""
    if not os.path.isfile(RUN):
        raise Stop("no run is open, so there is nothing to stop")
    run, ccs, goes, _ = the_work(work, written=False)
    step = (
        "check"
        if os.path.isfile(os.path.join(work, "evaluator-brief.json"))
        else "read"
        if os.path.isfile(os.path.join(work, "first-user-brief.json"))
        else "write"
    )
    write_json(run["out"], returned(ccs, predictive_cue=[{"next": f"stopped: {step}"}]))
    close(work, [f"stopped: {step} — CCS: {run['out']}"] + elsewhere(run, goes))
