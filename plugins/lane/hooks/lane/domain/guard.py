"""Decides what the guard does on each moment of a conversation: which of the Runs of the plugin's
skills that go on side by side the moment goes to, whether it lies in a Run and of a role whose
Lanes name it, which facts of it the run record keeps, when a Run starts and ends, whether each
call, start, and end passes, and what the main conversation or the role reads, from the laid set
and the run record alone."""

from __future__ import annotations

from collections.abc import Sequence
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
    the run records in the folder `temp`. It works out each Run of the conversation from the lines
    of its run record, as `routes.stand` does, and adds to the record, before it answers, each fact
    of the moment that no later payload gives again: a skill's call, a Start let through with its
    skill, its tie to a subagent, a Result that a run of result.py gave, a subagent's end, a command
    typed that a Route waits for or goes after, and each line that a Lane's command printed. It
    stops what it can't check, with why and who must fix it, and never raises."""
    raise NotImplementedError("guard.decide")


def in_run(event: Event, laid_set: LaidSet, runs: Sequence[Run]) -> bool:
    """Whether the guard checks the moment, given the conversation's Runs: it lies between the call
    of a skill of the plugin and the end of that skill's Run, and comes from the main conversation
    while such a Run goes on and stands aside from no other plugin's run, or from a subagent that a
    Start of such a Run ties, as the principle The guard checks only the run says."""
    raise NotImplementedError("guard.in_run")


def run_of(event: Event, laid_set: LaidSet, runs: Sequence[Run]) -> Run | None:
    """The Run among the conversation's that the moment goes to: a subagent's, the Run of the Start
    that its `agent_id` ties; a skill's call, typed or by the Skill tool, the Run of that skill; a
    run of result.py by the main conversation, the Run of the skill that its command names; a start
    of the main conversation, the Run whose moves open it, the one that began first where the moves
    of two open it; and None where none such goes on, as for a subagent that no Start ties."""
    raise NotImplementedError("guard.run_of")


def result_since(run: Run, agent: str) -> Result | None:
    """The Result that the subagent gave by result.py since its last Start or resume, as the Run
    records it, or None where it gave none; never what the subagent wrote in its reply."""
    raise NotImplementedError("guard.result_since")


def starts_from_main(event: Event) -> bool:
    """Whether a start of a role, or a call of the plugin's skill, comes from the main conversation,
    the only one that starts the roles in a Run."""
    raise NotImplementedError("guard.starts_from_main")
