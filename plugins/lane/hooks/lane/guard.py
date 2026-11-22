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
from place import Event, Move, SkillCall, Turn
from plugin import plugin_root
from plugin_command import Unchecked
from record import Run
from report import Report
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
    """The interface, its answer stopping nothing and saying what Lane couldn't check and why
    where Lane can't check the event, as a plugin's rules out of form or an adapter that failed."""

    def checked(*taken: object) -> Answer:
        try:
            return answers(*taken)
        except (OutOfForm, AdapterFailed) as couldnt:
            return Answer(said=str(couldnt))

    return cast(_Answers, checked)


def answer(event: Event) -> Answer:
    """The guard's answer to a hook event.

    Takes: a hook event of hooks/hooks.json: PreToolUse, PostToolUse, PostToolUseFailure, Stop,
    SubagentStop, UserPromptSubmit, or UserPromptExpansion.
    Gives: the answers, joined and stopping where any stops, of run_opened for each run that
    place.opening gives; of turn_begun or turn_opened for the run or the turn that
    place.turn_beginning or place.turn_opening gives; and of skill_called for the call that
    place.skill_call gives, else of the interface that the move of place.place reaches. An empty
    answer where the event lies outside each run, or its run's plugin gives no rules. The starts
    due that an answer gives, or holds a start to, are those that adapters.starts_due gives for
    the run once the move is added, none while the run waits; each sentence said once.
    Changes: what each interface it reaches changes.
    Refuses: nothing; where Lane can't check the event, such as where the run record can't be
    read, a plugin's rules are out of form, or an adapter failed, the answer stops nothing for that
    and says what Lane couldn't check and why.
    """
    try:
        return _answered(event)
    except record.Unread as unread:
        return Answer(said=str(unread))


def _answered(event: Event) -> Answer:
    """The guard's answer to a hook event, as answer gives it, where the run record can be read."""
    session = event["session_id"]
    answers = [run_opened(event, run) for run in place.opening(event, record.runs(session))]
    # Read again, as an opening adds its run's folder; _placed reads once more, as a turn's
    # opening adds the turn's steps, which hold the event's move.
    runs = record.runs(session)
    answers.append(_turn_begun_or_opened(event, runs))
    call = place.skill_call(event, runs)
    if call is not None:
        answers.append(skill_called(call))
    else:
        answers.append(_placed(event))
    said = _joined(*dict.fromkeys(each.said for each in answers))
    return Answer(any(each.stop for each in answers), said)


@_checked
def _placed(event: Event) -> Answer:
    """The answer of the interface that the event's move reaches, an empty one where it makes
    none."""
    runs = record.runs(event["session_id"])
    move = place.place(event, runs, lambda run: _due(run, event))
    return Answer() if move is None else _ANSWERS[move.kind](move)


@_checked
def _turn_begun_or_opened(event: Event, runs: list[Run]) -> Answer:
    """The answer of turn_begun, for the run whose next turn the event's prompt begins, and of
    turn_opened, for the turn whose steps the event is the first to need; an empty one where it
    reaches neither."""
    begun = place.turn_beginning(event, runs)
    if begun is not None:
        return turn_begun(event, begun)
    turn = place.turn_opening(event, runs)
    return Answer() if turn is None else turn_opened(event, turn)


def turn_begun(event: Event, run: Run) -> Answer:
    """S11: the first prompt after the main conversation's turn's end that the guard let through,
    which begins the next turn of a role that takes its steps at each turn.

    Takes: the UserPromptSubmit, the person's prompt or the `<task-notification>` of a subagent's
    end, and the run that place.turn_beginning gives for it.
    Gives: an empty answer.
    Changes: the run record, by a `turn_begun` entry with the event's `prompt` as Claude Code gives
    it, which turn_opened gives the plugin's adapter of the rules.
    Refuses: nothing.
    """
    entry: record.Entry = {"kind": "turn_begun", "run": run.id, "prompt": event["prompt"]}
    record.add(run.session_id, [entry])
    return Answer()


