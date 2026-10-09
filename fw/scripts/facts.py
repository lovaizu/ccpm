#!/usr/bin/env python3
"""SubagentStop: each time one of fw's roles replies, write the facts of its turn, read from its own
JSONL, into its CCS: each message it was sent and each reply, under its kind and in the order of the
JSONL; the text of each command it ran with its exit status; the files it read with the Read tool;
the files it wrote with a writing tool; and the turn's records: `turn` once it has replied, `worked`
once it has replied to go, and, for the maker, `made` when the work changed between go and that
reply. What a command read or wrote shows only in its text, so it is not claimed as a file read or
written. The role's own account is not a source of these facts."""
import json
import os
import re
import sys

import ccs
import talk

SHORT = 160  # characters kept of a command, so the CCS stays small


def calls(transcript):
    """Each tool call paired with its result."""
    uses, results = [], {}
    for entry in talk.entries(transcript):
        for block in talk.blocks(entry):
            if block.get("type") == "tool_use":
                uses.append(block)
            elif block.get("type") == "tool_result":
                results[block["tool_use_id"]] = block
    return [(u["name"], u["input"], results.get(u["id"])) for u in uses]


def exit_status(result):
    if result is None:
        return None
    text = result.get("content")
    text = text if isinstance(text, str) else json.dumps(text)
    found = re.match(r"Exit code (\d+)", text)
    return int(found.group(1)) if found else (1 if result.get("is_error") else 0)


def facts(tool_calls, root):
    trace, read = [], []
    for name, args, result in tool_calls:
        if name == "Bash":
            status = exit_status(result)
            command = args.get("command", "")
            command = command if len(command) <= SHORT else command[:SHORT] + "…"
            trace.append(("executed" if status == 0 else "failed", f"{command} → exit {status}"))
        elif name == "Read":
            read.append(("read", os.path.relpath(args["file_path"], root)))
        elif name in ("Write", "Edit", "NotebookEdit"):
            path = args.get("file_path") or args.get("notebook_path")
            inside = os.path.realpath(path).startswith(os.path.realpath(root) + os.sep)
            trace.append(("wrote" if inside else "wrote_outside", path))
    return trace, list(dict.fromkeys(read))


def record(state, task, transcript, said, work):
    """The turn's records, added once each."""
    mine = {kind for kind, value in state["retrieved_artifacts"]
            if kind in ccs.RECORDS and value.endswith(" " + transcript)}
    if "turn" not in mine:
        number = max((n for n, *_ in ccs.records(task)), default=0) + 1
        state["retrieved_artifacts"].append(("turn", f"#{number} {transcript}"))
    number = next(v.split(" ")[0] for k, v in state["retrieved_artifacts"]
                  if k == "turn" and v.endswith(" " + transcript))
    if "worked" not in mine and any(kind == "reply" and re.search(r"reply to go\b", line) for kind, line in said):
        state["retrieved_artifacts"].append(("worked", f"{number} {transcript}"))
        before = ccs.first(state, "episodic_trace", "work_before")
        if work is not None and before and ccs.digest(work) != before:
            state["retrieved_artifacts"].append(("made", f"{number} {transcript}"))


def main():
    hook = json.load(sys.stdin)
    transcript = hook.get("agent_transcript_path")
    role = {agent: role for role, agent in ccs.ROLES.items()}.get(hook.get("agent_type"))
    if not role or not transcript or not os.path.isfile(transcript):
        return
    root = hook.get("cwd") or os.getcwd()
    said = talk.exchange(transcript)
    request = next((line for kind, line in said if kind == "request"), None)
    found = talk.header(request)
    if not found or found[2] != role or not os.path.isfile(os.path.join(root, found[1])):
        return
    path = os.path.join(root, found[1])
    state = ccs.load(path)
    trace, read = facts(calls(transcript), root)
    work = ccs.first(state, "focal_entities", "work") if role == "make" else None
    record(state, os.path.dirname(path), transcript, said, work and os.path.join(root, work))
    kept = [e for e in state["episodic_trace"] if e[0] == "work_before"]
    state["episodic_trace"] = kept + said + trace
    state["retrieved_artifacts"] = [e for e in state["retrieved_artifacts"] if e[0] != "read"] + read
    ccs.dump(state, path)


if __name__ == "__main__":
    main()
