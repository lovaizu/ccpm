"""Tries each of turn's two roles on its own: the real role and its lanes, started by a stand-in for
the orchestrator with the prompt the flow gives it, on the orchestrator trial's task of two items,
one answered at its part and one in each part. Between the roles the run is set as a trial means:
the orchestrator's check finds each item's Good in the decisions, and the generator's work is
replaced by a set README that names no license. Prints, for each role, its session, the minutes and
cost, each tool it used, each stop, and whether its reply is in its form.

    python3 dev/turn/trials/roles/roles.py

Each run makes a folder of its own, `turn/<yyyymmdd>-roles-<random>/` in the system's temporary
folder, and prints its path. It holds the repository and the copy of turn, and is removed when the
run ends, however it ends; the records stay in Claude Code's own folder of each session.
"""

from __future__ import annotations

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import shared

CALL = shared.call("has")

if len(sys.argv) != 1:
    sys.exit("usage: roles.py")
trial = shared.Run.made("roles")
place = trial.repo
plugin = shared.turn(trial)
shared.use(plugin)

# The copy of turn's scripts, on the path only once it is made.
import flow
import prompts
import state


def role(agent: str, prompt: dict) -> None:
    """Starts the role with the prompt, as the orchestrator would, and prints what it did and
    whether its reply is in its form."""
    ask = f"""Start the `{agent}` agent with the JSON on the line below as its whole prompt, exactly
as it is, and wait for its reply. Then reply with its reply as it is.
{json.dumps(prompt, ensure_ascii=False)}"""
    start = time.time()
    end = shared.claude(ask, [plugin], cwd=place)
    session = end["session_id"]
    print(f"=== {agent}  minutes: {round((time.time() - start) / 60, 1)}")
    print("session:", session, "cost:", end.get("total_cost_usd"))
    for path in shared.agents(session):
        shared.show(path)
    reply = prompt["reply"]
    if os.path.exists(reply):
        with open(reply, encoding="utf-8") as f:
            text = f.read()
        said = flow.PROBLEMS[agent](state.going(CALL["result"]), text)
        print("reply:", text.strip())
        print("form:", "filled" if not said else said)
    else:
        print("reply: none written")


with shared.removed(trial.top):
    shared.task(place, CALL)
    os.chdir(place)
    shared.begun(plugin, place, CALL)
    kept = state.going(CALL["result"])
    role(prompts.GENERATOR, kept["next"]["prompt"])
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(shared.UNLICENSED)
    role(prompts.FIRST_USER, prompts.reader(kept))
    os.chdir(shared.ROOT)