def turn_opened(event: Event, turn: Turn) -> Answer:
    """S11: the main conversation's turn's first call or end, where its role takes its steps from
    the plugin's adapter of the rules at each turn.

    Takes: the PreToolUse or Stop of the main conversation, whose `cwd` is the conversation's
    folder, and the turn that place.turn_opening gives for it, with its run, role, and prompt,
    empty for the run's first turn.
    Gives: an empty answer, the event's own move then held to the turn's steps.
    Changes: the run record, by a `turn` entry with the turn's role and prompt, and the steps that
    adapters.given_steps gives for them with the role and prompt of each of the run's earlier
    `turn` entries, oldest first, which hold the turn's calls, marks, and end until the
    turn's end that the guard lets through.
    Refuses: AdapterFailed, where the plugin's adapter of the rules is missing, fails, or gives out
    of its form, which answer gives as what Lane couldn't check and why, stopping nothing, the
    event's own move then held to no step, and the turn's next call or end asking the adapter
    again.
    """
    run = turn.run
    turns: list[adapters.EarlierTurn] = [
        {"role": entry["role"], "prompt": entry["prompt"]} for entry in run.state.turns
    ]
    asked: adapters.Asked = {"role": turn.role, "prompt": turn.prompt, "turns": turns}
    steps = adapters.given_steps(_root(run), event["cwd"], run, asked)
    entry: record.Entry = {
        "kind": "turn",
        "run": run.id,
        "role": turn.role,
        "prompt": turn.prompt,
        "steps": steps,
    }
    record.add(run.session_id, [entry])
    return Answer()


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
    gives none, or the transcript holds no base directory of the skill yet; what Lane couldn't
    check and why, stopping nothing, where the transcript can't be read, a plugin's rules are out
    of form, or an adapter failed.
    Changes: the run record, by the run's folder, where the transcript gives it.
    Refuses: nothing.
    """
    try:
        root = plugin_root(event["transcript_path"], run.skill)
    except FileNotFoundError:
        root = None
    except (OSError, ValueError) as error:
        return Answer(
            said=f"Lane couldn't check the run of {run.skill}: its plugin's folder can't be found"
            f" from {event['transcript_path']}: {error}"
        )
    if root is None:
        return Answer()
    record.add(run.session_id, [{"kind": "folder", "run": run.id, "plugin_root": root}])
    opened = replace(run, plugin_root=root)
    return Answer() if read_rules(root) is None else Answer(said=_due_said(_due(opened, event)))


def start_made(move: Move) -> Answer:
    """S9: the main conversation starts a subagent of the plugin, or resumes one by SendMessage.

    Takes: a `start` move at the PreToolUse of an Agent or SendMessage call, a SendMessage's with
    the role and the prompt of the start it resumes, as place gives them.
    Gives: an empty answer for a start of a role due, or of the plugin's role where Lane can't
    check which starts are due; for any other start of the plugin's subagents, or one by a
    subagent, a stop with the starts due, or, where none is due or Lane can't check which are, with
    the sentence that no start of the plugin's subagents is due and to go on without it; each
    saying what Lane couldn't check and why, where an adapter failed.
    Changes: the run record, by the start with its prompt, a resume's with the move's role and
    prompt, and with the steps that adapters.given_steps gives from the prompt, with no turn, where
    start_rules.asks_adapter says the start takes rules from the plugin's adapter of the rules, a
    resume asking it again so that its steps follow what changed while it waited, untied until the
    PostToolUse of its call; each step marked done and each read stay as they stood, as Move.done
    counts them across the subagent's starts; a start whose steps the plugin's adapter of the rules
    doesn't give, as it is missing, fails, or gives out of its form, with no steps.
    Refuses: nothing.
    """
    resume = move.event["tool_name"] == "SendMessage"
    role = move.role if resume else move.event["tool_input"].get("subagent_type", "")
    plugin = move.run.skill.partition(":")[0]
    if role.partition(":")[0] != plugin and move.agent_id is None:
        return Answer()
    due, unchecked = _asked(lambda: _due(move.run, move.event))
    held = due is None or any(s["role"] == role for s in due.get("starts", []))
    if move.agent_id is not None or not held:
        return Answer(True, _joined(_due_said(due or {}) or _none_due(plugin), unchecked))
    entry: record.Entry = {
        "kind": "start",
        "run": move.run.id,
        "role": role,
        "tool_use_id": move.event["tool_use_id"],
        "prompt": move.prompt or "",
    }
    if asks_adapter(_rules(move.run), role):
        asked: adapters.Asked = {"role": role, "prompt": entry["prompt"], "turns": []}
        try:
            entry["steps"] = adapters.given_steps(
                _root(move.run), move.event["cwd"], move.run, asked
            )
        except AdapterFailed as failed:
            unchecked = _joined(unchecked, str(failed))
    record.add(move.run.session_id, [entry])
    return Answer(said=unchecked)


def turn_ended(move: Move) -> Answer:
    """S5, S8, S9, and S11: the main conversation ends its turn, held to its role's steps, or the
    turn's, and to the starts due.

    Takes: a `turn_end` move at the main conversation's Stop, with the steps that place gives it:
    its role's, or, where the role takes its steps at each turn, those of the turn's `turn` entry.
    Gives: a stop with the sentence that rule_types.judge_end gives, where the move has steps, its
    marks and result those that Move.done gives for the turn; else a stop with the starts
    due, where a start is due and the turn didn't end on a result that a step's `ends` names, as
    rule_types.ended_at_a_step gives it, since that result says the AI can't go on, which no start
    mends; else an answer that stops nothing, saying what Lane couldn't check and why where
    rule_types.judge_end refuses with Unchecked or an adapter of the starts due fails, and empty
    where neither does.
    Changes: the run record, by dropping each start still untied; and, where the turn's end goes
    through, by an `ended` entry where adapters.starts_due, asked with the turn ended, says the run
    ends, and, where the role takes its steps at each turn, by a `turn_ended` entry, so that the
    next prompt begins the next turn; a turn's end that it stops goes on in the same turn; where
    an adapter of the starts due fails, no `ended` entry, as Lane can't tell whether the run ends.
    Refuses: nothing.
    """
    run = _untied_dropped(move.run)
    said, unchecked = _judged(rule_types.judge_end, replace(move, run=run))
    if said is not None:
        return Answer(True, said)
    due, couldnt = _asked(lambda: _due(run, move.event))
    if due is not None and due.get("starts") and not rule_types.ended_at_a_step(move):
        return Answer(True, _due_said(due))
    if due is not None:
        _, couldnt = _asked(lambda: _end_if(run, move.event, turn_ended=True))
    if asks_adapter(_rules(run), move.role):
        record.add(run.session_id, [{"kind": "turn_ended", "run": run.id}])
    return Answer(said=_joined(unchecked, couldnt))


def _untied_dropped(run: Run) -> Run:
    """The run with each start that no tie or drop settled dropped, in the record too, as an Agent
    call that another plugin's PreToolUse hook denies comes to no PostToolUse, so that its role is
    due again."""
    drops: list[record.Entry] = [
        {"kind": "drop", "run": run.id, "tool_use_id": start.entry["tool_use_id"]}
        for start in run.state.starts
        if start.tie is None and not start.dropped
    ]
    if drops:
        record.add(run.session_id, drops)
    return replace(run, entries=[*run.entries, *drops])


def command_typed(move: Move) -> Answer:
    """S9 and S10: a command of the plugin, typed by the person or called by the Skill tool, moves
    the run that stands, as a conversation holds one run of a plugin at a time.

    Takes: a `typed` move at the UserPromptExpansion of the command, or at the PostToolUse of its
    Skill call, which place gives while the run of the command's plugin stands.
    Gives: where the run stands: the starts due once the command is added; what Lane couldn't
    check and why where an adapter of the starts due fails.
    Changes: the run record, by the command.
    Refuses: nothing.
    """
    command = place.command_of(move.event) or ""
    typed: record.Entry = {"kind": "typed", "run": move.run.id, "command": command}
    record.add(move.run.session_id, [typed])
    run = replace(move.run, entries=[*move.run.entries, typed])
    due, unchecked = _asked(lambda: _end_if(run, move.event))
    return Answer(said=_joined(_due_said(due or {}), unchecked))


def result_reached(move: Move) -> Answer:
    """S9: a subagent's end reaches the main conversation, with its result.

    Takes: a `result_reached` move at the UserPromptSubmit of the subagent's
    `<task-notification>`.
    Gives: the result, and the starts due after it; the start's role due again, where the order
    gives it, as a start stopped with no result counts as not made; what Lane couldn't check and
    why where an adapter of the starts due fails.
    Changes: the run record, by a `stopped` entry of the subagent's start, where it was stopped
    with no result, such as by TaskStop; else nothing.
    Refuses: nothing.
    """
    run = move.run
    if "<status>killed</status>" in move.event["prompt"]:
        stopped: record.Entry = {"kind": "stopped", "run": run.id, "agent_id": move.agent_id}
        record.add(run.session_id, [stopped])
        run = replace(run, entries=[*run.entries, stopped])
        told = f"{move.role} stopped with no result."
    else:
        gave = move.done.result
        told = f"{move.role} gave {gave}." if gave else ""
    due, unchecked = _asked(lambda: _end_if(run, move.event))
    said = " ".join(each for each in (told, _due_said(due or {})) if each)
    return Answer(said=_joined(said, unchecked))


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
    if move.kind != "read":
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
    """S3, S5, S6, S7, and S12: a start runs a reporter of bin/, which counts as done only where its
    step's rules hold, or, for a step gone back to, where the step is marked done.

    Takes: a `report` move at the PostToolUse of the reporter's Bash call.
    Gives: for a step done, a stop with the sentence that rule_types.judge_mark gives; for a step
    gone back to that its role's steps don't name, or that Move.done gives no mark of, a stop with
    the sentence naming the step at hand and the step gone back to, as no rule names where a step
    may go back; an empty answer where the report holds, saying what Lane couldn't check and why
    where rule_types.judge_mark refuses with Unchecked.
    Changes: the run record, by the mark or the result, where it holds; for a step gone back to, by
    a `back` entry with the step and each step after it in its role's steps as `undone`, whose
    marks and items made before it no longer count in Move.done.
    Refuses: nothing.
    """
    reported = cast(Report, move.report)
    names = [step["name"] for step in move.steps]
    unchecked = ""
    if reported["kind"] == "step":
        said, unchecked = _judged(rule_types.judge_mark, move)
        if said is not None:
            return Answer(True, said)
    entry: record.Entry = {**reported, "run": move.run.id, "role": move.role}
    entry.update(kind=_KINDS.get(reported["kind"], "mark"), agent_id=move.agent_id)
    if reported["kind"] == "back":
        back = reported["step"]
        if back not in names or back not in move.done.steps:
            return Answer(True, _not_gone_back(move, back))
        entry["undone"] = names[names.index(back) :]
    record.add(move.run.session_id, [entry])
    return Answer(said=unchecked)


# The kind of entry that each kind of report adds, a mark for any other.
_KINDS = {"result": "result", "back": "back"}


def _not_gone_back(move: Move, step: str) -> str:
    """The sentence of a step gone back to that the move's start hasn't marked done."""
    at_hand = (
        f"You've marked each step of {move.role} done, and `{step}` isn't one of them."
        if move.step is None
        else f"You're at the step `{move.step}` of {move.role}, and `{step}` isn't marked done."
    )
    return f"{at_hand}\nGo back only to a step marked done, with lane-back <step>."


def subagent_ended(move: Move) -> Answer:
    """S7 and S8: a start ends, held to its result, its steps, and the plugin's own check.

    Takes: an `end` move at the subagent's SubagentStop, a pass after a message queued to it ending
    the same start.
    Gives: a stop with the sentence that rule_types.judge_end gives; an answer that stops nothing
    where it gives none, saying what Lane couldn't check and why where it refuses with Unchecked,
    and empty where it doesn't.
    Changes: nothing.
    Refuses: nothing.
    """
    said, unchecked = _judged(rule_types.judge_end, move)
    return Answer(said=unchecked) if said is None else Answer(True, said)


def _judged(judge: Callable[[Move], str | None], move: Move) -> tuple[str | None, str]:
    """The sentence of the rule that the move breaks, by the judge, None for none; and, where none
    breaks, what Lane couldn't check and why, as Unchecked says it, empty where it checked each."""
    try:
        return judge(move), ""
    except Unchecked as couldnt:
        return None, str(couldnt)


