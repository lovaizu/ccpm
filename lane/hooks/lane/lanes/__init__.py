"""The lanes lane lays, one module each holding its action, its wording as the README's Lanes writes
it, the tools it watches and its check; and the lanes a hook's command lays, each a sentence of a
subagent's step with the check that notices a drift from it.

A hook's command gives the subagent as `<plugin>:<name>`, as Claude Code gives it in the event's
agent_type, and each lane as `<step>:<lane>:<what it takes>`, the things taken joined by commas."""

from __future__ import annotations

import re
from typing import Any

import call
import step

from lanes import hands_off

LANES = {"hands_off": hands_off}
# Where a wording shows what the lane takes, in quotes.
TAKEN = re.compile(r"`<[a-z]+>`")
# A plugin's or a subagent's name, as a hook's command carries it unquoted.
NAME = r"[A-Za-z0-9._-]+"
AGENT = re.compile(rf"{NAME}:{NAME}")
LANE = re.compile(r"(?P<step>[0-9]+):(?P<lane>[a-z_]+):(?P<takes>.*)")


def sentence(lane: str, takes: list[str]) -> str:
    """The lane's sentence: its wording with what it takes put in, each thing in quotes of its own,
    listed with commas and `or` before the last."""
    quoted = [f"`{t}`" for t in takes]
    listed = " or ".join(filter(None, [", ".join(quoted[:-1]), quoted[-1]]))
    # Given as a function, the text put in is taken as it is, a backslash in it among the rest.
    return TAKEN.sub(lambda _: listed, LANES[lane].WORDING)


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
        said = sentence(self.lane, self.takes)
        if not step.holds(self.root, self.name, self.number, said):
            gone = f"step {self.number} of {self.name} no longer says: {said}"
            again = f"lane:up must be run again on {self.plugin}, so its lanes match its steps"
            return [f"{gone} Stop here and reply that {again}."]
        return [said] if LANES[self.lane].drifts(call.read(event), self.takes) else []


def laid(root: str, words: list[str]) -> tuple[str, list[Laid]]:
    """The subagent a hook's command names and the lanes it lays in it; stops with ValueError
    saying which word is not as lane:up writes it."""
    if not words or not AGENT.fullmatch(words[0]):
        raise ValueError("gives no subagent as <plugin>:<name>")
    found = []
    for w in words[1:]:
        m = LANE.fullmatch(w)
        takes = m["takes"].split(",") if m else []
        if not m or m["lane"] not in LANES or not all(takes):
            raise ValueError(f"gives `{w}`, no lane as <step>:<lane>:<what it takes>")
        found.append(Laid(root, words[0], int(m["step"]), m["lane"], takes))
    return words[0], found
