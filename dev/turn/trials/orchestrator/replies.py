"""The replies the stand-in roles of the orchestrator trial give, by the way the run takes, each
built from the pieces the ways share: the README the generator writes, its claim and the first
user's reading of it, each item at its lines or, where the first user finds no Good, with what the
reader would need."""

from __future__ import annotations

from typing import Any

from shared import LICENSED, UNLICENSED

CHECKLIST = "checklist.md"
MIT = {"checklist": CHECKLIST, "item": "B-1", "lines": ["README.md:11-11"]}
NEED = {
    "checklist": CHECKLIST,
    "item": "B-1",
    "need": "Before using demo in their own work, the reader can tell on what terms they may.",
}


def each_part(licensed: bool) -> dict[str, Any]:
    """B-2, at lines in each part of the README, the part of its license among them where it has
    one."""
    lines = ["README.md:3-3", "README.md:7-7"] + ["README.md:11-11"] * licensed
    return {"checklist": CHECKLIST, "item": "B-2", "lines": lines}


def made(write: str, *items: dict[str, Any]) -> dict[str, Any]:
    """The generator writing the README and running demo, then claiming the items."""
    return {"write": write, "run": ["sh demo.sh"], "reply": {"items": list(items), "chosen": []}}


def read(*items: dict[str, Any]) -> dict[str, Any]:
    """The first user's reading of the items."""
    return {"reply": {"items": list(items)}}


# Each way's replies, by role, in the order the docstring of orchestrator.py lists them.
WAYS = {
    "plain": {
        "generator": [made(LICENSED, MIT, each_part(True))],
        "first-user": [read(MIT, each_part(True))],
    },
    "left": {
        "generator": [made(UNLICENSED, dict(MIT, lines=["README.md:1-7"]), each_part(False))],
        "first-user": [read(NEED, each_part(False))],
    },
}
