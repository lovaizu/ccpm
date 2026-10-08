#!/usr/bin/env python3
"""SubagentStop: when pith's first user stops, write the facts of what it did, read from its own
JSONL, into the CCS it was handed: the text of each command it ran with its exit status, the files
it read with the Read tool, and the files it wrote with a writing tool. What a command read or wrote
shows only in its text, so it is not claimed as a file read or written. The first user's own account
is not a source of these facts."""
import json
import os
import re
import sys

import ccs

AGENT = "pith:first-user"
SHORT = 160  # characters kept of a command, so the CCS stays near 2,000 bytes


def calls(transcript):
    """The handed arguments, and each tool call paired with its result."""
    uses, results, handed = [], {}, None
    with open(transcript) as f:
        for line in f:
            entry = json.loads(line)
            content = (entry.get("message") or {}).get("content")
            if entry.get("type") == "user" and handed is None:
                handed = content if isinstance(content, str) else json.dumps(content)
            for block in content if isinstance(content, list) else []:
                if block.get("type") == "tool_use":
                    uses.append(block)
                elif block.get("type") == "tool_result":
                    results[block["tool_use_id"]] = block
    return handed or "", [(u["name"], u["input"], results.get(u["id"])) for u in uses]


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


def main():
    hook = json.load(sys.stdin)
    if hook.get("agent_type") != AGENT or not hook.get("agent_transcript_path"):
        return
    root = hook.get("cwd") or os.getcwd()
    handed, tool_calls = calls(hook["agent_transcript_path"])
    found = ccs.PATH.search(handed)
    if not found:
        return
    path = os.path.join(root, found.group(0))
    state = ccs.load(path)
    trace, read = facts(tool_calls, root)
    state["episodic_trace"] = trace
    state["retrieved_artifacts"] = [e for e in state["retrieved_artifacts"] if e[0] != "read"] + read
    ccs.dump(state, path)


if __name__ == "__main__":
    main()
