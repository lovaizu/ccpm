"""The unit cases of hooks/lane/adapters.py: starts_due, one for each order that answers, the
plugin's own adapter, the route adapter, and none, and for each class of what the plugin's adapter
gives: the starts due, the run's end, a failure, and output out of its form; and given_steps, one
for each class of what the adapter of the rules gives, no adapter among them, for a start and for a
turn of the main conversation, with its earlier turns at none, one, and several; with what Lane
gives an adapter on its standard input, and the folder it runs in; with each exit other than 0,
output on standard error beside a good answer, the turn ended or not beside each order, an adapter
that can't be run, and each refusal saying what Lane couldn't check, naming the adapter's path and
what went wrong."""

from __future__ import annotations

import json
import os
from typing import Any

import lane_bench
import lane_entries
import pytest
from adapters import AdapterFailed, Asked, EarlierTurn, given_steps, starts_due
from record import Entry, Run
from repo_files import write_files

RULES: Any = lane_bench.RULES
ECHO = lane_bench.ECHO
# The rules of a plugin that gives no order: steps for its skill, and no routes.
NO_ORDER: Any = {"roles": {"log:up": RULES["roles"]["log:up"]}}
WRITER_DUE = {"starts": [{"role": "log:writer", "count": 1}]}


def run(log: str, *entries: Entry) -> Run:
    """The run r1 of log:up for 1.2.0 in log's folder, with the entries after its command."""
    head: list[Entry] = [
        {"kind": "run", "run": "r1", "skill": "log:up", "words": "1.2.0"},
        {"kind": "folder", "run": "r1", "plugin_root": log},
    ]
    return Run("r1", "session-1", "log:up", "1.2.0", log, [*head, *entries])


def start(role: str, prompt: str) -> Asked:
    """What a start of the role asks the adapter of the rules for, with the prompt and no turn."""
    return {"role": role, "prompt": prompt, "turns": []}


def adapter(log: str, name: str, code: str) -> None:
    """Writes the adapter of `log`."""
    write_files(log, {f"lane/adapters/{name}": code})


def printing(log: str, name: str, printed: Any) -> None:
    """Writes the adapter of `log` that prints the JSON given."""
    adapter(log, name, f"print({json.dumps(printed)!r})\n")


def given(cwd: str) -> dict[str, object]:
    """What the echoing adapter was given, and the folder it ran in."""
    return lane_bench.echoed(cwd)


def refused(call: Any, unchecked: str) -> str:
    """What AdapterFailed says of the call, which opens with what Lane couldn't check."""
    with pytest.raises(AdapterFailed) as raised:
        call()
    said = str(raised.value)
    assert said.startswith(f"Lane couldn't check {unchecked}: ")
    return said


# What Lane couldn't check where an adapter fails: the starts due, and a writer's steps.
DUE = "which starts are due"
WRITERS = "the steps of log:writer"


def path(log: str, name: str) -> str:
    """The path of log's adapter of the name."""
    return os.path.join(log, "lane", "adapters", name)


# starts_due


@pytest.mark.supports("test_the_starts_due_are_those_that_the_plugins_order_gives")
@pytest.mark.parametrize(
    "printed",
    [
        {"starts": [{"role": "log:reviewer", "count": 1}]},
        {"starts": [{"role": "log:writer", "count": 2}, {"role": "log:reviewer", "count": 1}]},
        {"starts": []},
        {"ends": True},
    ],
)
def test_the_plugins_adapter_gives_its_starts_due_or_the_runs_end(log: str, cwd: str, printed: Any):
    """Given `log`'s adapter of the starts due, which prints one start, two roles, none, or the
    run's end
    When Lane asks for the starts due of the run
    Then they are what it printed, in place of what log's routes give"""
    printing(log, "starts_due.py", printed)
    assert starts_due(log, cwd, run(log), RULES, False) == printed


