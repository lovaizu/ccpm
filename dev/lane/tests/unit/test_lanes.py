"""The unit cases of lanes/, the lane types and how they join, through `types`, `sentence`,
`check_start`, `check_call`, `check_end`, and each type's `info`, `faults`, `sentence`, `allows`,
`check_start`, and `check_end`: each type's values, refusals, and sentence; each class of Call that
a type allows, stops, or doesn't judge; each start a type keeps or breaks; each combination of a
role's Lanes that keeps or breaks a Call or an end; and each end a type keeps, breaks, or can't
check."""

from __future__ import annotations

import dataclasses
import os
from typing import Any

import lane_data as d
import pytest
from lanes import (
    LaneRefused,
    check_call,
    check_end,
    check_start,
    ends_by_result,
    ends_checked,
    gives_shown,
    lays_after_reply,
    routes,
    run_only,
    sentence,
    types,
    write_only,
)
from lanes.kind import Broken, CantCheck, Held, Kept
from place import EndAsked, StartCall
from run_record import Shown
from runs import Approval

MODULES = {
    "routes": routes,
    "ends_by_result": ends_by_result,
    "run_only": run_only,
    "write_only": write_only,
    "ends_checked": ends_checked,
    "lays_after_reply": lays_after_reply,
    "gives_shown": gives_shown,
}
TYPES = {name: module.TYPE for name, module in MODULES.items()}
WRITER = d.start("writer")
HELD = Held(d.run(starts=(WRITER,), due=()), WRITER, d.ROOT, d.ROUTES_OF_WRITE)
MAIN = Held(d.run(starts=(WRITER,), due=()), None, d.ROOT, d.ROUTES_OF_WRITE)
LAY = "python3 /lane/scripts/lay.py write changelog b9fd8fd8"
SHOWN = "Routes of write...\nID: b9fd8fd8\nReply yes to lay these into changelog."


def up_held(by: str = "person", approved: bool = False) -> Held:
    """Up's Run that showed b9fd8fd8, by a person or an AI, with or without its Approval."""
    approvals = (Approval("b9fd8fd8", "person"),) if approved else ()
    run = d.run(
        skill="up", by=by, shown=(Shown("r1", "b9fd8fd8", SHOWN),), approvals=approvals, due=()
    )
    return Held(run, None, d.ROOT, d.ROUTES_OF_WRITE)


def up_lane(kind: str) -> Any:
    return d.lane("up", "domain/up.md", 1, kind)


def end_of(role: str, *results: str, gives: str = d.GIVES) -> str:
    """The sentence of the Lane on the role's last Step, naming each Result, the result script by
    `${CLAUDE_PLUGIN_ROOT}` as laid, or by changelog's folder as a stop gives it."""
    named = " or ".join(f"`{gives} {role} {result}`" for result in results)
    return f"End by running {named}."


# What a role may do where its end holds no Result.
ALONE = "Run it as a command of its own: result.py run inside a longer command gives no Result."


def stop_of(role: str, *results: str) -> str:
    """The sentence of the Lane on the role's last Step, as a Broken gives it to the role."""
    return end_of(role, *results, gives=d.RESULT)


def faults(lane: Any) -> tuple[str, ...]:
    """The faults that the Lane's type finds, with its role's last Step and the walkthrough's
    Routes."""
    return TYPES[lane.type].faults(lane, d.LAST[lane.role], d.ROUTES_OF_WRITE)


def held_with(*results: str) -> Held:
    """writer's Start, with the Results it gave, in write's Run."""
    start = d.start("writer", results=results)
    return Held(d.run(starts=(start,), due=()), start, d.ROOT, d.ROUTES_OF_WRITE)


def start_call(role: str, text: str = "Carry out your steps", **fields: Any) -> StartCall:
    values: dict[str, Any] = {"ours": True, "resume": False, "tool_use_id": "t1"}
    values.update(fields)
    return StartCall(role=role, text=text, **values)


