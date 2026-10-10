"""What the conversation's JSONL says of the current turn: where `turn:up` was called with what, and
which of turn's agents were called after it, in order."""
import glob
import json
import os
import re

AGENTS = {"turn:maker": "maker", "turn:first-user": "first-user", "turn:learner": "learner"}
COMMAND = re.compile(r"<command-name>/turn:up</command-name>")
COMMAND_ARGS = re.compile(r"<command-args>(.*?)</command-args>", re.S)


def entries(path):
    out = []
    with open(path) as f:
        for line in f:
            try:
                out.append(json.loads(line))
            except ValueError:
                continue
    return out


def session_path():
    """This conversation's JSONL, found from the session ID Claude Code gives its tools."""
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    home = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")
    found = glob.glob(os.path.join(home, "projects", "*", sid + ".jsonl")) if sid else []
    return found[0] if found else None


def blocks(entry):
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    return [b for b in content or [] if isinstance(b, dict)]


def parse_args(text):
    out = {}
    for line in text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def last_turn(items):
    """(the index of the last `turn:up` call, its in/out/domain), or (None, {})."""
    for i in range(len(items) - 1, -1, -1):
        for b in blocks(items[i]):
            if b.get("type") == "tool_use" and b.get("name") == "Skill" and \
                    (b.get("input") or {}).get("skill") == "turn:up":
                return i, parse_args(b["input"].get("args") or "")
            if b.get("type") == "text" and COMMAND.search(b.get("text", "")):
                m = COMMAND_ARGS.search(b["text"])
                return i, parse_args(m.group(1) if m else "")
    return None, {}


def agent_ids(items):
    """Each Agent call's ID as its result names it."""
    out = {}
    for e in items:
        result = e.get("toolUseResult")
        if isinstance(result, dict) and result.get("agentId"):
            for b in blocks(e):
                if b.get("type") == "tool_result":
                    out[b.get("tool_use_id")] = result["agentId"]
    return out


def calls(items, start):
    """turn's agent calls after `start`, as (what, agent ID): what is maker, first-user or learner
    for a new agent, and made for a message that tells a maker to go on."""
    ids = agent_ids(items)
    makers, out = set(), []
    for e in items[start + 1:]:
        for b in blocks(e):
            if b.get("type") != "tool_use":
                continue
            inp = b.get("input") or {}
            what = AGENTS.get(inp.get("subagent_type")) if b.get("name") in ("Agent", "Task") else None
            if what:
                aid = ids.get(b.get("id"))
                out.append((what, aid))
                if what == "maker" and aid:
                    makers.add(aid)
            elif b.get("name") == "SendMessage" and inp.get("to") in makers:
                out.append(("made", inp["to"]))
    return out


def agent_path(transcript, agent_id):
    return os.path.join(transcript[:-len(".jsonl")], "subagents", f"agent-{agent_id}.jsonl")
