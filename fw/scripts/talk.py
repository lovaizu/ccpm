"""The exchanges between the conductor and fw's roles, read from the JSONL files Claude Code writes.

In the conductor's JSONL, a role is started with the Agent tool and continued with SendMessage; its
reply comes back as the Agent tool's result when it ran in the foreground, or else as a
task-notification naming the agent. In the role's own JSONL, each message the conductor sent is a
user entry, and each reply is the role's last text before the next message.
"""
import json
import re

import ccs

NOTICE = re.compile(r"<task-id>([^<]+)</task-id>")
HEADER = re.compile(r"(?m)^\s*(request|go|check|ok) +(\S*/(make|use|learn)\.yaml)\b")
REPLY = re.compile(r"(?m)^\W*reply to (request|go|check|ok)\b")


def entries(path):
    with open(path) as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def blocks(entry):
    content = (entry.get("message") or {}).get("content")
    return content if isinstance(content, list) else []


def text(content):
    return "\n".join(b.get("text", "") for b in content)


def header(message):
    """(kind, CCS path, role) of a conductor message's first line, or None."""
    found = HEADER.match(message or "")
    return found and (found.group(1), found.group(2), found.group(3))


def roles(conductor):
    """Each fw role the conductor started: agent id -> {"path", "role", "waiting"}, where "waiting"
    is the kind of the message still waiting for the role's reply, or None."""
    sent, agents = {}, {}
    for entry in entries(conductor):
        if entry.get("type") == "user" and isinstance((entry.get("message") or {}).get("content"), str):
            found = NOTICE.search(entry["message"]["content"])
            if found and found.group(1) in agents:
                agents[found.group(1)]["waiting"] = None
        for block in blocks(entry):
            if block.get("type") == "tool_use" and block.get("name") in ("Agent", "SendMessage"):
                args = block.get("input") or {}
                said = header(args.get("prompt") if block["name"] == "Agent" else args.get("message"))
                if said and (block["name"] == "SendMessage" or args.get("subagent_type") in ccs.ROLES.values()):
                    sent[block["id"]] = (said, args.get("to"))
            elif block.get("type") == "tool_result" and block.get("tool_use_id") in sent:
                (kind, path, role), to = sent.pop(block["tool_use_id"])
                result = entry.get("toolUseResult") if isinstance(entry.get("toolUseResult"), dict) else {}
                agent = to or result.get("agentId")
                if agent and not block.get("is_error") and result.get("success", True):
                    replied = result.get("status") == "completed"
                    agents[agent] = {"path": path, "role": role, "waiting": None if replied else kind}
    return agents


def exchange(transcript):
    """What the conductor sent the role and what it replied, in the order of the role's JSONL:
    [(kind, first line)], kind being the message's kind or "reply"."""
    said, reply = [], None
    for entry in entries(transcript):
        if entry.get("type") == "user" and isinstance((entry.get("message") or {}).get("content"), str):
            message = entry["message"]["content"]
            found = HEADER.search(message)
            if found:
                if reply:
                    said.append(("reply", reply))
                said.append((found.group(1), found.group(0).strip()))
                reply = None
        elif entry.get("type") == "assistant":
            written = text(blocks(entry)).strip()
            reply = written.splitlines()[0] if written else reply
    if reply:
        said.append(("reply", reply))
    return said
