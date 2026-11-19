"""The unit cases of hooks/lane/adapters.py: starts_due, one for each order that answers, the
plugin's own adapter, the route adapter, and none, and for each class of what the plugin's adapter
gives: the starts due, the run's end, a failure, and output out of its form; and given_steps, one
for each class of what the adapter of the rules gives, no adapter among them; with what Lane gives
an adapter on its standard input, and the folder it runs in."""

from __future__ import annotations

import json
import os
from typing import Any

import lane_bench
import lane_entries
import pytest
from adapters import AdapterFailed, given_steps, starts_due
from record import Entry, Run
from repo_files import write_files

UNBUILT = pytest.mark.xfail(strict=True, reason="Lane's parts have no bodies yet")

RULES: Any = lane_bench.RULES
# The rules of a plugin that gives no order: steps for its skill, and no routes.
NO_ORDER: Any = {"roles": {"log:up": RULES["roles"]["log:up"]}}
# An adapter that writes what it was given and the folder it runs in beside the conversation's
# files, and prints the output given.
ECHO = """\
import json, os, sys

with open("given.json", "w") as f:
    json.dump({{"input": json.load(sys.stdin), "cwd": os.getcwd()}}, f)
print({printed!r})
"""
WRITER_DUE = {"starts": [{"role": "log:writer", "count": 1}]}


def run(log: str, *entries: Entry) -> Run:
    """The run r1 of log:up for 1.2.0 in log's folder, with the entries after its command."""
    head: list[Entry] = [
        {"kind": "run", "run": "r1", "skill": "log:up", "words": "1.2.0"},
        {"kind": "folder", "run": "r1", "plugin_root": log},
    ]
    return Run("r1", "session-1", "log:up", "1.2.0", log, [*head, *entries])


def adapter(log: str, name: str, code: str) -> None:
    """Writes the adapter of `log`."""
    write_files(log, {f"lane/adapters/{name}": code})


def printing(log: str, name: str, printed: Any) -> None:
    """Writes the adapter of `log` that prints the JSON given."""
    adapter(log, name, f"print({json.dumps(printed)!r})\n")


def given(cwd: str) -> dict[str, object]:
    """What the echoing adapter was given, and the folder it ran in."""
    with open(os.path.join(cwd, "given.json"), encoding="utf-8") as f:
        return json.load(f)


def refused(call: Any) -> str:
    """What AdapterFailed says of the call."""
    with pytest.raises(AdapterFailed) as raised:
        call()
    return str(raised.value)


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
@UNBUILT
def test_the_plugins_adapter_gives_its_starts_due_or_the_runs_end(log: str, cwd: str, printed: Any):
    """Given `log`'s adapter of the starts due, which prints one start, two roles, none, or the
    run's end
    When Lane asks for the starts due of the run
    Then they are what it printed, in place of what log's routes give"""
    printing(log, "starts_due.py", printed)
    assert starts_due(log, cwd, run(log), RULES, False) == printed


@pytest.mark.supports("test_the_order_tells_the_starts_of_one_role_apart_by_their_prompts")
@UNBUILT
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
@UNBUILT
def test_a_plugin_with_no_order_has_no_start_due(log: str, cwd: str):
    """Given rules with no routes, and no adapter of the starts due
    When Lane asks for the starts due while the turn runs
    Then none is due"""
    assert starts_due(log, cwd, run(log), NO_ORDER, False) == {"starts": []}


@pytest.mark.supports(
    "test_a_run_of_a_plugin_with_no_order_ends_at_the_turns_end_that_its_steps_let_through"
)
@UNBUILT
def test_a_plugin_with_no_order_has_its_run_end_once_the_turn_ended(log: str, cwd: str):
    """Given rules with no routes, and no adapter of the starts due
    When Lane asks for the starts due with the turn ended
    Then the run ends"""
    assert starts_due(log, cwd, run(log), NO_ORDER, True) == {"ends": True}


@pytest.mark.supports(
    "test_an_adapter_of_the_starts_due_that_fails_stops_with_the_adapter_and_what_it_said"
)
@UNBUILT
def test_an_adapter_of_the_starts_due_that_fails_is_refused_with_its_file_and_what_it_said(
    log: str, cwd: str
):
    """Given an adapter of the starts due that exits 1 saying it found no version
    When Lane asks it for the starts due
    Then it refuses with AdapterFailed naming starts_due.py and what it said"""
    adapter(log, "starts_due.py", "import sys\n\nsys.exit('no version found')\n")
    said = refused(lambda: starts_due(log, cwd, run(log), RULES, False))
    assert "starts_due.py" in said
    assert "no version found" in said


