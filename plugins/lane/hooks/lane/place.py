"""Which run, start, role, and step each move of a conversation belongs to, and what kind of move it
is, by what Claude Code's hook events carry, as dev/lane/claude-code-states.md lists: among them,
whether a command of a plugin calls its skill or is a move of the plugin's run that stands, as a
conversation holds one run of a plugin at a time."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import Any, Callable

from named_files import named, of_call
from order import StartsDue
from record import Entry, Run
from report import Report, read_report
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
    """One move placed on its run: its `kind`, one of `call`, `start`, `tie`, `drop`,
    `read`, `report`, `end`, `turn_end`, `typed`, and `result_reached`; the role whose steps hold
    it, the subagent's agent type, or for the main conversation the skill of the run's latest
    command whose steps its plugin's rules give, the skill that called the run before any, and for
    a SendMessage's `start` the role of the start it resumes; the subagent's `agent_id`, None for
    the main conversation; for a `start`, the prompt that the main conversation gives it, the
    prompt of the start it resumes for a SendMessage, and None for any other move; the steps that
    hold its start, as start_rules.steps gives them from the plugin's rules and the steps that its
    `start` entry holds, a SendMessage's `start` held to those of the start it resumes; the step
    its start stands at; and the report where a reporter made the move."""

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
    skill = command_of(event)
    if skill is None:
        return None
    given = event.get("command_args", event.get("tool_input", {}).get("args", ""))
    words = given if isinstance(given, str) else ""
    plugin = skill.partition(":")[0]
    if any(run.skill.partition(":")[0] == plugin and not _ended(run) for run in runs):
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
    output; the PostToolUse of a SendMessage that made a start as a `tie`; a subagent's
    SubagentStop as the `end` of its start, a pass after a message queued to it ending the same
    start; None where the event lies outside each run, such as an `agent_id` that no start ties.
    Changes: nothing.
    Refuses: OutOfForm, where the rules of the plugin's run are out of form at its command.
    """
    run = _run_of(event, runs)
    rules = read_rules(run.plugin_root) if run is not None and run.plugin_root else None
    if run is None or rules is None:
        return None
    if command_of(event) is not None:
        return replace(_call(event, run, rules), kind="typed")
    name = event.get("hook_event_name", "")
    if name == "PreToolUse":
        return _before(event, run, rules, due)
    if name in _AFTER:
        return _AFTER[name](event, run, rules)
    return replace(_call(event, run, rules), kind=_ENDS[name]) if name in _ENDS else None


def _failed(event: Event, run: Run, rules: Rules) -> Move | None:
    """The PostToolUseFailure of a start's Agent call as a `drop`; none of any other call."""
    start = _start_of(run, event.get("tool_use_id", ""))
    return None if start is None else replace(_call(event, run, rules), kind="drop")


def command_of(event: Event) -> str | None:
    """The skill that a command names, by its plugin's prefix.

    Takes: a hook event.
    Gives: the skill, such as `log:tag`, of a UserPromptExpansion's `command_name`, or of the
    PostToolUse of a Skill call's `tool_input.skill`; None for any other event, or a skill whose
    name holds no plugin's prefix, as Lane checks only a plugin's skill.
    Changes: nothing.
    Refuses: nothing.
    """
    name = event.get("hook_event_name")
    if name == "UserPromptExpansion":
        skill = event["command_name"]
    elif (name, event.get("tool_name")) == ("PostToolUse", "Skill"):
        skill = event["tool_input"]["skill"]
    else:
        return None
    return skill if ":" in skill else None


def _run_of(event: Event, runs: list[Run]) -> Run | None:
    """The run that the event belongs to: a command's, the standing run of its plugin; the main
    conversation's, the latest run not ended; a subagent's, the run of the start it's tied to."""
    command = command_of(event)
    if command is not None:
        plugin = command.partition(":")[0]
        mine = [run for run in runs if run.skill.partition(":")[0] == plugin]
        return _standing(mine)
    agent_id = event.get("agent_id")
    return _standing(runs) if agent_id is None else _tied(runs, agent_id)


def _reached(event: Event, run: Run, rules: Rules) -> Move | None:
    """The UserPromptSubmit of a task-notification of a subagent of the run as its result
    reaching, by the subagent that its task-id names; none for any other prompt."""
    told = re.search(r"<task-notification>.*?<task-id>(.*?)</task-id>", event["prompt"], re.DOTALL)
    if told is None or not any(_ties(entry, told[1]) for entry in run.entries):
        return None
    return replace(_call(event, run, rules, told[1]), kind="result_reached")


def marked(run: Run, agent_id: str | None) -> set[str]:
    """The steps that a start marked done.

    Takes: the run, and the subagent's `agent_id`, None for the main conversation.
    Gives: the name of each step that the run record holds a reporter's mark of, by the subagent
    or the main conversation, the marks of items left out.
    Changes: nothing.
    Refuses: nothing.
    """
    return {
        entry["step"]
        for entry in run.entries
        if entry["kind"] == "mark" and entry.get("agent_id") == agent_id and "item" not in entry
    }


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


