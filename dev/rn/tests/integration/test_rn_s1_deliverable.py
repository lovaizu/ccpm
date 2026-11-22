"""The integration cases of S1, a deliverable made in rounds: each path through its sequence, from
the user's request to the last sign-off, on the bench's own request for invoicer. Each runs rn
and Lane through the double of Claude Code and the double of gh, with a double of each prompt's
work, as rn's Test strategy says under Integration testing."""

from __future__ import annotations

import json
import os

import pytest
import rn_files
from claude_code import Conversation
from gh import gh_double
from repo_files import git
from rn_bench import (
    CHANGELOG,
    COMMAND_TEXT,
    Bench,
    apart_tree,
    command_signed,
    confirmed,
    cut,
    cut_of,
    decided_command,
    ended,
    evaluated,
    evaluator_started,
    generated,
    heard,
    held,
    items,
    judged_command,
    listed,
    made_command,
    marked,
    next_round,
    planned_tree,
    pointed,
    put_up,
    put_up_plan,
    ran,
    reached,
    requested,
    sent_back,
    short_twice,
    signed,
    signed_apart,
    signed_plan,
    started,
    stopped,
    taken,
    to_plan_signoff,
    touched_items,
    written_tree,
)
from rn_files import COMMAND, GOAL, GUIDE
from rn_runs import branch_run


def log(b: Bench, ref: str) -> list[str]:
    """Each commit message's subject on the ref of the user's repository, newest first."""
    return git(b.repo, "log", "--format=%s", ref).splitlines()


@pytest.mark.supports("S1", "Design tree")
def test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put(b: Bench):
    """Given invoicer's repository on main, with a remote
    When the user types /rn:on, and, asked what they want to make, the walkthrough's words, and the
    orchestrator makes the run by repository.py new with the goal as put and commits it
    Then the run's worktree has the branch rn-<name> checked out from main's head, its design tree
    holds the goal by reasoning, the plan as its one deliverable, and no work, committed with the
    ground as its message, and the user's own branch and files are as they were"""
    head = git(b.repo, "rev-parse", "main").strip()
    requested(b)
    branch = f"rn-{b.name()}"
    assert git(b.worktree, "branch", "--show-current").strip() == branch
    assert git(b.repo, "merge-base", "main", branch).strip() == head
    assert b.tree() == rn_files.tree(
        [rn_files.plan(b.name(), good=False)], goal=GOAL, by="reasoning"
    )
    assert log(b, branch)[0] == "The goal as put."
    assert git(b.repo, "branch", "--show-current").strip() == "main"
    assert git(b.repo, "rev-parse", "main").strip() == head
    assert git(b.repo, "status", "--porcelain").strip() == ""


@pytest.mark.supports("S1", "Design tree")
def test_an_answer_after_the_request_goes_into_the_run_the_request_made(b: Bench):
    """Given invoicer's repository with a paused run 20261101-old, newest by its last commit, whose
    plan waits on its sign-off
    When the user types /rn:on, then the walkthrough's words, and the orchestrator makes the run by
    repository.py new and keeps the shared steps; and the user confirms the goal, and the
    orchestrator writes the plan into the run's design tree and keeps the shared steps
    Then Lane lets each move through, and the run made holds the plan, 20261101-old's tree as it
    was"""
    old = "20261101-old"
    waiting = rn_files.tree([rn_files.plan(old, good=False)], goal=GOAL, by="reasoning")
    folder = branch_run(b.repo, old, waiting, "2099-01-01T09:00:00")
    c = requested(b)
    confirmed(b, c)
    assert b.tree() == planned_tree(b, answered=False)
    assert rn_files.read_json(os.path.join(folder, "design-tree.json")) == waiting


@pytest.mark.supports("S1")
def test_rn_on_asks_what_to_make_writing_nothing_and_running_no_command(b: Bench):
    """Given invoicer's repository with no run of rn
    When the user types /rn:on, and the orchestrator writes a file, runs repository.py new, marks
    `hear` done, and ends its turn asking what they want to make
    Then Lane stops the write and the command at the step `hear`, the end goes through, and the
    repository has no worktree of rn"""
    c = b.converse()
    typed = c.type("/rn:on")
    assert "domain/orchestrator.md" in typed.output
    wrote = c.write(None, b.at("NOTES.md"), "A goal.\n")
    assert wrote.blocked and "`hear`" in wrote.said
    answer = c.bash(b.script("repository", "new", rn_files.WORDS, GOAL, *rn_files.LANGUAGES))
    assert answer.blocked and "`hear`" in answer.said
    marked(c, "hear")
    ended(c, "What do you want to make?")
    assert not os.path.exists(b.at(".claude/worktrees"))
    assert not os.path.exists(b.at("NOTES.md"))


