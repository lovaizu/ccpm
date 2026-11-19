"""How Lane's guard meets Claude Code's hooks: which decision of Lane answers each hook event that
hooks/hooks.json enters it on, and the answer in the form that Claude Code reads from a hook."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, replace
from typing import Callable, TypeVar, cast

import adapters
import place
import record
import rule_types
from adapters import AdapterFailed
from named_files import of_call
from order import StartsDue
from place import Event, Move, SkillCall
from plugin import plugin_root
from record import Run
from report import Report
from rule_types.result import given
from rules import OutOfForm, Rules, read_rules
from start_rules import asks_adapter


@dataclass
class Answer:
    """What the guard answers an event: whether it stops what the event follows, and what the
    main conversation or the subagent reads, such as the step's sentence or the starts due."""

    stop: bool = False
    said: str = ""


_Answers = TypeVar("_Answers", bound=Callable[..., Answer])


def _checked(answers: _Answers) -> _Answers:
    """The interface, its answer stopping the call with what's wrong and who fixes it where Lane
    can't check it, as a plugin's rules out of form or an adapter that failed."""

    def checked(*given: object) -> Answer:
        try:
            return answers(*given)
        except (OutOfForm, AdapterFailed) as wrong:
            return Answer(True, str(wrong))

    return cast(_Answers, checked)


def answer(event: Event) -> Answer:
    """The guard's answer to a hook event.

    Takes: a hook event of hooks/hooks.json: PreToolUse, PostToolUse, PostToolUseFailure, Stop,
    SubagentStop, UserPromptSubmit, or UserPromptExpansion.
    Gives: first, for each run that place.opening gives, the answer of run_opened; then the answer
    of the interface below that the event's move reaches: skill_called for the skill's call that
    place.skill_call gives, and for the others the move that place.place gives, with the starts due
    that adapters.starts_due gives, held to the rules
    in its run's plugin's folder; the answers joined, stopping where either stops; an empty answer
    where the event lies outside each run, or its run's plugin gives no rules. Wherever an answer
    gives the starts due, or holds a start to them, they are those that adapters.starts_due gives
    for the run as it stands once the move is added, none while the run waits; turn_ended asks
    them of a turn's end that it lets through.
    Changes: what each interface it reaches changes; where adapters.starts_due says the run ends,
    the run record, by an `ended` entry of the run.
    Refuses: nothing; where Lane can't check the event, such as a plugin's rules out of form or an
    adapter that failed, the answer says why and who fixes that, and stops the call.
    """
    session = event["session_id"]
    answers = [run_opened(event, run) for run in place.opening(event, record.runs(session))]
    runs = record.runs(session)
    call = place.skill_call(event, runs)
    if call is not None:
        answers.append(skill_called(call))
    else:
        answers.append(_placed(event))
    said = "\n".join(given.said for given in answers if given.said)
    return Answer(any(given.stop for given in answers), said)


@_checked
def _placed(event: Event) -> Answer:
    """The answer of the interface that the event's move reaches, an empty one where it makes
    none."""
    runs = record.runs(event["session_id"])
    move = place.place(event, runs, lambda run: _due(run, event))
    return Answer() if move is None else _ANSWERS[move.kind](move)


def skill_called(call: SkillCall) -> Answer:
    """S9 and S10: the main conversation calls the skill, with the words typed after the command.

    Takes: the skill's call that place.skill_call gives, where no run of its plugin stands in the
    conversation, such as the plugin's first command in it, or one typed once its run ended.
    Gives: an empty answer, as the transcript holds the skill's base directory only from the
    conversation's next event, where run_opened gives the starts due.
    Changes: the run record, by a new run of the skill and the words, with no folder.
    Refuses: nothing.
    """
    entry: record.Entry = {
        "kind": "run",
        "run": f"r{len(record.runs(call.session_id)) + 1}",
        "skill": call.skill,
        "words": call.words,
    }
    record.add(call.session_id, [entry])
    return Answer()


