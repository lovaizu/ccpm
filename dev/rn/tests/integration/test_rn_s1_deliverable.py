"""The integration cases of S1, a deliverable made in rounds: each path through its sequence, from
the user's request to the last sign-off, on the bench's own request for invoicer. Each runs rn's
scripts as the orchestrator and each role run them, with the double of gh, and a double of each
prompt's work, as rn's Test strategy says under Integration testing."""

from __future__ import annotations

import json
import os

import pytest
import rn_files
from gh import gh_double
from repo_files import git
from rn_bench import (
    CHANGELOG,
    Bench,
    apart_tree,
    checked_whole,
    command_signed,
    confirmed,
    cut_move,
    cut_of,
    evaluated,
    evaluator_cut,
    generated,
    held,
    judged_command,
    next_round,
    planned_tree,
    pointed,
    put_up,
    put_up_plan,
    refactored,
    requested,
    reviewed,
    sent_back,
    short_twice,
    signed,
    signed_apart,
    signed_plan,
    to_plan_signoff,
)
from rn_files import COMMAND, GOAL, GUIDE
from rn_runs import branch_run


def linked(b: Bench, path: str) -> str:
    """The link that put-up prints of the deliverable's file at the path, at the commit that the
    work's branch holds."""
    commit = git(b.worktree, "rev-parse", "HEAD").strip()
    return f"http://github.com/owner/repo/blob/{commit}/{path}"


def log(b: Bench, ref: str) -> list[str]:
    """Each commit message's subject on the ref of the user's repository, newest first."""
    return git(b.repo, "log", "--format=%s", ref).splitlines()


def committed_tree(b: Bench) -> dict:
    """The design tree as the work's branch's last commit holds it."""
    branch = f"rn-{b.name()}"
    return json.loads(git(b.worktree, "show", f"{branch}:.rn/{b.name()}/design-tree.json"))


@pytest.mark.supports("S1", "Design tree")
def test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put(b: Bench):
    """Given invoicer's repository on main, with a remote
    When the orchestrator makes the run of the walkthrough's words by repository.py new with the
    goal as put, and commits it
    Then the run's worktree has the branch rn-<name> checked out from main's head, its design tree
    holds the goal by reasoning, the plan as its one deliverable, and no work, committed with the
    ground as its message, and the user's own branch and files are as they were"""
    head = git(b.repo, "rev-parse", "main").strip()
    requested(b)
    branch = f"rn-{b.name()}"
    assert git(b.worktree, "branch", "--show-current").strip() == branch
    assert git(b.repo, "merge-base", "main", branch).strip() == head
    expected = rn_files.tree([rn_files.plan(b.name(), good=False)], goal=GOAL, by="reasoning")
    assert b.tree() == expected
    assert log(b, branch)[0] == "The goal as put."
    assert git(b.repo, "branch", "--show-current").strip() == "main"
    assert git(b.repo, "rev-parse", "main").strip() == head
    assert git(b.repo, "status", "--porcelain").strip() == ""


@pytest.mark.supports("S1", "Design tree")
def test_an_answer_after_the_request_goes_into_the_run_the_request_made(b: Bench):
    """Given invoicer's repository with a paused run 20261101-old, newest by its last commit, whose
    plan waits on its sign-off
    When the orchestrator makes the run of the walkthrough's words by repository.py new, and, at
    the user's confirmation, writes the plan into the folder that new printed and commits it
    Then the run made holds the plan, and 20261101-old's tree is as it was"""
    old = "20261101-old"
    waiting = rn_files.tree([rn_files.plan(old, good=False)], goal=GOAL, by="reasoning")
    folder = branch_run(b.repo, old, waiting, "2099-01-01T09:00:00")
    made = b.ran("repository", "new", rn_files.NAMED, GOAL, *rn_files.LANGUAGES).strip()
    assert made == b.run
    reviewed(b, ground="The goal as put.")
    confirmed(b)
    assert b.tree() == planned_tree(b, answered=False)
    assert rn_files.read_json(os.path.join(folder, "design-tree.json")) == waiting


@pytest.mark.supports("S1")
def test_a_new_request_with_no_origin_is_refused_with_no_worktree_made(b: Bench):
    """Given invoicer's repository with no remote origin
    When the orchestrator runs repository.py new for the walkthrough's words
    Then it gives 1 saying that origin's HEAD names no default branch, and the repository has no
    worktree of rn"""
    git(b.repo, "remote", "remove", "origin")
    refused = b.script("repository", "new", rn_files.NAMED, GOAL, *rn_files.LANGUAGES)
    assert refused.code == 1
    assert "origin's HEAD names no default branch" in refused.err
    assert not os.path.exists(b.at(".claude/worktrees"))


