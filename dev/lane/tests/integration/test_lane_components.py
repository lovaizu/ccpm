"""The integration cases of each decision that a component of Lane's architecture alone makes, and
of each handoff between the parts with the data it passes, as the data model names it: the guard's
finding of the plugin's folder, its choice of the order that answers, its stop where an adapter
fails or gives out of its form, and the adapters and the check run in the conversation's folder;
the rule types' order of checking a mark; the reporters' refusal and their report for the subagent
that ran it; the route adapter's starts due from the routes; and the Rules out of form and the Run
that keeps two results. Each runs `log` and Lane through the double of Claude Code."""

from __future__ import annotations

import pytest
from lane_bench import (
    ENTRY,
    ORDER,
    UNBUILT,
    WORDS,
    Bench,
    ending,
    opened,
    prompt,
    reached,
    reviewed,
    started,
    steps_from_adapter,
    to_review,
    written,
)
from repo_files import write_files

pytestmark = UNBUILT


# guard


@pytest.mark.supports("guard")
def test_the_starts_due_come_at_the_main_conversations_next_event_after_the_skills_call(b: Bench):
    """Given a conversation with `log` and Lane
    When the person types /log:up 1.2.0, and the main conversation runs `git status`
    Then the command's answer gives no start due, as the transcript holds the skill's base
    directory only from the next event, and the main conversation reads the writer due at
    `git status`"""
    c = b.converse()
    assert "log:writer" not in c.type(f"/log:up {WORDS}").said
    assert "log:writer" in c.bash("git status").said


@pytest.mark.supports("guard", "route adapter")
def test_the_plugins_own_adapter_of_the_starts_due_answers_in_place_of_its_routes(b: Bench):
    """Given `log` with its routes and ORDER, its adapter of the starts due, and the repository
    holding the entry of 1.2.0
    When the person types /log:up 1.2.0, and the main conversation ends its turn
    Then the end is stopped with the reviewer due, as ORDER gives, and not the writer that the route
    after the command makes due"""
    b.adapter("starts_due.py", ORDER)
    write_files(b.repo, {"CHANGELOG.md": ENTRY})
    c = opened(b)
    answer = c.stop("Started.")
    assert answer.blocked
    assert "log:reviewer" in answer.said
    assert c.start("log:writer", prompt("log:writer"), "Write the entry")[1] is None


@pytest.mark.supports("guard")
def test_an_adapter_of_the_starts_due_that_fails_stops_with_the_adapter_and_what_it_said(
    b: Bench,
):
    """Given `log` whose adapter of the starts due exits 1 saying it found no version
    When the person types /log:up 1.2.0, and the main conversation ends its turn
    Then the end is stopped, naming the adapter and what it said, for the plugin's author to mend"""
    b.adapter("starts_due.py", "import sys\n\nsys.exit('no version found')\n")
    answer = opened(b).stop("Started.")
    assert answer.blocked
    assert "starts_due.py" in answer.said
    assert "no version found" in answer.said


@pytest.mark.supports("guard", "Starts due")
def test_starts_due_out_of_their_form_stop_naming_the_adapter(b: Bench):
    """Given `log` whose adapter of the starts due gives a start with no count
    When the person types /log:up 1.2.0, and the main conversation ends its turn
    Then the end is stopped, naming the adapter and the field its form takes"""
    b.adapter("starts_due.py", 'print(\'{"starts": [{"role": "log:writer"}]}\')\n')
    answer = opened(b).stop("Started.")
    assert answer.blocked
    assert "starts_due.py" in answer.said
    assert "count" in answer.said


@pytest.mark.supports("guard")
def test_a_start_of_a_role_with_no_steps_and_no_adapter_of_the_rules_is_stopped_saying_so(
    b: Bench,
):
    """Given `log` whose rules name the writer with no steps, and no adapter of the rules
    When the person types /log:up 1.2.0, and the main conversation starts the writer
    Then the start is stopped, naming lane/adapters/rules.py and the writer, for the plugin's author
    to add"""
    steps_from_adapter(b)
    b.adapter("rules.py", None)
    answer, agent = opened(b).start("log:writer", prompt("log:writer"), "Write the entry")
    assert agent is None
    assert "lane/adapters/rules.py" in answer.said
    assert "log:writer" in answer.said


