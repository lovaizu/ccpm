#!/usr/bin/env python3
"""PreToolUse on Agent, SendMessage and Write: before one of fw's roles is started, sent a message,
or a task's result file is written, what the flow needs at that step is in the task's CCS and the
role is not still answering an earlier message; otherwise the call is stopped with what is missing.
Every other call goes through untouched."""
import json
import os
import re
import sys

import ccs
import talk

RESULT = re.compile(r"(.*)/open/\d\d-report-([^/]+)\.md$")
AGENTS = {agent: role for role, agent in ccs.ROLES.items()}


def start(call, cwd, conductor):
    """What stops starting a role with the Agent tool, or None to let it through."""
    role = AGENTS.get(call.get("subagent_type"))
    if not role:
        return None
    said = talk.header(call.get("prompt"))
    if not said or said[0] != "request" or said[2] != role:
        return f"Begin the prompt with `request <task>/{role}.yaml`, the path of the task's {role}.yaml."
    return ready(role, said[1], cwd, request=True)


def send(call, cwd, conductor):
    """What stops a message to a role, or None to let it through."""
    started = talk.roles(conductor) if conductor and os.path.isfile(conductor) else {}
    said = talk.header(call.get("message"))
    agent = started.get(call.get("to"))
    if not said:
        return agent and (f"Begin the message with `<request|go|check|ok> {agent['path']}`: "
                          f"what it is, and the CCS of the role it goes to.")
    kind, path, role = said
    if kind == "request":
        return "A turn starts with the Agent tool: start a new role with `request <task>/<role>.yaml`."
    if not agent or agent["path"] != path:
        return (f"{call.get('to')} was not started for {path}. Send to the agent started with "
                f"`request {path}`, or start one.")
    if agent["waiting"]:
        return (f"The reply of {ccs.ROLES[role]} to `{agent['waiting']} {path}` has not come. "
                f"Wait for it before sending it anything else.")
    return ready(role, path, cwd, request=False) if kind == "go" else None


def ready(role, path, cwd, request):
    """What the task's CCS lacks for this step of the role's turn."""
    full = os.path.join(cwd, path)
    if not os.path.isfile(full):
        return f"{path} does not exist. Write the role's CCS there first."
    state = ccs.load(full)
    if request:
        lacking = [f"{r['component']}: {r['type']} (from {r['from']})" for r in required(role, state)
                   if not ccs.first(state, r["component"], r["type"])]
        lacking += flow(role, state, os.path.dirname(full), cwd)
    else:
        lacking = [] if ccs.first(state, "goal_orientation", "agreed") else [
            "goal_orientation: agreed (what you and the role agreed it will do, written before go)"]
    gaps = [value for kind, value in state["uncertainty_signal"] if kind == "gap"]
    if lacking or gaps:
        step = "request" if request else "go"
        return (f"{path} is not ready for {step}. Missing: {'; '.join(lacking) or 'none'}. "
                f"Open gaps: {'; '.join(gaps) or 'none'}.")
    return None


def required(role, state):
    """fw's own IN list for the role, and the plugin's, read from the domain folder the CCS names."""
    with open(os.path.join(ccs.ROOT, "references", f"{role}.json")) as f:
        entries = json.load(f)
    domain = ccs.first(state, "retrieved_artifacts", "domain")
    plugin = os.path.join(domain or "", f"{role}.json")
    if domain and os.path.isfile(plugin):
        with open(plugin) as f:
            entries += json.load(f)
    elif domain:
        entries.append({"component": "retrieved_artifacts", "type": f"domain holding {role}.json",
                        "from": f"the plugin's entry skill; {plugin} does not exist"})
    return entries


def flow(role, state, task, cwd):
    """The conditions the task's flow sets on starting the role, read from the turns in its folder."""
    found = ccs.records(task)
    used, learned = ccs.last(found, "use", "worked"), ccs.last(found, "learn", "worked")
    lacking = []
    if role == "make" and used:
        lacking += [f"goal_orientation: {kind} (the judgment of the last turn)" for kind in ("fix", "keep")
                    if not ccs.first(state, "goal_orientation", kind)]
        if learned < used:
            lacking.append("the learner's learnings from the last use (start fw:learner first)")
    if role == "use":
        work = ccs.first(state, "focal_entities", "work") or ""
        if not os.path.isfile(os.path.join(cwd, work)) or ccs.last(found, "make", "made") <= used:
            lacking.append(f"a work made since the last use, at {work or 'focal_entities: work'}")
        if used and not ccs.first(state, "goal_orientation", "recheck"):
            lacking.append("goal_orientation: recheck (each stumbled place; a full use is once per task)")
    if role == "learn" and used <= learned:
        lacking.append("a use by the first user not yet learned from (start fw:first-user first)")
    return lacking


def result(call, cwd, conductor):
    """What stops writing a task's result file, or None to let it through."""
    found = RESULT.match(os.path.join(cwd, call.get("file_path") or ""))
    task = found and os.path.join(found.group(1), found.group(2))
    if not task or not any(os.path.isfile(os.path.join(task, f"{role}.yaml")) for role in ccs.ROLES):
        return None
    turns = ccs.records(task)
    used, learned = ccs.last(turns, "use", "worked"), ccs.last(turns, "learn", "worked")
    lacking = [] if used else ["a use by the first user (start fw:first-user)"]
    if learned < used or not used:
        lacking.append("the learner's learnings from the last use (start fw:learner)")
    if lacking:
        return f"{call['file_path']} cannot be written yet. Missing: {'; '.join(lacking)}."
    return None


def note(call, cwd, conductor):
    """Facts the turn needs and only the hook sees: the work as it was before the maker's go, to tell
    afterwards whether it made the work, and the conductor's JSONL, for the learner."""
    said = talk.header(call.get("prompt") or call.get("message"))
    if not said or said[0] not in ("request", "go"):
        return
    path = os.path.join(cwd, said[1])
    state = ccs.load(path)
    if said[0] == "go" and said[2] == "make":
        work = os.path.join(cwd, ccs.first(state, "focal_entities", "work") or "")
        state["episodic_trace"] = [e for e in state["episodic_trace"] if e[0] != "work_before"]
        state["episodic_trace"].append(("work_before", ccs.digest(work)))
    if said[0] == "request" and said[2] == "learn" and conductor:
        state["retrieved_artifacts"] = [e for e in state["retrieved_artifacts"] if e[0] != "conductor"]
        state["retrieved_artifacts"].append(("conductor", conductor))
    ccs.dump(state, path)


def main():
    hook = json.load(sys.stdin)
    call, cwd = hook.get("tool_input") or {}, hook.get("cwd") or os.getcwd()
    check = {"Agent": start, "SendMessage": send, "Write": result}.get(hook.get("tool_name"))
    if not check:
        return
    reason = check(call, cwd, hook.get("transcript_path"))
    if reason:
        print(reason, file=sys.stderr)
        sys.exit(2)
    if check is not result:
        note(call, cwd, hook.get("transcript_path"))


if __name__ == "__main__":
    main()