def _before(event: Event, run: Run, rules: Rules, due: Due) -> Move | None:
    """The move of a PreToolUse: a start by an Agent call, held to the steps of whoever starts it;
    a start by the main conversation's SendMessage to a subagent of the run that has ended and
    whose role the order makes due, with the role, the prompt, and the steps of the start it
    resumes, and no move for any
    other SendMessage, as talk, such as one that Claude Code queues to a subagent that still runs;
    else a call."""
    tool = event.get("tool_name")
    call = _call(event, run, rules)
    if tool == "Agent":
        return replace(call, kind="start", step=None, prompt=event["tool_input"].get("prompt", ""))
    if tool != "SendMessage":
        return call
    to = event["tool_input"].get("to", "")
    resumed = latest_start(run, to)
    roles = [each["role"] for each in due(run).get("starts", [])]
    ended = resumed is not None and _ended_start(run, to)
    if call.agent_id is not None or not ended or resumed["role"] not in roles:
        return None
    role = resumed["role"]
    steps = start_steps(rules, role, resumed.get("steps"))
    return Move("start", event, run, role, None, resumed["prompt"], steps, None, None)


def latest_start(run: Run, agent_id: str) -> Entry | None:
    """The start that the subagent was last tied to.

    Takes: the run, and the subagent's `agent_id`.
    Gives: the run's `start` entry of the call of the subagent's latest tie; None where no start of
    the run is tied to it.
    Changes: nothing.
    Refuses: nothing.
    """
    ties = [entry for entry in run.entries if _ties(entry, agent_id)]
    return _start_of(run, ties[-1]["tool_use_id"]) if ties else None


def _ended_start(run: Run, agent_id: str) -> bool:
    """Whether the subagent's latest start has ended, by a result or a stop after its tie."""
    ties = [i for i, entry in enumerate(run.entries) if _ties(entry, agent_id)]
    after = run.entries[ties[-1] :]
    return any(e["kind"] in ("result", "stopped") and e.get("agent_id") == agent_id for e in after)


def _after(event: Event, run: Run, rules: Rules) -> Move | None:
    """The move of a PostToolUse: a tie by a call that made a start, an Agent call or a
    SendMessage that resumed its subagent, of the role and steps of that start; a read by a Read; a
    report by a reporter's Bash call; else none."""
    tool = event.get("tool_name")
    start = _start_of(run, event["tool_use_id"])
    if start is not None:
        agent_id = (
            event["tool_response"]["agentId"] if tool == "Agent" else event["tool_input"]["to"]
        )
        role = start["role"]
        steps = start_steps(rules, role, start.get("steps"))
        return Move("tie", event, run, role, agent_id, None, steps, None, None)
    if tool == "Read":
        return _read(event, run, rules)
    # A comparison of the name with Bash changes nothing: of the tools that reach it, only Agent and
    # AskUserQuestion sort before Bash, and the PostToolUse of neither holds a report either way.
    if tool == "Bash":  # pragma: no mutate
        given = read_report(event["tool_response"].get("stdout", ""))
        return (
            None
            if given is None
            else replace(_call(event, run, rules), kind="report", report=given)
        )
    return None


def _read(event: Event, run: Run, rules: Rules) -> Move | None:
    """The PostToolUse of a Read as a `read` where a rule of the files to read whole, of any step
    of whoever reads, names the file, as a part read ahead of its step counts there; else none."""
    call = _call(event, run, rules)
    whole = [
        path
        for step in call.steps
        for rule in step["rules"]
        if rule["type"] == "reads_whole"
        for path in rule["paths"]
    ]
    return replace(call, kind="read") if named(whole, of_call(event)) else None


def _call(event: Event, run: Run, rules: Rules, agent_id: str | None = None) -> Move:
    """A call of the main conversation, held to the steps of the run's latest command whose skill
    the rules give steps of, or of a subagent, the event's or the one given, held to the steps of
    the start it's tied to; each at the first of its steps that it hasn't marked done."""
    agent_id = agent_id or event.get("agent_id")
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
    done = marked(run, agent_id)
    step = next((each["name"] for each in steps if each["name"] not in done), None)
    return Move("call", event, run, role, agent_id, None, steps, step, None)


# The move of each event that follows a call or a subagent's end, by the event's name.
_AFTER: dict[str, Callable[[Event, Run, Rules], Move | None]] = {
    "PostToolUse": _after,
    "PostToolUseFailure": _failed,
    "UserPromptSubmit": _reached,
}
# The move of each end: a subagent's, and the main conversation's turn's.
_ENDS = {"SubagentStop": "end", "Stop": "turn_end"}