@_checked
def run_opened(event: Event, run: Run) -> Answer:
    """S9 and S10: the main conversation's next event after the skill's call, where the guard first
    reads the plugin's folder and rules.

    Takes: the event, whose `transcript_path` holds the skill's base directory, and the run with no
    folder.
    Gives: the starts due of the run, where the plugin gives rules; an empty answer where the plugin
    gives none, or the transcript holds no base directory of the skill yet.
    Changes: the run record, by the run's folder, where the transcript gives it.
    Refuses: nothing; a plugin's rules out of form, or an adapter that failed, stops the event's
    call with what's wrong.
    """
    try:
        root = plugin_root(event["transcript_path"], run.skill)
    except FileNotFoundError:
        root = None
    if root is None:
        return Answer()
    record.add(run.session_id, [{"kind": "folder", "run": run.id, "plugin_root": root}])
    opened = replace(run, plugin_root=root)
    return Answer() if read_rules(root) is None else Answer(said=_due_said(_due(opened, event)))


@_checked
def start_made(move: Move) -> Answer:
    """S9: the main conversation starts a subagent of the plugin, or resumes one by SendMessage.

    Takes: a `start` move at the PreToolUse of an Agent or SendMessage call.
    Gives: an empty answer for a start of a role due; for any other start of the plugin's
    subagents, or one by a subagent, a stop with the starts due.
    Changes: the run record, by the start with its prompt, and with the steps that
    adapters.given_steps gives from the prompt where start_rules.asks_adapter says the start takes
    rules from the plugin's adapter of the rules, untied until the PostToolUse of its call; a
    resume, by its start with the prompt and the steps of the start it resumes.
    Refuses: nothing; an adapter of the starts due that failed stops the call with what's wrong,
    and so does, for a start that takes its steps from the plugin's adapter of the rules, an adapter
    of the rules that the plugin doesn't give, that fails, or that gives out of its form, its
    sentence saying that the plugin's author adds or mends lane/adapters/rules.py for the role.
    """
    resumed = _resumed(move)
    role = move.event["tool_input"].get("subagent_type", resumed.get("role", ""))
    due = _due(move.run, move.event)
    plugin = move.run.skill.partition(":")[0]
    if role.partition(":")[0] != plugin and move.agent_id is None:
        return Answer()
    if move.agent_id is not None or not any(s["role"] == role for s in due.get("starts", [])):
        return Answer(True, _due_said(due))
    entry: record.Entry = {
        "kind": "start",
        "run": move.run.id,
        "role": role,
        "tool_use_id": move.event["tool_use_id"],
        "prompt": resumed.get("prompt", move.prompt or ""),
    }
    if "steps" in resumed:
        entry["steps"] = resumed["steps"]
    elif not resumed and asks_adapter(_rules(move.run), role):
        cwd = move.event["cwd"]
        entry["steps"] = adapters.given_steps(_root(move.run), cwd, move.run, role, entry["prompt"])
    record.add(move.run.session_id, [entry])
    return Answer()


def _resumed(move: Move) -> record.Entry:
    """The start that a SendMessage resumes, as place.latest_start gives it for the subagent it
    names; none for an Agent call."""
    return place.latest_start(move.run, move.event["tool_input"].get("to", "")) or {}


@_checked
def turn_ended(move: Move) -> Answer:
    """S5, S8, and S9: the main conversation ends its turn, held to its skill's steps and to the
    starts due.

    Takes: a `turn_end` move at the main conversation's Stop.
    Gives: a stop with the sentence that rule_types.judge_end gives, where the rules give the steps
    of the move's role; else a stop with the starts due, where a start is due; an empty answer
    where none is.
    Changes: the run record, by dropping each start still untied; and, where the turn's end goes
    through, by an `ended` entry where adapters.starts_due, asked with the turn ended, says the run
    ends.
    Refuses: nothing; an adapter of the starts due that failed stops the turn's end with what's
    wrong.
    """
    entries = move.run.entries
    settled = {e.get("tool_use_id") for e in entries if e["kind"] in ("tie", "drop")}
    untied = [e for e in entries if e["kind"] == "start" and e["tool_use_id"] not in settled]
    drops: list[record.Entry] = [
        {"kind": "drop", "run": move.run.id, "tool_use_id": e["tool_use_id"]} for e in untied
    ]
    if drops:
        record.add(move.run.session_id, drops)
    run = replace(move.run, entries=[*entries, *drops])
    said = rule_types.judge_end(replace(move, run=run))
    if said is not None:
        return Answer(True, said)
    due = _due(run, move.event)
    if due.get("starts"):
        return Answer(True, _due_said(due))
    _end_if(run, move.event, turn_ended=True)
    return Answer()


