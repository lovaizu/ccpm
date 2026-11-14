"""The unit cases of domain/laid_set.py: the form of hooks/lanes.json, through `dumps`, `loads`,
`load`, `routes_of`, and `lanes_of`."""

from __future__ import annotations

import os
from typing import Any

import pytest
from domain.fault import Fault
from domain.laid_set import Laid, LaidSentence, dumps, lanes_of, load, loads, routes_of
from lane_parts import LANES, REVIEW_ROUTES, ROUTES, laid_set, two_skills

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)


@pytest.mark.supports("test_a_persons_yes_lays_the_proposal_and_validation_passes")
def test_a_laid_set_written_reads_back_as_it_was():
    """Given the walkthrough's laid set, with a laid sentence and a hook entry in its Laid
    When it's written by dumps and read by loads
    Then it reads back equal"""
    laid = Laid(
        (
            LaidSentence(
                "agents/writer.md", "2. Read the commits.", "Run only `git log --oneline`."
            ),
        ),
        (("PreToolUse", "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/hook.py"),),
    )
    given = two_skills(laid=laid, text_adapter="text")
    assert loads(dumps(given), "hooks/lanes.json") == given


@pytest.mark.supports(
    "test_a_call_that_the_guard_cant_check_is_stopped_with_why_and_who_must_fix_it"
)
def test_text_that_isnt_json_raises_a_fault_naming_the_file():
    """Given the text `{`
    When it's read as hooks/lanes.json
    Then a Fault names hooks/lanes.json, with the plugin's maker to fix it"""
    with pytest.raises(Fault, match="lanes.json") as raised:
        loads("{", "hooks/lanes.json")
    assert "maker" in raised.value.who


@pytest.mark.supports(
    "test_a_call_that_the_guard_cant_check_is_stopped_with_why_and_who_must_fix_it"
)
def test_json_without_a_field_raises_a_fault_naming_the_field():
    """Given a laid set's JSON without `routes`
    When it's read
    Then a Fault names `routes`"""
    with pytest.raises(Fault, match="routes"):
        loads('{"plugin": "changelog", "skill": "write", "roles": [], "lanes": []}', "lanes.json")


@pytest.mark.supports("test_the_main_conversations_own_work_before_and_after_a_run_goes_unchecked")
def test_a_plugin_with_no_lanes_json_has_no_laid_set(tmp_path: Any):
    """Given a plugin's folder with no hooks/lanes.json
    When its laid set is loaded
    Then there is none"""
    assert load(str(tmp_path)) is None


@pytest.mark.supports(
    "test_the_command_gives_the_first_start_and_each_result_gives_the_next_until_no_more"
)
def test_a_plugins_lanes_json_loads_as_its_laid_set(tmp_path: Any):
    """Given a plugin whose hooks/lanes.json holds the walkthrough's laid set
    When its laid set is loaded
    Then it is that laid set"""
    os.makedirs(os.path.join(str(tmp_path), "hooks"))
    with open(os.path.join(str(tmp_path), "hooks", "lanes.json"), "w", encoding="utf-8") as f:
        f.write(dumps(laid_set()))
    assert load(str(tmp_path)) == laid_set()


@pytest.mark.supports("test_a_call_that_keeps_every_lane_of_its_role_passes")
def test_the_lanes_of_a_role_are_its_own_in_the_order_of_its_steps():
    """Given the walkthrough's laid set
    When writer's Lanes are asked, and those of a role that no Lane names
    Then writer's are its Lanes of steps 2, 3, and 4, and the other's none"""
    assert lanes_of(laid_set(), "writer") == LANES[1:4]
    assert lanes_of(laid_set(), "helper") == ()


@pytest.mark.supports("test_runs_of_two_skills_go_on_side_by_side_each_moved_by_its_own_results")
def test_the_routes_of_a_skill_are_its_own_in_their_order():
    """Given the laid set of `changelog` with the skills `write` and `review`
    When the Routes of `write`, of `review`, and of writer, which is no skill, are asked
    Then each skill's are its own, in order, and writer's none"""
    assert routes_of(two_skills(), "write") == ROUTES
    assert routes_of(two_skills(), "review") == REVIEW_ROUTES
    assert routes_of(two_skills(), "writer") == ()
