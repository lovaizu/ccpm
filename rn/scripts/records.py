"""What Claude Code keeps of a conversation, read by lane's record.py, as rn's learnings are made
from it: the conversation's own entries, each part of a message as a line, and each text shown
wrapped so a read shows its every line whole."""

from __future__ import annotations

import json
import textwrap
from typing import Any

import record

# A line of a text shown, short enough for one read to show it whole.
WIDTH = 1000


def entries(path: str) -> list[dict[str, Any]]:
    """The conversation's own entries of the record at the path: Claude Code also keeps a copy of
    each request it sends, which says again what was shown."""
    kept = record.read(path) or []
    return [e for e in kept if e.get("type") in ("user", "assistant", "attachment")]


def said(part: dict[str, Any]) -> str:
    """One part of a message as a line: a tool used by its name, with what it was given."""
    if part.get("type") == "tool_use":
        return f"[tool_use {part.get('name')}] {given(part.get('input'))}"
    return f"[{part.get('type')}] {part.get('text', '')}"


def given(values: Any) -> str:
    """What a tool was given, each value under its name, text as it was written, so a quote of a
    file written is found with its quotes and lines as they are; any other value as JSON."""
    if not isinstance(values, dict):
        return json.dumps(values, ensure_ascii=False)
    return "\n".join(
        f"{name}: {v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)}"
        for name, v in values.items()
    )


def wrapped(text: str) -> str:
    """The text with each line longer than a read shows cut at its blanks, so every word is read; a
    quote across a cut is found, as the cut is a blank."""
    return "".join(
        textwrap.fill(line, WIDTH, break_long_words=False) + "\n"
        if len(line) > WIDTH
        else line + "\n"
        for line in text.splitlines()
    )