@pytest.mark.supports("S1", "Design tree")
def test_a_point_only_the_user_can_settle_is_kept_open_and_their_answer_written_by_user(b: Bench):
    """Given a run whose goal the user confirmed
    When the orchestrator keeps the tax rate's point as an open decision of the command's N1 and
    commits it, and the user answers it
    Then the committed tree holds the point open, and then the answer as its decision by user"""
    requested(b)
    confirmed(b)
    asked = committed_tree(b)["deliverables"][1]["necessary_conditions"][0]["decisions"]
    assert asked == [rn_files.decision(rn_files.TAX_ABOUT, None)]
    put_up_plan(b)
    answered = committed_tree(b)["deliverables"][1]["necessary_conditions"][0]["decisions"]
    assert answered == [rn_files.decision(rn_files.TAX_ABOUT, rn_files.TAX_ANSWER, "user")]


@pytest.mark.supports("S1", "Design tree")
def test_a_point_the_orchestrator_settles_is_committed_with_its_ground_as_the_message(b: Bench):
    """Given a run whose goal the user confirmed
    When the orchestrator settles a point of the guide's N1 by reasoning in its review and commits
    it with its ground
    Then the work's branch's last commit holds the decision, its message the ground word for
    word"""
    requested(b)
    confirmed(b)
    settled = rn_files.decision("its people", "The accounting team, at a terminal.", "reasoning")
    reviewed(b, held(b, GUIDE, [], {"N1": [settled]}), "The README names its people.")
    assert log(b, f"rn-{b.name()}")[0] == "The README names its people."
    assert settled in committed_tree(b)["deliverables"][2]["necessary_conditions"][0]["decisions"]


@pytest.mark.supports("S1", "Design tree")
def test_each_node_a_change_touches_is_read_again_before_the_commit(b: Bench):
    """Given a run whose goal the user confirmed
    When the orchestrator changes the command's path in its review, and runs tree.py touched
    Then it prints the guide, whose inputs name the command, among the nodes to read again"""
    requested(b)
    confirmed(b)
    changed = b.tree()
    changed["deliverables"][1]["path"] = "invoicer/cli.py"
    b.write_tree(changed)
    assert "/deliverables/2" in b.ran("tree", "touched", b.run).split()


@pytest.mark.supports("S1", "Design tree")
def test_the_plan_waiting_for_signoff_is_put_up_in_the_runs_pull_request(b: Bench):
    """Given a run whose plan has each condition good
    When the orchestrator puts it up by repository.py put-up
    Then it prints no link, as the plan is the message that shows it, the remote's branch
    rn-<name> holds the run's design tree, and gh was asked to open the pull request once"""
    requested(b)
    confirmed(b)
    assert put_up_plan(b) == ""
    assert f".rn/{b.name()}/design-tree.json" in b.branch_files(f"rn-{b.name()}")
    assert [each[:3] for each in b.asked_gh()].count(["gh", "pr", "create"]) == 1


@pytest.mark.supports("S1", "Design tree", "Cut")
def test_a_signoff_of_the_plan_makes_it_done_and_starts_the_generator_of_each_deliverable_due(
    b: Bench,
):
    """Given a run whose plan is put up
    When the user types /rn:ty, the orchestrator records it, and writes the command's Cut
    Then the plan is done in its one line, and the Cut lies in the command's Round content-1"""
    cut_path = signed_plan(b)
    assert b.tree()["deliverables"][0] == rn_files.done_node(
        GOAL, rn_files.plan_path(b.name()), "design-tree"
    )
    first = rn_files.round_of(b.folder, COMMAND, "content", 1)
    assert os.path.join(b.repo, cut_path) == os.path.join(first, "generator-cut.json")


@pytest.mark.supports("S1", "Design tree")
def test_a_send_back_of_the_plan_leaves_it_open_waiting_for_signoff(b: Bench):
    """Given a run whose plan is put up
    When the user types /rn:gm with what to change, and the orchestrator commits its review
    Then the plan stays open, and the commit holds it so"""
    to_plan_signoff(b)
    reviewed(b, ground="The user sends the plan back.")
    assert b.tree()["deliverables"][0]["status"] == "open"
    assert committed_tree(b)["deliverables"][0]["status"] == "open"


