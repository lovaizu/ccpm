"""The unit cases of domain/lanes/pattern.py: what a command or a path with names in braces stands
for, through `names`, `matches`, and `fill`."""

from __future__ import annotations

import pytest
from domain.lanes.pattern import fill, matches, names

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)


@pytest.mark.supports("test_a_run_value_holds_each_subagent_to_the_value_of_its_own_start")
def test_names_of_a_pattern_without_braces_are_none():
    """Given `git log --oneline`
    When its names are asked
    Then there are none"""
    assert names("git log --oneline") == ()


@pytest.mark.supports("test_a_run_value_holds_each_subagent_to_the_value_of_its_own_start")
def test_names_give_each_name_once_in_its_order():
    """Given `cp {a} {b} {a}`
    When its names are asked
    Then they are `a` and `b`, in that order"""
    assert names("cp {a} {b} {a}") == ("a", "b")


@pytest.mark.supports(
    "test_a_command_not_word_for_word_is_stopped_with_the_steps_sentence_and_the_commands"
)
def test_a_command_word_for_word_matches():
    """Given the pattern `git log --oneline`
    When `git log --oneline` is matched
    Then it matches"""
    assert matches("git log --oneline", "git log --oneline", {})


@pytest.mark.supports(
    "test_a_command_not_word_for_word_is_stopped_with_the_steps_sentence_and_the_commands"
)
def test_a_command_with_a_word_more_matches_not():
    """Given the pattern `git log --oneline`
    When `git -C /repo log --oneline` is matched
    Then it doesn't match"""
    assert not matches("git log --oneline", "git -C /repo log --oneline", {})


@pytest.mark.supports(
    "test_a_command_not_word_for_word_is_stopped_with_the_steps_sentence_and_the_commands"
)
def test_two_commands_joined_match_not_one_of_them():
    """Given the pattern `git show {commit}`
    When `git show d417d74 && git show 7a84e02` is matched
    Then it doesn't match"""
    assert not matches("git show {commit}", "git show d417d74 && git show 7a84e02", {})


@pytest.mark.supports("test_a_run_value_holds_each_subagent_to_the_value_of_its_own_start")
def test_a_name_with_no_value_matches_any_one_word():
    """Given the pattern `git show {commit}` and no run values
    When `git show d417d74` is matched
    Then it matches"""
    assert matches("git show {commit}", "git show d417d74", {})


@pytest.mark.supports("test_a_run_value_holds_each_subagent_to_the_value_of_its_own_start")
def test_a_name_with_no_value_matches_no_empty_word():
    """Given the pattern `git show {commit}` and no run values
    When `git show` is matched
    Then it doesn't match"""
    assert not matches("git show {commit}", "git show", {})


@pytest.mark.supports("test_a_run_value_holds_each_subagent_to_the_value_of_its_own_start")
def test_a_name_with_a_value_matches_that_value_alone():
    """Given the pattern `notes/{part}.md` and the run value `part` `a`
    When `notes/a.md` and `notes/b.md` are matched
    Then the first matches and the second doesn't"""
    assert matches("notes/{part}.md", "notes/a.md", {"part": "a"})
    assert not matches("notes/{part}.md", "notes/b.md", {"part": "a"})


@pytest.mark.supports("test_a_run_value_holds_each_subagent_to_the_value_of_its_own_start")
def test_a_name_in_a_path_matches_no_part_across_a_slash():
    """Given the pattern `notes/{part}.md` and no run values
    When `notes/a/b.md` is matched
    Then it doesn't match"""
    assert not matches("notes/{part}.md", "notes/a/b.md", {})


@pytest.mark.supports(
    "test_an_end_whose_check_of_the_plugins_own_gives_other_than_0_is_held_with_what_it_printed"
)
def test_fill_replaces_each_name_with_its_value():
    """Given `python3 check.py {result} {version}` and the values `result` `written` and
    `version` `0.2.0`
    When it's filled
    Then it reads `python3 check.py written 0.2.0`"""
    filled = fill("python3 check.py {result} {version}", {"result": "written", "version": "0.2.0"})
    assert filled == "python3 check.py written 0.2.0"


@pytest.mark.supports(
    "test_an_end_whose_check_names_a_value_its_start_didnt_give_is_held_with_who_must_fix_it"
)
def test_fill_gives_none_where_a_name_has_no_value():
    """Given `python3 check.py {version}` and no value of `version`
    When it's filled
    Then it gives None"""
    assert fill("python3 check.py {version}", {"result": "written"}) is None


@pytest.mark.supports(
    "test_an_end_whose_check_of_the_plugins_own_gives_other_than_0_is_held_with_what_it_printed"
)
def test_fill_leaves_a_pattern_without_names_as_it_is():
    """Given `python3 check.py`
    When it's filled with no values
    Then it reads as before"""
    assert fill("python3 check.py", {}) == "python3 check.py"