@pytest.mark.supports("S1")
def test_a_new_request_with_no_origin_ends_its_turn_on_blocked(b: Bench):
    """Given invoicer's repository with no remote origin
    When the user types /rn:on, then the walkthrough's words, the orchestrator runs repository.py
    new, gives blocked by lane-result, as nothing else can move, and ends its turn with the
    refusal
    Then repository.py new gives 1 saying that origin's HEAD names no default branch, the turn
    ends, Lane stopping no move, and the repository has no worktree of rn"""
    git(b.repo, "remote", "remove", "origin")
    c = heard(b)
    c.type(rn_files.WORDS)
    refused = c.bash(b.script("repository", "new", rn_files.WORDS, GOAL, *rn_files.LANGUAGES))
    assert not refused.blocked, refused.said
    assert refused.exit_code == 1
    assert "origin's HEAD names no default branch" in refused.output
    given = c.bash("lane-result blocked")
    assert not given.blocked, given.said
    ended(c, refused.output)
    assert not os.path.exists(b.at(".claude/worktrees"))


@pytest.mark.supports("S1")
def test_a_turn_with_the_plan_open_starts_no_role(b: Bench):
    """Given a run whose goal the orchestrator put to the user, the plan open
    When the orchestrator starts rn:generator
    Then Lane stops the start, as no start of rn's subagents is due"""
    c = requested(b)
    answer, agent = c.start("rn:generator", "Make the command.", "Run rn:generator")
    assert agent is None
    assert "No start of rn's subagents is due now." in answer.said


@pytest.mark.supports("S1", "Design tree")
def test_a_point_only_the_user_can_settle_is_kept_open_and_their_answer_written_by_user(b: Bench):
    """Given a run whose goal the user confirmed
    When the orchestrator keeps the tax rate's point as an open decision of the command's N1 and
    commits it, and the user answers it
    Then the committed tree holds the point open, and then the answer as its decision by user"""
    c = requested(b)
    confirmed(b, c)
    branch = f"rn-{b.name()}"
    committed = json.loads(git(b.worktree, "show", f"{branch}:.rn/{b.name()}/design-tree.json"))
    asked = committed["deliverables"][1]["necessary_conditions"][0]["decisions"]
    assert asked == [rn_files.decision(rn_files.TAX_ABOUT, None)]
    put_up_plan(b, c)
    committed = json.loads(git(b.worktree, "show", f"{branch}:.rn/{b.name()}/design-tree.json"))
    answered = committed["deliverables"][1]["necessary_conditions"][0]["decisions"]
    assert answered == [rn_files.decision(rn_files.TAX_ABOUT, rn_files.TAX_ANSWER, "user")]


@pytest.mark.supports("S1", "Design tree")
def test_a_point_the_orchestrator_settles_is_committed_with_its_ground_as_the_message(b: Bench):
    """Given a run whose goal the user confirmed
    When the orchestrator settles a point of the guide's N1 by reasoning in its review and commits
    it with its ground
    Then the work's branch's last commit holds the decision, its message the ground word for
    word"""
    c = requested(b)
    confirmed(b, c)
    c.type("The guide is for the accounting team.")
    settled = rn_files.decision("its people", "The accounting team, at a terminal.", "reasoning")
    taken(b, c, held(b, GUIDE, [], {"N1": [settled]}), "The README names its people.")
    branch = f"rn-{b.name()}"
    assert log(b, branch)[0] == "The README names its people."
    committed = json.loads(git(b.worktree, "show", f"{branch}:.rn/{b.name()}/design-tree.json"))
    assert settled in committed["deliverables"][2]["necessary_conditions"][0]["decisions"]