@pytest.mark.supports("S1", "Round", "Cut")
def test_a_generators_point_reaches_the_user_and_their_answer_resumes_it(b: Bench):
    """Given a run whose command's generator has its Cut
    When it ends with a point, the orchestrator keeps the point as an open decision of N1, the user
    answers, and the orchestrator writes the answer as its decision by user and writes the Cut
    Then check.py takes the point, and the Cut is the same Round's, content-1, holding the answer
    by user in the deliverable's N1"""
    first_cut = signed_plan(b)
    pointed(b, first_cut, "Should a line's quantity default to 1?")
    about = "a line's quantity"
    reviewed(b, held(b, COMMAND, [], {"N1": [rn_files.decision(about, None)]}), "The point.")
    answer = rn_files.decision(about, "yes, 1", "user")
    tree = b.tree()
    tree["deliverables"][1]["necessary_conditions"][0]["decisions"][-1] = answer
    cut_path = reviewed(b, tree, "The user's answer.", [cut_move(b, "generator", COMMAND)])[0]
    assert cut_path.strip() == first_cut
    given = cut_of(b, cut_path.strip())
    assert answer in given["deliverable"]["necessary_conditions"][0]["decisions"]


@pytest.mark.supports("S1", "Round", "Cut")
def test_a_generators_made_makes_the_evaluator_due_in_the_same_round(b: Bench):
    """Given a run whose command's generator made its Round, check.py taking its result
    When the orchestrator writes the evaluator's Cut
    Then the Cut lies in Round content-1 beside the generator's result"""
    cut_path = evaluator_cut(b)
    first = rn_files.round_of(b.folder, COMMAND, "content", 1)
    assert os.path.join(b.repo, cut_path) == os.path.join(first, "evaluator-cut.json")
    assert os.path.isfile(os.path.join(first, "generator.json"))


@pytest.mark.supports("S1", "Round", "Cut")
def test_an_evaluators_findings_go_to_the_next_rounds_generator_as_given(b: Bench):
    """Given a run whose command's evaluator judged Round content-1, N1 with more
    When the orchestrator holds N2 and N3 good, N1 not, and writes the generator's Cut
    Then the Cut lies in Round content-2, its findings the evaluator's good and more of content-1
    of N1 alone, the one condition the tree still holds not good, word for word, and its
    last_good the generator's good of content-1"""
    judged_command(b, {"N1": "The accountant prints an invoice with a comma in a line."})
    cut_path = next_round(b, COMMAND, ["N2", "N3"])
    first = rn_files.round_of(b.folder, COMMAND, "content", 1)
    second = rn_files.round_of(b.folder, COMMAND, "content", 2)
    assert os.path.join(b.repo, cut_path) == os.path.join(second, "generator-cut.json")
    given = cut_of(b, cut_path)
    judged = rn_files.read_json(os.path.join(first, "evaluator.json"))
    made = rn_files.read_json(os.path.join(first, "generator.json"))
    assert given["findings"] == {
        "good": [each for each in judged["good"] if each["condition"] == "N1"],
        "more": [each for each in judged["more"] if each["condition"] == "N1"],
    }
    assert given["last_good"] == made["good"]
    assert (given["stage"], given["number"]) == ("content", 2)


@pytest.mark.supports("S1", "Design tree", "Cut")
def test_a_finding_the_people_would_never_meet_is_dropped_by_holding_its_condition_good(b: Bench):
    """Given a run whose command's evaluator judged Round content-1, N1 with more
    When the orchestrator holds every condition good, N1 among them, and puts the command up
    Then repository.py put-up prints the link of the command's file, and tree.py cut of its
    generator gives 1, as it waits for the user's sign-off"""
    judged_command(b, {"N1": "The accountant prints an invoice in Klingon."})
    assert put_up(b, COMMAND, rn_files.conditions("light")) == linked(b, COMMAND)
    refused = b.script(*cut_move(b, "generator", COMMAND))
    assert refused.code == 1
    assert "sign-off" in refused.err