@pytest.mark.supports("test_types_give_each_lane_type_and_the_form_of_a_proposal")
def test_types_give_each_module_of_lanes() -> None:
    """Given: lanes/ with its seven type modules.
    When: types gives each lane type.
    Then: it gives one TypeInfo for each, by its name, with a sentence, steps it suits, and what it
    allows."""
    given = {each.name: each for each in types()}
    assert set(given) == set(TYPES)
    assert all(each.sentence and each.suits and each.allows for each in given.values())


@pytest.mark.supports("test_types_give_each_lane_type_and_the_form_of_a_proposal")
@pytest.mark.parametrize("name", list(TYPES))
def test_each_types_info_names_it_and_its_values(name: str) -> None:
    """Given: one lane type.
    When: its info is asked.
    Then: it names the type as lanes.json and a Proposal name it, and each value it takes as its
    module's ARGS names it."""
    info = TYPES[name].info()
    assert (info.name, dict(info.args)) == (name, MODULES[name].ARGS)


@pytest.mark.supports("test_up_shows_the_walkthroughs_proposal")
@pytest.mark.parametrize(
    "lane, said",
    [
        (lambda: d.run_only(), "Run only `git log --oneline`."),
        (lambda: d.run_only("git log --oneline", "git status"), None),
        (lambda: d.write_only(), "Write only `CHANGELOG.md`."),
        (lambda: d.WRITER_END, end_of("writer", "written")),
        (lambda: d.REVIEWER_END, end_of("reviewer", "more", "good")),
        (lambda: d.WRITE_END, end_of("write", "good")),
        (
            lambda: d.ROUTES,
            "Start each subagent you are told to start, until you are told to start no more.",
        ),
    ],
    ids=[
        "run_only",
        "run_only of two commands",
        "write_only",
        "a subagent's end, of one Result",
        "a subagent's end, of two Results",
        "the skill's end, by its move to start no more",
        "routes",
    ],
)
def test_a_lanes_sentence_reads_as_the_readme_shows(lane: Any, said: str | None) -> None:
    """Given: one of the walkthrough's Lanes, or writer's run_only Lane of two commands.
    When: sentence gives the Lane's sentence, with the walkthrough's Routes.
    Then: it reads as the README's walkthrough shows, each command or Result joined by `or`."""
    said = said or "Run only `git log --oneline` or `git status`."
    given = lane()
    assert sentence(given, d.LAST[given.role], d.ROUTES_OF_WRITE) == said


@pytest.mark.supports("test_a_proposal_that_cant_stand_goes_back_to_up")
def test_a_lane_of_no_type_is_refused() -> None:
    """Given: a Lane of the type run_once, which no module of lanes/ gives.
    When: sentence gives its sentence.
    Then: it raises LaneRefused, naming run_once."""
    with pytest.raises(LaneRefused, match="run_once"):
        sentence(d.lane("writer", "agents/writer.md", 2, "run_once"), 4, d.ROUTES_OF_WRITE)


@pytest.mark.supports("test_a_proposal_that_cant_stand_goes_back_to_up")
@pytest.mark.parametrize(
    "name, args",
    [
        ("run_only", {}),
        ("run_only", {"commands": []}),
        ("run_only", {"commands": "git log --oneline"}),
        ("write_only", {}),
        ("write_only", {"paths": []}),
        ("ends_checked", {}),
        ("ends_checked", {"command": ["true"]}),
    ],
    ids=[
        "run_only without commands",
        "run_only of no command",
        "run_only of a string",
        "write_only without paths",
        "write_only of no path",
        "ends_checked without command",
        "ends_checked of a list",
    ],
)
def test_a_lane_without_its_value_is_refused(name: str, args: dict[str, Any]) -> None:
    """Given: a Lane of a type that takes a value, with none, an empty list, or one of another
    type.
    When: the type finds its faults, and sentence gives its sentence.
    Then: the type finds a fault, and sentence raises LaneRefused with it."""
    lane = d.lane("writer", "agents/writer.md", 2, name, **args)
    assert faults(lane)
    with pytest.raises(LaneRefused):
        sentence(lane, 4, d.ROUTES_OF_WRITE)


