"""Which run, start or turn, role, and step each move of a conversation belongs to, and what kind of
move it is, by what Claude Code's hook events carry, as dev/lane/claude-code-states.md lists: among
them, whether a command of a plugin calls its skill or is a move of the plugin's run that stands, as
a conversation holds one run of a plugin at a time, and which event begins a turn of the main
conversation."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import Any, Callable

from named_files import named, of_call
from order import StartsDue
from record import Entry, Run
from report import Report, read_report
from rules import Rules, Step, read_rules
from start_rules import asks_adapter
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
class Turn:
    """S11: a turn of the main conversation that its first move begins, on its run: the main
    conversation's role, by the skill's name, and the prompt that began it, as Claude Code gives
    it."""

    run: Run
    role: str
    prompt: str


@dataclass
class Move:
    """One move placed on its run: its `kind`, one of `call`, `start`, `tie`, `drop`, `read`,
    `report`, `end`, `turn_end`, `typed`, and `result_reached`; the role and the steps that hold
    it, by start_rules.steps: a subagent's those of its start, a SendMessage's `start` those of the
    start it resumes, and the main conversation's those of its turn's `turn` entry, else of the
    run's latest command that the rules name, else of the skill that called the run; the
    subagent's `agent_id`, None for the main conversation; for a `start`, its prompt, that of the
    start it resumes for a SendMessage, and None for any other move; the step its start or turn
    stands at; and the report where a reporter made the move."""

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
    if _standing_of(runs, skill) is not None:
        return None
    return SkillCall(event["session_id"], event["transcript_path"], skill, words)


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


def turn_beginning(event: Event, runs: list[Run]) -> Run | None:
    """S11: the run whose next turn of the main conversation the event's prompt begins, where the
    main conversation's role takes its steps from the plugin's adapter of the rules at each turn.

    Takes: a hook event, and the runs of its conversation.
    Gives: the standing run, with its folder, at a UserPromptSubmit with no `agent_id`, the person's
    prompt or the `<task-notification>` of a subagent's end, where it is the first since the run's
    latest `turn_ended` entry, the Stop that the guard last let through, and the rules name the
    main conversation's role with no steps. None at any other event, at a UserPromptSubmit before
    that Stop, as it goes on in the same turn, for a run with no folder yet, or where the rules
    give that role's steps.
    Changes: nothing.
    Refuses: OutOfForm, where the rules of the plugin's run are out of form.
    """
    if event.get("hook_event_name") != "UserPromptSubmit" or "agent_id" in event:
        return None
    found = _per_turn(runs)
    if found is None:
        return None
    run = found[0]
    turn = run.state.turn
    return run if turn.after_an_end and turn.prompt is None else None


def turn_opening(event: Event, runs: list[Run]) -> Turn | None:
    """S11: the turn of the main conversation whose steps the event is the first to need, where
    the main conversation's role takes its steps from the plugin's adapter of the rules at each
    turn.

    Takes: a hook event, and the runs of its conversation.
    Gives: the turn, on the standing run with its folder, at the main conversation's PreToolUse or
    Stop, the turn's first call or end, where the run holds no `turn` entry since its latest
    `turn_ended` entry, or since its start, and the rules name the main conversation's role with no
    steps: its role the skill of the run's latest command that the rules name at that event, so
    that a command that the Skill tool calls later in the turn leaves the turn's steps as they
    stand; its prompt that of the turn's `turn_begun` entry, empty for the run's first turn, whose
    command and words the run holds. None at any other event, for a turn that holds its `turn`
    entry, for a run with no folder yet, or where the rules give that role's steps.
    Changes: nothing.
    Refuses: OutOfForm, where the rules of the plugin's run are out of form.
    """
    if event.get("hook_event_name") not in ("PreToolUse", "Stop") or "agent_id" in event:
        return None
    found = _per_turn(runs)
    if found is None or found[0].state.turn.entry is not None:
        return None
    run, role = found
    return Turn(run, role, run.state.turn.prompt or "")


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
    rules = _rules_of(run)
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


def own_entries(run: Run, agent_id: str | None) -> list[Entry]:
    """S11: the entries of the moves that count for a start, or for the main conversation's turn.

    Takes: the run, and the subagent's `agent_id`, None for the main conversation.
    Gives: each entry of the run with the subagent's `agent_id`, in their order; for the main
    conversation, each entry with no `agent_id`, and, where the run holds a `turn` entry, only those
    after the latest, which the turn's first call or end added, as each turn's steps start afresh,
    so that its marks, items, reads, and result count for the turn alone. S12: each mark of a step
    or of its item before a `back` entry among them that undid the step is left out, so that the
    step and each after it are taken again in order; reads, results, and later marks stay.
    Changes: nothing.
    Refuses: nothing.
    """
    entries = run.entries
    if agent_id is None:
        entries = _since(entries, lambda e: e["kind"] == "turn")
    undone: set[str] = set()
    kept: list[Entry] = []
    # From the latest back, as a step gone back to undoes only the marks made before it.
    for entry in reversed(entries):
        if entry.get("agent_id") != agent_id:
            continue
        if entry["kind"] == "back":
            undone.update(entry["undone"])
        elif entry["kind"] == "mark" and entry["step"] in undone:
            continue
        kept.append(entry)
    return kept[::-1]


def marked(run: Run, agent_id: str | None) -> set[str]:
    """The steps that a start marked done.

    Takes: the run, and the subagent's `agent_id`, None for the main conversation.
    Gives: the name of each step that the run record holds a reporter's mark of, among the entries
    that own_entries gives for the subagent or the main conversation, the marks of items left
    out.
    Changes: nothing.
    Refuses: nothing.
    """
    return {
        entry["step"]
        for entry in own_entries(run, agent_id)
        if entry["kind"] == "mark" and "item" not in entry
    }


def _run_of(event: Event, runs: list[Run]) -> Run | None:
    """The run that the event belongs to: a command's, the standing run of its plugin; the main
    conversation's, the latest run not ended; a subagent's, the run of the start it's tied to."""
    command = command_of(event)
    if command is not None:
        return _standing_of(runs, command)
    agent_id = event.get("agent_id")
    return _standing(runs) if agent_id is None else _tied(runs, agent_id)