@pytest.mark.supports("test_the_order_tells_the_starts_of_one_role_apart_by_their_prompts")
def test_the_plugins_adapter_takes_the_run_as_the_order_sees_it_in_the_conversations_folder(
    log: str, cwd: str
):
    """Given an adapter of the starts due that writes what it's given
    When Lane asks it for the starts due of a run with the writer started
    Then it was given the run's skill, words, and moves, the start with its prompt, as
    starts_due.in.schema.json says, and ran in the conversation's folder"""
    adapter(log, "starts_due.py", ECHO.format(printed=json.dumps({"starts": []})))
    start: Entry = lane_entries.start("u1", prompt="Write it.")
    starts_due(log, cwd, run(log, start), RULES, False)
    moves = [
        {"kind": "command", "command": "log:up"},
        {"kind": "start", "role": "log:writer", "prompt": "Write it."},
    ]
    assert given(cwd) == {
        "input": {"run": {"skill": "log:up", "words": "1.2.0", "moves": moves}},
        "cwd": os.path.realpath(cwd),
    }


@pytest.mark.supports("test_the_turns_end_while_the_commands_start_is_due_is_stopped_with_it")
@pytest.mark.parametrize("turn_ended", [False, True])
def test_a_plugin_with_routes_and_no_adapter_gets_the_route_adapters_starts_due(
    log: str, cwd: str, turn_ended: bool
):
    """Given `log` with its routes and no adapter of the starts due
    When Lane asks for the starts due of the run with only its command, the turn ended or not
    Then the writer is due, as the route after the command makes it"""
    assert starts_due(log, cwd, run(log), RULES, turn_ended) == WRITER_DUE


@pytest.mark.supports(
    "test_a_run_of_a_plugin_with_no_order_holds_the_main_conversation_to_its_skills_steps"
)
def test_a_plugin_with_no_order_has_no_start_due(log: str, cwd: str):
    """Given rules with no routes, and no adapter of the starts due
    When Lane asks for the starts due while the turn runs
    Then none is due"""
    assert starts_due(log, cwd, run(log), NO_ORDER, False) == {"starts": []}


@pytest.mark.supports(
    "test_a_run_of_a_plugin_with_no_order_ends_at_the_turns_end_that_its_steps_let_through"
)
def test_a_plugin_with_no_order_has_its_run_end_once_the_turn_ended(log: str, cwd: str):
    """Given rules with no routes, and no adapter of the starts due
    When Lane asks for the starts due with the turn ended
    Then the run ends"""
    assert starts_due(log, cwd, run(log), NO_ORDER, True) == {"ends": True}


@pytest.mark.supports(
    "test_an_adapter_of_the_starts_due_that_fails_lets_the_end_through_with_what_it_said"
)
def test_an_adapter_of_the_starts_due_that_fails_is_refused_with_its_file_and_what_it_said(
    log: str, cwd: str
):
    """Given an adapter of the starts due that exits 1 saying it found no version
    When Lane asks it for the starts due
    Then it refuses with AdapterFailed naming starts_due.py and what it said"""
    adapter(log, "starts_due.py", "import sys\n\nsys.exit('no version found')\n")
    said = refused(lambda: starts_due(log, cwd, run(log), RULES, False), DUE)
    assert said.endswith(f"{path(log, 'starts_due.py')} failed: no version found")


@pytest.mark.supports(
    "test_an_adapter_of_the_starts_due_that_fails_lets_the_end_through_with_what_it_said"
)
def test_an_adapter_that_cant_be_run_is_refused_with_its_file_and_why(log: str, tmp_path: Any):
    """Given an adapter of the starts due, and a conversation's folder that isn't there
    When Lane asks it for the starts due
    Then it refuses with AdapterFailed naming starts_due.py, which can't be run, and why"""
    printing(log, "starts_due.py", {"starts": []})
    gone = os.path.join(str(tmp_path), "gone")
    said = refused(lambda: starts_due(log, gone, run(log), RULES, False), DUE)
    assert f"{path(log, 'starts_due.py')} can't be run: " in said
    assert gone in said, "the folder that isn't there is named"