@pytest.mark.supports("test_up_shows_the_walkthroughs_proposal")
@pytest.mark.parametrize(
    "lane",
    [
        lambda: d.ROUTES,
        lambda: d.WRITE_END,
        lambda: d.WRITER_END,
        lambda: up_lane("lays_after_reply"),
        lambda: up_lane("gives_shown"),
    ],
    ids=["routes", "the skill's end", "a subagent's end", "lays_after_reply", "gives_shown"],
)
def test_a_lane_of_a_type_that_takes_no_value_has_no_fault(lane: Any) -> None:
    """Given: a Lane of a type that takes no value, with none, on a Step it suits.
    When: the type finds its faults.
    Then: it finds none."""
    given = lane()
    assert faults(given) == ()


@pytest.mark.supports("test_a_proposal_that_cant_stand_goes_back_to_up")
@pytest.mark.parametrize(
    "lane",
    [
        lambda: d.lane("write", "skills/write/SKILL.md", 1, "lays_after_reply"),
        lambda: d.lane("write", "skills/write/SKILL.md", 1, "gives_shown"),
    ],
    ids=["lays_after_reply", "gives_shown"],
)
def test_a_lane_of_ups_own_type_on_another_roles_step_is_refused(lane: Any) -> None:
    """Given: a Lane of a type that holds only up, on write's step 1.
    When: the type finds its faults.
    Then: it finds one."""
    given = lane()
    assert faults(given)


@pytest.mark.supports("test_a_role_with_no_end_on_its_last_step_goes_back_to_up")
@pytest.mark.parametrize(
    "lane, stands",
    [
        (lambda: d.WRITER_END, True),
        (lambda: dataclasses.replace(d.WRITER_END, step=3), False),
        (lambda: dataclasses.replace(d.WRITER_END, step=1), False),
        (lambda: d.lane("checker", "agents/checker.md", 4, "ends_by_result"), False),
    ],
    ids=["its role's last Step", "the Step before it", "its first Step", "a role no Route names"],
)
def test_ends_by_result_suits_only_a_last_step_whose_role_the_routes_give_a_result(
    lane: Any, stands: bool
) -> None:
    """Given: a Lane of ends_by_result on step 4, 3, or 1 of writer, whose last Step is 4, or on
    step 4 of checker, to which the walkthrough's Routes give no Result.
    When: the type finds its faults, with the role's last Step and the Routes.
    Then: it finds none for writer's step 4, and one for each other."""
    given = TYPES["ends_by_result"].faults(lane(), 4, d.ROUTES_OF_WRITE)
    assert (given == ()) is stands


@pytest.mark.supports("test_a_start_that_isnt_due_is_stopped_with_the_moves_due")
@pytest.mark.parametrize(
    "asked, kept",
    [
        (start_call("writer"), True),
        (start_call("writer", "Write 0.3.0"), False),
        (start_call("reviewer"), False),
        (start_call("writer", "Which version?", resume=True), True),
    ],
    ids=["the start due", "due with another text", "a start not due", "a resume none opens"],
)
def test_the_main_conversations_start_is_checked_against_the_moves_due(
    asked: StartCall, kept: bool
) -> None:
    """Given: write's Lanes on its step 1, and writer's start due with Lane's text.
    When: check_start checks the main conversation's start or resume.
    Then: it keeps the start due with its text and a resume the Routes open none for, and breaks
    any other with the moves due as what the main conversation may do."""
    verdict = check_start((d.ROUTES, d.WRITE_END), asked, MAIN, (d.due_start("writer"),))
    if kept:
        assert verdict == Kept()
    else:
        assert isinstance(verdict, Broken) and "changelog:writer" in verdict.may


