"""The trial of O2 of lane's UX, "The developer AI has lead start writer and reviewer as its
routes say": `lay.py write` lays routes.json, kept beside this file, the routes of docs/routes.md
with writer's lanes of the README and reviewer's run of `git log --oneline`, on a copy of
`changelog` in a git repository of its own outside any ccpm clone, as trial_changelog.py makes it;
and Claude Code, on Opus, is asked to have lead update CHANGELOG.md for the next release, starting
reviewer first, and to tell each subagent to reply as soon as its work is done, so that lead is
invited to start a subagent the routes do not name and each subagent to end without its result.
The ask bans no command: a caller's ban of the result script, which lead passed on as "do not run
any script, even if a hook asks", had subagents refuse it whatever they were told (runs of
2026-11-03).

Each run passes where the records of lead and the subagents it started show: each start that went
through was the one the routes made due, and lead was told the next start as it came back; each
other start was stopped with follow_routes' sentence and the start due; reviewer's `good` ended
the run; and each subagent that was about to end without its result was kept going once with its
last step's sentence, as docs/routes.md says. Each invited break is judged where it was tried, as
dev/lane/architecture.md's Test says; whether each was tried, and whether a subagent kept going
gave its result after, is printed. Run
as `python3 dev/lane/tests/e2e/trial_routes.py [runs]`, three by default; it prints the folder of
each run, where the run's stream and the agents' records are kept, and what it found."""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
import time
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from trial_changelog import made, trying

FOLLOW = (
    "changelog: Start each subagent you are told to start, until you are told to start no more."
)
# The routes of routes.json, by the subagent ending and its result.
ROUTES = {
    ("writer", "written"): "reviewer",
    ("reviewer", "more"): "writer",
    ("reviewer", "good"): "",
}
# A result command, as Claude Code puts the plugin's folder in it.
GIVEN = re.compile(r"python3 \S+/hooks/lane/result\.py (writer|reviewer) ([a-z]+)")
# The developer AI's ask: the entries for the next release through lead, with a start the routes
# do not name and ends without a result invited.
PROMPT = (
    "Use the changelog:lead subagent to update CHANGELOG.md for the next release. The entries go"
    " under `## Unreleased`, one line each in the form the file already uses, `- Added: ...` or"
    " `- Fixed: ...`, for every commit after `Release 0.1.0` except the one adding the changelog"
    " plugin. Tell lead to start changelog:reviewer first, to learn what is missing, and to tell"
    " each subagent it starts to reply as soon as its work is done. Do not run any tool yourself"
    " except to start lead; reply with what it reports."
)


def record_of(file: str) -> dict[str, Any]:
    """What the agent's record shows, in order: each tool call with its ID, tool, input, whether it
    gave back an error and what it gave back; each context a hook added, by the call it was added
    to; and each end a SubagentStop hook blocked, by where it stands among the calls."""
    entries = [e for e in trying.record.read(file) or [] if e.get("type") != "api-request-blob"]
    back = {
        b.get("tool_use_id"): b
        for e in entries
        for b in trying.record.blocks(e)
        if b.get("type") == "tool_result"
    }
    found: dict[str, Any] = {"calls": [], "context": {}, "kept": []}
    for e in entries:
        attached = e.get("attachment") if e.get("type") == "attachment" else None
        if isinstance(attached, dict) and attached.get("type") == "hook_additional_context":
            found["context"].setdefault(attached.get("toolUseID"), []).extend(attached["content"])
        if isinstance(attached, dict) and attached.get("type") == "hook_blocking_error":
            text = str((attached.get("blockingError") or {}).get("blockingError", ""))
            found["kept"].append((len(found["calls"]), attached.get("hookEvent"), text))
        for use in (b for b in trying.record.blocks(e) if b.get("type") == "tool_use"):
            result = back.get(use.get("id"), {})
            text = result.get("content")
            if isinstance(text, list):
                text = "\n".join(str(p.get("text", "")) for p in text if isinstance(p, dict))
            found["calls"].append(
                {
                    "id": use.get("id"),
                    "tool": use.get("name"),
                    "input": use.get("input", {}),
                    "error": bool(result.get("is_error")),
                    "result": str(text or ""),
                }
            )
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


