"""The unit cases of domain/lanes/write_only.py: a role writes or edits only the files that its step
names."""

from __future__ import annotations

import pytest
from domain.event import COMMAND, READ, WRITE, Call
from domain.lanes import PASSES, End, Where
from domain.lanes.write_only import LANE_TYPE
from lane_parts import ROOT

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)

WHERE = Where(ROOT, ROOT)


@pytest.mark.supports(
    "test_lay_types_gives_each_type_with_what_it_takes_the_steps_it_suits_and_its_sentence"
)
def test_the_sentence_names_the_file_in_backticks():
    """Given a write_only Lane that takes `CHANGELOG.md`
    When its sentence is made
    Then it reads `Write only `CHANGELOG.md`.`, as the walkthrough shows"""
    assert LANE_TYPE.sentence("writer", ("CHANGELOG.md",)) == "Write only `CHANGELOG.md`."


@pytest.mark.supports("test_lay_print_refuses_a_lane_of_a_type_there_isnt")
def test_a_lane_that_takes_no_path_cant_stand():
    """Given a write_only Lane that takes nothing
    When its faults are asked
    Then it has one"""
    assert LANE_TYPE.faults("writer", (), False)


@pytest.mark.supports("test_lay_print_shows_each_step_as_it_will_read_with_the_routes_and_an_id")
def test_it_lets_the_role_run_no_command():
    """Given a write_only Lane that takes `CHANGELOG.md`
    When its commands are asked
    Then there are none"""
    assert LANE_TYPE.commands("writer", ("CHANGELOG.md",)) == ()


@pytest.mark.supports("test_a_call_that_keeps_every_lane_of_its_role_passes")
def test_a_write_of_the_file_it_takes_passes():
    """Given a write_only Lane that takes `CHANGELOG.md`
    When writer writes CHANGELOG.md
    Then the call passes"""
    call = Call(WRITE, path=f"{ROOT}/CHANGELOG.md")
    assert LANE_TYPE.check_call(("CHANGELOG.md",), call, {}, WHERE, ()).passes


@pytest.mark.supports("test_a_write_of_a_file_that_no_write_only_lane_takes_is_stopped")
def test_a_write_of_another_file_fails():
    """Given a write_only Lane that takes `CHANGELOG.md`
    When writer writes NOTES.md
    Then the call fails"""
    call = Call(WRITE, path=f"{ROOT}/NOTES.md")
    assert not LANE_TYPE.check_call(("CHANGELOG.md",), call, {}, WHERE, ()).passes


@pytest.mark.supports("test_a_call_that_keeps_every_lane_of_its_role_passes")
def test_a_read_or_a_command_isnt_held():
    """Given a write_only Lane that takes `CHANGELOG.md`
    When writer reads NOTES.md, or runs `git log --oneline`
    Then the Lane gives PASSES for each"""
    read = Call(READ, path=f"{ROOT}/NOTES.md")
    run = Call(COMMAND, command="git log --oneline")
    assert LANE_TYPE.check_call(("CHANGELOG.md",), read, {}, WHERE, ()) == PASSES
    assert LANE_TYPE.check_call(("CHANGELOG.md",), run, {}, WHERE, ()) == PASSES


@pytest.mark.supports("test_a_call_that_keeps_every_lane_of_its_role_passes")
def test_an_end_isnt_held():
    """Given a write_only Lane that takes `CHANGELOG.md`
    When writer ends
    Then the Lane gives PASSES"""
    assert LANE_TYPE.check_end(("CHANGELOG.md",), End("writer", "Done."), WHERE) == PASSES