@pytest.mark.supports("guard")
@pytest.mark.parametrize(
    "code, said",
    [
        ("import sys\n\nsys.exit('no prompt to read')\n", "no prompt to read"),
        ('print(\'{"steps": [{"name": "write"}]}\')\n', "rules"),
    ],
)
def test_an_adapter_of_the_rules_that_fails_or_gives_out_of_its_form_stops_the_start(
    b: Bench, code: str, said: str
):
    """Given `log` whose rules name the writer with no steps, and whose adapter of the rules exits
    1, or gives a step with no rules
    When the person types /log:up 1.2.0, and the main conversation starts the writer
    Then the start is stopped, naming rules.py and what's wrong"""
    steps_from_adapter(b)
    b.adapter("rules.py", code)
    answer, agent = opened(b).start("log:writer", prompt("log:writer"), "Write the entry")
    assert agent is None
    assert "rules.py" in answer.said
    assert said in answer.said


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


@pytest.mark.supports("guard", "S10")
def test_the_plugins_adapter_runs_in_the_worktree_the_conversation_works_in(b: Bench):
    """Given `log` deciding its order by ORDER, and a conversation in a worktree whose CHANGELOG.md
    holds the entry of 1.2.0, which the repository's top doesn't
    When the person types /log:up 1.2.0, and the main conversation ends its turn
    Then the end is stopped with the reviewer due, as ORDER read the worktree"""
    b.adapter("starts_due.py", ORDER)
    c = b.converse()
    c.enter_worktree("entry")
    write_files(c.cwd, {"CHANGELOG.md": ENTRY})
    c.type(f"/log:up {WORDS}")
    assert "log:reviewer" in c.stop("Picked up.").said


# rule types


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


# reporters


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


# route adapter


@pytest.mark.supports("route adapter", "Route", "Starts due")
def test_a_role_named_twice_in_a_route_is_due_twice_at_once(b: Bench):
    """Given the reviewer's `split`, whose route names the writer twice
    When the main conversation starts one writer and ends its turn, then starts another and ends
    its turn
    Then the first end is stopped with the writer due, and the second goes through"""
    c = to_review(b)
    reviewed(c, "split")
    started(c)
    answer = c.stop("One writer runs.")
    assert answer.blocked
    assert "log:writer" in answer.said
    started(c)
    assert not c.stop("Both writers run.").blocked


@pytest.mark.supports("route adapter", "Route")
def test_the_run_waits_while_the_start_its_route_made_due_runs(b: Bench):
    """Given the writer running, the one start that the route after the command makes due
    When the main conversation ends its turn, and then writes a file that its skill's step doesn't
    name
    Then the end goes through, and the write is stopped, as the run waits for the writer's
    result"""
    c = opened(b)
    started(c)
    assert not c.stop("The writer runs.").blocked
    assert c.write(None, b.at("notes.txt"), "x\n").blocked


@pytest.mark.supports("route adapter", "Route")
def test_a_result_that_no_route_goes_after_ends_the_run_once_no_start_runs(b: Bench):
    """Given `log` whose writer's step `write` names `unclear` among the results that end the
    start, which no route goes after, and the writer running
    When it reports `unclear` and ends, and the main conversation writes a file that no step names
    Then the write goes through, as the run ended"""
    ending(b, 0, "unclear")
    c = opened(b)
    writer = started(c)
    writer.bash("lane-result unclear")
    reached(writer)
    assert not c.write(None, b.at("notes.txt"), "x\n").blocked


# Rules, and Run


@pytest.mark.supports("Rules")
def test_a_rule_of_a_type_that_lane_lacks_stops_saying_what_to_mend(b: Bench):
    """Given `log` whose writer's step holds a rule of the type `size`
    When the person types /log:up 1.2.0, and the main conversation ends its turn
    Then the end is stopped, naming lane/rules.json and the rule's type"""
    rules = {
        "roles": {"log:writer": {"steps": [{"name": "write", "rules": [{"type": "size"}]}]}},
        "routes": [{"after": {"command": "log:up"}, "start": ["log:writer"]}],
    }
    b.rules(rules)
    answer = opened(b).stop("Started.")
    assert answer.blocked
    assert "lane/rules.json" in answer.said
    assert "size" in answer.said


@pytest.mark.supports("Run")
def test_the_results_of_two_subagents_are_both_kept(b: Bench):
    """Given two writers running after the reviewer's `split`
    When each keeps each step and reports `written`, and then each ends
    Then both ends go through, as the run's record loses neither result"""
    c = to_review(b)
    reviewed(c, "split")
    first, second = started(c), started(c)
    written(first)
    written(second)
    assert not first.end("Done.")[0].blocked
    assert not second.end("Done.")[0].blocked
