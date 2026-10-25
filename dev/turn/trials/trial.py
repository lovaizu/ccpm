"""Tries turn as its user does: a stand-in for the calling AI, in a repository made of a task of
this folder, calls turn on it with the step text the README shows, the user away: it takes each
question's recommended answer as the user's, keeps it in the task's decisions and sends it to the
agent. When turn returns, it checks each Good against its lines in the work and each lesson's
quoted words against the records it names, and fixes nothing, as the work is judged as it came
back. With `stopped`, it stops turn during the first user's reading, once the first user has
started and before it replies, and calls it again with the same call. Prints the stand-in's
session, from whose JSONL and its agents' the trial is judged, the minutes from the call to the
work coming back, read from turn's records, and the work and the result.

    python3 dev/turn/trials/trial.py <task folder, such as dev/turn/trials/one> <new folder> [stopped]

The repository and the copy of turn are removed when the run ends; what the run gave back is kept
in `<new folder>.work/` for the judge, and the records in Claude Code's own folder of the session.
The turn of this working tree is used as it is when the run starts.
"""

from __future__ import annotations

import os
import time

import shared

CALL = shared.call("has")
USAGE = "trial.py <task folder, such as dev/turn/trials/one> <new folder> [stopped]"
# The README's step text after the call, as its Example writes it, then what the user being away
# asks of the stand-in.
STEP = """Put each question it sends to the user and send it the answer.

The user is away: take each question's recommended answer as theirs, write it into the decisions
file .tasks/ccs.json names, in place of what it changes there or as a line of its own, so the
decisions say one thing, and where the answer changes what the CCS names, such as a file added to
the work, change the CCS too; then send it to the agent with SendMessage, loaded with ToolSearch,
to the agent ID its start gave back. turn sends you a line before each move and after each
outcome; nothing need answer them. Fix nothing in the work: it is judged as it came back.

When it returns, check each Good of the result against its lines in the work, and each lesson's
quoted words in the record each ground names by its path, one JSON entry to a line, so find each
quote in the entries' text, as JSON escapes some of its characters. End with a list of each item
of the result, saying whether its Good holds at its lines and why, and of each lesson, whether its
quoted words are in the records it names."""
STOP = """Once a line says `turn:first-user will`, the first time alone, wait until the first user has
started, with `until grep -qs '"agentType":"turn:first-user"' {}/*.meta.json; do sleep 2; done`
in a command of its own, then stop the agent with TaskStop, loaded with ToolSearch, and start the
`turn:up` agent in the background again with the same call.
"""

task, place, more = shared.arguments(USAGE, ("stopped",))
# The folder of each agent's record of a session run in place, where an agent's meta file names its
# type once it has started.
project = shared.folder(place)
records = os.path.dirname(shared.record.subagent(shared.record.conversation("*", project), "*"))
plugin = shared.turn(place)
with shared.removed(place, plugin):
    shared.repository(task, place, CALL)
    start = time.time()
    stop = STOP.format(records) if more else ""
    end = shared.claude(shared.start(CALL) + stop + STEP, [plugin], cwd=place, wait=120)
    print(end.get("result"))
    print("session:", end.get("session_id"), "cost:", end.get("total_cost_usd"))
    print("minutes:", round((time.time() - start) / 60, 1))
    # From the call to the work coming back: the first orchestrator's first entry to the last
    # one's last, as a call again starts another.
    times = []
    for path in shared.agents(end["session_id"]):
        if shared.record.agent_type(path) == "turn:up":
            times += [e.get("timestamp") for e in shared.record.read(path) or []]
    times = sorted(t for t in times if t)
    if times:
        print("call to return:", times[0], times[-1])
    shared.shown(task, place, CALL["result"])
    shared.keep(task, place, CALL["result"])
    print("kept:", shared.kept(place))