@pytest.mark.supports("S1", "Design tree", "Round")
def test_a_finding_left_past_two_content_rounds_goes_to_the_user_as_a_proposal(b: Bench):
    """Given a run whose command's N1 the evaluator found short in Rounds content-1 and content-2
    When the orchestrator keeps the finding as an open decision of N1, puts the command up, and
    the user signs it off
    Then the put-up prints the link of the command's file, and the command is done once signed
    off"""
    short_twice(b)
    proposal = rn_files.decision("a comma in a line", None)
    url = reviewed(
        b,
        held(b, COMMAND, ["N2", "N3"], {"N1": [proposal]}),
        "Left past its Rounds.",
        [("repository", "put-up", b.run, COMMAND)],
    )[0].strip()
    assert url == linked(b, COMMAND)
    signed(b)
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
    generated(b, command_signed(b))
    evaluated(b, next_round(b, GUIDE, [], "evaluator"))
    cut_path = next_round(b, GUIDE, rn_files.conditions("readme"))
    refactor = rn_files.round_of(b.folder, GUIDE, "refactor", 2)
    assert os.path.join(b.repo, cut_path) == os.path.join(refactor, "generator-cut.json")
    given = cut_of(b, cut_path)
    assert (given["stage"], given["number"]) == ("refactor", 2)
    assert os.path.normpath(os.path.join(b.repo, given["best_practice"])) == os.path.join(
        b.rn, "domain", "best-practices", "refactor-doc"
    )


@pytest.mark.supports("S1", "Round", "Cut")
def test_the_refactoring_generators_made_waits_on_the_signoff_with_no_evaluator(b: Bench):
    """Given a run whose guide was judged good on each condition in Round content-1, and whose new
    generator refactored it in Round refactor-2, running the repository's tests as its developers
    run them, and ended with made
    When the orchestrator holds each condition good, puts the guide up, and writes the evaluator's
    Cut
    Then the generator's result lies in Round refactor-2, repository.py put-up puts the guide up,
    and tree.py cut gives 1 saying the guide waits on the user's sign-off, writing no evaluator's
    Cut"""
    generated(b, command_signed(b))
    evaluated(b, next_round(b, GUIDE, [], "evaluator"))
    generated(b, next_round(b, GUIDE, rn_files.conditions("readme")))
    refactor = rn_files.round_of(b.folder, GUIDE, "refactor", 2)
    assert os.path.isfile(os.path.join(refactor, "generator.json"))
    assert put_up(b, GUIDE, rn_files.conditions("readme")) == linked(b, GUIDE)
    refused = b.script(*cut_move(b, "evaluator", GUIDE))
    assert refused.code == 1
    assert "waits on the user's sign-off, not on its evaluator" in refused.err
    assert not os.path.exists(os.path.join(refactor, "evaluator-cut.json"))


@pytest.mark.supports("S1", "Design tree", "Round")
def test_a_send_back_after_the_refactor_round_is_remade_in_a_new_content_round(b: Bench):
    """Given a run whose guide was judged good in Round content-1, refactored in refactor-2, and
    put up for the user's sign-off
    When the user types /rn:gm with what to change, and the orchestrator writes it as a decision
    by user of N1, holds N1 not good, and writes the generator's Cut
    Then the Cut lies in Round content-3, the last Round, its stage content, its deliverable holding
    the user's words"""
    refactored(b)
    words = "the guide is for the accounting team alone"
    cut_path = sent_back(b, GUIDE, rn_files.conditions("readme"), words)
    content = rn_files.round_of(b.folder, GUIDE, "content", 3)
    assert os.path.join(b.repo, cut_path) == os.path.join(content, "generator-cut.json")
    given = cut_of(b, cut_path)
    assert (given["stage"], given["number"]) == ("content", 3)
    n1 = given["deliverable"]["necessary_conditions"][0]
    assert (n1["id"], n1["good"]) == ("N1", False)
    assert rn_files.decision(words, words, "user") in n1["decisions"]


@pytest.mark.supports("S1", "Design tree", "Round")
def test_a_send_back_after_the_contents_last_round_is_remade_in_a_new_content_round(b: Bench):
    """Given a run whose command, of the kind light, which has no refactoring, the evaluator judged
    good in Round content-1, put up for the user's sign-off
    When the user types /rn:gm with what to change, and the orchestrator writes it as a decision
    by user of N1, holds N1 not good, and writes the generator's Cut
    Then the Cut lies in Round content-2, its stage content"""
    judged_command(b)
    put_up(b, COMMAND, rn_files.conditions("light"))
    words = "print the total on its own last line"
    cut_path = sent_back(b, COMMAND, rn_files.conditions("light"), words)
    content = rn_files.round_of(b.folder, COMMAND, "content", 2)
    assert os.path.join(b.repo, cut_path) == os.path.join(content, "generator-cut.json")
    assert (cut_of(b, cut_path)["stage"], cut_of(b, cut_path)["number"]) == ("content", 2)


