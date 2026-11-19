"""Which run, start, role, and step each move of a conversation belongs to, and what kind of move it
is, by what Claude Code's hook events carry, as dev/lane/claude-code-states.md lists: among them,
whether a command of a plugin calls its skill or is a move of the plugin's run that stands, as a
conversation holds one run of a plugin at a time."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Callable

from order import StartsDue
from record import Entry, Run
from report import Report
from rules import Rules, Step, read_rules
from start_rules import steps as start_steps

# A hook event as Claude Code sends it on standard input.
Event = dict[str, Any]
# The starts due of a run, or its end, as the plugin's order gives them.
Due = Callable[[Run], StartsDue]


@dataclass
class SkillCall:
    """A call of a skill, typed by the person or made by the Skill tool, with the words given
    after it."""

    session_id: str
    transcript_path: str
    skill: str
    words: str


@dataclass
class Move:
    """One move placed on its run: its `kind`, one of `call`, `start`, `tie`, `queue`, `drop`,
    `read`, `report`, `end`, `turn_end`, `typed`, and `result_reached`; the role whose steps hold
    it, the subagent's agent type, or for the main conversation the skill of the run's latest
    command whose steps its plugin's rules give, the skill that called the run before any; the
    subagent's `agent_id`, None for the main conversation; for a `start`, the prompt that the main
    conversation gives it, the prompt of the start it resumes for a SendMessage, and None for any
    other move; the steps that hold its start, as start_rules.steps gives them from the plugin's
    rules and the steps that its `start` entry holds; the step its start stands at; and the report
    where a reporter made the move."""

    kind: str
    event: Event
    run: Run
    role: str
    agent_id: str | None
    prompt: str | None
    steps: list[Step]
    step: str | None
    report: Report | None


def skill_call(event: Event, runs: list[Run]) -> SkillCall | None:
    """The skill that the event calls.

    Takes: a UserPromptExpansion, or a PostToolUse of Skill, so that a Skill call denied at its
    PreToolUse calls no skill; and the runs of its conversation.
    Gives: the skill by `command_name` or `tool_input.skill`, with `command_args` or `args`, only
    where the skill's name holds its plugin's prefix, as Lane checks only a plugin's skill, and no
    run of the skill's plugin, by the name before its `:`, stands in the conversation: where each
    such run holds an `ended` entry, or none was added. None for a command, typed or by
    the Skill tool, of a plugin whose run stands, with no folder yet or not ended, as that command
    is a `typed` move of the run, which place gives; and for any other event.
    Changes: nothing.
    Refuses: nothing.
    """
    name = event.get("hook_event_name")
    if name == "UserPromptExpansion":
        skill, words = event["command_name"], event.get("command_args", "")
    elif name == "PostToolUse" and event.get("tool_name") == "Skill":
        skill, words = event["tool_input"]["skill"], event["tool_input"].get("args", "")
    else:
        return None
    plugin, prefixed, _ = skill.partition(":")
    if not prefixed or any(
        run.skill.partition(":")[0] == plugin and not _ended(run) for run in runs
    ):
        return None
    return SkillCall(event["session_id"], event["transcript_path"], skill, words)


def opening(event: Event, runs: list[Run]) -> list[Run]:
    """The runs whose plugin's folder the event first lets the guard read from the transcript.

    Takes: a hook event, and the runs of its conversation.
    Gives: each run with no folder yet, at an event of the main conversation after the skill's
    call, as the transcript holds the skill's base directory only from then: any event with no
    `agent_id` but the UserPromptExpansion of the call and the PreToolUse and PostToolUse of its
    Skill call; none at a subagent's event.
    Changes: nothing.
    Refuses: nothing.
    """
    name = event.get("hook_event_name")
    of_skill = name in ("PreToolUse", "PostToolUse") and event.get("tool_name") == "Skill"
    if "agent_id" in event or name == "UserPromptExpansion" or of_skill:
        return []
    return [run for run in runs if run.plugin_root is None]


def place(event: Event, runs: list[Run], due: Due) -> Move | None:
    """The move that the event makes, on the run whose start it belongs to.

    Takes: a hook event, the runs of its conversation, and the starts due of a run, as the plugin's
    order gives them.
    Gives: the move, placed by `session_id`, by a missing `agent_id` for the main conversation, by
    the `agent_id` that the PostToolUse of an Agent call tied to a start, and by the skill that a
    result names; the PreToolUse of an Agent call as a `start` with its `tool_input.prompt`; the
    main conversation's PreToolUse of a SendMessage to a subagent of the run as a `start` where the
    order makes that subagent's role due, and as no move where it doesn't, so that it goes through
    as talk, as does a subagent's SendMessage to another subagent; a command, typed or by the Skill
    tool, that skill_call gives no call of as a `typed` move on the run of its plugin that stands; a
    reporter's Bash call as a `report` move with the report that report.read_report gives of its
    output; the PostToolUse of a SendMessage that made a start as a `tie` where it resumed the
    subagent, and as a `queue` where it queued the message to a subagent that still runs; that
    subagent's SubagentStop as the `end` of the pass that ran, on the start tied to it before, with
    the resume queued still untied; None where the event lies outside each run, such as an
    `agent_id` that no start ties.
    Changes: nothing.
    Refuses: OutOfForm, where the rules of the plugin's run are out of form at its command.
    """
    agent_id = event.get("agent_id")
    run = _standing(runs) if agent_id is None else _tied(runs, agent_id)
    if run is None or run.plugin_root is None:
        return None
    rules = read_rules(run.plugin_root)
    if rules is None:
        return None
    name = event.get("hook_event_name")
    if name == "PreToolUse":
        return _before(event, run, rules)
    if name == "PostToolUse":
        return _after(event, run, rules)
    if name == "UserPromptSubmit" and "<task-notification>" not in event.get("prompt", ""):
        return None
    raise NotImplementedError(f"place.place of {name}")


def _ended(run: Run) -> bool:
    """Whether the run's order said it ends."""
    return any(entry["kind"] == "ended" for entry in run.entries)