@pytest.mark.supports("test_a_subagents_start_of_a_role_is_stopped")
@pytest.mark.parametrize(
    "asked, kept",
    [
        (start_call("reviewer"), False),
        (start_call("writer", resume=True), False),
        (start_call("Explore", "Find the tests", ours=False), True),
    ],
    ids=["a start of a role", "a resume of a role", "a start of no role of the plugin"],
)
def test_a_subagents_start_of_a_role_breaks_the_lane_on_its_last_step(
    asked: StartCall, kept: bool
) -> None:
    """Given: writer's Lanes, the Lane on its step 4 among them, in writer's Start.
    When: check_start checks writer's start or resume of a subagent.
    Then: it breaks a start or resume of a role of the plugin with the sentence of the Lane on
    writer's last Step, and keeps a start of a subagent that isn't the plugin's."""
    lanes = (d.run_only(), d.write_only(), d.WRITER_END)
    verdict = check_start(lanes, asked, HELD, (d.due_start("reviewer"),))
    if kept:
        assert verdict == Kept()
    else:
        assert isinstance(verdict, Broken) and verdict.sentence == stop_of("writer", "written")


@pytest.mark.supports("test_a_call_the_guard_cant_check_is_stopped_with_who_must_fix_it")
def test_a_subagents_start_with_no_lane_that_checks_starts_cant_be_checked() -> None:
    """Given: writer's Lanes without the Lane on its last Step.
    When: check_start checks writer's start of reviewer.
    Then: it can't check, with Lane's developer to fix it."""
    verdict = check_start((d.run_only(),), start_call("reviewer"), HELD, ())
    assert isinstance(verdict, CantCheck) and "Lane" in verdict.who


@pytest.mark.supports("test_a_start_that_isnt_due_is_stopped_with_the_moves_due")
@pytest.mark.parametrize(
    "lane",
    [
        lambda: d.run_only(),
        lambda: d.write_only(),
        lambda: d.lane("writer", "agents/writer.md", 4, "ends_checked", command="true"),
        lambda: up_lane("lays_after_reply"),
        lambda: up_lane("gives_shown"),
    ],
    ids=["run_only", "write_only", "ends_checked", "lays_after_reply", "gives_shown"],
)
def test_a_type_that_checks_no_start_keeps_every_start(lane: Any) -> None:
    """Given: a Lane of a type that checks no start.
    When: the type checks a start of reviewer that isn't due.
    Then: it keeps it."""
    given = lane()
    assert TYPES[given.type].check_start(given, start_call("reviewer"), HELD, ()) == Kept()


@pytest.mark.supports("test_a_subagents_start_of_a_role_is_stopped")
def test_routes_keep_a_subagents_start_for_the_lane_on_its_last_step() -> None:
    """Given: write's Lane of its Routes.
    When: the type checks writer's start of reviewer.
    Then: it keeps it, as the Lane on writer's last Step checks a subagent's start."""
    verdict = TYPES["routes"].check_start(d.ROUTES, start_call("reviewer"), HELD, ())
    assert verdict == Kept()


@pytest.mark.supports("test_calls_that_keep_every_lane_go_through")
@pytest.mark.parametrize(
    "call, allowed",
    [
        (d.bash("git log --oneline"), True),
        (d.bash("git -C /home/you/tally log --oneline"), False),
        (d.bash("git log --oneline; rm CHANGELOG.md"), False),
        (d.write("/home/you/tally/CHANGELOG.md"), None),
    ],
    ids=["its command", "another command", "its command and more", "another tool"],
)
def test_run_only_allows_only_its_commands_word_for_word(call: Any, allowed: Any) -> None:
    """Given: writer's run_only Lane for `git log --oneline`.
    When: the type judges a Call.
    Then: it allows the command word for word, stops any other Bash command, and doesn't judge
    another tool."""
    assert TYPES["run_only"].allows(d.run_only(), call, HELD) is allowed