@pytest.mark.supports("S1", "Design tree")
def test_a_deliverable_signed_off_is_done_and_the_one_resting_on_it_starts(b: Bench):
    """Given a run whose command the evaluator judged good in Round content-1, put up
    When the user signs it off, and the orchestrator writes the guide's Cut
    Then the command is done in its one line, its item of the work gone, and the guide's Cut's
    inputs name the command's path in the run's worktree"""
    cut_path = command_signed(b)
    tree = b.tree()
    assert rn_files.done_node(rn_files.COMMAND_NAME, COMMAND, "light") in tree["deliverables"]
    assert tree["work"] == [rn_files.work("make", GUIDE)]
    given = cut_of(b, cut_path)
    assert [os.path.normpath(os.path.join(b.repo, each)) for each in given["inputs"]] == [
        os.path.join(b.worktree, COMMAND)
    ]


@pytest.mark.supports("S1")
def test_the_last_signoff_ends_the_run_with_each_deliverable_on_the_pull_requests_branch(b: Bench):
    """Given a run whose guide was judged good, refactored, and put up
    When the user signs the guide off, and the orchestrator has the work checked whole
    Then each deliverable of the tree is done, and the remote's branch holds the command and the
    guide"""
    refactored(b)
    signed(b)
    checked_whole(b)
    assert all(each["status"] == "done" for each in b.tree()["deliverables"])
    files = b.branch_files(f"rn-{b.name()}")
    assert COMMAND in files and GUIDE in files