@pytest.mark.supports("S1", "Design tree")
def test_each_node_a_change_touches_is_read_again_before_the_commit(b: Bench):
    """Given a run whose goal the user confirmed, and the orchestrator's change to the command's
    path written in its review
    When it reports the step `touched` done before any of the nodes that tree.py touched prints
    Then Lane stops the mark, naming the guide, whose inputs name the command, among the items"""
    c = requested(b)
    confirmed(b, c)
    c.type("Name the command invoicer/cli.py.")
    changed = b.tree()
    changed["deliverables"][1]["path"] = "invoicer/cli.py"
    answer = written_tree(b, c, changed)
    assert not answer.blocked, answer.said
    marked(c, "take")
    marked(c, "review")
    nodes = ran(c, b.script("tree", "touched", b.run)).split()
    answer = c.bash("lane-step touched")
    assert "/deliverables/2" in nodes
    assert answer.said == (
        f"You're at the step `touched` of rn:on, whose checklist isn't done: {listed(nodes)}.\n"
        "Do each and mark it done with lane-item touched <item> first."
    )


@pytest.mark.supports("S1", "Design tree")
def test_the_plan_waiting_for_signoff_is_put_up_in_the_runs_pull_request(b: Bench):
    """Given a run whose plan has each condition good
    When the orchestrator puts it up by repository.py put-up
    Then it prints the pull request's changes, http://github.com/owner/repo/pull/1/files, the
    remote's branch rn-<name> holds the run's design tree, and gh was asked to open the pull
    request once"""
    c = requested(b)
    confirmed(b, c)
    url = put_up_plan(b, c)
    assert url == "http://github.com/owner/repo/pull/1/files"
    assert f".rn/{b.name()}/design-tree.json" in b.branch_files(f"rn-{b.name()}")
    assert [each[:3] for each in b.asked_gh()].count(["gh", "pr", "create"]) == 1


@pytest.mark.supports("S1", "Design tree", "Cut")
def test_a_signoff_of_the_plan_makes_it_done_and_starts_the_generator_of_each_deliverable_due(
    b: Bench,
):
    """Given a run whose plan is put up
    When the user types /rn:ty, the orchestrator records it, and writes the command's Cut
    Then the plan is done in its one line, the Cut lies in the command's Round content-1, Lane lets
    the command's generator start, and a second generator, for the guide that rests on the command,
    is stopped as not due"""
    c, _ = signed_plan(b)
    assert b.tree()["deliverables"][0] == rn_files.done_node(
        GOAL, rn_files.plan_path(b.name()), "design-tree"
    )
    first = rn_files.round_of(b.folder, COMMAND, "content", 1)
    assert os.path.isfile(os.path.join(first, "generator-cut.json"))
    answer, agent = c.start("rn:generator", "Make the guide.", "Run rn:generator")
    assert agent is None
    assert "No start of rn's subagents is due now." in answer.said


@pytest.mark.supports("S1", "Design tree")
def test_a_send_back_of_the_plan_leaves_it_open_and_starts_no_role(b: Bench):
    """Given a run whose plan is put up
    When the user types /rn:gm with what to change, and the orchestrator keeps the shared steps
    and ends its turn
    Then the plan stays open, a start of rn:generator is stopped as not due, and the turn ends,
    Lane stopping no move but the start"""
    c = to_plan_signoff(b)
    c.type("/rn:gm the guide is for the accounting team alone")
    taken(b, c, ground="The user sends the plan back.")
    assert b.tree()["deliverables"][0]["status"] == "open"
    answer, agent = c.start("rn:generator", "Make the command.", "Run rn:generator")
    assert agent is None
    assert "No start of rn's subagents is due now." in answer.said
    ended(c, "The plan, for your sign-off:\n  1. ...")


@pytest.mark.supports("S1", "Round", "Cut")
def test_a_generators_point_reaches_the_user_and_their_answer_resumes_it(b: Bench):
    """Given a run whose command's generator runs
    When it ends with a point, the orchestrator keeps the point as an open decision of N1, the user
    answers, and the orchestrator writes the answer as its decision by user and writes the Cut
    Then the generator's end reads `rn:generator gave point.`, the Cut is the same Round's,
    content-1, holding the answer by user in the deliverable's N1, SendMessage resumes the
    generator, and each turn ends, Lane stopping no move"""
    c, generator = signed_plan(b)
    notified = pointed(b, c, generator, "Should a line's quantity default to 1?")
    assert "rn:generator gave point." in notified.said
    about = "a line's quantity"
    taken(
        b,
        c,
        held(b, COMMAND, [], {"N1": [rn_files.decision(about, None)]}),
        "The generator's point.",
    )
    ended(c, "A question that's yours:\n  Should a line's quantity default to 1?")
    c.type("yes, 1")
    answer = rn_files.decision(about, "yes, 1", "user")
    tree = b.tree()
    tree["deliverables"][1]["necessary_conditions"][0]["decisions"][-1] = answer
    cut_path = taken(
        b, c, tree, "The user's answer.", [b.script("tree", "cut", b.run, "generator", COMMAND)]
    )[0].strip()
    first = rn_files.round_of(b.folder, COMMAND, "content", 1)
    assert os.path.join(b.repo, cut_path) == os.path.join(first, "generator-cut.json")
    given = rn_files.read_json(os.path.join(b.repo, cut_path))
    assert answer in given["deliverable"]["necessary_conditions"][0]["decisions"]
    resumed = c.resume(generator, "yes, 1")
    assert not resumed.blocked, resumed.said
    ended(c, f'Making "{rn_files.COMMAND_NAME}".')


