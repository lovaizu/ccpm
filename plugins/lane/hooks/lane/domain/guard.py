"""Decides what the guard does on each moment of a conversation: whether the moment lies in a Run
of the plugin and of a role whose Lanes name it, when a Run starts and ends, whether each call,
start, and end passes, and what the main conversation or the role reads, from the laid set and
the run record alone."""

from __future__ import annotations

from dataclasses import dataclass

from domain.event import Event
from domain.laid_set import LaidSet
from domain.run_record import Result, Run


@dataclass(frozen=True)
class Decision:
    """What the guard gives on a moment: `stop` whether it stops the call, the end, or the prompt,
    `said` what the one stopped reads, and `context` what the main conversation reads beside the
    moment, such as the start due."""

    stop: bool = False
    said: str = ""
    context: str = ""


LET_THROUGH = Decision()


def decide(event: Event, laid_set: LaidSet, plugin_root: str, temp: str) -> Decision:
    """What the guard of the plugin in the folder, holding its laid set, gives on the moment, with
    the run records in the folder `temp`. It keeps the Run in its run record before it answers. It
    stops what it can't check, with why and who must fix it, and never raises."""
    raise NotImplementedError("guard.decide")


def in_run(event: Event, laid_set: LaidSet, run: Run | None) -> bool:
    """Whether the guard checks the moment: it lies between the call of the plugin's skill and the
    end of its Run, and comes from the main conversation or from a subagent of a role of the
    plugin, as the principle The guard checks only the run says."""
    raise NotImplementedError("guard.in_run")


def result_since(run: Run, agent: str) -> Result | None:
    """The Result that the subagent gave by result.py since its last Start or resume, as the Run
    records it, or None where it gave none; never what the subagent wrote in its reply."""
    raise NotImplementedError("guard.result_since")


def starts_from_main(event: Event) -> bool:
    """Whether a start of a role, or a call of the plugin's skill, comes from the main conversation,
    the only one that starts the roles in a Run."""
    raise NotImplementedError("guard.starts_from_main")