def _standing(runs: list[Run]) -> Run | None:
    """The run that the main conversation's moves belong to: the latest that hasn't ended."""
    return next((run for run in reversed(runs) if not _ended(run)), None)


def _tied(runs: list[Run], agent_id: str) -> Run | None:
    """The run of the start that the subagent is tied to."""
    tied = (run for run in runs for entry in run.entries if _ties(entry, agent_id))
    return next(tied, None)


def _ties(entry: Entry, agent_id: str) -> bool:
    return entry["kind"] == "tie" and entry["agent_id"] == agent_id


def _start_of(run: Run, tool_use_id: str) -> Entry | None:
    """The run's start of the call."""
    starts = (e for e in run.entries if e["kind"] == "start" and e["tool_use_id"] == tool_use_id)
    return next(starts, None)


def _before(event: Event, run: Run, rules: Rules) -> Move | None:
    """The move of a PreToolUse: a start by an Agent call, held to the steps of whoever starts it,
    else a call."""
    tool = event.get("tool_name")
    if tool == "Agent":
        call = _call(event, run, rules)
        return replace(call, kind="start", step=None, prompt=event["tool_input"].get("prompt", ""))
    if tool in ("SendMessage", "Skill"):
        raise NotImplementedError(f"place.place of the PreToolUse of {tool}")
    return _call(event, run, rules)


def _after(event: Event, run: Run, rules: Rules) -> Move | None:
    """The move of a PostToolUse: a tie by an Agent call, else none of the calls that S1 makes."""
    tool = event.get("tool_name")
    if tool == "Agent":
        start = _start_of(run, event["tool_use_id"])
        if start is None:
            return None
        role = start["role"]
        steps = start_steps(rules, role, start.get("steps"))
        agent_id = event["tool_response"]["agentId"]
        return Move("tie", event, run, role, agent_id, None, steps, None, None)
    if tool in ("SendMessage", "Skill", "Bash", "Read"):
        raise NotImplementedError(f"place.place of the PostToolUse of {tool}")
    return None


def _call(event: Event, run: Run, rules: Rules) -> Move:
    """A call of the main conversation, held to the steps of the run's latest command whose skill
    the rules give steps of, or of a subagent, held to the steps of the start it's tied to; each
    at the first of its steps that it hasn't marked done."""
    agent_id = event.get("agent_id")
    if agent_id is None:
        role = run.skill
        for entry in run.entries:
            if entry["kind"] == "typed" and start_steps(rules, entry["command"], None):
                role = entry["command"]
        steps = start_steps(rules, role, None)
    else:
        tie = next(e for e in reversed(run.entries) if _ties(e, agent_id))
        start = next(e for e in run.entries if e.get("tool_use_id") == tie["tool_use_id"])
        role = start["role"]
        steps = start_steps(rules, role, start.get("steps"))
    done = {
        entry["step"]
        for entry in run.entries
        if entry["kind"] == "mark" and entry.get("agent_id") == agent_id and "item" not in entry
    }
    step = next((each["name"] for each in steps if each["name"] not in done), None)
    return Move("call", event, run, role, agent_id, None, steps, step, None)