@pytest.mark.supports("S1", "Round", "Cut")
def test_a_generators_made_makes_the_evaluator_due_in_the_same_round(b: Bench):
    """Given a run whose command's generator runs
    When it keeps its steps and ends with made, and the orchestrator writes the evaluator's Cut
    Then the end reads `rn:generator gave made. Due: rn:evaluator.`, and the evaluator's Cut lies in
    Round content-1 beside the generator's result"""
    c, notified = made_command(b)
    assert "rn:generator gave made. Due: rn:evaluator." in notified.said
    cut_path = taken(b, c, moves=[b.script("tree", "cut", b.run, "evaluator", COMMAND)])[0].strip()
    first = rn_files.round_of(b.folder, COMMAND, "content", 1)
    assert os.path.join(b.repo, cut_path) == os.path.join(first, "evaluator-cut.json")
    assert os.path.isfile(os.path.join(first, "generator.json"))
    assert started(c, "rn:evaluator", cut_path) is not None


@pytest.mark.supports("S1", "Round", "Cut")
def test_an_evaluators_findings_go_to_the_next_rounds_generator_as_given(b: Bench):
    """Given a run whose command's evaluator judged Round content-1, N1 with more
    When the orchestrator holds N2 and N3 good, N1 not, and writes the generator's Cut
    Then the Cut lies in Round content-2, its findings the evaluator's good and more of content-1
    of N1 alone, the one condition the tree still holds not good, word for word, and its
    last_good the generator's good of content-1"""
    c, notified = judged_command(
        b, {"N1": "The accountant prints an invoice with a comma in a line."}
    )
    assert "rn:evaluator gave judged. Due: rn:generator." in notified.said
    cut_path, _ = next_round(b, c, COMMAND, ["N2", "N3"])
    first = rn_files.round_of(b.folder, COMMAND, "content", 1)
    second = rn_files.round_of(b.folder, COMMAND, "content", 2)
    assert os.path.join(b.repo, cut_path) == os.path.join(second, "generator-cut.json")
    given = rn_files.read_json(os.path.join(b.repo, cut_path))
    judged = rn_files.read_json(os.path.join(first, "evaluator.json"))
    made = rn_files.read_json(os.path.join(first, "generator.json"))
    short = {"N1"}
    assert given["findings"] == {
        "good": [each for each in judged["good"] if each["condition"] in short],
        "more": [each for each in judged["more"] if each["condition"] in short],
    }
    assert given["last_good"] == made["good"]
    assert (given["stage"], given["number"]) == ("content", 2)


@pytest.mark.supports("S1", "Design tree", "Cut")
def test_a_finding_the_people_would_never_meet_is_dropped_by_holding_its_condition_good(b: Bench):
    """Given a run whose command's evaluator judged Round content-1, N1 with more
    When the orchestrator holds every condition good, N1 among them, and commits
    Then the command waits for the user's sign-off, and repository.py put-up puts it up"""
    c, _ = judged_command(b, {"N1": "The accountant prints an invoice in Klingon."})
    url = put_up(b, c, COMMAND, rn_files.conditions("light"))
    assert url == "http://github.com/owner/repo/pull/1/files"
    answer = c.start("rn:generator", "Make the command again.", "Run rn:generator")[0]
    assert "No start of rn's subagents is due now." in answer.said


