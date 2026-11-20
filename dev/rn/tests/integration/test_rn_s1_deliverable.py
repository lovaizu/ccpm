"""The integration cases of S1, a deliverable made in rounds: each path through its sequence, from
the user's request to the last sign-off, on the README's walkthrough with invoicer. Each runs rn
and Lane through the double of Claude Code and the double of gh, with a double of each prompt's
work, as rn's Test strategy says under Integration testing."""

from __future__ import annotations

import json
import os

import pytest
import rn_files
from repo_files import git
from rn_bench import (
    NOT_BUILT,
    Bench,
    command_signed,
    confirmed,
    cut,
    evaluated,
    evaluator_started,
    generated,
    held,
    judged_command,
    made_command,
    marked,
    next_round,
    pointed,
    put_up,
    put_up_plan,
    ran,
    requested,
    shared_steps,
    short_twice,
    signed,
    signed_plan,
    started,
    to_plan_signoff,
    written_tree,
)
from rn_files import COMMAND, GOAL, GUIDE

pytestmark = pytest.mark.xfail(strict=True, reason=NOT_BUILT)


def log(b: Bench, ref: str) -> list[str]:
    """Each commit message's subject on the ref of the user's repository, newest first."""
    return git(b.repo, "log", "--format=%s", ref).splitlines()


@pytest.mark.supports("S1", "Design tree")
def test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put(b: Bench):
    """Given invoicer's repository on main, with a remote
    When the user types /rn:up with the walkthrough's words, and the orchestrator makes the run by
    repository.py new with the goal as put and commits it
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
    shared_steps(b, c, held(b, GUIDE, [], {"N1": [settled]}), "The README names its people.")
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
    marked(c, "review")
    answer = c.bash("lane-step touched")
    assert answer.blocked
    assert "/deliverables/2" in answer.said


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
    Then the plan stays open, and a start of rn:generator is stopped as not due"""
    c = to_plan_signoff(b)
    c.type("/rn:gm the guide is for the accounting team alone")
    shared_steps(b, c, ground="The user sends the plan back.")
    assert b.tree()["deliverables"][0]["status"] == "open"
    answer, agent = c.start("rn:generator", "Make the command.", "Run rn:generator")
    assert agent is None
    assert "No start of rn's subagents is due now." in answer.said


@pytest.mark.supports("S1", "Round", "Cut")
def test_a_generators_point_reaches_the_user_and_their_answer_resumes_it(b: Bench):
    """Given a run whose command's generator runs
    When it ends with a point, the orchestrator keeps the point as an open decision of N1, the user
    answers, and the orchestrator writes the answer as its decision by user and writes the Cut
    Then the generator's end reads `rn:generator gave point.`, the Cut is the same Round's,
    content-1, holding the answer by user in the deliverable's N1, and SendMessage resumes the
    generator"""
    c, generator = signed_plan(b)
    notified = pointed(b, c, generator, "Should a line's quantity default to 1?")
    assert "rn:generator gave point." in notified.said
    about = "a line's quantity"
    shared_steps(
        b,
        c,
        held(b, COMMAND, [], {"N1": [rn_files.decision(about, None)]}),
        "The generator's point.",
    )
    c.stop("A question that's yours:\n  Should a line's quantity default to 1?")
    c.type("yes, 1")
    answer = rn_files.decision(about, "yes, 1", "user")
    tree = b.tree()
    tree["deliverables"][1]["necessary_conditions"][0]["decisions"][-1] = answer
    cut_path = shared_steps(
        b, c, tree, "The user's answer.", [b.script("tree", "cut", b.run, "generator", COMMAND)]
    )[0].strip()
    first = rn_files.round_of(b.folder, COMMAND, "content", 1)
    assert os.path.join(b.repo, cut_path) == os.path.join(first, "generator-cut.json")
    given = rn_files.read_json(os.path.join(b.repo, cut_path))
    assert answer in given["deliverable"]["necessary_conditions"][0]["decisions"]
    resumed = c.resume(generator, "yes, 1")
    assert not resumed.blocked, resumed.said


@pytest.mark.supports("S1", "Round", "Cut")
def test_a_generators_made_makes_the_evaluator_due_in_the_same_round(b: Bench):
    """Given a run whose command's generator runs
    When it keeps its steps and ends with made, and the orchestrator writes the evaluator's Cut
    Then the end reads `rn:generator gave made. Due: rn:evaluator.`, and the evaluator's Cut lies in
    Round content-1 beside the generator's result"""
    c, notified = made_command(b)
    assert "rn:generator gave made. Due: rn:evaluator." in notified.said
    cut_path = shared_steps(b, c, moves=[b.script("tree", "cut", b.run, "evaluator", COMMAND)])[
        0
    ].strip()
    first = rn_files.round_of(b.folder, COMMAND, "content", 1)
    assert os.path.join(b.repo, cut_path) == os.path.join(first, "evaluator-cut.json")
    assert os.path.isfile(os.path.join(first, "generator.json"))
    assert started(c, "rn:evaluator", cut_path) is not None


