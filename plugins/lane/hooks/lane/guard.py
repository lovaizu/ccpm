"""How Lane's guard meets Claude Code's hooks: which decision of Lane answers each hook event that
hooks/hooks.json enters it on, and the answer in the form that Claude Code reads from a hook."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass

from place import Event, Move, SkillCall
from record import Run


@dataclass
class Answer:
    """What the guard answers an event: whether it stops what the event follows, and what the
    main conversation or the subagent reads, such as the step's sentence or the starts due."""

    stop: bool = False
    said: str = ""


def answer(event: Event) -> Answer:
    """The guard's answer to a hook event.

    Takes: a hook event of hooks/hooks.json: PreToolUse, PostToolUse, PostToolUseFailure, Stop,
    SubagentStop, UserPromptSubmit, or UserPromptExpansion.
    Gives: first, for each run that place.opening gives, the answer of run_opened; then the answer
    of the interface below that the event's move reaches: skill_called for a skill's call, and for
    the others the move that place.place gives, held to the rules in its run's plugin's folder; the
    answers joined, stopping where either stops; an empty answer where the event lies outside each
    run, or its run's plugin gives no rules.
    Changes: what each interface it reaches changes.
    Refuses: nothing; where Lane can't check the event, such as a plugin's rules out of form or an
    adapter that failed, the answer says why and who fixes that, and stops the call.
    """
    raise NotImplementedError("guard.answer")


def skill_called(call: SkillCall) -> Answer:
    """S9 and S10: the main conversation calls the skill, with the words typed after the command.

    Takes: the skill's call.
    Gives: the starts due, each with its text, of a run of the skill that the run record holds
    with its folder and that its plugin's rules show not ended, where it stands; else an empty
    answer, as the transcript holds the skill's base directory only from the conversation's next
    event, where run_opened gives the starts due.
    Changes: the run record, by a new run of the skill and the words, with no folder, where it
    holds no such run.
    Refuses: nothing; a plugin's rules out of form, or a start adapter that failed, stops the call
    with what's wrong.
    """
    raise NotImplementedError("guard.skill_called")


def run_opened(event: Event, run: Run) -> Answer:
    """S9 and S10: the main conversation's next event after the skill's call, where the guard first
    reads the plugin's folder and rules.

    Takes: the event, whose `transcript_path` holds the skill's base directory, and the run with no
    folder.
    Gives: the starts due of the run, each with its text, after each result that the plugin's kept
    adapter gives for the run's words, where the plugin gives rules; an empty answer where the
    plugin gives none, or the transcript holds no base directory of the skill yet.
    Changes: the run record, by the run's folder and its kept results, in one write, where the
    transcript gives the folder.
    Refuses: nothing; a plugin's rules out of form, or an adapter that failed, stops the event's
    call with what's wrong.
    """
    raise NotImplementedError("guard.run_opened")


def start_made(move: Move) -> Answer:
    """S9: the main conversation starts a subagent of the plugin, or resumes one by SendMessage.

    Takes: a `start` move at the PreToolUse of an Agent or SendMessage call.
    Gives: an empty answer for a start due; for any other start of the plugin's subagents, or one
    by a subagent, a stop with the starts due.
    Changes: the run record, by the start, untied until the PostToolUse of its call; a resume that
    the PostToolUse finds queued to a subagent that still runs stays untied until that subagent's
    SubagentStop, where subagent_ended ties it, as Lane hooks no SubagentStart.
    Refuses: nothing.
    """
    raise NotImplementedError("guard.start_made")


def turn_ended(move: Move) -> Answer:
    """S9: the main conversation ends its turn.

    Takes: a `turn_end` move at the main conversation's Stop.
    Gives: a stop with the starts due, where a start is due; an empty answer where none is.
    Changes: the run record, by dropping each start still untied but a resume queued to a subagent
    that still runs.
    Refuses: nothing.
    """
    raise NotImplementedError("guard.turn_ended")


def command_typed(move: Move) -> Answer:
    """S9: the person types a command that a route waits for.

    Takes: a `typed` move at the UserPromptExpansion of the command.
    Gives: the starts that its route makes due, in place of those before.
    Changes: the run record, by the command.
    Refuses: nothing.
    """
    raise NotImplementedError("guard.command_typed")


def result_reached(move: Move) -> Answer:
    """S9: a subagent's end reaches the main conversation, with its result.

    Takes: a `result_reached` move at the UserPromptSubmit of the subagent's
    `<task-notification>`.
    Gives: the result, and the starts that its route makes due, each with its text; the start due
    again where the subagent was stopped with no result.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("guard.result_reached")


def fact_added(move: Move) -> Answer:
    """A move that only adds a fact to the run: a start tied at the PostToolUse of its Agent call,
    or of a SendMessage that resumed its subagent; a resume queued at the PostToolUse of a
    SendMessage to a subagent that still runs; a start dropped at its PostToolUseFailure; or a Read
    of a file that a rule of the files to read whole names, at its PostToolUse.

    Takes: a `tie`, `queue`, `drop`, or `read` move.
    Gives: an empty answer.
    Changes: the run record, by the fact.
    Refuses: nothing.
    """
    raise NotImplementedError("guard.fact_added")


def call_made(move: Move) -> Answer:
    """S1, S2, and S4: a start, or the main conversation in a run, calls a tool, held to the rules
    of its step.

    Takes: a `call` move at its PreToolUse.
    Gives: a stop with the sentence that lanes.judge_call gives; an empty answer where it gives
    none.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("guard.call_made")


def report_made(move: Move) -> Answer:
    """S3, S5, S6, and S7: a start runs a reporter of bin/, which counts as done only where its
    step's rules hold.

    Takes: a `report` move at the PostToolUse of the reporter's Bash call.
    Gives: for a step done, the sentence that lanes.judge_mark gives, with the step's items that
    the plugin's checklist adapter gives; an empty answer where the report holds.
    Changes: the run record, by the mark or the result, where it holds.
    Refuses: nothing.
    """
    raise NotImplementedError("guard.report_made")


def subagent_ended(move: Move) -> Answer:
    """S7 and S8: a start ends, held to its result, its steps, and the plugin's own check.

    Takes: an `end` move at the subagent's SubagentStop, the end of the pass that ran where a resume
    is queued to the subagent.
    Gives: a stop with the sentence that lanes.judge_end gives; an empty answer where it gives
    none.
    Changes: where the end holds and a resume is queued to the subagent, the run record, by tying
    that resume's start to the subagent; else nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("guard.subagent_ended")


def written(event: Event, given: Answer) -> str:
    """The answer in the form that Claude Code reads from a hook of the event.

    Takes: the hook event, and the guard's answer.
    Gives: the JSON that the hooks reference names for the event: a deny with its reason at a
    PreToolUse, a block with its reason at a PostToolUse, Stop, SubagentStop, UserPromptSubmit, or
    UserPromptExpansion, and what the reader reads as additional context.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("guard.written")


def main() -> int:
    """Reads the hook event on standard input, and prints the guard's answer to it."""
    event = json.load(sys.stdin)
    print(written(event, answer(event)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