@pytest.mark.supports("S1", "Design tree")
def test_the_pull_request_stays_a_draft_while_a_deliverable_is_left_open(b: Bench):
    """Given a run whose plan and command were put up and signed off, the guide still open
    When the orchestrator writes the guide's Cut
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


@pytest.mark.supports("S1", "scripts")
def test_the_final_check_pushes_the_work_and_reads_its_whole_diff_and_ci(b: Bench):
    """Given a run whose plan and command are done, and whose guide was judged good, refactored,
    and put up
    When the user signs the guide off, and the final check's subagent runs repository.py diff, then
    repository.py ci
    Then diff prints the diff of the command and the guide against the default branch, origin's
    branch holds the worktree's last commit, its tree with each deliverable done, and ci prints
    that each check passed"""
    refactored(b)
    signed(b)
    whole, checks = checked_whole(b)
    assert f"+++ b/{COMMAND}" in whole and f"+++ b/{GUIDE}" in whole
    branch = f"rn-{b.name()}"
    assert git(b.origin, "rev-parse", branch) == git(b.worktree, "rev-parse", "HEAD")
    pushed = json.loads(git(b.origin, "show", f"{branch}:.rn/{b.name()}/design-tree.json"))
    assert [each["status"] for each in pushed["deliverables"]] == ["done", "done", "done"]
    assert "tests\tpass" in checks
    assert "fail" not in checks


@pytest.mark.supports("S1", "Design tree")
def test_an_answer_of_where_the_user_checks_signs_off_the_plan(b: Bench):
    """Given a run whose plan is put up as the way to the goal, a step of the command and one of
    the guide
    When the user answers that they check each step, and the orchestrator writes each step's
    sign-off true, runs tree.py signoff, commits, and writes the command's Cut
    Then the plan is done, each step's sign-off is true, and the command's Cut is written"""
    to_plan_signoff(b)
    design_tree = b.tree()
    design_tree["steps"] = [
        rn_files.step("what it does", [COMMAND], True),
        rn_files.step("how it's used", [GUIDE], True),
    ]
    b.write_tree(design_tree)
    b.ran("tree", "signoff", b.run)
    cut_path = reviewed(
        b, ground="The user checks each step.", moves=[cut_move(b, "generator", COMMAND)]
    )[0].strip()
    tree = b.tree()
    assert tree["deliverables"][0]["status"] == "done"
    assert [each["signoff"] for each in tree["steps"]] == [True, True]
    assert os.path.isfile(os.path.join(b.repo, cut_path))


@pytest.mark.supports("S1", "Design tree")
def test_a_deliverable_at_a_step_the_user_doesnt_check_is_done_once_put_up_and_the_next_starts(
    b: Bench,
):
    """Given a run whose plan is done with a step of the command, which the user doesn't check,
    and one of the guide, and whose command the evaluator judged good in Round content-1
    When the orchestrator holds each condition good, puts the command up by repository.py put-up,
    and writes the guide's Cut
    Then the command is done in its one line, tree.py signoff finds none waiting, and the guide's
    Cut is written"""
    judged_command(b)
    design_tree = held(b, COMMAND, rn_files.conditions("light"))
    design_tree["steps"] = [
        rn_files.step("what it does", [COMMAND], False),
        rn_files.step("how it's used", [GUIDE], True),
    ]
    cut_path = reviewed(
        b,
        design_tree,
        "The Round's findings.",
        [("repository", "put-up", b.run, COMMAND), cut_move(b, "generator", GUIDE)],
    )[1].strip()
    assert rn_files.done_node(rn_files.COMMAND_NAME, COMMAND, "light") in b.tree()["deliverables"]
    assert b.script("tree", "signoff", b.run).code == 1
    assert os.path.isfile(os.path.join(b.repo, cut_path))


@pytest.mark.supports("S1", "Round")
def test_a_resumed_generator_after_its_answer_ends_with_made_and_the_evaluator_is_due(b: Bench):
    """Given a run whose command's generator gave a point that the user answered, and whose Cut
    the orchestrator wrote again with the answer
    When the generator makes the command and ends with made
    Then check.py takes its result, and tree.py cut writes the evaluator's Cut in Round
    content-1"""
    cut_path = signed_plan(b)
    pointed(b, cut_path, "Should a line's quantity default to 1?")
    answered = {"N1": [rn_files.decision("a line's quantity", "yes, 1", "user")]}
    reviewed(b, held(b, COMMAND, [], answered), "Answered.", [cut_move(b, "generator", COMMAND)])
    generated(b, cut_path)
    evaluator = b.ran(*cut_move(b, "evaluator", COMMAND)).strip()
    first = rn_files.round_of(b.folder, COMMAND, "content", 1)
    assert os.path.join(b.repo, evaluator) == os.path.join(first, "evaluator-cut.json")


@pytest.mark.supports("S1", "Round")
def test_an_evaluators_answers_lie_in_its_round_and_hold_its_check(b: Bench):
    """Given a run whose command's evaluator has its Cut
    When it tries the command in the people's folder and ends with judged
    Then check.py takes its answers, which lie in Round content-1"""
    evaluated(b, evaluator_cut(b))
    first = rn_files.round_of(b.folder, COMMAND, "content", 1)
    assert rn_files.read_json(os.path.join(first, "evaluator.json"))["result"] == "judged"


@pytest.mark.supports("S1", "Design tree")
def test_a_blocker_only_the_user_can_mend_stops_only_its_deliverable(b: Bench):
    """Given a run whose plan holds the command and a changelog, each resting on none, signed off,
    the command made and judged good, the changelog's generator still making it, and gh with no
    login
    When the orchestrator puts the command up, which repository.py put-up refuses, keeps the
    blocker as an open decision of the command's N1, and, at the changelog's generator's end,
    writes the changelog's evaluator's Cut
    Then the put-up gives 1 saying gh has no login, the changelog's evaluator's Cut is written,
    and tree.py cut of the command's generator gives 1, as it waits on the user's answer"""
    command, changelog = signed_apart(b, apart_tree(b), [COMMAND, CHANGELOG])
    generated(b, command)
    evaluated(b, next_round(b, COMMAND, [], "evaluator"))
    gh_double.logged_out(b.gh)
    reviewed(b, held(b, COMMAND, rn_files.conditions("light")), "The Round's findings.")
    refused = b.script("repository", "put-up", b.run, COMMAND)
    assert refused.code == 1
    assert "You are not logged into any GitHub hosts." in refused.err
    generated(b, changelog, {CHANGELOG: "# Changes\n"})
    blocker = rn_files.decision("gh's login", None)
    cut_path = reviewed(
        b,
        held(b, COMMAND, rn_files.conditions("light"), {"N1": [blocker]}),
        "The put-up waits on gh's login.",
        [cut_move(b, "evaluator", CHANGELOG)],
    )[0].strip()
    assert os.path.isfile(os.path.join(b.repo, cut_path))
    again = b.script(*cut_move(b, "generator", COMMAND))
    assert again.code == 1
    assert "the user's answer" in again.err