def _before(event: Event, run: Run, rules: Rules, due: Due) -> Move | None:
    """The move of a PreToolUse: a start by an Agent call, held to the steps of whoever starts it;
    a start by the main conversation's SendMessage to a subagent of the run that has ended and
    whose role the order makes due, with the role, the prompt, and the steps of the start it
    resumes; no move for any other SendMessage, as talk, such as one that Claude Code queues to a
    subagent that still runs; else a call."""
    tool = event.get("tool_name")
    call = _call(event, run, rules)
    if tool == "Agent":
        return replace(call, kind="start", step=None, prompt=event["tool_input"].get("prompt", ""))
    if tool != "SendMessage":
        return call
    to = event["tool_input"].get("to", "")
    resumed = run.state.tied.get(to)
    roles = [each["role"] for each in due(run).get("starts", [])]
    if call.agent_id is not None or resumed is None or not resumed.ended:
        return None
    if resumed.entry["role"] not in roles:
        return None
    role, steps = _held(rules, resumed.entry)
    return Move("start", event, run, role, None, resumed.entry["prompt"], steps, None, None)


def _after(event: Event, run: Run, rules: Rules) -> Move | None:
    """The move of a PostToolUse: a tie by a call that made a start, an Agent call or a
    SendMessage that resumed its subagent, of the role and steps of that start; a read by a Read; a
    report by a reporter's Bash call; else none."""
    tool = event.get("tool_name")
    start = run.state.calls.get(event["tool_use_id"])
    if start is not None:
        agent_id = (
            event["tool_response"]["agentId"] if tool == "Agent" else event["tool_input"]["to"]
        )
        role, steps = _held(rules, start.entry)
        return Move("tie", event, run, role, agent_id, None, steps, None, None)
    if tool == "Read":
        return _read(event, run, rules)
    if tool == "Bash":
        given = read_report(event["tool_response"].get("stdout", ""))
        return (
            None
            if given is None
            else replace(_call(event, run, rules), kind="report", report=given)
        )
    return None


