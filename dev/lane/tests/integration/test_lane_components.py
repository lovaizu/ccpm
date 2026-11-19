"""The integration cases of each decision that a component of Lane's architecture alone makes, and
of each handoff between the parts with the data it passes, as the data model names it: the guard's
finding of the plugin's folder, its stop where an adapter fails, the rule types' order of checking a
mark, the reporters' refusal and their report for the subagent that ran them, the Rules out of
form, the Run that keeps two results, and the adapters and the check run in the conversation's
folder. Each runs `log` and Lane through the double of Claude Code."""

from __future__ import annotations

import pytest
from lane_bench import UNREPORTED, WORDS, Bench, opened, reviewed, started, text, to_review, written

pytestmark = UNREPORTED


@pytest.mark.supports("guard")
def test_the_starts_due_come_at_the_main_conversations_next_event_after_the_skills_call(b: Bench):
    """Given a conversation with `log` and Lane
    When the person types /log:up 1.2.0, and the main conversation runs `git status`
    Then the command's answer holds no start, as the transcript holds the skill's base directory
    only from the next event, and the main conversation reads the writer due at `git status`"""
    c = b.converse()
    assert text("log:writer") not in c.type(f"/log:up {WORDS}").said
    assert text("log:writer") in c.bash("git status").said


@pytest.mark.supports("guard")
def test_a_start_adapter_that_fails_stops_with_the_adapter_and_what_it_said(b: Bench):
    """Given `log` whose start adapter exits 1 saying it found no version
    When the person types /log:up 1.2.0, and the main conversation ends its turn
    Then the end is stopped, naming the adapter and what it said"""
    b.adapter("start.py", "import sys\n\nsys.exit('no version found')\n")
    answer = opened(b).stop("Started.")
    assert answer.blocked
    assert "start.py" in answer.said
    assert "no version found" in answer.said


@pytest.mark.supports("guard")
def test_a_start_adapters_output_out_of_its_form_stops_naming_the_adapter(b: Bench):
    """Given `log` whose start adapter prints an object with no `text`
    When the person types /log:up 1.2.0, and the main conversation ends its turn
    Then the end is stopped, naming the adapter and the field its form takes"""
    b.adapter("start.py", 'print(\'{"words": "Write it."}\')\n')
    answer = opened(b).stop("Started.")
    assert answer.blocked
    assert "start.py" in answer.said
    assert "text" in answer.said


@pytest.mark.supports("rule types", "S5", "S3")
def test_a_mark_is_checked_for_the_step_due_before_the_files_it_reads_whole(b: Bench):
    """Given the writer running, its step `write` not done, CHANGELOG.md never read
    When it reports the step `report` done
    Then it reads the sentence naming `write` as the step due, and not CHANGELOG.md"""
    said = started(opened(b)).bash("lane-step report").said
    assert "write" in said
    assert "CHANGELOG.md" not in said


@pytest.mark.supports("rule types", "S3", "S6")
def test_a_mark_is_checked_for_the_files_it_reads_whole_before_its_items(b: Bench):
    """Given the writer running, NOTES.md never read, no item done
    When it reports the step `write` done
    Then it reads the sentence naming NOTES.md, and no item"""
    said = started(opened(b)).bash("lane-step write").said
    assert "NOTES.md" in said
    assert "dated" not in said


@pytest.mark.supports("reporters")
def test_a_reporter_given_words_that_dont_fit_its_kind_exits_2_with_what_it_takes(b: Bench):
    """Given the writer running
    When it runs `lane-item write`, with no item
    Then the reporter exits 2, saying what `lane-item` takes"""
    answer = started(opened(b)).bash("lane-item write")
    assert answer.exit_code == 2
    assert "lane-item" in answer.output


@pytest.mark.supports("reporters", "Run")
def test_a_reporters_result_counts_for_the_subagent_that_ran_it(b: Bench):
    """Given two writers running after the reviewer's `split`
    When the second reports `written`, and the first ends
    Then the first's end is stopped, as the result is the second's"""
    c = to_review(b)
    reviewed(c, "split")
    first, second = started(c), started(c)
    second.bash("lane-result written")
    assert first.end("Done.")[0].blocked


@pytest.mark.supports("Run")
def test_the_results_of_two_subagents_are_both_kept(b: Bench):
    """Given two writers running after the reviewer's `split`
    When each reports `written`, and then each ends
    Then both ends go through, as the run's record loses neither result"""
    c = to_review(b)
    reviewed(c, "split")
    first, second = started(c), started(c)
    first.bash("lane-result written")
    second.bash("lane-result written")
    assert not first.end("Done.")[0].blocked
    assert not second.end("Done.")[0].blocked


@pytest.mark.supports("Rules")
def test_a_rule_of_a_type_that_lane_lacks_stops_saying_what_to_mend(b: Bench):
    """Given `log` whose writer's step holds a rule of the type `size`
    When the person types /log:up 1.2.0, and the main conversation ends its turn
    Then the end is stopped, naming lane/rules.json and the rule's place in it"""
    rules = {
        "roles": {"log:writer": {"steps": [{"name": "write", "rules": [{"type": "size"}]}]}},
        "routes": [{"after": {"command": "log:up"}, "start": ["log:writer"]}],
    }
    b.rules(rules)
    answer = opened(b).stop("Started.")
    assert answer.blocked
    assert "lane/rules.json" in answer.said
    assert "size" in answer.said


@pytest.mark.supports("guard", "S8")
def test_the_plugins_check_runs_in_the_worktree_the_conversation_works_in(b: Bench):
    """Given the person typed /log:up 1.2.0 and the main conversation entered a worktree
    When the writer keeps each step there, writing the worktree's CHANGELOG.md, and ends
    Then the end goes through, as the check reads the worktree, though the repository's top holds
    no CHANGELOG.md"""
    c = opened(b)
    c.enter_worktree("entry")
    writer = started(c)
    written(writer)
    assert not writer.end("Done.")[0].blocked


@pytest.mark.supports("guard", "Kept results")
def test_the_kept_adapter_runs_in_the_worktree_the_conversation_works_in(b: Bench):
    """Given a new conversation in a worktree whose .log/ keeps the writer's `written` for 1.2.0,
    which the repository's top doesn't
    When the person types /log:up 1.2.0, and the main conversation ends its turn
    Then the end is stopped with the reviewer due"""
    c = b.converse()
    c.enter_worktree("entry")
    b.kept(WORDS, [{"role": "log:writer", "result": "written"}], folder=c.cwd)
    c.type(f"/log:up {WORDS}")
    assert text("log:reviewer") in c.stop("Picked up.").said