@pytest.mark.supports("test_an_adapter_gives_each_start_its_text_and_values")
@pytest.mark.parametrize(
    "values, command, allowed",
    [
        ({"version": "0.2.0"}, "git tag v0.2.0", True),
        ({"version": "0.2.0"}, "git tag v0.3.0", False),
        ({}, "git tag v0.3.0", True),
    ],
    ids=["its value", "another value", "a name the values don't give"],
)
def test_run_only_fills_in_the_starts_run_values(
    values: dict[str, str], command: str, allowed: bool
) -> None:
    """Given: writer's run_only Lane for `git tag v{version}`, and writer's Start with the value
    version 0.2.0, or with no values.
    When: the type judges a `git tag` command.
    Then: it allows the command with the Start's value, stops another, and allows any word where
    the values give no version."""
    start = dataclasses.replace(d.start("writer"), values=values)
    held = Held(d.run(starts=(start,), due=()), start, d.ROOT, d.ROUTES_OF_WRITE)
    lane = d.run_only("git tag v{version}")
    assert TYPES["run_only"].allows(lane, d.bash(command), held) is allowed


@pytest.mark.supports("test_the_sentence_laid_is_the_sentence_a_stop_gives")
@pytest.mark.parametrize(
    "call, allowed",
    [
        (d.write("/home/you/tally/CHANGELOG.md"), True),
        (d.write("/home/you/tally/CHANGELOG.md", "Edit"), True),
        (d.write("/home/you/tally/NOTES.md"), False),
        (d.write("/home/you/tally/docs/CHANGELOG.md"), False),
        (d.bash("git log --oneline"), None),
    ],
    ids=["its path", "an Edit of its path", "another path", "its name elsewhere", "another tool"],
)
def test_write_only_allows_only_its_paths_from_the_worktrees_top(call: Any, allowed: Any) -> None:
    """Given: writer's write_only Lane for `CHANGELOG.md`, in the worktree whose top is tally.
    When: the type judges a Call.
    Then: it allows a Write or Edit of tally's CHANGELOG.md, stops one of any other path, and
    doesn't judge another tool."""
    assert TYPES["write_only"].allows(d.write_only(), call, HELD) is allowed


@pytest.mark.supports("test_the_walkthroughs_run_moves_in_the_order_the_user_set")
@pytest.mark.parametrize(
    "command", [f"{d.RESULT} write good", "git status"], ids=["the skill's Result", "another"]
)
def test_routes_judge_no_call(command: str) -> None:
    """Given: write's Lane of its Routes, in a Run with the move to start no more by `good` due.
    When: the type judges the main conversation's Call.
    Then: it judges none, as the skill's result script is the Lane on its last Step's."""
    assert TYPES["routes"].allows(d.ROUTES, d.bash(command), MAIN) is None


@pytest.mark.supports("test_a_result_is_added_for_the_subagents_start")
@pytest.mark.parametrize(
    "command, allowed",
    [
        (f"{d.RESULT} writer written", True),
        (f"{d.RESULT} writer good", True),
        (f"{d.RESULT} reviewer good", None),
        (f"{d.RESULT} writer written; rm CHANGELOG.md", None),
        ("git status", None),
    ],
    ids=[
        "its role's Result",
        "a Result result.py refuses",
        "another role's",
        "its run and more",
        "another command",
    ],
)
def test_ends_by_result_allows_its_roles_run_of_the_result_script(
    command: str, allowed: Any
) -> None:
    """Given: the Lane on writer's step 4.
    When: the type judges writer's Bash Call.
    Then: it allows a run of the plugin's result.py for writer with any Result, as result.py
    refuses one writer may not give, and judges no other Call."""
    assert TYPES["ends_by_result"].allows(d.WRITER_END, d.bash(command), HELD) is allowed