@pytest.mark.supports("test_starts_due_out_of_their_form_let_the_end_through_naming_the_adapter")
@pytest.mark.parametrize(
    "code",
    [
        "print('the writer')\n",
        'print(\'{"starts": [{"role": "log:writer"}]}\')\n',
        'print(\'{"starts": [{"role": "log:writer", "count": 0}]}\')\n',
        'print(\'{"starts": [{"role": "", "count": 1}]}\')\n',
        "print('{\"ends\": false}')\n",
        'print(\'{"starts": [], "ends": true}\')\n',
        "print('{}')\n",
    ],
)
def test_starts_due_out_of_their_form_are_refused_naming_the_adapter(log: str, cwd: str, code: str):
    """Given an adapter of the starts due that prints text that isn't JSON, a start with no count,
    a count of 0, a role with no name, `ends` false, both starts and `ends`, or neither
    When Lane asks it for the starts due
    Then it refuses with AdapterFailed naming starts_due.py"""
    adapter(log, "starts_due.py", code)
    said = refused(lambda: starts_due(log, cwd, run(log), RULES, False), DUE)
    assert path(log, "starts_due.py") in said


# given_steps

STEPS = [{"name": "write", "rules": [{"type": "writes", "paths": ["docs/changes/1.2.0.md"]}]}]


@pytest.mark.supports(
    "test_a_role_with_no_fixed_steps_takes_them_from_the_plugins_adapter_for_each_start"
)
def test_the_adapter_of_the_rules_gives_the_starts_steps_from_its_prompt(log: str, cwd: str):
    """Given `log`'s adapter of the rules, RULES_ADAPTER
    When Lane asks it for the steps of a writer's start whose prompt names docs/changes/1.2.0.md
    Then it gives the step `write`, which writes that file"""
    adapter(log, "rules.py", lane_bench.RULES_ADAPTER)
    prompt = "Write docs/changes/1.2.0.md."
    assert given_steps(log, cwd, run(log), start("log:writer", prompt)) == STEPS


@pytest.mark.supports(
    "test_a_role_with_no_fixed_steps_takes_them_from_the_plugins_adapter_for_each_start"
)
def test_the_adapter_of_the_rules_takes_the_run_the_role_and_the_prompt(log: str, cwd: str):
    """Given an adapter of the rules that writes what it's given
    When Lane asks it for the steps of a writer's start
    Then it was given the run's skill and words, the role, the prompt, and no turn, as
    rules.in.schema.json says, and ran in the conversation's folder"""
    adapter(log, "rules.py", ECHO.format(printed=json.dumps({"steps": []})))
    given_steps(log, cwd, run(log), start("log:writer", "Write it."))
    assert given(cwd) == {
        "input": {
            "run": {"skill": "log:up", "words": "1.2.0"},
            "role": "log:writer",
            "prompt": "Write it.",
            "turns": [],
        },
        "cwd": os.path.realpath(cwd),
    }


@pytest.mark.supports(
    "test_a_start_of_a_role_with_no_steps_and_no_adapter_of_the_rules_goes_through_saying_so"
)
def test_a_plugin_without_an_adapter_of_the_rules_is_refused_naming_it_and_the_role(
    log: str, cwd: str
):
    """Given `log` with no adapter of the rules
    When Lane asks for the steps of a writer's start
    Then it refuses with AdapterFailed naming lane/adapters/rules.py and the writer"""
    said = refused(
        lambda: given_steps(log, cwd, run(log), start("log:writer", "Write it.")), WRITERS
    )
    assert "lane/adapters/rules.py" in said
    assert log in said


