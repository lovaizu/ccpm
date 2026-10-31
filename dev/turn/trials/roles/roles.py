"""Tries each of turn's two roles on its own: the real role and its lanes, started by a stand-in for
the orchestrator with the prompt the orchestrator gives it, on the orchestrator trial's task of two
items, one answered at its part and one in each part. The generator makes the work from nothing;
the first user then reads a set README that gives every item, so it finds every Good and ends
without sending anything. Prints, for each role, its session, the minutes and cost, each tool it
used, each stop, and whether its reply is in its form, as turn.py checks it.

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
import prompts


def role(agent: str, prompt: dict) -> None:
    """Starts the role with the prompt, as the orchestrator would, and prints what it did and
    whether its reply is in its form."""
    ask = f"""Start the `turn:{agent}` agent with the JSON on the line below as its whole prompt,
exactly as it is, and wait for its reply. Then reply with its reply as it is.
{json.dumps(prompt, ensure_ascii=False)}"""
    start = time.time()
    end = shared.claude(ask, [plugin], cwd=place)
    session = end["session_id"]
    print(f"=== {agent}  minutes: {round((time.time() - start) / 60, 1)}")
    print("session:", session, "cost:", end.get("total_cost_usd"))
    for path in shared.agents(session):
        shared.show(path)
    run = prompts.laid_out(prompt["result"])
    text = prompts.last(run, agent)
    if text is None:
        print("reply: none written")
        return
    said = prompts.problems(run, agent, text)
    print("reply:", text.strip())
    print("form:", "filled" if not said else said)


with shared.removed(trial.top):
    shared.task(place, CALL)
    os.chdir(place)
    result = shared.begun(plugin, place, CALL)
    role(prompts.GENERATOR, {"result": result})
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(shared.LICENSED)
    # The first user ends without sending, as the README gives every item; the ID names no agent.
    role(prompts.FIRST_USER, {"result": result, "generator": "none"})
    os.chdir(shared.ROOT)
