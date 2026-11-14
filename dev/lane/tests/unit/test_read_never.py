"""The unit cases of domain/lanes/read_never.py: a role reads nothing of the paths it takes, save
each part under `!`, by any tool, save a command that the role may run."""

from __future__ import annotations

import pytest
from domain.event import COMMAND, READ, WRITE, Call
from domain.lanes import PASSES, End, Where
from domain.lanes.read_never import LANE_TYPE
from lane_parts import ROOT

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)

WHERE = Where(ROOT, ROOT)
TAKES = ("notes/", "!notes/public.md")


@pytest.mark.supports(
    "test_lay_types_gives_each_type_with_what_it_takes_the_steps_it_suits_and_its_sentence"
)
def test_the_sentence_names_each_path_kept_unread_and_each_part_it_may_read():
    """Given a read_never Lane that takes `notes/` and `!notes/public.md`
    When its sentence is made
    Then it names `notes/` and `notes/public.md`"""
    sentence = LANE_TYPE.sentence("reviewer", TAKES)
    assert "`notes/`" in sentence and "`notes/public.md`" in sentence


@pytest.mark.supports("test_lay_print_refuses_a_lane_of_a_type_there_isnt")
def test_a_lane_that_takes_only_parts_under_bang_cant_stand():
    """Given a read_never Lane that takes only `!notes/public.md`
    When its faults are asked
    Then it has one, as it keeps nothing unread"""
    assert LANE_TYPE.faults("reviewer", ("!notes/public.md",), False)


@pytest.mark.supports(
    "test_a_read_of_a_path_that_read_never_keeps_unread_is_stopped_and_its_bang_part_passes"
)
def test_a_read_of_a_file_under_a_kept_path_fails():
    """Given a read_never Lane that takes `notes/` and `!notes/public.md`
    When reviewer reads notes/secret.md
    Then the call fails"""
    call = Call(READ, path=f"{ROOT}/notes/secret.md")
    assert not LANE_TYPE.check_call(TAKES, call, {}, WHERE, ()).passes


@pytest.mark.supports(
    "test_a_read_of_a_path_that_read_never_keeps_unread_is_stopped_and_its_bang_part_passes"
)
def test_a_read_of_the_part_under_bang_passes():
    """Given a read_never Lane that takes `notes/` and `!notes/public.md`
    When reviewer reads notes/public.md
    Then the call passes"""
    call = Call(READ, path=f"{ROOT}/notes/public.md")
    assert LANE_TYPE.check_call(TAKES, call, {}, WHERE, ()).passes


@pytest.mark.supports(
    "test_a_read_of_a_path_that_read_never_keeps_unread_is_stopped_and_its_bang_part_passes"
)
def test_a_command_that_names_a_kept_path_fails():
    """Given a read_never Lane that takes `notes/`
    When reviewer runs `cat notes/secret.md`
    Then the call fails"""
    call = Call(COMMAND, command="cat notes/secret.md")
    assert not LANE_TYPE.check_call(TAKES, call, {}, WHERE, ()).passes


@pytest.mark.supports(
    "test_a_read_of_a_path_that_read_never_keeps_unread_is_stopped_and_its_bang_part_passes"
)
def test_a_command_that_the_role_may_run_passes_though_it_names_a_kept_path():
    """Given a read_never Lane that takes `notes/`, and reviewer may run `python3 notes/check.py`
    When reviewer runs `python3 notes/check.py`
    Then the call passes"""
    call = Call(COMMAND, command="python3 notes/check.py")
    assert LANE_TYPE.check_call(TAKES, call, {}, WHERE, ("python3 notes/check.py",)).passes


@pytest.mark.supports(
    "test_a_read_of_a_path_that_read_never_keeps_unread_is_stopped_and_its_bang_part_passes"
)
def test_a_read_outside_every_kept_path_passes():
    """Given a read_never Lane that takes `notes/`
    When reviewer reads CHANGELOG.md
    Then the call passes"""
    call = Call(READ, path=f"{ROOT}/CHANGELOG.md")
    assert LANE_TYPE.check_call(TAKES, call, {}, WHERE, ()).passes


@pytest.mark.supports("test_a_call_that_keeps_every_lane_of_its_role_passes")
def test_a_write_and_an_end_arent_held():
    """Given a read_never Lane that takes `notes/`
    When reviewer writes CHANGELOG.md, and ends
    Then the Lane gives PASSES for each"""
    call = Call(WRITE, path=f"{ROOT}/CHANGELOG.md")
    assert LANE_TYPE.check_call(TAKES, call, {}, WHERE, ()) == PASSES
    assert LANE_TYPE.check_end(TAKES, End("reviewer", "Done."), WHERE) == PASSES
