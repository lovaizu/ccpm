"""The lanes lane lays, one module each holding its action, its wording as the README's Lanes writes
it, the tools it watches and its check; and the lanes a hook's command lays, each a sentence of a
subagent's step with the check that notices a drift from it.

A hook's command gives the subagent as `<plugin>:<name>`, as Claude Code gives it in the event's
agent_type, and each lane as `<step>:<lane>:<what it takes>`, the things taken joined by commas.
A lane is held on a tool call, the PreToolUse event, or, where its module names it, on the
subagent about to end, the SubagentStop event; each event's script runs the lanes held on it."""

from __future__ import annotations

import os
import re
import sys
from typing import Any

import call
import hook
import step

from lanes import (
    end_when,
    every_item,
    hands_off,
    read_only,
    read_whole,
    start_with,
    test_after,
    write_only,
)

LANES = {
    "start_with": start_with,
    "read_only": read_only,
    "read_whole": read_whole,
    "write_only": write_only,
    "hands_off": hands_off,
    "test_after": test_after,
    "end_when": end_when,
    "every_item": every_item,
}
# Where a wording shows what the lane takes, in quotes.
TAKEN = re.compile(r"`<[a-z]+>`")
# A plugin's or a subagent's name, as a hook's command carries it unquoted.
NAME = r"[A-Za-z0-9._-]+"
AGENT = re.compile(rf"{NAME}:{NAME}")
LANE = re.compile(r"(?P<step>[0-9]+):(?P<lane>[a-z_]+):(?P<takes>.*)")


def held_on(lane: str) -> str:
    """The event the lane is held on: the one its module names, PreToolUse where it names none."""
    return getattr(LANES[lane], "EVENT", "PreToolUse")


def slots(lane: str) -> int:
    """How many places the lane's wording shows for what it takes."""
    return len(TAKEN.findall(LANES[lane].WORDING))


def sentence(lane: str, takes: list[str]) -> str:
    """The lane's sentence: its wording with what it takes put in, one thing in each place in order,
    the last place taking the rest, each thing in quotes of its own, listed with commas and `or`
    before the last."""
    last = slots(lane) - 1
    parts = iter([*([t] for t in takes[:last]), takes[last:]])

    def listed(_: re.Match[str]) -> str:
        quoted = [f"`{t}`" for t in next(parts)]
        return " or ".join(filter(None, [", ".join(quoted[:-1]), quoted[-1]]))

    # Given as a function, the text put in is taken as it is, a backslash in it among the rest.
    return TAKEN.sub(listed, LANES[lane].WORDING)


def word(number: int, lane: str, takes: list[str]) -> str:
    """The lane as a hook's command gives it."""
    return f"{number}:{lane}:{','.join(takes)}"


class Laid:
    """A lane laid on a step of a subagent of the plugin at root."""

    def __init__(self, root: str, agent: str, number: int, lane: str, takes: list[str]) -> None:
        self.root, self.plugin, self.name = root, *agent.split(":")
        self.number, self.lane, self.takes = number, lane, takes

    def check(self, event: dict[str, Any]) -> list[str]:
        """The lane's sentence where the call drifts from it; where the step no longer says it,
        that lane:up must be run again; nothing otherwise."""
        # A lane held as the subagent ends lets it end where what it did is not known, or where,
        # told before, it has answered with words alone, so it is told and never held for good.
        end = call.ended(event) if held_on(self.lane) in ("SubagentStop",) else None
        if end is not None and (end.made is None or end.answered):
            return []
        said = sentence(self.lane, self.takes)
        if not step.holds(self.root, self.name, self.number, said):
            gone = f"step {self.number} of {self.name} no longer says: {said}"
            again = f"lane:up must be run again on {self.plugin}, so its lanes match its steps"
            return [f"{gone} Stop here and reply that {again}."]
        # Each lane's check takes what its event gives: the call, or how the subagent ends.
        lane: Any = LANES[self.lane]
        return [said] if lane.drifts(call.read(event) if end is None else end, self.takes) else []


def laid(root: str, words: list[str], held: str = "PreToolUse") -> tuple[str, list[Laid]]:
    """The subagent a hook's command names and the lanes it lays in it, each held on the event
    given; stops with ValueError saying which word is not as lane:up writes it."""
    if not words or not AGENT.fullmatch(words[0]):
        raise ValueError("gives no subagent as <plugin>:<name>")
    found = []
    for w in words[1:]:
        m = LANE.fullmatch(w)
        takes = m["takes"].split(",") if m else []
        if not m or m["lane"] not in LANES or not all(takes):
            raise ValueError(f"gives `{w}`, no lane as <step>:<lane>:<what it takes>")
        if held_on(m["lane"]) not in (held,) or len(takes) < slots(m["lane"]):
            raise ValueError(
                f"gives `{w}`, no lane held on {held} taking a thing for each `<...>` it shows"
            )
        found.append(Laid(root, words[0], int(m["step"]), m["lane"], takes))
    return words[0], found


def main(held: str, words: list[str]) -> int:
    """Runs the lanes a hook's command lays, held on the event, on the event Claude Code hands on
    stdin, for the plugin found where Claude Code gives its folder, CLAUDE_PLUGIN_ROOT; what the
    event script exits with. A command not in the form lane:up writes lets the subagent go on,
    telling the user, as no subagent or lane can be told from it."""
    try:
        agent, found = laid(os.environ.get("CLAUDE_PLUGIN_ROOT", ""), words, held)
    except ValueError as wrong:
        sys.stderr.write(
            f"lane: the hook's command {wrong}, not as lane:up writes it, so this goes on"
            " unchecked; run lane:up again on the plugin to write its hooks anew\n"
        )
        return hook.UNREAD
    return hook.run(agent.split(":")[0], found, sys.stdin, sys.stderr, agent)
