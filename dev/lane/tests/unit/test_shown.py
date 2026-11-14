"""The unit cases of scripts/shown.py: how `lay.py print` shows a Proposal, through `reads`,
`notes`, and `text`, each as the walkthrough shows it."""

from __future__ import annotations

import os
from typing import Any

import pytest
from domain.laid_set import Laid
from lane_example import PROPOSAL, WRITER, put, put_plugin, shown
from proposal import keep, parse
from shown import notes, reads, text
from steps import Step, roles

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)

STEP_2 = "2. Read the commits since then with `git log --oneline`."


@pytest.fixture
def plugin(tmp_path: Any) -> str:
    return put_plugin(os.path.join(os.path.realpath(str(tmp_path)), "changelog"))


@pytest.mark.supports("test_lay_print_shows_each_step_as_it_will_read_with_the_routes_and_an_id")
def test_a_step_reads_with_its_sentence_after_one_space():
    """Given writer's step 2 and the sentence `Run only `git log --oneline`.`
    When it's read as it'll be laid
    Then it reads as the walkthrough shows"""
    step = Step("writer", 2, "agents/writer.md", STEP_2)
    assert (
        reads(step, ["Run only `git log --oneline`."]) == f"{STEP_2} Run only `git log --oneline`."
    )


@pytest.mark.supports(
    "test_up_again_on_unchanged_steps_proposes_each_step_without_the_text_lane_laid"
)
def test_a_step_that_says_its_sentence_already_reads_as_it_is():
    """Given writer's step 2 that already ends with `Run only `git log --oneline`.`
    When it's read as it'll be laid with that sentence
    Then it reads as before, with the sentence once"""
    words = f"{STEP_2} Run only `git log --oneline`."
    assert (
        reads(Step("writer", 2, "agents/writer.md", words), ["Run only `git log --oneline`."])
        == words
    )


@pytest.mark.supports("test_lay_print_notes_a_step_that_names_a_command_its_subagent_may_not_run")
def test_a_step_that_names_a_command_its_subagent_may_not_run_gets_a_note(plugin: str):
    """Given writer's step 1 that names `cat CHANGELOG.md`, which no Lane lets writer run
    When the notes of the walkthrough's Proposal are asked
    Then one names step 1 of writer and `cat CHANGELOG.md`"""
    put(plugin, "agents/writer.md", WRITER.replace("Read `CHANGELOG.md`", "Run `cat CHANGELOG.md`"))
    found = notes(parse(PROPOSAL, "p.json"), roles(plugin, Laid()))
    assert any("step 1" in n and "cat CHANGELOG.md" in n for n in found), found


@pytest.mark.supports("test_lay_print_shows_each_step_as_it_will_read_with_the_routes_and_an_id")
def test_a_role_whose_steps_name_no_command_gets_a_note_that_lane_holds_only_its_end(plugin: str):
    """Given the walkthrough's reviewer, whose steps name no command
    When the notes of the walkthrough's Proposal are asked
    Then one names reviewer"""
    found = notes(parse(PROPOSAL, "p.json"), roles(plugin, Laid()))
    assert any("reviewer" in n for n in found), found


@pytest.mark.supports(
    "test_a_laid_sentence_that_the_user_changed_is_kept_as_their_words_with_a_note"
)
def test_a_laid_sentence_the_user_changed_gets_a_note(plugin: str):
    """Given writer's step 2 holding a laid sentence the user changed to `Run only git log.`
    When the notes of the walkthrough's Proposal are asked
    Then one names step 2 of writer and says Lane keeps it as the user's own words"""
    put(plugin, "agents/writer.md", WRITER.replace(STEP_2, f"{STEP_2} Run only git log."))
    from domain.laid_set import LaidSentence

    laid = Laid((LaidSentence("agents/writer.md", STEP_2, "Run only `git log --oneline`."),))
    found = notes(parse(PROPOSAL, "p.json"), roles(plugin, laid))
    assert any("step 2" in n and "own words" in n for n in found), found


@pytest.mark.supports("test_lay_print_shows_each_step_as_it_will_read_with_the_routes_and_an_id")
def test_the_text_of_the_walkthroughs_proposal_is_what_the_walkthrough_shows(
    plugin: str, tmp_path: Any
):
    """Given the walkthrough's Proposal kept on `changelog`
    When its text is made
    Then it is what the walkthrough shows, with its ID"""
    found = roles(plugin, Laid())
    given = keep(parse(PROPOSAL, "p.json"), found, str(tmp_path))
    assert text(given, found) == shown(given.id)