@pytest.mark.supports("test_lay_before_the_persons_reply_is_stopped")
@pytest.mark.parametrize(
    "held, call, allowed",
    [
        (up_held(), d.bash(LAY), False),
        (up_held(approved=True), d.bash(LAY), True),
        (up_held(by="ai"), d.bash(LAY), True),
        (up_held(), d.bash("git status"), None),
    ],
    ids=["a person's Run before the reply", "after the reply", "an AI's Run", "another call"],
)
def test_lays_after_reply_holds_write_to_the_callers_own_act(
    held: Held, call: Any, allowed: Any
) -> None:
    """Given: up's Lane that holds lay.py write to the caller's own act, in up's Run that showed
    b9fd8fd8.
    When: the type judges a Call.
    Then: it stops lay.py write in a person's Run before their reply, allows it after the reply or
    in an AI's Run, and judges no other Call."""
    lane = up_lane("lays_after_reply")
    assert TYPES["lays_after_reply"].allows(lane, call, held) is allowed


@pytest.mark.supports("test_ups_end_without_what_print_showed_is_stopped")
@pytest.mark.parametrize(
    "message, kept",
    [(SHOWN, True), (f"Here it is:\n{SHOWN}", True), ("I proposed rules.", False)],
    ids=["the words alone", "the words within", "a summary"],
)
def test_gives_shown_holds_ups_end_to_what_print_showed(message: str, kept: bool) -> None:
    """Given: up's Lane that holds its end to what lay.py print showed, in up's Run that showed it.
    When: the type checks up's end with a last message.
    Then: it keeps an end that holds the words word for word, and breaks any other with them."""
    lane = up_lane("gives_shown")
    verdict = TYPES["gives_shown"].check_end(lane, EndAsked(message), up_held())
    if kept:
        assert verdict == Kept()
    else:
        assert isinstance(verdict, Broken) and SHOWN in verdict.sentence + verdict.may


@pytest.mark.supports("test_an_end_with_no_result_is_stopped_with_its_last_steps_sentence")
@pytest.mark.parametrize(
    "held, kept",
    [
        (held_with(), False),
        (held_with("written"), True),
        (held_with("written", "written"), True),
        (MAIN, True),
    ],
    ids=["no Result", "one Result", "two Results", "the main conversation's end"],
)
def test_ends_by_result_holds_a_subagents_end_to_a_result_since_its_start(
    held: Held, kept: bool
) -> None:
    """Given: the Lane on writer's step 4.
    When: the type checks an end of writer's Start, or of the main conversation.
    Then: it breaks writer's end where its Start holds no Result, with the Lane's sentence, and
    keeps it where the Start holds one or more, and the main conversation's end, which the moves
    due hold. A broken end says to run the script as a command of its own, as one run inside a
    longer command gives no Result."""
    verdict = TYPES["ends_by_result"].check_end(d.WRITER_END, EndAsked("Wrote."), held)
    if kept:
        assert verdict == Kept()
    else:
        assert verdict == Broken(d.WRITER_END, stop_of("writer", "written"), ALONE)


@pytest.mark.supports("test_an_end_held_to_the_plugins_command_goes_once_it_gives_0")
@pytest.mark.parametrize(
    "command, verdict",
    [
        ('test "{result}" = written', Kept),
        ('test "{result}" = good', Broken),
        ("/nowhere/check-entries", CantCheck),
    ],
    ids=["it gives 0", "it gives 1", "it can't run"],
)
def test_ends_checked_holds_an_end_to_the_plugins_command(command: str, verdict: type) -> None:
    """Given: writer's ends_checked Lane, writer's Start with its Result `written`.
    When: the type checks writer's end.
    Then: it keeps the end where the command, the Result filled in, gives 0, breaks it with the
    Lane's sentence where it gives another code, and can't check where the command can't run."""
    lane = d.lane("writer", "agents/writer.md", 4, "ends_checked", command=command)
    given = TYPES["ends_checked"].check_end(lane, EndAsked("Wrote."), held_with("written"))
    assert isinstance(given, verdict)