def command_typed(move: Move) -> Answer:
    """S9 and S10: a command of the plugin, typed by the person or called by the Skill tool, moves
    the run that stands, as a conversation holds one run of a plugin at a time.

    Takes: a `typed` move at the UserPromptExpansion of the command, or at the PostToolUse of its
    Skill call, which place gives while the run of the command's plugin stands.
    Gives: where the run stands: the starts due once the command is added.
    Changes: the run record, by the command.
    Refuses: AdapterFailed, where an adapter of the starts due fails, which answer gives as a stop
    of the call with what's wrong.
    """
    command = place.command_of(move.event) or ""
    typed: record.Entry = {"kind": "typed", "run": move.run.id, "command": command}
    record.add(move.run.session_id, [typed])
    run = replace(move.run, entries=[*move.run.entries, typed])
    return Answer(said=_due_said(_end_if(run, move.event)))


def result_reached(move: Move) -> Answer:
    """S9: a subagent's end reaches the main conversation, with its result.

    Takes: a `result_reached` move at the UserPromptSubmit of the subagent's
    `<task-notification>`.
    Gives: the result, and the starts due after it; the start's role due again, where the order
    gives it, as a start stopped with no result counts as not made.
    Changes: the run record, by a `stopped` entry of the subagent's start, where it was stopped
    with no result, such as by TaskStop; else nothing.
    Refuses: AdapterFailed, where an adapter of the starts due fails, which answer gives as a stop
    of the call with what's wrong.
    """
    run = move.run
    if "<status>killed</status>" in move.event["prompt"]:
        stopped: record.Entry = {"kind": "stopped", "run": run.id, "agent_id": move.agent_id}
        record.add(run.session_id, [stopped])
        run = replace(run, entries=[*run.entries, stopped])
        told = f"{move.role} stopped with no result."
    else:
        gave = given(move)
        told = f"{move.role} gave {gave}." if gave else ""
    due = _end_if(run, move.event)
    return Answer(said=" ".join(each for each in (told, _due_said(due)) if each))


def fact_added(move: Move) -> Answer:
    """A move that only adds a fact to the run: a start tied at the PostToolUse of its Agent call,
    or of a SendMessage that resumed its subagent; a start dropped at its PostToolUseFailure; or a
    Read of a file that a rule of the files to read whole names, at its PostToolUse.

    Takes: a `tie`, `drop`, or `read` move.
    Gives: an empty answer.
    Changes: the run record, by the fact.
    Refuses: nothing.
    """
    entry: record.Entry = {"kind": move.kind, "run": move.run.id, "agent_id": move.agent_id}
    # `is not` in place of `!=` changes nothing, as place gives each kind by a literal of its own,
    # which Python keeps as one object.
    if move.kind != "read":  # pragma: no mutate
        entry["tool_use_id"] = move.event["tool_use_id"]
    else:
        lines = move.event["tool_response"]["file"]
        entry["path"] = of_call(move.event)
        entry["first_line"] = lines["startLine"]
        entry["last_line"] = lines["startLine"] + lines["numLines"] - 1
    record.add(move.run.session_id, [entry])
    return Answer()


def call_made(move: Move) -> Answer:
    """S1, S2, and S4: a start, or the main conversation in a run, calls a tool, held to the rules
    of its step.

    Takes: a `call` move at its PreToolUse.
    Gives: a stop with the sentence that rule_types.judge_call gives; an empty answer where it gives
    none.
    Changes: nothing.
    Refuses: nothing.
    """
    said = rule_types.judge_call(move)
    return Answer() if said is None else Answer(True, said)


