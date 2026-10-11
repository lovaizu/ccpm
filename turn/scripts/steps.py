"""Turns an agent's conversation record into its steps, numbered: what it ran or opened, and what came out.

A record is long and gets looked into a piece at a time; the steps are the same facts, short enough
to be read whole.
"""
import json
import os

HEAD, TAIL = 30, 10
PLACE = {"Read": "file_path", "Write": "file_path", "Edit": "file_path", "NotebookEdit": "notebook_path",
         "Bash": "command"}


def text(content):
    if isinstance(content, list):
        return "\n".join(c.get("text", "") for c in content if isinstance(c, dict))
    return content if isinstance(content, str) else ""


def shorten(out):
    lines = out.splitlines()
    if len(lines) <= HEAD + TAIL:
        return out
    return "\n".join(lines[:HEAD] + [f"({len(lines) - HEAD - TAIL} lines left out)"] + lines[-TAIL:])


def steps(record, name):
    """The steps in the record, as dicts with step, did, came_out and error."""
    calls, results = [], {}
    with open(record, encoding="utf-8") as f:
        for line in f:
            content = json.loads(line).get("message", {}).get("content")
            for c in content if isinstance(content, list) else []:
                if c.get("type") == "tool_use":
                    calls.append(c)
                elif c.get("type") == "tool_result":
                    results[c.get("tool_use_id")] = c
    out = []
    for n, c in enumerate(calls, 1):
        given = c.get("input", {})
        key = PLACE.get(c["name"])
        did = given[key] if key in given else json.dumps(given, ensure_ascii=False)
        r = results.get(c.get("id"), {})
        out.append({"step": f"{name}#{n}", "did": f"{c['name']} {did}", "came_out": shorten(text(r.get("content"))),
                    "error": bool(r.get("is_error"))})
    return out


def write(work, name, found):
    """Writes steps-<name>.json for scripts and steps-<name>.md for agents to read."""
    with open(os.path.join(work, f"steps-{name}.json"), "w", encoding="utf-8") as f:
        json.dump(found, f, ensure_ascii=False, indent=2)
    parts = [f"# Steps of {name}\n"]
    for s in found:
        mark = " (error)" if s["error"] else ""
        parts.append(f"## {s['step']}{mark}\n\nDid: {s['did']}\n\nCame out:\n\n```\n{s['came_out']}\n```\n")
    with open(os.path.join(work, f"steps-{name}.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
