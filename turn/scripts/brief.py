"""What each agent of a run is handed, once the steps before it are done."""

import glob
import os
import shutil
import subprocess
import tempfile

from ccs import entries
from forms import PLACES, check, learned, serves, without_good
from questions import asked, unanswered
from repo import drop
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


def brief(work, n, role):
    """Writes what the agent of the role is handed, once the steps before it are done."""
    if role not in AGENTS:
        raise Stop(f"no brief for {role}; briefs are for {', '.join(AGENTS)}")
    run = read_json(RUN, RUN)
    if int(n) != run["round"]:
        raise Stop(f"round {run['round']} is running")
    n = int(n)
    run, ccs, deliverable, path = the_work(work, n, written=role != "generator")
    here = os.path.join(work, str(n))
    should = {
        "receiver": "; ".join(entries(ccs, "focal_entities", "receiver")),
        "use": "; ".join(entries(ccs, "goal_orientation", "use")),
        "acceptance": entries(ccs, "goal_orientation", "acceptance"),
        "sources": entries(ccs, "retrieved_artifacts", "source"),
        "constraints": [f"{k}: {v}" for e in ccs["constraints"] for k, v in e.items()]
        + [f"answer: {q['question']} {q['answer']}" for q in asked(work) if "answer" in q],
    }
    given = {
        "list": os.path.join(work, "list.json"),
        "work": path,
        "form": os.path.join(here, f"{role}.json"),
        "check": f'cd "{os.getcwd()}" && python3 "{SCRIPT}" check {work} {n} {role}',
    }
    hand_on = read_json(os.path.join(here, "hand-on.json"), "the form")
    if role == "generator":
        if not os.path.isfile(os.path.join(here, "aim.txt")):
            raise Stop(
                f"step 4: set the aim with `up.py aim {work} {n} <text>` and say what it prints, "
                "before the work is written"
            )
        if n == 1 and "from" in run:
            given["started from"] = run["from"]
        sent = [
            serves([dict(p, item=i)], p["way"]) for i, p in hand_on.items() if p.get("met") is False
        ]
        if sent or n == 1:
            ways = sent
        else:
            ways = [
                {k: v for k, v in w.items() if k != "in"}
                for w in learned(work, 1)[0]
                if w["in"] == PLACES[0]
            ]
            should["constraints"] += [f"rule: {r}" for r in learned(work, 1)[1]]
        given.update(should, ways=ways, questions=os.path.join(work, "questions.json"))
    elif role == "first-user":
        unseen = [i for i, p in hand_on.items() if p.get("met") is not True]
        if unanswered(work):
            raise Stop(
                "step 8: wait for the user: "
                + ", ".join(f"question {k} is not answered" for k in unanswered(work))
            )
        if unseen:
            raise Stop(
                "step 8: the work goes back to the generator until every item is seen given; "
                "not yet: " + ", ".join(unseen)
            )
        place = tempfile.mkdtemp(prefix="turn-copy-")
        subprocess.run(["git", "clone", "-q", ".", place], check=True)
        os.makedirs(os.path.dirname(os.path.join(place, deliverable)), exist_ok=True)
        shutil.copyfile(path, os.path.join(place, deliverable))
        given = {
            "copy": place,
            "deliverable": deliverable,
            "receiver": should["receiver"],
            "use": should["use"],
            "list": os.path.abspath(given["list"]),
            "form": given["form"],
            "check": given["check"],
        }
    elif role == "evaluator":
        first = os.path.join(here, "first-user-brief.json")
        if not os.path.isfile(first):
            raise Stop("step 9: the first user has not been handed the work")
        read = records("first-user")
        found = check(work, n, "first-user")
        if found:
            raise Stop("\n".join(found))
        place = read_json(first, "the first user's brief")["copy"]
        if os.path.exists(place):
            drop(place)
        given.update(
            {k: should[k] for k in ("receiver", "use", "acceptance")},
            reading=os.path.join(here, "first-user.json"),
            records=read,
        )
    else:
        found = check(work, n, "orchestrator")
        if found:
            raise Stop("\n".join(found))
        if not without_good(work, n):
            raise Stop("every item is met, so there is nothing to learn")
        given.update(
            should,
            questions=os.path.join(work, "questions.json"),
            reading=os.path.join(here, "first-user.json"),
            decisions=os.path.join(here, "orchestrator.json"),
            records={"first user": records("first-user"), "generator": records("generator")},
        )
    out = os.path.join(here, f"{role}-brief.json")
    write_json(out, given)
    print(out)