@pytest.mark.supports("S1", "Design tree", "Round")
def test_a_finding_left_past_two_content_rounds_goes_to_the_user_as_a_proposal(b: Bench):
    """Given a run whose command's N1 the evaluator found short in Rounds content-1 and content-2,
    its second evaluator's end reaching the main conversation
    When the orchestrator keeps the finding as an open decision of N1, puts the command up, and
    the user signs it off
    Then the put-up prints the pull request's changes, the turn ends, Lane stopping no move, and
    the command is done once signed off"""
    c = short_twice(b)
    proposal = rn_files.decision("a comma in a line", None)
    url = taken(
        b,
        c,
        held(b, COMMAND, ["N2", "N3"], {"N1": [proposal]}),
        "Left past its Rounds.",
        [b.script("repository", "put-up", b.run, COMMAND)],
    )[0].strip()
    assert url == "http://github.com/owner/repo/pull/1/files"
    ended(c, "Proposals left past its Rounds:\n  - a comma in a line")
    signed(b, c)
    assert rn_files.done_node(rn_files.COMMAND_NAME, COMMAND, "light") in b.tree()["deliverables"]


@pytest.mark.supports("S1", "Best practice", "Cut")
def test_a_deliverable_with_each_condition_good_is_refactored_by_its_refactor_best_practice(
    b: Bench,
):
    """Given a run whose guide, of the kind readme, the evaluator judged good on each condition in
    Round content-1
    When the orchestrator holds each condition good and writes the generator's Cut
    Then the Cut lies in Round refactor-2, its stage refactor, number 2, the guide's second Round,
    and its best practice rn's refactor-doc"""
    c, generator = command_signed(b)
    generated(b, c, generator)
    _, evaluator = next_round(b, c, GUIDE, [], "evaluator")
    evaluated(b, c, evaluator)
    cut_path, _ = next_round(b, c, GUIDE, rn_files.conditions("readme"))
    refactor = rn_files.round_of(b.folder, GUIDE, "refactor", 2)
    assert os.path.join(b.repo, cut_path) == os.path.join(refactor, "generator-cut.json")
    given = rn_files.read_json(os.path.join(b.repo, cut_path))
    assert (given["stage"], given["number"]) == ("refactor", 2)
    assert os.path.normpath(os.path.join(b.repo, given["best_practice"])) == os.path.join(
        b.rn, "domain", "best-practices", "refactor-doc"
    )


@pytest.mark.supports("S1", "Round", "Cut")
def test_the_refactoring_generators_made_waits_on_the_signoff_with_no_evaluator(b: Bench):
    """Given a run whose guide, of the kind readme, the evaluator judged good on each condition in
    Round content-1, and whose orchestrator started a new generator with the Cut of Round
    refactor-2
    When that generator refactors the guide by rn's refactor-doc, runs the repository's tests as
    its developers run them, runs repository.py checks on its files, and ends with made, and the
    orchestrator holds each condition good, puts the guide up, and writes the evaluator's Cut
    Then Lane lets the tests through, the end reads `rn:generator gave made.` with no role due, its
    result lies in Round refactor-2, repository.py put-up puts the guide up, and tree.py cut gives
    1 saying the guide waits on the user's sign-off, writing no evaluator's Cut"""
    c, generator = command_signed(b)
    generated(b, c, generator)
    _, evaluator = next_round(b, c, GUIDE, [], "evaluator")
    evaluated(b, c, evaluator)
    _, refactoring = next_round(b, c, GUIDE, rn_files.conditions("readme"))
    assert refactoring is not generator
    notified = generated(b, c, refactoring)
    assert "rn:generator gave made." in notified.said
    assert "Due:" not in notified.said
    refactor = rn_files.round_of(b.folder, GUIDE, "refactor", 2)
    assert os.path.isfile(os.path.join(refactor, "generator.json"))
    good = held(b, GUIDE, rn_files.conditions("readme"))
    url = taken(b, c, good, "Refactored.", [b.script("repository", "put-up", b.run, GUIDE)])[0]
    assert url.strip() == "http://github.com/owner/repo/pull/1/files"
    refused = c.bash(b.script("tree", "cut", b.run, "evaluator", GUIDE))
    assert refused.exit_code == 1
    assert "waits on the user's sign-off, not on its evaluator" in refused.output
    assert not os.path.exists(os.path.join(refactor, "evaluator-cut.json"))
    ended(c, f"For your sign-off. Changes: {url.strip()}")