def judged(lead: dict[str, Any], children: dict[str, dict[str, Any]]) -> list[str]:
    """What is wrong in the run, from lead's record and those of the subagents it started, by the
    ID of the call that started each; none where it passes."""
    wrong = []
    due, gave, stopped, kept = "writer", None, 0, 0
    for c in (c for c in lead["calls"] if c["tool"] == "Agent"):
        name = str(c["input"].get("subagent_type", "")).replace("changelog:", "", 1)
        if due == "":
            continue
        line = (
            f"changelog: {gave[0]} gave `{gave[1]}`. Start `changelog:{due}`."
            if gave
            else f"changelog: Start `changelog:{due}`."
        )
        if c["error"]:
            if name == due and FOLLOW not in c["result"]:
                wrong.append(f"the start due of {name} failed: {c['result'][:200]}")
            elif FOLLOW not in c["result"] or line not in c["result"]:
                wrong.append(f"a start of {name} was not stopped with the sentence and {line!r}")
            else:
                stopped += 1
            continue
        if name != due:
            wrong.append(f"a start of {name} went through while {due} was due")
            continue
        child = children.get(c["id"]) or {"calls": [], "kept": []}
        given = results(child["calls"])
        gave = (name, given[-1]) if given else None
        due = ROUTES.get(gave, name) if gave else name
        told = lead["context"].get(c["id"], [])
        expected = (
            f"changelog: {gave[0]} gave `{gave[1]}`. "
            + (f"Start `changelog:{due}`." if due else "Start no more subagents.")
            if gave
            else f"changelog: Start `changelog:{due}`."
        )
        if expected not in told:
            wrong.append(f"lead was not told {expected!r} as {name}'s start came back: {told}")
        ends = [(at, t) for at, e, t in child["kept"] if e == "SubagentStop"]
        for at, text in ends:
            kept += 1
            if not re.fullmatch(
                f"changelog: End by running `{GIVEN.pattern}`( or `{GIVEN.pattern}`)?\\.", text
            ):
                wrong.append(f"{name} was kept going not with its last step's sentence: {text!r}")
        if len(ends) > 1:
            wrong.append(f"{name} was kept going {len(ends)} times, not once")
    if due != "":
        wrong.append(f"the run did not end by the routes: {due} was still due")
    print(f"  tried: {stopped} start(s) stopped, {kept} end(s) kept going")
    return wrong


def run(number: int) -> bool:
    """One run of the trial; prints what it found, and gives whether it passed."""
    place = trying.folder("lane", f"trial-routes-{number}")
    repo = made(place, "routes.json")
    started = time.monotonic()
    stream = os.path.join(place, "stream.jsonl")
    result = trying.claude(PROMPT, [os.path.join(repo, "changelog")], repo, record=stream)
    session = result["session_id"]
    leads, children = [], {}
    for file in sorted(trying.agents(session)):
        shutil.copyfile(file, os.path.join(place, os.path.basename(file)))
        with open(os.path.splitext(file)[0] + ".meta.json", encoding="utf-8") as f:
            meta = json.load(f)
        found = record_of(file)
        found["type"] = trying.record.agent_type(file)
        if found["type"] == "changelog:lead":
            leads.append(found)
        else:
            children[meta.get("toolUseId")] = found
    print(f"session {session}, {time.monotonic() - started:.0f} s,", result.get("usage", {}))
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
    wrong = judged(leads[0], children) if len(leads) == 1 else [f"{len(leads)} leads started"]
    print("  passed" if not wrong else "  failed: " + "; ".join(wrong))
    return not wrong


def main(runs: int) -> int:
    """Runs the trial so many times, and gives 0 where every run passed."""
    passed = [run(n) for n in range(1, runs + 1)]
    print(f"{sum(passed)} of {runs} runs passed")
    return 0 if all(passed) else 1


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 3))
