"""What Claude Code keeps of an agent's conversation, read as the learner is shown it, page by
page."""

from __future__ import annotations

import json
from typing import Any

# A page of a record is short enough for one read to show it whole.
PAGE = 20000


def entries(path: str) -> list[dict[str, Any]]:
    """The agent's own entries: Claude Code also keeps a copy of each request it sends, which says
    again what the agent was shown."""
    with open(path, encoding="utf-8") as f:
        kept = [json.loads(line) for line in f]
    return [e for e in kept if e.get("type") in ("user", "assistant", "attachment")]


def pages(path: str) -> list[str]:
    """A record's pages: what the role was given, said, used and was shown, in order."""
    return split(shown(path))


def split(text: str) -> list[str]:
    """A text cut into pages, each short enough for one read to show it whole."""
    return [text[i : i + PAGE] for i in range(0, len(text), PAGE)] or [""]


def shown(path: str) -> str:
    lines: list[str] = []
    for entry in entries(path):
        attachment = entry.get("attachment")
        if isinstance(attachment, dict) and attachment.get("type") == "edited_text_file":
            lines.append(f"[shown {attachment.get('filename')}] {attachment.get('snippet')}")
        content = entry.get("message", {}).get("content")
        if isinstance(content, str):
            lines.append(f"[{entry.get('type')}] {content}")
        for part in content if isinstance(content, list) else []:
            lines.append(said(part))
    return "\n".join(lines) + "\n"


def said(part: dict[str, Any]) -> str:
    """One part of a message as the learner reads it."""
    if part.get("type") == "tool_use":
        return f"[tool_use {part.get('name')}] {json.dumps(part.get('input'), ensure_ascii=False)}"
    if part.get("type") == "tool_result":
        return f"[tool_result] {result(part)}"
    return f"[{part.get('type')}] {part.get('text', '')}"


def result(part: dict[str, Any]) -> str:
    """What a tool gave back, its text parts joined."""
    content = part.get("content")
    if isinstance(content, list):
        return "\n".join(str(c.get("text", "")) for c in content)
    return str(content)