def refactored(b: Bench) -> Conversation:
    """A conversation whose guide the evaluator judged good in Round content-1, a new generator
    refactored in Round refactor-2, and the orchestrator put up for the user's sign-off."""
    c, generator = command_signed(b)
    generated(b, c, generator)
    _, evaluator = next_round(b, c, GUIDE, [], "evaluator")
    evaluated(b, c, evaluator)
    _, refactoring = next_round(b, c, GUIDE, rn_files.conditions("readme"))
    generated(b, c, refactoring)
    put_up(b, c, GUIDE, rn_files.conditions("readme"))
    return c


@pytest.mark.supports("S1", "Design tree", "Round")
def test_a_send_back_after_the_refactor_round_is_remade_in_a_new_content_round(b: Bench):
    """Given a run whose guide was judged good in Round content-1, refactored in refactor-2, and
    put up for the user's sign-off
    When the user types /rn:gm with what to change, and the orchestrator writes it as a decision
    by user of N1, holds N1 not good, and writes the generator's Cut
    Then the Cut lies in Round content-3, the last Round, its stage content, its deliverable holding
    the user's words, and the generator starts"""
    c = refactored(b)
    words = "the guide is for the accounting team alone"
    cut_path = sent_back(b, c, GUIDE, rn_files.conditions("readme"), words)
    content = rn_files.round_of(b.folder, GUIDE, "content", 3)
    assert os.path.join(b.repo, cut_path) == os.path.join(content, "generator-cut.json")
    given = rn_files.read_json(os.path.join(b.repo, cut_path))
    assert (given["stage"], given["number"]) == ("content", 3)
    n1 = given["deliverable"]["necessary_conditions"][0]
    assert (n1["id"], n1["good"]) == ("N1", False)
    assert rn_files.decision(words, words, "user") in n1["decisions"]
    assert started(c, "rn:generator", cut_path) is not None


@pytest.mark.supports("S1", "Design tree", "Round")
def test_a_send_back_after_the_contents_last_round_is_remade_in_a_new_content_round(b: Bench):
    """Given a run whose command, of the kind light, which has no refactoring, the evaluator judged
    good in Round content-1, put up for the user's sign-off
    When the user types /rn:gm with what to change, and the orchestrator writes it as a decision
    by user of N1, holds N1 not good, and writes the generator's Cut
    Then the Cut lies in Round content-2, its stage content, and the generator starts"""
    c, _ = judged_command(b)
    put_up(b, c, COMMAND, rn_files.conditions("light"))
    words = "print the total on its own last line"
    cut_path = sent_back(b, c, COMMAND, rn_files.conditions("light"), words)
    content = rn_files.round_of(b.folder, COMMAND, "content", 2)
    assert os.path.join(b.repo, cut_path) == os.path.join(content, "generator-cut.json")
    given = rn_files.read_json(os.path.join(b.repo, cut_path))
    assert (given["stage"], given["number"]) == ("content", 2)
    assert started(c, "rn:generator", cut_path) is not None


@pytest.mark.supports("S1", "Design tree")
def test_a_deliverable_signed_off_is_done_and_the_one_resting_on_it_starts(b: Bench):
    """Given a run whose command the evaluator judged good in Round content-1, put up
    When the user signs it off, and the orchestrator writes the guide's Cut
    Then the command is done in its one line, its item of the work gone, and the guide's generator
    starts with a Cut whose inputs name the command's path in the run's worktree"""
    c, generator = command_signed(b)
    tree = b.tree()
    assert rn_files.done_node(rn_files.COMMAND_NAME, COMMAND, "light") in tree["deliverables"]
    assert tree["work"] == [rn_files.work("make", GUIDE)]
    given = rn_files.read_json(os.path.join(c.cwd, generator.start_use["tool_input"]["prompt"]))
    assert [os.path.normpath(os.path.join(b.repo, each)) for each in given["inputs"]] == [
        os.path.join(b.worktree, COMMAND)
    ]


@pytest.mark.supports("S1")
def test_the_last_signoff_ends_the_run_with_each_deliverable_on_the_pull_requests_branch(b: Bench):
    """Given a run whose guide the evaluator judged good in its Round of content, which a new
    generator refactored, and put up
    When the user signs the guide off
    Then each deliverable of the tree is done, the remote's branch holds the command and the guide,
    and the orchestrator's turn ends with no start due"""
    c, generator = command_signed(b)
    generated(b, c, generator)
    _, evaluator = next_round(b, c, GUIDE, [], "evaluator")
    evaluated(b, c, evaluator)
    _, generator = next_round(b, c, GUIDE, rn_files.conditions("readme"))
    generated(b, c, generator)
    put_up(b, c, GUIDE, rn_files.conditions("readme"))
    signed(b, c)
    assert all(each["status"] == "done" for each in b.tree()["deliverables"])
    files = b.branch_files(f"rn-{b.name()}")
    assert COMMAND in files and GUIDE in files
    stopped = c.stop(
        "Done. The pull request is ready for your merge: http://github.com/owner/repo/pull/1"
    )
    assert not stopped.blocked, stopped.said


