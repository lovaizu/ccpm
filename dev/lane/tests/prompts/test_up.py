"""The unit tests of up's prompt, `skills/up/SKILL.md` with `domain/up.md`: up runs alone on Opus,
k = 3 times for each case, on the walkthrough's `changelog` in a throwaway repository with lay.py
real, and each case passes only where all k runs pass, deciding by code each point that a run's
record shows. Each case names the integration case whose double of up it shows the real up keeps."""

from __future__ import annotations

import pytest
from lane_example import (
    PROPOSAL,
    REVIEWER,
    WRITE,
    WRITER,
    WRITER_STEP_2_MENDED,
)
from up_runs import UpRun, runs

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)

CHANGELOG = {
    "changelog/.claude-plugin/plugin.json": '{"name": "changelog", "version": "0.1.0"}',
    "changelog/skills/write/SKILL.md": WRITE,
    "changelog/agents/writer.md": WRITER,
    "changelog/agents/reviewer.md": REVIEWER,
    "CHANGELOG.md": "# Changelog\n\n## [0.1.0]\n",
}


Lanes = set[tuple[str, int, str, tuple[str, ...]]]


def lanes_of(run: UpRun) -> Lanes:
    """Each Lane of the last Proposal of the run, as its role, step, type, and takes."""
    return {
        (each["role"], each["step"], each["type"], tuple(each["takes"]))
        for each in run.proposals[-1]["lanes"]
    }


@pytest.mark.supports("test_lay_print_shows_each_step_as_it_will_read_with_the_routes_and_an_id")
def test_up_proposes_the_walkthroughs_lanes_and_routes_and_gives_the_person_what_print_showed():
    """Given the walkthrough's `changelog`
    When the person types `/lane:up changelog`
    Then on every run up's last Proposal holds the walkthrough's Lanes and Routes, and its last
    message holds what `lay.py print` showed, word for word, with no `lay.py write`"""
    done = runs(CHANGELOG, ["/lane:up changelog"])
    expected = {(e["role"], e["step"], e["type"], tuple(e["takes"])) for e in PROPOSAL["lanes"]}
    assert all(lanes_of(run) == expected for run in done), [lanes_of(r) for r in done]
    assert all(run.proposals[-1]["routes"] == PROPOSAL["routes"] for run in done)
    assert all(run.printed[-1].strip() in run.said[-1] for run in done)
    assert not any(run.laid for run in done)


@pytest.mark.supports("test_lay_print_shows_each_step_as_it_will_read_with_the_routes_and_an_id")
def test_up_names_a_result_where_a_subagents_steps_name_none():
    """Given the walkthrough's `changelog`, whose writer names no result
    When the person types `/lane:up changelog`
    Then on every run up's Proposal gives writer a gives_result Lane on its last step with one
    result, and a Route after it"""
    done = runs(CHANGELOG, ["/lane:up changelog"])
    named = [
        [lane for lane in lanes_of(run) if lane[0] == "writer" and lane[2] == "gives_result"]
        for run in done
    ]
    assert all(len(n) == 1 and n[0][1] == 4 and len(n[0][3]) == 1 for n in named), named


@pytest.mark.supports(
    "test_lay_print_refuses_a_proposal_that_leaves_out_an_adapter_and_shows_the_mended_one"
)
def test_up_mends_a_proposal_that_lay_print_refused_and_shows_the_one_that_stands():
    """Given `changelog` with an adapter `text` in hooks/adapters/
    When the person types `/lane:up changelog`
    Then on every run up's last Proposal names `text` as its adapter of a start's text, and its
    last message holds what `lay.py print` showed for it"""
    files = {**CHANGELOG, "changelog/hooks/adapters/text": '#!/bin/sh\necho \'{"text": "t"}\'\n'}
    done = runs(files, ["/lane:up changelog"])
    assert all(run.proposals[-1].get("text_adapter") == "text" for run in done)
    assert all(run.printed[-1].strip() in run.said[-1] for run in done)