def written(event: Event, answered: Answer) -> str:
    """The answer in the form that Claude Code reads from a hook of the event.

    Takes: the hook event, and the guard's answer.
    Gives: the JSON that the hooks reference names for the event: a deny with its reason at a
    PreToolUse, a block with its reason at a PostToolUse, Stop, SubagentStop, UserPromptSubmit, or
    UserPromptExpansion, and what the reader reads as additional context.
    Changes: nothing.
    Refuses: nothing.
    """
    if not answered.stop and not answered.said:
        return ""
    name = event["hook_event_name"]
    if not answered.stop:
        output: dict[str, object] = {
            "hookSpecificOutput": {"hookEventName": name, "additionalContext": answered.said}
        }
    elif name == "PreToolUse":
        output = {
            "hookSpecificOutput": {
                "hookEventName": name,
                "permissionDecision": "deny",
                "permissionDecisionReason": answered.said,
            }
        }
    else:
        output = {"decision": "block", "reason": answered.said}
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


def _due(run: Run, event: Event, turn_ended: bool = False) -> StartsDue:
    """The starts due of the run as it stands, by its plugin's order, while the turn runs or once
    its end is let through."""
    return adapters.starts_due(_root(run), event["cwd"], run, _rules(run), turn_ended)


def _end_if(run: Run, event: Event, turn_ended: bool = False) -> StartsDue:
    """The starts due that _due gives, the run record given an `ended` entry where the order says
    the run ends."""
    due = _due(run, event, turn_ended)
    if due.get("ends"):
        record.add(run.session_id, [{"kind": "ended", "run": run.id}])
    return due


def _asked(ask: Callable[[], StartsDue]) -> tuple[StartsDue | None, str]:
    """The starts due that the call gives, and an empty sentence; or, where an adapter of the starts
    due fails, None, and what Lane couldn't check and why."""
    try:
        return ask(), ""
    except AdapterFailed as failed:
        return None, str(failed)


def _joined(*said: str) -> str:
    """The sentences said, one a line, leaving out each empty one."""
    return "\n".join(each for each in said if each)


def _due_said(due: StartsDue) -> str:
    """What the main conversation reads of the starts due: each role due, and how many at once;
    nothing while the run waits or once it ends."""
    roles = [
        s["role"] if s["count"] == 1 else f"{s['role']} {s['count']} times at once"
        for s in due.get("starts", [])
    ]
    return f"Due: {', '.join(roles)}." if roles else ""


def _none_due(plugin: str) -> str:
    """What the main conversation reads at a start of the plugin's subagents while none is due."""
    return (
        f"No start of {plugin}'s subagents is due now.\n"
        "Go on without it, and start one once Lane says it's due."
    )


def main() -> int:
    """Reads the hook event on standard input, and prints the guard's answer to it."""
    event = json.load(sys.stdin)
    print(written(event, answer(event)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