@pytest.mark.supports("S1", "Design tree")
def test_the_pull_request_stays_a_draft_while_a_deliverable_is_left_open(b: Bench):
    """Given a run whose plan and command were put up and signed off, the guide still open
    When the guide's generator starts
    Then the commit of the command's sign-off is the branch's last, origin's branch doesn't hold
    it, and gh was asked to open the pull request once, as a draft, and never to mark it ready"""
    command_signed(b)
    branch = f"rn-{b.name()}"
    assert log(b, branch)[0] == "The user signs it off."
    assert git(b.origin, "rev-parse", branch) != git(b.worktree, "rev-parse", "HEAD")
    asked = b.asked_gh()
    created = [each for each in asked if each[1:3] == ["pr", "create"]]
    assert len(created) == 1
    assert "--draft" in created[0], "the pull request opens as a draft"
    assert [each for each in asked if each[1:3] == ["pr", "ready"]] == []


@pytest.mark.supports("S1", "Design tree")
def test_the_last_signoffs_commit_is_pushed_before_the_pull_request_is_marked_ready(b: Bench):
    """Given a run whose plan and command are done, and whose guide was judged good, refactored,
    and put up
    When the user signs the guide off, and the orchestrator records it and commits the change
    Then origin's branch holds the commit of the sign-off, its tree with each deliverable done,
    and gh was asked once to mark the work's branch's pull request ready, after it opened it"""
    c, generator = command_signed(b)
    generated(b, c, generator)
    _, evaluator = next_round(b, c, GUIDE, [], "evaluator")
    evaluated(b, c, evaluator)
    _, generator = next_round(b, c, GUIDE, rn_files.conditions("readme"))
    generated(b, c, generator)
    put_up(b, c, GUIDE, rn_files.conditions("readme"))
    signed(b, c)
    branch = f"rn-{b.name()}"
    assert git(b.origin, "rev-parse", branch) == git(b.worktree, "rev-parse", "HEAD")
    assert git(b.origin, "log", "-1", "--format=%s", branch).strip() == "The user signs it off."
    pushed = json.loads(git(b.origin, "show", f"{branch}:.rn/{b.name()}/design-tree.json"))
    assert [each["status"] for each in pushed["deliverables"]] == ["done", "done", "done"]
    asked = [each for each in b.asked_gh() if each[1:3] in (["pr", "create"], ["pr", "ready"])]
    assert [each[2] for each in asked] == ["create", "ready"]
    assert asked[1] == ["gh", "pr", "ready", branch]


@pytest.mark.supports("S1", "Round")
def test_a_resumed_generator_after_its_answer_ends_with_made_and_the_evaluator_is_due(b: Bench):
    """Given a run whose command's generator gave a point that the user answered, and that the
    orchestrator resumed with the answer
    When the generator keeps its steps and ends with made
    Then its end reads `rn:generator gave made. Due: rn:evaluator.`"""
    c, generator = signed_plan(b)
    pointed(b, c, generator, "Should a line's quantity default to 1?")
    about = "a line's quantity"
    taken(
        b,
        c,
        held(b, COMMAND, [], {"N1": [rn_files.decision(about, "yes, 1", "user")]}),
        "Answered.",
    )
    cut(b, c, "generator", COMMAND)
    c.resume(generator, "yes, 1")
    notified = generated(b, c, generator)
    assert "rn:generator gave made. Due: rn:evaluator." in notified.said


@pytest.mark.supports("S1", "Round")
def test_an_evaluator_started_reads_only_its_cut_and_tries_in_the_peoples_folder(b: Bench):
    """Given a run whose command's evaluator started with its Cut
    When it keeps its steps and ends with judged
    Then its end reads `rn:evaluator gave judged.`, and its answers lie in Round content-1"""
    c, evaluator = evaluator_started(b)
    notified = evaluated(b, c, evaluator)
    assert "rn:evaluator gave judged." in notified.said
    first = rn_files.round_of(b.folder, COMMAND, "content", 1)
    assert rn_files.read_json(os.path.join(first, "evaluator.json"))["result"] == "judged"


