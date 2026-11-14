"""The unit cases of domain/lanes/names_printed.py: a subagent ends only where its last message
starts a line with a line that a command it takes printed since its Start or resume."""

from __future__ import annotations

import pytest
from domain.event import COMMAND, Call
from domain.lanes import PASSES, End, Where
from domain.lanes.names_printed import LANE_TYPE
from lane_parts import ROOT

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)

WHERE = Where(ROOT, ROOT)
TAKES = ("git log --oneline",)
PRINTED = ("d417d74 Add --lines", "7a84e02 Add --chars")


@pytest.mark.supports(
    "test_an_end_that_starts_no_line_with_a_line_that_its_command_printed_is_held"
)
def test_an_end_that_starts_a_line_with_a_printed_line_passes():
    """Given a names_printed Lane on `git log --oneline`, which printed two lines
    When writer ends with `d417d74 Add --lines` on a line of its own, and more after
    Then the end passes"""
    end = End("writer", "Newest:\nd417d74 Add --lines\nis the newest.", printed=PRINTED)
    assert LANE_TYPE.check_end(TAKES, end, WHERE).passes


@pytest.mark.supports(
    "test_an_end_that_starts_no_line_with_a_line_that_its_command_printed_is_held"
)
def test_an_end_that_names_no_printed_line_fails_with_each_line_printed():
    """Given a names_printed Lane on `git log --oneline`, which printed two lines
    When writer ends with `I wrote the entries.`
    Then the end fails, giving each line printed"""
    verdict = LANE_TYPE.check_end(
        TAKES, End("writer", "I wrote the entries.", printed=PRINTED), WHERE
    )
    assert (verdict.passes, verdict.may) == (False, PRINTED)


@pytest.mark.supports(
    "test_an_end_that_starts_no_line_with_a_line_that_its_command_printed_is_held"
)
def test_an_end_that_holds_a_printed_line_only_inside_a_line_fails():
    """Given a names_printed Lane on `git log --oneline`, which printed `d417d74 Add --lines`
    When writer ends with `See d417d74 Add --lines.`
    Then the end fails"""
    end = End("writer", "See d417d74 Add --lines.", printed=PRINTED)
    assert not LANE_TYPE.check_end(TAKES, end, WHERE).passes


@pytest.mark.supports(
    "test_an_end_that_starts_no_line_with_a_line_that_its_command_printed_is_held"
)
def test_an_end_after_its_commands_printed_nothing_fails():
    """Given a names_printed Lane on `git log --oneline`, which printed nothing since the Start
    When writer ends with any message
    Then the end fails"""
    assert not LANE_TYPE.check_end(TAKES, End("writer", "d417d74 Add --lines"), WHERE).passes


@pytest.mark.supports(
    "test_lay_types_gives_each_type_with_what_it_takes_the_steps_it_suits_and_its_sentence"
)
def test_the_sentence_names_each_command_whose_lines_the_end_names():
    """Given a names_printed Lane on `git log --oneline`
    When its sentence is made
    Then it names `git log --oneline` in backticks"""
    assert "`git log --oneline`" in LANE_TYPE.sentence("writer", TAKES)


@pytest.mark.supports("test_lay_print_shows_each_step_as_it_will_read_with_the_routes_and_an_id")
def test_it_lets_the_role_run_each_command_it_takes():
    """Given a names_printed Lane on `git log --oneline`
    When its commands are asked
    Then they are `git log --oneline`"""
    assert LANE_TYPE.commands("writer", TAKES) == TAKES


@pytest.mark.supports("test_lay_print_refuses_a_lane_of_a_type_there_isnt")
def test_a_lane_that_takes_no_command_cant_stand():
    """Given a names_printed Lane that takes nothing
    When its faults are asked
    Then it has one"""
    assert LANE_TYPE.faults("writer", (), False)


@pytest.mark.supports("test_a_call_that_keeps_every_lane_of_its_role_passes")
def test_a_call_isnt_held():
    """Given a names_printed Lane on `git log --oneline`
    When writer runs `git status`
    Then the Lane gives PASSES"""
    call = Call(COMMAND, command="git status")
    assert LANE_TYPE.check_call(TAKES, call, {}, WHERE, ()) == PASSES