@pytest.mark.supports("S1", "Round", "Cut")
def test_an_evaluators_findings_go_to_the_next_rounds_generator_as_given(b: Bench):
    """Given a run whose command's evaluator judged Round content-1, N1 with more
    When the orchestrator holds N2 and N3 good, N1 not, and writes the generator's Cut
    Then the Cut lies in Round content-2, its findings the evaluator's good and more of content-1
    word for word, and its last_good the generator's good of content-1"""
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
    assert given["findings"] == {"good": judged["good"], "more": judged["more"]}
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
    """Given a run whose command's N1 the evaluator found short in Rounds content-1 and content-2
    When the orchestrator writes the generator's Cut, then keeps the finding as an open decision of
    N1, puts the command up, and the user signs it off
    Then tree.py cut gives 1 naming the orchestrator, the put-up prints the pull request's changes,
    and the command is done once signed off"""
    c, refused = short_twice(b)
    assert refused.exit_code == 1
    assert "orchestrator" in refused.output
    proposal = rn_files.decision("a comma in a line", None)
    shared_steps(b, c, held(b, COMMAND, ["N2", "N3"], {"N1": [proposal]}), "Left past its Rounds.")
    url = ran(c, b.script("repository", "put-up", b.run, COMMAND)).strip()
    assert url == "http://github.com/owner/repo/pull/1/files"
    c.stop("Proposals left past its Rounds:\n  - a comma in a line")
    signed(b, c)
    assert rn_files.done_node(rn_files.COMMAND_NAME, COMMAND, "light") in b.tree()["deliverables"]


@pytest.mark.supports("S1", "Best practice", "Cut")
def test_a_deliverable_with_each_condition_good_is_refactored_by_its_refactor_best_practice(
    b: Bench,
):
    """Given a run whose guide, of the kind readme, the evaluator judged good on each condition in
    Round content-1
    When the orchestrator holds each condition good and writes the generator's Cut
    Then the Cut lies in Round refactor-1, its stage refactor, number 1, and its best practice
    rn's refactor-doc"""
    c, generator = command_signed(b)
    generated(b, c, generator)
    _, evaluator = next_round(b, c, GUIDE, [], "evaluator")
    evaluated(b, c, evaluator)
    cut_path, _ = next_round(b, c, GUIDE, rn_files.conditions("readme"))
    refactor = rn_files.round_of(b.folder, GUIDE, "refactor", 1)
    assert os.path.join(b.repo, cut_path) == os.path.join(refactor, "generator-cut.json")
    given = rn_files.read_json(os.path.join(b.repo, cut_path))
    assert (given["stage"], given["number"]) == ("refactor", 1)
    assert os.path.normpath(os.path.join(b.repo, given["best_practice"])) == os.path.join(
        b.rn, "domain", "best-practices", "refactor-doc"
    )


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
    """Given a run whose guide the evaluator judged good in its Rounds, and put up
    When the user signs the guide off
    Then each deliverable of the tree is done, the remote's branch holds the command and the guide,
    and the orchestrator's turn ends with no start due"""
    c, generator = command_signed(b)
    generated(b, c, generator)
    _, evaluator = next_round(b, c, GUIDE, [], "evaluator")
    evaluated(b, c, evaluator)
    _, generator = next_round(b, c, GUIDE, rn_files.conditions("readme"))
    generated(b, c, generator)
    _, evaluator = next_round(b, c, GUIDE, rn_files.conditions("readme"), "evaluator")
    evaluated(b, c, evaluator)
    put_up(b, c, GUIDE, rn_files.conditions("readme"))
    signed(b, c)
    assert all(each["status"] == "done" for each in b.tree()["deliverables"])
    files = b.branch_files(f"rn-{b.name()}")
    assert COMMAND in files and GUIDE in files
    stopped = c.stop(
        "Done. The pull request is ready for your merge: http://github.com/owner/repo/pull/1"
    )
    assert not stopped.blocked, stopped.said


@pytest.mark.supports("S1", "Round")
def test_a_resumed_generator_after_its_answer_ends_with_made_and_the_evaluator_is_due(b: Bench):
    """Given a run whose command's generator gave a point that the user answered, and that the
    orchestrator resumed with the answer
    When the generator keeps its steps and ends with made
    Then its end reads `rn:generator gave made. Due: rn:evaluator.`"""
    c, generator = signed_plan(b)
    pointed(b, c, generator, "Should a line's quantity default to 1?")
    about = "a line's quantity"
    shared_steps(
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
