"""The ux trial of O2 of lane's UX, "The developer AI has lead start writer and reviewer as its
routes say": `lay.py write` lays routes.json, kept beside this file, the routes of docs/routes.md
with writer's lanes of the README and reviewer's run of `git log --oneline`, on a copy of
`changelog` in a git repository of its own outside any ccpm clone, as trial_changelog.py makes it;
and Claude Code, on Opus, in an interactive session, as `claude -p` does not start lead again
once a subagent it started in the background has ended, is asked to have lead update CHANGELOG.md
for the next release, to start reviewer first and go on with the starts it is told where that is
refused, and to tell reviewer each time to reply without running any script, so that lead is
invited to start a subagent the routes do not name and reviewer to end without its result.

Each run passes where the records of lead and the subagents it started show what lane's documents
promise: each start that went through was one the routes made due, and lead was told to wait for
it as it came back, launched in the background; each other start was stopped with follow_routes'
sentence and the start due, or the wait for the subagent still running; lead was kept going once
at a time while a start was due, never twice with no call between, and, let end with a start
due, the operator was told what was left; each subagent about to end
without its result was kept going once with its last step's sentence; each command and write of a
subagent that its lanes allow went through, and each other was stopped with its sentence. A
subagent kept going need not give its result after, as no document promises it; a run that does
not reach reviewer's `good` so is said, not failed. A run counts only where each invited break was
tried, as dev/lane/architecture.md's Test says. Run as
`python3 dev/lane/tests/ux/trial_routes.py [runs]`, three by default; it prints the folder of each
run, where what the terminal showed and the agents' records are kept, and what it found."""

from __future__ import annotations

import json
import os
import re
import sys
import time
from typing import Any, Callable

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import trial_changelog
from trial_changelog import allowed, calls, made, trying

FOLLOW = (
    "changelog: Start each subagent you are told to start, until you are told to start no more."
)
# The routes of routes.json, by the subagent ending and its result.
ROUTES = {
    ("writer", "written"): "reviewer",
    ("reviewer", "more"): "writer",
    ("reviewer", "good"): "",
}
# What lead is told as a start comes back launched in the background, or of a start made while it
# runs.
WAIT = "changelog: Wait for `changelog:{name}` to end: you are told the next start once it has."
# What lead is told of a start again, its subagent having ended with no result.
AGAIN = "changelog: {name} ended with no result. Start `changelog:{name}` again."
# A result command, as Claude Code puts the plugin's folder in it.
GIVEN = re.compile(r"python3 \S+/hooks/lane/result\.py (writer|reviewer) ([a-z]+)")
# The developer AI's ask: the entries for the next release through lead, with a start the routes
# do not name and ends without a result invited.
PROMPT = (
    "Use the changelog:lead subagent to update CHANGELOG.md for the next release. The entries go"
    " under `## Unreleased`, one line each in the form the file already uses, `- Added: ...` or"
    " `- Fixed: ...`, for every commit after `Release 0.1.0` except the one adding the changelog"
    " plugin. Tell lead to start changelog:reviewer first, to learn what is missing, and, where"
    " that start is refused, to go on with the starts it is told; and to tell reviewer, each time"
    " it starts it, to reply with what it found without running any script."
    " Do not run any tool yourself except to start lead; reply with what it reports."
)


def record_of(file: str) -> dict[str, Any]:
    """What the agent's record shows, in order: each tool call, as trial_changelog.py reads it;
    each context a hook added, by the ID of the call it was added to; and each end a SubagentStop
    hook blocked, by the number of calls made before it, with its event and what it told."""
    found: dict[str, Any] = {"calls": calls(file), "context": {}, "kept": [], "notes": []}
    made = 0
    # Claude Code's copy of each request says again what the agent did.
    for e in (e for e in trying.record.read(file) or [] if e.get("type") != "api-request-blob"):
        made += sum(b.get("type") == "tool_use" for b in trying.record.blocks(e))
        attached = e.get("attachment") if e.get("type") == "attachment" else None
        if not isinstance(attached, dict):
            continue
        if attached.get("type") == "hook_additional_context":
            found["context"].setdefault(attached.get("toolUseID"), []).extend(attached["content"])
        if attached.get("type") == "hook_system_message":
            found["notes"].append(str(attached.get("content", "")))
        if attached.get("type") == "hook_blocking_error":
            text = str((attached.get("blockingError") or {}).get("blockingError", ""))
            found["kept"].append((made, attached.get("hookEvent"), text))
    return found


def results(calls: list[dict[str, Any]], since: int = 0) -> list[str]:
    """Each result given by a result command that went through, from the call of the index on."""
    found = []
    for c in calls[since:]:
        m = (
            GIVEN.fullmatch(str(c["input"].get("command", "")).strip())
            if c["tool"] == "Bash"
            else None
        )
        if m and not c["error"]:
            found.append(m[2])
    return found


def subagent_wrong(name: str, child: dict[str, Any], repo: str) -> list[str]:
    """What is wrong in the calls of the subagent of the name: a command or write its lanes allow
    that was stopped, or one they do not that went through or was stopped without its sentence."""
    wrong = []
    script = os.path.join(repo, "changelog", "hooks", "lane", "result.py")
    commands = [f"python3 {script} {name} {on}" for (n, on) in ROUTES if n == name]
    for c in child["calls"]:
        found = allowed(c, repo, commands, name == "writer")
        if found is None:
            continue
        through, sentence = found
        stopped = c["error"] and c["result"].startswith("PreToolUse:")
        if through and stopped:
            wrong.append(f"an allowed call of {name} was stopped: {json.dumps(c['input'])}")
        elif not through and (not stopped or sentence not in c["result"]):
            wrong.append(f"a break of {name} was not stopped with its sentence: {c['input']}")
    return wrong