def report_made(move: Move) -> Answer:
    """S3, S5, S6, and S7: a start runs a reporter of bin/, which counts as done only where its
    step's rules hold.

    Takes: a `report` move at the PostToolUse of the reporter's Bash call.
    Gives: for a step done, a stop with the sentence that rule_types.judge_mark gives; an empty
    answer where the report holds.
    Changes: the run record, by the mark or the result, where it holds.
    Refuses: nothing.
    """
    given = cast(Report, move.report)
    # `>=` in place of `==` changes nothing, as no kind of report sorts after `step`.
    if given["kind"] == "step":  # pragma: no mutate
        said = rule_types.judge_mark(move)
        if said is not None:
            return Answer(True, said)
    entry: record.Entry = {**given, "run": move.run.id, "role": move.role}
    entry.update(kind="result" if given["kind"] == "result" else "mark", agent_id=move.agent_id)
    record.add(move.run.session_id, [entry])
    return Answer()


def subagent_ended(move: Move) -> Answer:
    """S7 and S8: a start ends, held to its result, its steps, and the plugin's own check.

    Takes: an `end` move at the subagent's SubagentStop, a pass after a message queued to it ending
    the same start.
    Gives: a stop with the sentence that rule_types.judge_end gives; an empty answer where it gives
    none.
    Changes: nothing.
    Refuses: nothing.
    """
    said = rule_types.judge_end(move)
    return Answer() if said is None else Answer(True, said)


def written(event: Event, given: Answer) -> str:
    """The answer in the form that Claude Code reads from a hook of the event.

    Takes: the hook event, and the guard's answer.
    Gives: the JSON that the hooks reference names for the event: a deny with its reason at a
    PreToolUse, a block with its reason at a PostToolUse, Stop, SubagentStop, UserPromptSubmit, or
    UserPromptExpansion, and what the reader reads as additional context.
    Changes: nothing.
    Refuses: nothing.
    """
    if not given.stop and not given.said:
        return ""
    name = event["hook_event_name"]
    if not given.stop:
        output: dict[str, object] = {
            "hookSpecificOutput": {"hookEventName": name, "additionalContext": given.said}
        }
    elif name == "PreToolUse":
        output = {
            "hookSpecificOutput": {
                "hookEventName": name,
                "permissionDecision": "deny",
                "permissionDecisionReason": given.said,
            }
        }
    else:
        output = {"decision": "block", "reason": given.said}
    return json.dumps(output)


# The interface that answers each kind of move.
_ANSWERS: dict[str, Callable[[Move], Answer]] = {
    "call": call_made,
    "start": start_made,
    "tie": fact_added,
    "drop": fact_added,
    "read": fact_added,
    "report": report_made,
    "end": subagent_ended,
    "turn_end": turn_ended,
    "typed": command_typed,
    "result_reached": result_reached,
}


def _root(run: Run) -> str:
    """The folder of the run's plugin, which a run on which place gives a move has."""
    return cast(str, run.plugin_root)


def _rules(run: Run) -> Rules:
    """The rules of the run's plugin, which a run on which place gives a move has."""
    return cast(Rules, read_rules(_root(run)))


def _due(run: Run, event: Event) -> StartsDue:
    """The starts due of the run as it stands, by its plugin's order, while the turn runs."""
    return adapters.starts_due(_root(run), event["cwd"], run, _rules(run), False)


def _end_if(run: Run, event: Event, turn_ended: bool = False) -> StartsDue:
    """The starts due of the run as it stands, by its plugin's order, its record given an `ended`
    entry where the order says the run ends."""
    due = adapters.starts_due(_root(run), event["cwd"], run, _rules(run), turn_ended)
    if due.get("ends"):
        record.add(run.session_id, [{"kind": "ended", "run": run.id}])
    return due


def _due_said(due: StartsDue) -> str:
    """What the main conversation reads of the starts due: each role due, and how many at once;
    nothing while the run waits or once it ends."""
    roles = [
        s["role"] if s["count"] == 1 else f"{s['role']} {s['count']} times at once"
        for s in due.get("starts", [])
    ]
    return f"Due: {', '.join(roles)}." if roles else ""


def main() -> int:
    """Reads the hook event on standard input, and prints the guard's answer to it."""
    event = json.load(sys.stdin)
    print(written(event, answer(event)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