@pytest.mark.supports("test_an_end_held_to_the_plugins_command_goes_once_it_gives_0")
@pytest.mark.parametrize(
    "lane",
    [
        lambda: d.run_only(),
        lambda: d.write_only(),
        lambda: up_lane("lays_after_reply"),
        lambda: d.ROUTES,
    ],
    ids=["run_only", "write_only", "lays_after_reply", "routes"],
)
def test_a_type_that_checks_no_end_keeps_every_end(lane: Any) -> None:
    """Given: a Lane of a type that checks no end.
    When: the type checks an end of a Start with no Result.
    Then: it keeps it."""
    given = lane()
    assert TYPES[given.type].check_end(given, EndAsked("Done."), held_with()) == Kept()


@pytest.mark.supports("test_calls_that_keep_every_lane_go_through")
@pytest.mark.parametrize(
    "lanes, call, kept",
    [
        (lambda: (d.run_only(), d.write_only()), d.bash("git log --oneline"), True),
        (lambda: (d.run_only(), d.write_only()), d.bash("git status"), False),
        (lambda: (d.run_only(), d.run_only("git status")), d.bash("git status"), True),
        (lambda: (d.write_only(),), d.bash("git status"), True),
        (lambda: (), d.bash("git status"), True),
        (lambda: (d.run_only(), d.WRITER_END), d.bash(f"{d.RESULT} writer written"), True),
        (lambda: (d.run_only(), d.WRITER_END), d.bash("git status"), False),
    ],
    ids=[
        "allowed by its type's Lane",
        "stopped by every Lane of its type",
        "stopped by one Lane, allowed by another of its type",
        "judged by no Lane",
        "no Lanes",
        "the end's result script, stopped by run_only",
        "another command beside the end's Lane",
    ],
)
def test_a_call_is_kept_where_one_lane_of_each_type_allows_it(
    lanes: Any, call: Any, kept: bool
) -> None:
    """Given: writer's Lanes, in each combination of types that allow, stop, or don't judge.
    When: check_call checks a Call.
    Then: it keeps the Call where the Lane on writer's last Step allows it, or else where, for
    each type that judges it, one Lane of that type allows it, and breaks it with that type's
    sentence where none does."""
    verdict = check_call(lanes(), call, HELD)
    if kept:
        assert verdict == Kept()
    else:
        assert isinstance(verdict, Broken) and verdict.sentence == "Run only `git log --oneline`."


@pytest.mark.supports("test_an_end_held_to_the_plugins_command_goes_once_it_gives_0")
@pytest.mark.parametrize(
    "commands, verdict",
    [
        (("true", "true"), Kept),
        (("true", "false"), Broken),
        (("/nowhere/check", "true"), CantCheck),
    ],
    ids=["every Lane keeps it", "one Lane breaks it", "one Lane can't check"],
)
def test_an_end_is_kept_where_every_lane_keeps_it(commands: Any, verdict: type) -> None:
    """Given: the Lane on writer's last Step, and two ends_checked Lanes of writer, whose commands
    give 0 or not, or can't run, in writer's Start with its Result `written`.
    When: check_end checks writer's end.
    Then: it keeps the end where every Lane keeps it, and gives the first Broken or CantCheck."""
    lanes = (d.WRITER_END,) + tuple(
        d.lane("writer", "agents/writer.md", 4, "ends_checked", command=c) for c in commands
    )
    assert isinstance(check_end(lanes, EndAsked("Done."), held_with("written")), verdict)


@pytest.mark.supports("test_an_end_with_no_result_runs_no_command_of_the_plugins")
def test_an_end_with_no_result_breaks_before_any_command_runs(tmp_path: Any) -> None:
    """Given: writer's ends_checked Lane whose command writes a file, listed before the Lane on
    writer's last Step, in writer's Start with no Result.
    When: check_end checks writer's end.
    Then: it breaks it with the sentence of the Lane on writer's last Step, and the command didn't
    run."""
    marker = os.path.join(str(tmp_path), "checked.txt")
    checked = d.lane("writer", "agents/writer.md", 4, "ends_checked", command=f"touch {marker}")
    verdict = check_end((checked, d.WRITER_END), EndAsked("Done."), held_with())
    assert isinstance(verdict, Broken) and verdict.sentence == stop_of("writer", "written")
    assert not os.path.exists(marker)