@pytest.mark.supports("test_lay_print_refuses_a_subagent_whose_file_doesnt_set_background_true")
def test_up_tells_the_person_what_to_fix_where_a_file_of_the_plugin_cant_carry_the_proposal():
    """Given `changelog` whose reviewer doesn't set `background: true`
    When the person types `/lane:up changelog`
    Then on every run up leaves agents/reviewer.md as it was, and its last message names it and
    `background: true`"""
    files = {
        **CHANGELOG,
        "changelog/agents/reviewer.md": REVIEWER.replace("background: true\n", ""),
    }
    done = runs(files, ["/lane:up changelog"])
    assert all(
        run.files["changelog/agents/reviewer.md"] == files["changelog/agents/reviewer.md"]
        for run in done
    )
    assert all("reviewer.md" in run.said[-1] and "background: true" in run.said[-1] for run in done)


@pytest.mark.supports("test_a_change_the_person_asks_goes_into_the_step_and_up_proposes_again")
def test_up_writes_a_change_the_person_asks_into_its_step_and_proposes_again():
    """Given up showed the person the walkthrough's Proposal
    When the person asks that writer may also read each commit with `git show {commit}`
    Then on every run writer's step 2 names `git show {commit}`, up's last Proposal lets writer run
    it, and nothing is laid"""
    done = runs(
        CHANGELOG, ["/lane:up changelog", "Let writer also read each commit with git show."]
    )
    assert all("git show {commit}" in run.files["changelog/agents/writer.md"] for run in done)
    assert all(
        any("git show {commit}" in lane[3] for lane in lanes_of(run) if lane[0] == "writer")
        for run in done
    )
    assert not any(run.laid for run in done)


@pytest.mark.supports("test_a_persons_yes_lays_the_proposal_and_validation_passes")
def test_up_runs_lay_write_only_after_the_persons_yes():
    """Given up showed the person the walkthrough's Proposal
    When the person replies `yes`
    Then on every run up runs `lay.py write` on the ID that `lay.py print` showed, and its last
    message holds `claude plugin validate passed`"""
    done = runs(CHANGELOG, ["/lane:up changelog", "yes"])
    assert all(run.laid for run in done)
    assert all("claude plugin validate passed" in run.said[-1] for run in done)


@pytest.mark.supports("test_a_reply_that_is_neither_yes_nor_a_change_ends_the_run_of_up")
def test_up_lays_nothing_on_a_reply_that_asks_for_other_work():
    """Given up showed the person the walkthrough's Proposal
    When the person asks what tally does
    Then on every run up runs no `lay.py write`, and changes no file of the plugin"""
    done = runs(CHANGELOG, ["/lane:up changelog", "What does tally do?"])
    assert not any(run.laid for run in done)
    assert all(run.files["changelog/agents/writer.md"] == WRITER for run in done)


@pytest.mark.supports(
    "test_an_ai_that_called_up_by_the_skill_tool_lays_by_its_own_run_of_lay_write"
)
def test_up_called_by_an_ai_reads_the_proposal_and_approves_it_by_its_own_act():
    """Given the walkthrough's `changelog`
    When the main conversation's AI calls `lane:up` by the Skill tool for `changelog`
    Then on every run up lays a Proposal with no person's reply"""
    done = runs(CHANGELOG, ["changelog"], by_skill=True)
    assert all(run.laid for run in done)


@pytest.mark.supports(
    "test_up_again_after_the_steps_changed_shows_the_lanes_of_the_steps_as_they_now_read"
)
def test_up_on_mended_steps_proposes_from_the_steps_as_they_now_read():
    """Given `changelog` whose writer's step 2 reads as the walkthrough mends it
    When the person types `/lane:up changelog`
    Then on every run up's Proposal lets writer run `git log --oneline` and `git show {commit}`"""
    mended = WRITER.replace(
        "2. Read the commits since then with `git log --oneline`.", WRITER_STEP_2_MENDED
    )
    done = runs({**CHANGELOG, "changelog/agents/writer.md": mended}, ["/lane:up changelog"])
    expected = ("writer", 2, "run_only", ("git log --oneline", "git show {commit}"))
    assert all(expected in lanes_of(run) for run in done), [lanes_of(r) for r in done]


@pytest.mark.supports("test_the_main_conversations_own_work_before_and_after_a_run_goes_unchecked")
def test_up_isnt_run_for_a_request_to_write_the_changelog():
    """Given the walkthrough's `changelog` and Lane installed
    When the person asks `Write the CHANGELOG.md entries for the new commits.`
    Then on every run no `lay.py` command runs"""
    done = runs(CHANGELOG, ["Write the CHANGELOG.md entries for the new commits."])
    assert not any("lay.py" in command for run in done for command in run.commands)
