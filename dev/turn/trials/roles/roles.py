"""Tries each of turn's four roles on its own: the real role and its lanes, started by a stand-in for
the orchestrator with the prompt the flow gives it, on the flow trial's task of two items, one
answered at its part and one in each part. Between the roles the run is set as a trial means: the
orchestrator's check finds each item's Good in the decisions, the generator's work is replaced by a
set README that names no license, the evaluator is given the first user's Goods, and the learner is
given B-1 without Good and the records of the three roles before it. Prints, for each role, its
session, the minutes and cost, each tool it used, each stop, and whether its reply is in its form.

    python3 dev/turn/trials/roles/roles.py <new folder>

The repository and the copy of turn are removed when the run ends; the records stay in Claude
Code's own folder of each session.
"""

import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import shared

CALL = shared.call("has")
UNMET = {
    "checklist": "checklist.md",
    "item": "B-1",
    "gets": "The reader learns under which license they may use demo.",
    "places": ["README.md:1-4", "README.md:5-7"],
}

place = os.path.abspath(sys.argv[1])
shared.task(place, CALL)
plugin = shared.turn(place)
sys.path.insert(0, os.path.join(plugin, "scripts"))
os.chdir(place)

# The copy of turn's scripts, on the path only once it is made.
import forms
import run


def turn(*args: str, given: str = "") -> str:
    done = subprocess.run(
        ["python3", os.path.join(plugin, "scripts", "turn.py"), *args],
        input=given,
        capture_output=True,
        text=True,
        check=True,
    )
    return done.stdout


def role(agent: str, prompt: dict) -> str:
    """Starts the role with the prompt, as the orchestrator would, and gives its agent ID."""
    ask = f"""Start the `{agent}` agent with the JSON on the line below as its whole prompt, exactly
as it is, and wait for its reply. Then reply with its reply as it is.
{json.dumps(prompt, ensure_ascii=False)}"""
    start = time.time()
    end = shared.claude(ask, [plugin], cwd=place)
    session = end["session_id"]
    print(f"=== {agent}  minutes: {round((time.time() - start) / 60, 1)}")
    print("session:", session, "cost:", end.get("total_cost_usd"))
    found = shared.agents(session)
    for path in found:
        shared.show(path)
    reply = prompt["reply"]
    if os.path.exists(reply):
        with open(reply, encoding="utf-8") as f:
            text = f.read()
        kept = run.running(CALL["result"])
        said = forms.check(
            text,
            kept["items"],
            kept["work"],
            run.FORMS[agent],
            records=tuple(kept.get("learnt", [])),
            each=run.each(kept),
        )
        print("reply:", text.strip())
        print("form:", "filled" if not said else said)
    else:
        print("reply: none written")
    return os.path.basename(found[0])[len("agent-") : -len(".jsonl")] if found else ""


turn("start", json.dumps(CALL))
turn("next", CALL["result"], given=json.dumps(shared.CHECK))
kept = run.running(CALL["result"])
ids = [role(run.GENERATOR, kept["next"]["prompt"])]
with open("README.md", "w", encoding="utf-8") as f:
    f.write(shared.UNLICENSED)
ids.append(role(run.FIRST_USER, run.reader_given(kept, run.FIRST_USER)))
ids.append(role(run.EVALUATOR, dict(run.reader_given(kept, run.EVALUATOR), reading=[])))
kept["records"] = [i for i in ids if i]
run.settle(kept, [UNMET], [])
kept = run.running(CALL["result"])
role(run.LEARNER, kept["next"]["prompt"])
os.chdir(shared.ROOT)
shutil.rmtree(place)
shutil.rmtree(plugin)