@pytest.mark.supports(
    "test_an_adapter_of_the_rules_that_fails_or_gives_out_of_its_form_lets_the_start_through"
)
@pytest.mark.parametrize(
    "code",
    [
        "import sys\n\nsys.exit('no prompt to read')\n",
        "print('[]')\n",
        'print(\'{"steps": [{"name": "write"}]}\')\n',
        'print(\'{"steps": [{"name": "", "rules": []}]}\')\n',
        'print(\'{"steps": [{"name": "write", "rules": [{"type": "size"}]}]}\')\n',
    ],
)
def test_an_adapter_of_the_rules_that_fails_or_gives_out_of_its_form_is_refused(
    log: str, cwd: str, code: str
):
    """Given an adapter of the rules that exits 1, prints no object, a step with no rules, a step
    with no name, or a rule of a type Lane lacks
    When Lane asks it for the steps of a writer's start
    Then it refuses with AdapterFailed naming rules.py"""
    adapter(log, "rules.py", code)
    said = refused(lambda: given_steps(log, cwd, run(log), start("log:writer", "Write.")), WRITERS)
    assert path(log, "rules.py") in said


@pytest.mark.supports(
    "test_a_role_with_no_fixed_steps_takes_them_from_the_plugins_adapter_for_each_start"
)
def test_the_adapter_of_the_rules_may_give_no_step(log: str, cwd: str):
    """Given an adapter of the rules that gives no step
    When Lane asks it for the steps of a writer's start
    Then there's none"""
    printing(log, "rules.py", {"steps": []})
    assert given_steps(log, cwd, run(log), start("log:writer", "Write it.")) == []


@pytest.mark.supports(
    "test_the_plugins_own_adapter_of_the_starts_due_answers_in_place_of_its_routes"
)
@pytest.mark.parametrize("rules", [RULES, NO_ORDER])
def test_the_plugins_adapter_answers_though_the_turn_ended_beside_routes_or_none(
    log: str, cwd: str, rules: Any
):
    """Given `log`'s adapter of the starts due, which gives none, beside rules with routes or none
    When Lane asks for the starts due of the run with the turn ended
    Then none is due, and the run doesn't end, as the adapter alone says when it ends"""
    printing(log, "starts_due.py", {"starts": []})
    assert starts_due(log, cwd, run(log), rules, True) == {"starts": []}


@pytest.mark.supports("test_the_run_waits_while_the_start_its_route_made_due_runs")
def test_a_plugin_with_routes_gives_the_route_adapters_wait_though_the_turn_ended(
    log: str, cwd: str
):
    """Given `log` with its routes and no adapter of the starts due, and the writer started and
    running
    When Lane asks for the starts due with the turn ended
    Then none is due, and the run doesn't end, as the routes alone say when it ends"""
    start: Entry = lane_entries.start("u1")
    assert starts_due(log, cwd, run(log, start), RULES, True) == {"starts": []}


@pytest.mark.supports(
    "test_an_adapter_of_the_starts_due_that_fails_lets_the_end_through_with_what_it_said"
)
@pytest.mark.parametrize(
    "code",
    [
        "import sys\n\nsys.stderr.write('no version found')\nsys.exit(2)\n",
        (
            "import sys\n\nprint('{\"starts\": []}')\nsys.stderr.write('no version found')\n"
            "sys.exit(1)\n"
        ),
    ],
)
def test_an_adapter_that_exits_other_than_0_is_refused_though_it_printed_its_answer(
    log: str, cwd: str, code: str
):
    """Given an adapter of the starts due that exits 2, or prints an answer in its form and exits
    1, saying it found no version
    When Lane asks it for the starts due
    Then it refuses with AdapterFailed naming its path and what it said"""
    adapter(log, "starts_due.py", code)
    said = refused(lambda: starts_due(log, cwd, run(log), RULES, False), DUE)
    assert said.endswith(f"{path(log, 'starts_due.py')} failed: no version found")


@pytest.mark.supports("test_the_starts_due_are_those_that_the_plugins_order_gives")
def test_an_adapter_that_says_more_on_standard_error_and_exits_0_answers(log: str, cwd: str):
    """Given an adapter of the starts due that prints the reviewer due, says more on standard
    error, and exits 0
    When Lane asks it for the starts due
    Then the reviewer is due"""
    code = (
        "import sys\n\nsys.stderr.write('read CHANGELOG.md')\n"
        'print(\'{"starts": [{"role": "log:reviewer", "count": 1}]}\')\n'
    )
    adapter(log, "starts_due.py", code)
    gave = starts_due(log, cwd, run(log), RULES, False)
    assert gave == {"starts": [{"role": "log:reviewer", "count": 1}]}