@pytest.mark.supports("S1", "Round")
def test_a_generator_whose_trial_falls_short_goes_back_to_decide_and_makes_it_again(b: Bench):
    """Given a run whose command's generator decided, wrote the command at make, and tried it as
    its people would, a condition that they meet falling short
    When it goes back to decide by lane-back, marks make before deciding again, then reports each
    decide item, writes the command again, tries it, runs the checks, and ends with made
    Then the lane-back goes through, Lane stops the early mark naming `decide`, and the end reads
    `rn:generator gave made. Due: rn:evaluator.`"""
    c, generator = decided_command(b)
    given = cut_of(c, generator)
    command = os.path.join(b.worktree, COMMAND)
    generator.write(command, "print('invoice')\n")
    items(c, generator, "make", rn_files.items_at("light", "make"))
    marked(c, "make", generator)
    back = generator.bash("lane-back decide")
    assert not back.blocked and not stopped(back.said), back.said
    early = generator.bash("lane-step make")
    assert stopped(early.said) and "`decide`" in early.said
    items(c, generator, "decide", rn_files.items_at("light", "decide"))
    marked(c, "decide", generator)
    generator.write(command, COMMAND_TEXT)
    items(c, generator, "make", rn_files.items_at("light", "make"))
    marked(c, "make", generator)
    made = rn_files.made([(each, ["import sys"]) for each in rn_files.conditions("light")])
    generator.write(os.path.join(c.cwd, given["round"], "generator.json"), json.dumps(made))
    marked(c, "try", generator)
    ran(c, b.script("repository", "checks", b.run, COMMAND), generator)
    generator.bash("lane-result made")
    marked(c, "check", generator)
    assert "rn:generator gave made. Due: rn:evaluator." in reached(generator).said


@pytest.mark.supports("S1", "Design tree")
def test_a_blocker_only_the_user_can_mend_stops_only_its_deliverable(b: Bench):
    """Given a run whose plan holds the command and a changelog, each resting on none, signed off,
    both generators started, the command made and judged good, and gh with no login
    When the orchestrator puts the command up at the step move, which repository.py put-up
    refuses, tells the user the blocker, and ends its turn; and then, at the changelog's
    generator's end, keeps the blocker as an open decision of the command's N1 and starts the
    changelog's evaluator
    Then the put-up gives 1 saying gh has no login, the first turn ends with no blocked while the
    changelog's generator runs, Lane stopping no move, the changelog's evaluator starts, and a start
    of the command's generator is stopped as not due"""
    c, cuts = signed_apart(b, apart_tree(b), [COMMAND, CHANGELOG])
    generator = started(c, "rn:generator", cuts[0])
    other = started(c, "rn:generator", cuts[1])
    ended(c, "Making both.")
    generated(b, c, generator)
    evaluator = next_round(b, c, COMMAND, [], "evaluator")[1]
    evaluated(b, c, evaluator)
    gh_double.logged_out(b.gh)
    held_good = held(b, COMMAND, rn_files.conditions("light"))
    written_tree(b, c, held_good)
    for step in ("take", "review"):
        marked(c, step)
    touched_items(b, c)
    marked(c, "touched")
    ran(c, b.script("tree", "commit", b.run, "The Round's findings."))
    marked(c, "commit")
    refused = c.bash(b.script("repository", "put-up", b.run, COMMAND))
    assert refused.exit_code == 1
    assert "You are not logged into any GitHub hosts." in refused.output
    marked(c, "move")
    ended(c, f"A blocker that's yours: {refused.output}The changelog goes on.")
    notified = generated(b, c, other, {CHANGELOG: "# Changes\n"})
    assert "rn:generator gave made. Due: rn:evaluator." in notified.said
    blocker = rn_files.decision("gh's login", None)
    cut_path = taken(
        b,
        c,
        held(b, COMMAND, rn_files.conditions("light"), {"N1": [blocker]}),
        "The put-up waits on gh's login.",
        [b.script("tree", "cut", b.run, "evaluator", CHANGELOG)],
    )[0].strip()
    assert started(c, "rn:evaluator", cut_path) is not None
    answer, agent = c.start("rn:generator", "Make the command again.", "Run rn:generator")
    assert agent is None
    assert "No start of rn's subagents is due now." in answer.said