def _failed(event: Event, run: Run, rules: Rules) -> Move | None:
    """The PostToolUseFailure of a start's Agent call as a `drop`; none of any other call."""
    start = run.state.calls.get(event.get("tool_use_id", ""))
    return None if start is None else replace(_call(event, run, rules), kind="drop")


def _reached(event: Event, run: Run, rules: Rules) -> Move | None:
    """The UserPromptSubmit of a task-notification of a subagent of the run as its result
    reaching, by the subagent that its task-id names; none for any other prompt."""
    told = re.search(r"<task-notification>.*?<task-id>(.*?)</task-id>", event["prompt"], re.DOTALL)
    if told is None or told[1] not in run.state.tied:
        return None
    return replace(_call(event, run, rules, told[1]), kind="result_reached")


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
    """A call of a subagent, the event's or the one given, held to the start it's tied to, or of
    the main conversation, held to its turn's `turn` entry, else to its role's steps; each at the
    first of its steps that it hasn't marked done."""
    agent_id = agent_id or event.get("agent_id")
    if agent_id is not None:
        holder = run.state.tied[agent_id].entry
    else:
        holder = run.state.turn.entry or {"role": _main_role(run, rules)}
    role, steps = _held(rules, holder)
    done = marked(run, agent_id)
    step = next((each["name"] for each in steps if each["name"] not in done), None)
    return Move("call", event, run, role, agent_id, None, steps, step, None)


def _held(rules: Rules, holder: Entry) -> tuple[str, list[Step]]:
    """The role and the steps of the entry that holds a start's moves, or a turn's, as a `turn`
    entry holds the main conversation's moves as a `start` entry holds a subagent's."""
    return holder["role"], start_steps(rules, holder["role"], holder.get("steps"))


def _main_role(run: Run, rules: Rules) -> str:
    """The main conversation's role: the skill of the run's latest command whose role the rules
    give steps of or leave to the plugin's adapter of the rules at each turn, else the skill that
    called the run."""
    role = run.skill
    for command in run.state.commands:
        if start_steps(rules, command, None) or asks_adapter(rules, command):
            role = command
    return role


def _rules_of(run: Run | None) -> Rules | None:
    """The rules of the run's plugin; None for no run, a run with no folder yet, or a plugin that
    gives no rules."""
    return read_rules(run.plugin_root) if run is not None and run.plugin_root else None


def _standing(runs: list[Run]) -> Run | None:
    """The run that the main conversation's moves belong to: the latest that hasn't ended."""
    return next((run for run in reversed(runs) if not run.state.ended), None)


def _standing_of(runs: list[Run], skill: str) -> Run | None:
    """The run of the skill's plugin, by the name before its `:`, that hasn't ended."""
    plugin = skill.partition(":")[0]
    return _standing([run for run in runs if run.skill.partition(":")[0] == plugin])


def _tied(runs: list[Run], agent_id: str) -> Run | None:
    """The run of the start that the subagent is tied to."""
    return next((run for run in runs if agent_id in run.state.tied), None)


def _per_turn(runs: list[Run]) -> tuple[Run, str] | None:
    """The standing run, with its folder, and the main conversation's role, where its plugin's
    rules leave the role's steps to the plugin's adapter of the rules at each turn; else None."""
    run = _standing(runs)
    rules = _rules_of(run)
    if run is None or rules is None:
        return None
    role = _main_role(run, rules)
    return (run, role) if asks_adapter(rules, role) else None


def _since(entries: list[Entry], latest: Callable[[Entry], bool]) -> list[Entry]:
    """The entries after the latest one that `latest` gives True for, or all where none does."""
    found = [i for i, entry in enumerate(entries) if latest(entry)]
    return entries[found[-1] + 1 :] if found else entries


# The move of each event that follows a call or a subagent's end, by the event's name.
_AFTER: dict[str, Callable[[Event, Run, Rules], Move | None]] = {
    "PostToolUse": _after,
    "PostToolUseFailure": _failed,
    "UserPromptSubmit": _reached,
}
# The move of each end: a subagent's, and the main conversation's turn's.
_ENDS = {"SubagentStop": "end", "Stop": "turn_end"}