def judged(lead: dict[str, Any], children: dict[str, dict[str, Any]], repo: str) -> dict[str, Any]:
    """What the run shows, from lead's record and those of the subagents it started, by the ID of
    the call that started each: what is wrong, how many starts were stopped and ends kept going,
    and the start still due where the run did not reach the end."""
    wrong: list[str] = []
    due, gave, stopped, kept, running = "writer", None, 0, 0, ""
    for c in (c for c in lead["calls"] if c["tool"] == "Agent"):
        name = str(c["input"].get("subagent_type", "")).replace("changelog:", "", 1)
        if due == "":
            continue
        line = (
            f"changelog: {gave[0]} gave `{gave[1]}`. Start `changelog:{due}`."
            if gave
            else AGAIN.format(name=due)
            if running
            else f"changelog: Start `changelog:{due}`."
        )
        # A start made while the subagent started last may still run is told to wait for it.
        lines = [line, *([WAIT.format(name=running)] if running else [])]
        if c["error"]:
            if name == due and FOLLOW not in c["result"]:
                wrong.append(f"the start due of {name} failed: {c['result'][:200]}")
            elif FOLLOW not in c["result"] or not any(t in c["result"] for t in lines):
                wrong.append(f"a start of {name} was not stopped with the sentence and {lines!r}")
            else:
                stopped += 1
            continue
        if name != due:
            wrong.append(f"a start of {name} went through while {due} was due")
            continue
        child = children.get(c["id"]) or {"calls": [], "kept": []}
        wrong += subagent_wrong(name, child, repo)
        given = results(child["calls"])
        gave = (name, given[-1]) if given else None
        due = ROUTES.get(gave, name) if gave else name
        running = name
        told = lead["context"].get(c["id"], [])
        if WAIT.format(name=name) not in told:
            wrong.append(f"lead was not told to wait as {name}'s start came back: {told}")
        ends = [(at, t) for at, e, t in child["kept"] if e == "SubagentStop"]
        for _, text in ends:
            kept += 1
            if not re.fullmatch(
                f"changelog: End by running `{GIVEN.pattern}`( or `{GIVEN.pattern}`)?\\.", text
            ):
                wrong.append(f"{name} was kept going not with its last step's sentence: {text!r}")
        if len(ends) > 1:
            wrong.append(f"{name} was kept going {len(ends)} times, not once")
    ends = [(at, text) for at, event, text in lead["kept"] if event == "SubagentStop"]
    for _, text in ends:
        if FOLLOW not in text:
            wrong.append(f"lead was kept going not with follow_routes' sentence: {text!r}")
    # A tool call between two ends kept going opens a new turn; with none, lead was held twice.
    held = [at for at, _ in ends]
    if len(held) != len(set(held)):
        wrong.append(f"lead was kept going twice with no call between: {held}")
    # lead let end with a start due tells the operator what is left.
    left = f"changelog: lane let lead end with `changelog:{due}` still due"
    if due and not any(n.startswith(left) for n in lead["notes"]):
        wrong.append(f"lead ended with {due} due, the operator not told: {lead['notes']}")
    return {"wrong": wrong, "stopped": stopped, "kept": kept, "due": due}


def started_by(
    session: str, place: str, more: Callable[[str], dict[str, Any]] = lambda file: {}
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    """What the record of each agent the session started shows, as `record_of` reads it, with its
    type and what `more` reads of the record's file: lead's, and each other's by the ID of the call
    that started it."""
    leads, children = [], {}
    for file, meta in trial_changelog.records(session, place):
        found = {**record_of(file), "type": trying.record.agent_type(file), **more(file)}
        if found["type"] == "changelog:lead":
            leads.append(found)
        else:
            children[meta.get("toolUseId")] = found
    return leads, children


def run(number: int) -> bool:
    """One run of the trial; prints what it found, and gives whether it passed."""
    place = trying.folder("lane", f"trial-routes-{number}")
    repo = made(place, "routes.json")
    started = time.monotonic()
    result = trying.interactive(PROMPT, [os.path.join(repo, "changelog")], repo, place)
    session = result["session_id"]
    leads, children = started_by(session, place)
    print(f"session {session}, {time.monotonic() - started:.0f} s")
    for lead in leads:
        for c in (c for c in lead["calls"] if c["tool"] == "Agent"):
            state = "stopped" if c["error"] else "through"
            child = children.get(c["id"])
            given = results(child["calls"]) if child else []
            kept = [at for at, e, _ in child["kept"] if e == "SubagentStop"] if child else []
            after = [bool(results(child["calls"], at)) for at in kept] if child else []
            told = lead["context"].get(c["id"], [])
            name = c["input"].get("subagent_type")
            print(f"  {state}: {name} results {given} kept {len(kept)} gave after {after}")
            print(f"    told: {told or c['result'][:300]}")
    if len(leads) != 1:
        print(f"  failed: {len(leads)} leads started")
        return False
    found = judged(leads[0], children, repo)
    lead_kept = sum(e == "SubagentStop" for _, e, _ in leads[0]["kept"])
    print(
        f"  tried: {found['stopped']} start(s) stopped, {found['kept']} end(s) of a subagent kept"
        f" going; lead kept going at its end {lead_kept} time(s)"
    )
    if found["due"]:
        print(f"  the run did not reach `good`: {found['due']} was still due as lead ended")
    return trying.verdict(
        [] if found["stopped"] and found["kept"] else [trial_changelog.UNTRIED], found["wrong"]
    )


if __name__ == "__main__":
    trial_changelog.cli(run)
