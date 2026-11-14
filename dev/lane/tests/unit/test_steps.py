"""The unit cases of scripts/steps.py: where a plugin's Roles and Steps lie, and how each Step reads
without Lane's text, through `roles`, `files_of`, and `fingerprint`, on plugins each test writes."""

from __future__ import annotations

import os
from typing import Any

import pytest
from domain.fault import Fault
from domain.laid_set import Laid, LaidSentence
from lane_example import WRITER, put, put_plugin
from steps import files_of, fingerprint, roles

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)

STEP_2 = "2. Read the commits since then with `git log --oneline`."
SENTENCE = "Run only `git log --oneline`."


@pytest.fixture
def plugin(tmp_path: Any) -> str:
    """The walkthrough's `changelog` in a folder of the test's own."""
    return put_plugin(os.path.realpath(str(tmp_path)))


NOTHING_LAID = Laid()


def by_name(
    plugin: str, laid: Laid = NOTHING_LAID, commands: dict[str, str] | None = None
) -> dict[str, Any]:
    return {role.name: role for role in roles(plugin, laid, commands)}


@pytest.mark.supports("test_lay_print_shows_each_step_as_it_will_read_with_the_routes_and_an_id")
def test_the_skill_and_each_subagent_come_with_their_steps_in_order(plugin: str):
    """Given the walkthrough's `changelog`
    When its Roles are read
    Then they are the skill `write` with 1 Step, writer with 4, and reviewer with 2, each Step's
    words as written"""
    found = by_name(plugin)
    assert found["write"].skill and not found["writer"].skill
    assert [len(found[n].steps) for n in ("write", "writer", "reviewer")] == [1, 4, 2]
    assert found["writer"].steps[1].words == STEP_2


@pytest.mark.supports("test_lay_print_refuses_two_roles_that_take_their_steps_from_one_file")
def test_steps_in_a_file_that_the_body_names_by_the_plugin_root_belong_to_the_role(plugin: str):
    """Given writer's body that names `${CLAUDE_PLUGIN_ROOT}/domain/writer.md`, which holds its
    Steps
    When the Roles are read
    Then writer's Steps are those of domain/writer.md, and that file is one of writer's files"""
    put(plugin, "domain/writer.md", "## Steps\n\n1. Read `CHANGELOG.md`.\n")
    put(
        plugin,
        "agents/writer.md",
        "---\nname: writer\nbackground: true\n---\n\n"
        "Read ${CLAUDE_PLUGIN_ROOT}/domain/writer.md.\n",
    )
    writer = by_name(plugin)["writer"]
    assert [s.words for s in writer.steps] == ["1. Read `CHANGELOG.md`."]
    assert "domain/writer.md" in files_of(writer)


@pytest.mark.supports("test_a_move_that_waits_for_a_command_is_due_once_the_person_types_it")
def test_the_skills_steps_hold_those_of_each_command_named(plugin: str):
    """Given `changelog` with a command `approve` whose SKILL.md holds one Step
    When the Roles are read with `approve` named as a command of a Route of `write`
    Then the Steps of `write` hold that Step, and approve is no Role of its own"""
    put(plugin, "skills/approve/SKILL.md", "---\nname: approve\n---\n\n## Steps\n\n1. Go on.\n")
    found = by_name(plugin, commands={"approve": "write"})
    assert "approve" not in found
    assert "1. Go on." in [s.words for s in found["write"].steps]


@pytest.mark.supports(
    "test_up_again_on_unchanged_steps_proposes_each_step_without_the_text_lane_laid"
)
def test_a_laid_sentence_still_word_for_word_is_taken_out(plugin: str):
    """Given writer's step 2 that ends with the sentence that the Laid names
    When the Roles are read with that Laid
    Then step 2 reads as the user wrote it"""
    put(plugin, "agents/writer.md", WRITER.replace(STEP_2, f"{STEP_2} {SENTENCE}"))
    laid = Laid((LaidSentence("agents/writer.md", STEP_2, SENTENCE),))
    assert by_name(plugin, laid)["writer"].steps[1].words == STEP_2


@pytest.mark.supports(
    "test_a_laid_sentence_that_the_user_changed_is_kept_as_their_words_with_a_note"
)
def test_a_laid_sentence_the_user_changed_is_kept_as_theirs(plugin: str):
    """Given writer's step 2 whose laid sentence the user changed to `Run only git log.`
    When the Roles are read with the Laid
    Then step 2 keeps `Run only git log.`, and names it as kept"""
    put(plugin, "agents/writer.md", WRITER.replace(STEP_2, f"{STEP_2} Run only git log."))
    laid = Laid((LaidSentence("agents/writer.md", STEP_2, SENTENCE),))
    step = by_name(plugin, laid)["writer"].steps[1]
    assert "Run only git log." in step.words and step.kept == ("Run only git log.",)


@pytest.mark.supports("test_lay_print_shows_each_step_as_it_will_read_with_the_routes_and_an_id")
def test_a_plugin_with_no_skill_raises_a_fault(plugin: str):
    """Given `changelog` with no skill
    When its Roles are read
    Then a Fault says so, with the plugin's maker to fix it"""
    os.remove(os.path.join(plugin, "skills", "write", "SKILL.md"))
    with pytest.raises(Fault) as raised:
        roles(plugin, Laid())
    assert "maker" in raised.value.who


@pytest.mark.supports("test_lay_print_shows_each_step_as_it_will_read_with_the_routes_and_an_id")
def test_a_role_with_no_numbered_steps_raises_a_fault_naming_its_file(plugin: str):
    """Given reviewer's file with no numbered list under `## Steps`
    When the Roles are read
    Then a Fault names agents/reviewer.md"""
    put(plugin, "agents/reviewer.md", "---\nname: reviewer\nbackground: true\n---\n\nReview.\n")
    with pytest.raises(Fault, match="agents/reviewer.md"):
        roles(plugin, Laid())


@pytest.mark.supports(
    "test_lay_write_after_the_steps_changed_since_the_proposal_was_shown_is_refused"
)
def test_the_fingerprint_changes_with_a_steps_words_and_stays_without(plugin: str):
    """Given the walkthrough's `changelog`
    When its fingerprint is taken, again unchanged, and once writer's step 3 changed
    Then the first two agree, and the third differs"""
    first = fingerprint(roles(plugin, Laid()))
    same = fingerprint(roles(plugin, Laid()))
    put(plugin, "agents/writer.md", WRITER.replace("new entries", "entries"))
    changed = fingerprint(roles(plugin, Laid()))
    assert first == same != changed


@pytest.mark.supports("test_a_move_that_waits_for_a_command_is_due_once_the_person_types_it")
def test_a_second_skill_that_no_route_names_as_a_command_raises_a_fault(plugin: str):
    """Given `changelog` with a second skill `approve`
    When the Roles are read with no command named
    Then a Fault names skills/approve/SKILL.md"""
    put(plugin, "skills/approve/SKILL.md", "---\nname: approve\n---\n\n## Steps\n\n1. Go on.\n")
    with pytest.raises(Fault, match="approve"):
        roles(plugin, Laid())