@pytest.mark.supports("test_starts_due_out_of_their_form_stop_naming_the_adapter")
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
@UNBUILT
def test_starts_due_out_of_their_form_are_refused_naming_the_adapter(log: str, cwd: str, code: str):
    """Given an adapter of the starts due that prints text that isn't JSON, a start with no count,
    a count of 0, a role with no name, `ends` false, both starts and `ends`, or neither
    When Lane asks it for the starts due
    Then it refuses with AdapterFailed naming starts_due.py"""
    adapter(log, "starts_due.py", code)
    assert "starts_due.py" in refused(lambda: starts_due(log, cwd, run(log), RULES, False))


# given_steps

STEPS = [{"name": "write", "rules": [{"type": "writes", "paths": ["docs/changes/1.2.0.md"]}]}]


@pytest.mark.supports(
    "test_a_role_with_no_fixed_steps_takes_them_from_the_plugins_adapter_for_each_start"
)
@UNBUILT
def test_the_adapter_of_the_rules_gives_the_starts_steps_from_its_prompt(log: str, cwd: str):
    """Given `log`'s adapter of the rules, RULES_ADAPTER
    When Lane asks it for the steps of a writer's start whose prompt names docs/changes/1.2.0.md
    Then it gives the step `write`, which writes that file"""
    adapter(log, "rules.py", lane_bench.RULES_ADAPTER)
    prompt = "Write docs/changes/1.2.0.md."
    assert given_steps(log, cwd, run(log), "log:writer", prompt) == STEPS


@pytest.mark.supports(
    "test_a_role_with_no_fixed_steps_takes_them_from_the_plugins_adapter_for_each_start"
)
@UNBUILT
def test_the_adapter_of_the_rules_takes_the_run_the_role_and_the_prompt(log: str, cwd: str):
    """Given an adapter of the rules that writes what it's given
    When Lane asks it for the steps of a writer's start
    Then it was given the run's skill and words, the role, and the prompt, as rules.in.schema.json
    says, and ran in the conversation's folder"""
    adapter(log, "rules.py", ECHO.format(printed=json.dumps({"steps": []})))
    given_steps(log, cwd, run(log), "log:writer", "Write it.")
    assert given(cwd) == {
        "input": {
            "run": {"skill": "log:up", "words": "1.2.0"},
            "role": "log:writer",
            "prompt": "Write it.",
        },
        "cwd": os.path.realpath(cwd),
    }


@pytest.mark.supports(
    "test_a_start_of_a_role_with_no_steps_and_no_adapter_of_the_rules_is_stopped_saying_so"
)
@UNBUILT
def test_a_plugin_without_an_adapter_of_the_rules_is_refused_naming_it_and_the_role(
    log: str, cwd: str
):
    """Given `log` with no adapter of the rules
    When Lane asks for the steps of a writer's start
    Then it refuses with AdapterFailed naming lane/adapters/rules.py and the writer"""
    said = refused(lambda: given_steps(log, cwd, run(log), "log:writer", "Write it."))
    assert "lane/adapters/rules.py" in said
    assert "log:writer" in said


@pytest.mark.supports(
    "test_an_adapter_of_the_rules_that_fails_or_gives_out_of_its_form_stops_the_start"
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
@UNBUILT
def test_an_adapter_of_the_rules_that_fails_or_gives_out_of_its_form_is_refused(
    log: str, cwd: str, code: str
):
    """Given an adapter of the rules that exits 1, prints no object, a step with no rules, a step
    with no name, or a rule of a type Lane lacks
    When Lane asks it for the steps of a writer's start
    Then it refuses with AdapterFailed naming rules.py"""
    adapter(log, "rules.py", code)
    assert "rules.py" in refused(lambda: given_steps(log, cwd, run(log), "log:writer", "Write."))


@pytest.mark.supports(
    "test_a_role_with_no_fixed_steps_takes_them_from_the_plugins_adapter_for_each_start"
)
@UNBUILT
def test_the_adapter_of_the_rules_may_give_no_step(log: str, cwd: str):
    """Given an adapter of the rules that gives no step
    When Lane asks it for the steps of a writer's start
    Then there's none"""
    printing(log, "rules.py", {"steps": []})
    assert given_steps(log, cwd, run(log), "log:writer", "Write it.") == []
