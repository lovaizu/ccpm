"""What each agent of a run is handed, once the steps before it are done."""

import glob
import os

from ccs import entries
from forms import check, serves, without_good
from state import RUN, Stop, read_json, the_work, write_json

AGENTS = {"generator": 4, "first-user": 9, "evaluator": 10, "learner": 12}
SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "up.py")


def records(role):
    """The records Claude Code keeps of the run's last agent of the role."""
    session = read_json(RUN, RUN)["session"]
    found = []
    for meta in glob.glob(
        os.path.join(
            os.path.expanduser("~"),
            ".claude",
            "projects",
            "*",
            session,
            "subagents",
            "agent-*.meta.json",
        )
    ):
        path = meta[: -len(".meta.json")] + ".jsonl"
        if read_json(meta, meta).get("agentType") == f"turn:{role}" and os.path.isfile(path):
            found.append((os.path.getmtime(path), path))
    if not found:
        raise Stop(f"no records of the {role.replace('-', ' ')} in session {session}")
    return max(found)[1]


def brief(work, role):
    """Writes what the agent of the role is handed, once the steps before it are done."""
    if role not in AGENTS:
        raise Stop(f"no brief for {role}; briefs are for {', '.join(AGENTS)}")
    run, ccs, deliverable, path = the_work(work, written=role != "generator")
    should = {
        "receiver": "; ".join(entries(ccs, "focal_entities", "receiver")),
        "use": "; ".join(entries(ccs, "goal_orientation", "use")),
        "acceptance": entries(ccs, "goal_orientation", "acceptance"),
        "content": entries(ccs, "retrieved_artifacts", "content"),
        "references": entries(ccs, "retrieved_artifacts", "reference"),
        "constraints": [f"{k}: {v}" for e in ccs["constraints"] for k, v in e.items()],
    }
    given = {
        "list": os.path.join(work, "list.json"),
        "work": path,
        "form": os.path.join(work, f"{role}.json"),
        "check": f'cd "{os.getcwd()}" && python3 "{SCRIPT}" check {work} {role}',
    }
    hand_on = read_json(os.path.join(work, "hand-on.json"), "the form")
    if role == "generator":
        if not os.path.isfile(os.path.join(work, "aim.txt")):
            raise Stop(
                f"step 4: set the aim with `up.py aim {work} <text>` and say what it prints, "
                "before the work is written"
            )
        sent = [
            serves([dict(p, item=i)], p["way"])
            for i, p in hand_on.items()
            if p.get("met") is False and "question" not in p
        ]
        given.update(
            should, ways=sent or run["ways"], questions=os.path.join(work, "questions.json")
        )
    elif role == "first-user":
        unseen = [i for i, p in hand_on.items() if p.get("met") is not True and "question" not in p]
        if unseen:
            raise Stop(
                "step 8: the work goes back to the generator until every item is seen given or "
                "waits on a question left open; not yet: " + ", ".join(unseen)
            )
        given = {
            "work": path,
            "deliverable": deliverable,
            "opens": entries(ccs, "retrieved_artifacts", "receiver_opens"),
            "receiver": should["receiver"],
            "use": should["use"],
            "list": os.path.abspath(given["list"]),
            "form": given["form"],
            "check": given["check"],
        }
    elif role == "evaluator":
        first = os.path.join(work, "first-user-brief.json")
        if not os.path.isfile(first):
            raise Stop("step 9: the first user has not been handed the work")
        read = records("first-user")
        found = check(work, "first-user")
        if found:
            raise Stop("\n".join(found))
        given.update(
            {k: should[k] for k in ("receiver", "use", "acceptance")},
            reading=os.path.join(work, "first-user.json"),
            records=read,
        )
    else:
        found = check(work, "orchestrator")
        if found:
            raise Stop("\n".join(found))
        if not without_good(work):
            raise Stop("every item is met, so there is nothing to learn")
        given.update(
            should,
            questions=os.path.join(work, "questions.json"),
            reading=os.path.join(work, "first-user.json"),
            decisions=os.path.join(work, "orchestrator.json"),
            records={"first user": records("first-user"), "generator": records("generator")},
        )
    out = os.path.join(work, f"{role}-brief.json")
    write_json(out, given)
    print(out)