@pytest.mark.supports("test_starts_due_out_of_their_form_let_the_end_through_naming_the_adapter")
def test_an_adapter_that_prints_no_json_is_refused_with_what_it_printed(log: str, cwd: str):
    """Given an adapter of the starts due that prints `the writer`, which isn't JSON
    When Lane asks it for the starts due
    Then it refuses with AdapterFailed naming its path and what it printed"""
    adapter(log, "starts_due.py", "print('the writer')\n")
    said = refused(lambda: starts_due(log, cwd, run(log), RULES, False), DUE)
    assert path(log, "starts_due.py") in said
    assert "the writer" in said


@pytest.mark.supports("test_starts_due_out_of_their_form_let_the_end_through_naming_the_adapter")
def test_starts_due_out_of_their_form_are_refused_naming_the_place(log: str, cwd: str):
    """Given an adapter of the starts due that prints a start with a count of 0
    When Lane asks it for the starts due
    Then it refuses with AdapterFailed naming the place of the count"""
    printing(log, "starts_due.py", {"starts": [{"role": "log:writer", "count": 0}]})
    said = refused(lambda: starts_due(log, cwd, run(log), RULES, False), DUE)
    assert "starts/0/count" in said


@pytest.mark.supports(
    "test_a_role_with_no_fixed_steps_takes_them_from_the_plugins_adapter_for_each_start"
)
def test_the_adapter_of_the_rules_may_give_several_steps_in_their_order(log: str, cwd: str):
    """Given an adapter of the rules that gives the steps `draft`, `write`, and `report`
    When Lane asks it for the steps of a writer's start
    Then they are those three, in their order, each with its rules"""
    given = [
        {"name": "draft", "rules": []},
        {"name": "write", "rules": [{"type": "writes", "paths": ["CHANGELOG.md"]}]},
        {"name": "report", "rules": [{"type": "result", "results": ["written"]}]},
    ]
    printing(log, "rules.py", {"steps": given})
    assert given_steps(log, cwd, run(log), start("log:writer", "Write it.")) == given


@pytest.mark.supports(
    "test_the_runs_first_turn_takes_its_steps_from_the_adapter_with_the_runs_words",
    "test_a_subagents_end_after_the_turns_end_begins_a_turn_held_to_steps_from_its_notification",
    "test_a_turns_adapter_of_the_rules_is_given_each_earlier_turn_with_its_role_and_prompt",
)
@pytest.mark.parametrize(
    "prompt, turns",
    [
        ("", []),
        (
            "<task-notification>Wrote it.</task-notification>",
            [{"role": "log:up", "prompt": ""}],
        ),
        (
            "/log:tag",
            [
                {"role": "log:up", "prompt": ""},
                {"role": "log:up", "prompt": "Write docs/notes.md."},
            ],
        ),
    ],
    ids=["first", "one-earlier", "several-earlier"],
)
def test_the_adapter_of_the_rules_takes_the_main_conversations_role_the_prompt_and_the_turns(
    log: str, cwd: str, prompt: str, turns: list[EarlierTurn]
):
    """Given an adapter of the rules that writes what it's given
    When Lane asks it for the steps of a turn of the main conversation in log:up: the run's first,
    with an empty prompt and no earlier turn; one begun by a task-notification after the first; or
    one begun by /log:tag after two
    Then it was given the run's skill and words, log:up as the role, the turn's prompt, and each
    earlier turn with its role and prompt, oldest first, and ran in the conversation's folder"""
    adapter(log, "rules.py", ECHO.format(printed=json.dumps({"steps": []})))
    given_steps(log, cwd, run(log), {"role": "log:up", "prompt": prompt, "turns": turns})
    assert given(cwd) == {
        "input": {
            "run": {"skill": "log:up", "words": "1.2.0"},
            "role": "log:up",
            "prompt": prompt,
            "turns": turns,
        },
        "cwd": os.path.realpath(cwd),
    }
