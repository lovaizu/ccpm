"""The unit cases of domain/lanes/ends_checked.py: an end passes only where the plugin's own
command, filled with the run values and `{result}`, gives 0 in the folder that the conversation
works in."""

from __future__ import annotations

import os
from typing import Any

import pytest
from domain.event import COMMAND, Call
from domain.fault import Fault
from domain.lanes import PASSES, End, Where
from domain.lanes.ends_checked import LANE_TYPE

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)


@pytest.fixture
def where(tmp_path: Any) -> Where:
    """A folder that the conversation works in, holding check.py, which prints its arguments and
    exits 0 where the first is `good`, else 1."""
    folder = os.path.realpath(str(tmp_path))
    with open(os.path.join(folder, "check.py"), "w", encoding="utf-8") as f:
        f.write("import sys\nprint(' '.join(sys.argv[1:]))\nsys.exit(sys.argv[1:2] != ['good'])\n")
    return Where(folder, folder)


@pytest.mark.supports(
    "test_an_end_whose_check_of_the_plugins_own_gives_other_than_0_is_held_with_what_it_printed"
)
def test_an_end_whose_command_gives_0_passes(where: Where):
    """Given an ends_checked Lane that runs `python3 check.py {result}`
    When reviewer ends having given `good`
    Then the end passes"""
    end = End("reviewer", "Done.", result="good")
    assert LANE_TYPE.check_end(("python3 check.py {result}",), end, where).passes


@pytest.mark.supports(
    "test_an_end_whose_check_of_the_plugins_own_gives_other_than_0_is_held_with_what_it_printed"
)
def test_an_end_whose_command_gives_1_fails_with_what_it_printed(where: Where):
    """Given an ends_checked Lane that runs `python3 check.py {result} {version}`
    When reviewer ends having given `more`, its Start giving `version` `0.2.0`
    Then the end fails, with `more 0.2.0`, what the command printed"""
    end = End("reviewer", "Done.", values={"version": "0.2.0"}, result="more")
    verdict = LANE_TYPE.check_end(("python3 check.py {result} {version}",), end, where)
    assert (verdict.passes, verdict.printed.strip()) == (False, "more 0.2.0")


@pytest.mark.supports(
    "test_an_end_whose_check_names_a_value_its_start_didnt_give_is_held_with_who_must_fix_it"
)
def test_an_end_whose_command_names_a_value_its_start_didnt_give_raises_a_fault(where: Where):
    """Given an ends_checked Lane that runs `python3 check.py {version}`
    When reviewer ends, its Start giving no `version`
    Then the check raises a Fault naming `{version}`"""
    with pytest.raises(Fault, match="version"):
        LANE_TYPE.check_end(("python3 check.py {version}",), End("reviewer", "Done."), where)


@pytest.mark.supports(
    "test_lay_print_refuses_an_ends_checked_lane_of_the_skill_naming_a_value_no_start_fills"
)
def test_a_lane_of_the_skill_naming_a_value_other_than_result_cant_stand():
    """Given an ends_checked Lane on the skill that runs `python3 check.py {deliverable}`
    When its faults are asked
    Then it has one naming `{deliverable}`"""
    faults = LANE_TYPE.faults("write", ("python3 check.py {deliverable}",), True)
    assert faults and "{deliverable}" in faults[0]


@pytest.mark.supports(
    "test_a_lane_of_the_skill_holds_its_turns_end_until_the_plugins_command_gives_0"
)
def test_a_lane_of_the_skill_naming_only_result_stands():
    """Given an ends_checked Lane on the skill that runs `python3 check.py {result}`
    When its faults are asked
    Then it has none"""
    assert LANE_TYPE.faults("write", ("python3 check.py {result}",), True) == []


@pytest.mark.supports(
    "test_an_end_whose_check_names_a_value_its_start_didnt_give_is_held_with_who_must_fix_it"
)
def test_a_lane_of_a_subagent_naming_any_value_stands():
    """Given an ends_checked Lane on writer that runs `python3 check.py {version}`
    When its faults are asked
    Then it has none, as an adapter may give writer's Start the value"""
    assert LANE_TYPE.faults("writer", ("python3 check.py {version}",), False) == []


@pytest.mark.supports("test_lay_print_refuses_a_lane_of_a_type_there_isnt")
def test_a_lane_that_takes_other_than_one_command_cant_stand():
    """Given an ends_checked Lane that takes no command, and one that takes two
    When their faults are asked
    Then each has one"""
    assert LANE_TYPE.faults("writer", (), False)
    assert LANE_TYPE.faults("writer", ("python3 a.py", "python3 b.py"), False)


@pytest.mark.supports(
    "test_lay_types_gives_each_type_with_what_it_takes_the_steps_it_suits_and_its_sentence"
)
def test_a_step_that_names_the_command_says_the_sentence_already():
    """Given a step that names `python3 check.py {result}`
    When it's asked whether the step says the sentence of the Lane on that command
    Then it does"""
    step = "4. Check your record with `python3 check.py {result}`."
    assert LANE_TYPE.said(step, "writer", ("python3 check.py {result}",))


@pytest.mark.supports(
    "test_lay_types_gives_each_type_with_what_it_takes_the_steps_it_suits_and_its_sentence"
)
def test_the_sentence_names_the_command():
    """Given an ends_checked Lane that runs `python3 check.py {result}`
    When its sentence is made
    Then it names `python3 check.py {result}` in backticks"""
    assert "`python3 check.py {result}`" in LANE_TYPE.sentence(
        "writer", ("python3 check.py {result}",)
    )


@pytest.mark.supports("test_a_call_that_keeps_every_lane_of_its_role_passes")
def test_it_lets_the_role_run_no_command_and_holds_no_call(where: Where):
    """Given an ends_checked Lane that runs `python3 check.py {result}`
    When its commands are asked, and writer runs `git status`
    Then it names none, and gives PASSES for the call, as the guard runs the command"""
    takes = ("python3 check.py {result}",)
    assert LANE_TYPE.commands("writer", takes) == ()
    assert LANE_TYPE.check_call(takes, Call(COMMAND, command="git status"), {}, where, ()) == PASSES
