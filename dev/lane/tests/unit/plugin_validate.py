"""The double of `claude plugin validate` that the unit cases of laying.py give `lay` in its place:
each result comes from a line of recorded/claude-code-2.1.323-plugin-validate.jsonl, a record of
runs of Claude Code 2.1.323's `claude plugin validate`, as the plugin guide's Each result of a
double from a record says. The record's warnings of a plugin directory, which change no result,
are left out."""

from __future__ import annotations

import json
import os
from typing import Any

RECORDED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recorded")
RECORD = "claude-code-2.1.323-plugin-validate.jsonl"


def line(record: str, event: str) -> dict[str, Any]:
    """The line of the record in recorded/ that the event names."""
    with open(os.path.join(RECORDED, record), encoding="utf-8") as f:
        return next(each for each in map(json.loads, f) if each["event"] == event)


def passes(root: str) -> tuple[bool, str]:
    """What `claude plugin validate` gives on a valid plugin: it passes, and what it said."""
    ran = line(RECORD, "a valid plugin passes")
    return ran["exit"] == 0, ran["said"]


def fails(root: str) -> tuple[bool, str]:
    """What `claude plugin validate` gives on a plugin whose plugin.json holds a number as its
    version: it fails, and what it said."""
    ran = line(RECORD, "a plugin.json whose version is a number fails")
    return ran["exit"] == 0, ran["said"]
