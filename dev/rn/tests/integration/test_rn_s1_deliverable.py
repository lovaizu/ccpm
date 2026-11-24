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
    COMMAND_TEXT,
    GUIDE_TEXT,
    PUSH_REFUSAL,
    STEPS,
    Bench,
    apart_tree,
    checked_whole,
    command_signed,
    cut_move,
    cut_of,
    decision_named,
    evaluated,
    evaluator_cut,
    fix_written,
    fixed,
    generated,
    heard,
    heard_tree,
    held,
    judged_command,
    new_run,
    next_round,
    pointed,
    pruned,
    push_refused,
    put_up,
    refactor_made,
    refactored,
    refactoring_put_up,
    reviewed,
    sent_back,
    short_twice,
    signed,
    signed_apart,
    signed_plan,
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


def command_done() -> dict:
    """The command done with each condition good, its N1 keeping the user's answer about the tax
    rate, as the walkthrough's plan gave it."""
    tax = rn_files.decision(rn_files.TAX_ABOUT, rn_files.TAX_ANSWER, "user")
    return rn_files.done_node(rn_files.COMMAND_NAME, COMMAND, "light", decisions={"N1": [tax]})


def committed_tree(b: Bench) -> dict:
    """The design tree as the work's branch's last commit holds it."""
    branch = f"rn-{b.name()}"
    return json.loads(git(b.worktree, "show", f"{branch}:.rn/{b.name()}/design-tree.json"))


@pytest.mark.supports("S1", "Design tree")
def test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_open(b: Bench):
    """Given invoicer's repository on main, with a remote
    When the orchestrator makes the run of the walkthrough's words by repository.py new, with the
    languages and no goal
    Then the run's worktree has the branch rn-<name> checked out from main's head, its design tree
    holds the goal open, the plan unnamed as its one deliverable, and no work, which tree.py check
    takes as it is, and the user's own branch and files are as they were"""
    head = git(b.repo, "rev-parse", "main").strip()
    assert new_run(b).strip() == b.run
    branch = f"rn-{b.name()}"
    assert git(b.worktree, "branch", "--show-current").strip() == branch
    assert git(b.repo, "merge-base", "main", branch).strip() == head
    assert b.tree() == rn_files.started(b.name())
    assert b.script("tree", "check", b.run) == (0, "", "")
    assert git(b.repo, "branch", "--show-current").strip() == "main"
    assert git(b.repo, "rev-parse", "main").strip() == head
    assert git(b.repo, "status", "--porcelain").strip() == ""


@pytest.mark.supports("S1", "orchestrator", "pruner", "Design tree", "Cut")
def test_the_hearing_settled_is_written_by_one_pruner_and_the_plans_signoff_recorded(b: Bench):
    """Given a run that repository.py new made, its goal open
    When the orchestrator holds the hearing with the user, starting no pruner, until the way to
    the goal is settled; hands it to one new pruner, which writes the goal by user, the plan named
    by it, the command, the guide, the tax rate's answer by user, and the steps with the user
    checking each; commits the tree; and, with no point open, records the plan's sign-off by
    tree.py signoff, commits it, and writes the command's Cut
    Then the tree is as new made it until the hearing ends; the work's branch then holds the
    hearing's tree in one commit, its message the ground; the plan is done with the steps as the
    user settled them, put up nowhere, as gh was asked to open no pull request; and the Cut lies in
    the command's Round content-1"""
    new_run(b)
    assert b.tree() == rn_files.started(b.name())
    branch = f"rn-{b.name()}"
    before = int(git(b.repo, "rev-list", "--count", branch))
    reviewed(b, heard_tree(b), "The way to the goal, as the user settled it.")
    assert committed_tree(b) == heard_tree(b)
    assert int(git(b.repo, "rev-list", "--count", branch)) == before + 1
    assert log(b, branch)[0] == "The way to the goal, as the user settled it."
    cut_path = signed(b, [cut_move(b, "generator", COMMAND)])[0].strip()
    tree = b.tree()
    assert tree["goal"] == {"decided": GOAL, "by": "user"}
    assert tree["deliverables"][0] == rn_files.done_node(
        GOAL, rn_files.plan_path(b.name()), "design-tree"
    )
    assert tree["steps"] == list(STEPS)
    assert ["gh", "pr", "create"] not in [each[:3] for each in b.asked_gh()]
    first = rn_files.round_of(b.folder, COMMAND, "content", 1)
    assert os.path.join(b.repo, cut_path) == os.path.join(first, "generator-cut.json")


@pytest.mark.supports("S1", "Cut")
@pytest.mark.parametrize("role", ["generator", "evaluator"])
def test_a_cut_waits_while_the_goal_is_open(b: Bench, role: str):
    """Given a run that repository.py new made, its goal open, which the pruner hasn't written yet
    When the orchestrator writes a role's Cut of the plan by tree.py cut
    Then it gives 1 saying that the goal is open and to hand the request to a new pruner, and the
    run's folder holds no Round"""
    new_run(b)
    refused = b.script(*cut_move(b, role, rn_files.plan_path(b.name())))
    assert refused.code == 1
    assert "goal is open; hand the request to a new pruner" in refused.err
    assert not os.path.exists(os.path.join(b.folder, "rounds"))


@pytest.mark.supports("S1", "scripts")
def test_a_put_up_while_the_goal_is_open_is_refused_before_any_push(b: Bench):
    """Given a run that repository.py new made, its goal open
    When the orchestrator puts the plan up by repository.py put-up
    Then it gives 1 saying that the goal is open, the remote holds no branch of the run, and gh
    was asked only for its login, opening no pull request"""
    new_run(b)
    refused = b.script("repository", "put-up", b.run, rn_files.plan_path(b.name()))
    assert refused.code == 1
    assert "goal is open" in refused.err
    assert f"rn-{b.name()}" not in git(b.origin, "branch", "--list").split()
    assert [each[:3] for each in b.asked_gh()] == [["gh", "auth", "status"]]


@pytest.mark.supports("S1", "Design tree")
def test_an_answer_after_the_request_goes_into_the_run_the_request_made(b: Bench):
    """Given invoicer's repository with a paused run 20261101-old, newest by its last commit, whose
    plan waits on its sign-off
    When the orchestrator makes the run of the walkthrough's words by repository.py new, holds the
    hearing, and hands it to one pruner, which writes it into the folder that new printed, and the
    orchestrator commits it
    Then the run made holds the hearing's tree, and 20261101-old's tree is as it was"""
    old = "20261101-old"
    waiting = rn_files.tree([rn_files.plan(old, good=False)], goal=GOAL, by="reasoning")
    folder = branch_run(b.repo, old, waiting, "2099-01-01T09:00:00")
    assert new_run(b).strip() == b.run
    reviewed(b, heard_tree(b), "The way to the goal, as the user settled it.")
    assert b.tree() == heard_tree(b)
    assert rn_files.read_json(os.path.join(folder, "design-tree.json")) == waiting


@pytest.mark.supports("S1")
def test_a_new_request_with_no_origin_is_refused_with_no_worktree_made(b: Bench):
    """Given invoicer's repository with no remote origin
    When the orchestrator runs repository.py new for the walkthrough's words
    Then it gives 1 saying that origin's HEAD names no default branch, and the repository has no
    worktree of rn"""
    git(b.repo, "remote", "remove", "origin")
    refused = b.script("repository", "new", rn_files.NAMED, *rn_files.LANGUAGES)
    assert refused.code == 1
    assert "origin's HEAD names no default branch" in refused.err
    assert not os.path.exists(b.at(".claude/worktrees"))


@pytest.mark.supports("S1", "Design tree")
def test_a_point_only_the_user_can_settle_is_kept_open_and_their_answer_written_by_user(b: Bench):
    """Given a run that repository.py new made
    When the hearing's pruner leaves the tax rate's point open as a decision of the command's N1,
    the orchestrator commits it, talks it over with the user until they settle it, and hands what
    they settled to one pruner, which writes it, and the orchestrator commits it
    Then the committed tree holds the point open, tree.py signoff finding nothing waiting, and then
    the answer as its decision by user, the plan waiting on its sign-off"""
    heard(b, answered=False)
    asked = committed_tree(b)["deliverables"][1]["necessary_conditions"][0]["decisions"]
    assert asked == [rn_files.decision(rn_files.TAX_ABOUT, None)]
    assert b.script("tree", "signoff", b.run).code == 1
    reviewed(b, heard_tree(b), "The user's answer.")
    answered = committed_tree(b)["deliverables"][1]["necessary_conditions"][0]["decisions"]
    assert answered == [rn_files.decision(rn_files.TAX_ABOUT, rn_files.TAX_ANSWER, "user")]
    assert b.ran("tree", "signoff", b.run).strip() == os.path.relpath(b.tree_path, b.repo)


@pytest.mark.supports("S1", "Design tree")
def test_a_point_the_pruner_settles_is_committed_with_its_ground_as_the_message(b: Bench):
    """Given a run whose hearing one pruner wrote
    When the pruner settles a point of the guide's N1 by reasoning, and the orchestrator commits
    it with its ground
    Then the work's branch's last commit holds the decision, its message the ground word for
    word"""
    heard(b)
    settled = rn_files.decision("its people", "The accounting team, at a terminal.", "reasoning")
    reviewed(b, held(b, GUIDE, [], {"N1": [settled]}), "The README names its people.")
    assert log(b, f"rn-{b.name()}")[0] == "The README names its people."
    assert settled in committed_tree(b)["deliverables"][2]["necessary_conditions"][0]["decisions"]


@pytest.mark.supports("S1", "pruner", "scripts", "Design tree")
def test_the_pruner_rewrites_each_node_its_change_touches_before_the_commit(b: Bench):
    """Given a run whose hearing one pruner wrote
    When a new pruner moves the command to invoicer/cli.py, in its step too, runs tree.py touched,
    rewrites itself the guide's inputs and the work's item of the command to the new path, and
    checks its write, and the orchestrator commits the tree, starting no other pruner
    Then tree.py touched listed the guide, whose inputs name the command, and the work's item of
    the command; and one commit holds the move with each node rewritten"""
    heard(b)
    branch = f"rn-{b.name()}"
    before = int(git(b.repo, "rev-list", "--count", branch))
    moved = b.tree()
    moved["deliverables"][1]["path"] = "invoicer/cli.py"
    moved["steps"][0]["deliverables"] = ["invoicer/cli.py"]
    guide = dict(moved["deliverables"][2], inputs=["invoicer/cli.py"])
    rewritten = {"/deliverables/2": guide, "/work/0": rn_files.work("make", "invoicer/cli.py")}
    listed = pruned(b, moved, rewritten)
    assert "/deliverables/2" in listed and "/work/0" in listed
    reviewed(b, ground="The command moves to invoicer/cli.py.")
    assert int(git(b.repo, "rev-list", "--count", branch)) == before + 1
    committed = committed_tree(b)
    assert committed["deliverables"][1]["path"] == "invoicer/cli.py"
    assert committed["deliverables"][2]["inputs"] == ["invoicer/cli.py"]
    assert committed["work"][0] == rn_files.work("make", "invoicer/cli.py")


@pytest.mark.supports("S1", "scripts", "Design tree")
def test_the_first_deliverable_whose_rounds_are_over_is_put_up_in_the_runs_pull_request(b: Bench):
    """Given a run whose command the evaluator judged good in Round content-1, the first
    deliverable whose Rounds are over
    When one pruner holds each condition good, and the orchestrator puts the command up by
    repository.py put-up
    Then it prints the link of the command's file, the remote's branch rn-<name> holds the run's
    design tree and the command, and gh was asked to open the pull request once, as a draft"""
    judged_command(b)
    assert put_up(b, COMMAND, rn_files.conditions("light")) == linked(b, COMMAND)
    files = b.branch_files(f"rn-{b.name()}")
    assert f".rn/{b.name()}/design-tree.json" in files and COMMAND in files
    created = [each for each in b.asked_gh() if each[1:3] == ["pr", "create"]]
    assert len(created) == 1 and "--draft" in created[0]


@pytest.mark.supports("S1", "Design tree", "Cut")
def test_a_signoff_of_the_plan_makes_it_done_and_starts_the_generator_of_each_deliverable_due(
    b: Bench,
):
    """Given a run whose hearing one pruner wrote
    When the orchestrator records the plan's sign-off, and writes the command's Cut
    Then the plan is done keeping its conditions, and the Cut lies in the command's Round
    content-1"""
    cut_path = signed_plan(b)
    assert b.tree()["deliverables"][0] == rn_files.done_node(
        GOAL, rn_files.plan_path(b.name()), "design-tree"
    )
    first = rn_files.round_of(b.folder, COMMAND, "content", 1)
    assert os.path.join(b.repo, cut_path) == os.path.join(first, "generator-cut.json")


@pytest.mark.supports("S1", "generator", "pruner", "Round", "Cut")
def test_a_generators_point_reaches_the_user_and_their_answer_resumes_it(b: Bench):
    """Given a run whose command's generator has its Cut
    When it ends with a point, which the orchestrator talks over with the user, starting no
    pruner, until they settle it; hands what they settled to one pruner, which writes it as a
    decision by user of N1; and writes the Cut
    Then check.py takes the point, the tree stays as it was until the user settles it, and the
    Cut is the same Round's, content-1, holding the answer by user in the deliverable's N1"""
    first_cut = signed_plan(b)
    before = b.tree()
    pointed(b, first_cut, "Should a line's quantity default to 1?")
    assert b.tree() == before
    answer = rn_files.decision("a line's quantity", "yes, 1", "user")
    settled = held(b, COMMAND, [], {"N1": [answer]})
    cut_path = reviewed(b, settled, "The user's answer.", [cut_move(b, "generator", COMMAND)])[0]
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


@pytest.mark.supports("S1", "Design tree", "Cut")
def test_a_finding_the_people_would_never_meet_is_dropped_by_holding_its_condition_good(b: Bench):
    """Given a run whose command's evaluator judged Round content-1, N1 with more
    When the pruner holds every condition good, N1 among them, and the orchestrator puts the
    command up
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
    When the pruner keeps the finding as an open decision of N1, the orchestrator puts the command
    up, and the user signs it off
    Then the put-up prints the link of the command's file, and the command is done once signed
    off, keeping the finding as the proposal the user signed off"""
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
    tax = rn_files.decision(rn_files.TAX_ABOUT, rn_files.TAX_ANSWER, "user")
    done = rn_files.done_node(
        rn_files.COMMAND_NAME, COMMAND, "light", ["N2", "N3"], {"N1": [tax, proposal]}
    )
    assert done in b.tree()["deliverables"]


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
    run them, and ended with made, which ends the guide's Rounds
    When the orchestrator, starting no pruner, puts the guide up, and writes the evaluator's Cut
    Then the generator's result lies in Round refactor-2, the tree is as the Round found it,
    repository.py put-up puts the guide up, and tree.py cut gives 1 saying the guide waits on the
    user's sign-off, writing no evaluator's Cut"""
    refactor_made(b)
    refactor = rn_files.round_of(b.folder, GUIDE, "refactor", 2)
    assert os.path.isfile(os.path.join(refactor, "generator.json"))
    before = committed_tree(b)
    assert refactoring_put_up(b) == linked(b, GUIDE)
    assert committed_tree(b) == before
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
    Then the command is done keeping its conditions and their decisions, its item of the work
    gone, and the guide's Cut's
    inputs name the command's path in the run's worktree"""
    cut_path = command_signed(b)
    tree = b.tree()
    assert command_done() in tree["deliverables"]
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
def test_a_deliverable_at_a_step_the_user_doesnt_check_is_done_once_put_up_and_the_next_starts(
    b: Bench,
):
    """Given a run whose plan is done with a step of the command, which the user doesn't check,
    and one of the guide, and whose command the evaluator judged good in Round content-1
    When the orchestrator holds each condition good, puts the command up by repository.py put-up,
    and writes the guide's Cut
    Then the command is done keeping its conditions and their decisions, tree.py signoff finds
    none waiting, and the guide's
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
    assert command_done() in b.tree()["deliverables"]
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


@pytest.mark.supports("S1", "pruner", "Design tree", "Cut")
def test_the_final_checks_findings_go_whole_to_one_pruner_which_sends_a_problem_back(b: Bench):
    """Given a run whose plan and command are done, and whose guide was refactored, put up, signed
    off, and checked whole by the final check's subagent
    When the orchestrator hands the subagent's findings, as one unit, to one pruner, which sends a
    problem that the people fail without back to the guide, open again with its N1 not good and
    the remedy a decision of N1, and the orchestrator commits it and writes the guide's Cut,
    starting no other pruner
    Then the Cut lies in the guide's Round content-3, a Round of its own after the put-up, its
    deliverable holding the remedy in N1"""
    refactored(b)
    signed(b)
    checked_whole(b)
    remedy = rn_files.decision("a line's format", "The guide shows a line's columns.", "maker")
    design_tree = b.tree()
    guide = rn_files.open_node(rn_files.GUIDE_NAME, GUIDE, "readme", [COMMAND], ["N2", "N3"])
    design_tree["deliverables"][2] = rn_files.decided(guide, {"N1": [remedy]})
    design_tree["work"] = [rn_files.work("make", GUIDE)]
    cut_path = reviewed(
        b, design_tree, "The final check's findings.", [cut_move(b, "generator", GUIDE)]
    )[0].strip()
    third = rn_files.round_of(b.folder, GUIDE, "content", 3)
    assert os.path.join(b.repo, cut_path) == os.path.join(third, "generator-cut.json")
    assert remedy in cut_of(b, cut_path)["deliverable"]["necessary_conditions"][0]["decisions"]


@pytest.mark.supports("S1", "fixer", "scripts", "Fix")
def test_a_put_up_that_the_repositorys_push_check_refuses_is_mended_by_a_fix_and_put_up_again(
    b: Bench,
):
    """Given a run whose repository checks each push, and whose command, with a line that ends in a
    space, the evaluator judged good in Round content-1
    When the orchestrator puts the command up, which the check refuses; judges that the mend keeps
    each decision, and writes the Fix by tree.py fix with the words that put-up printed; writes
    the fixer's Cut; the fixer strips the space and ends with fixed; and the orchestrator puts the
    command up again, and the user signs it off
    Then the first put-up gives non-zero with the check's words, and origin holds no branch of the
    run; the Fix lies in the command's fix-2, numbered with its Rounds, holding the problem as the
    source put-up and put-up's words; the fixer's Cut lies there; the second put-up prints the
    link of the command's file, origin's branch holding the command mended and the Fix; and the
    command is done"""
    refused = push_refused(b)
    assert refused.code != 0
    assert PUSH_REFUSAL in refused.err
    assert f"rn-{b.name()}" not in git(b.origin, "branch", "--list").split()
    fix = fix_written(b, COMMAND, "put-up", refused.err)
    assert fix == rn_files.round_of(b.folder, COMMAND, "fix", 2)
    problem = rn_files.read_json(os.path.join(fix, "problem.json"))
    assert problem == {"source": "put-up", "words": refused.err}
    cut_path = b.ran(*cut_move(b, "fixer", COMMAND)).strip()
    assert os.path.join(b.repo, cut_path) == os.path.join(fix, "fixer-cut.json")
    fixed(b, cut_path, {COMMAND: COMMAND_TEXT})
    assert b.ran("repository", "put-up", b.run, COMMAND).strip() == linked(b, COMMAND)
    branch = f"rn-{b.name()}"
    assert git(b.origin, "show", f"{branch}:{COMMAND}") == COMMAND_TEXT
    pushed = os.path.relpath(os.path.join(fix, "fixer.json"), b.worktree)
    assert pushed in b.branch_files(branch)
    signed(b)
    assert command_done() in b.tree()["deliverables"]


@pytest.mark.supports("S1", "fixer", "pruner", "Fix", "Round")
def test_a_fixers_decision_goes_to_one_pruner_and_the_deliverable_takes_content_rounds_again(
    b: Bench,
):
    """Given a run whose command's put-up the repository's push check refused, written as the
    command's Fix fix-2, whose fixer's Cut the orchestrator wrote
    When the fixer finds that its mend would change a decision of N1, mends nothing, and ends with
    decision; the orchestrator writes the generator's Cut and another Fix; then hands the decision
    to one pruner, which writes it as a decision of N1 and holds N1 not good, commits it, and
    writes the generator's Cut
    Then check.py takes the fixer's result; the first Cut and the Fix are each refused, as the
    command waits on the pruner, to weigh the decision its fixer named; and the Cut after the
    pruner lies in Round content-3, its stage content, its deliverable holding the decision"""
    refused = push_refused(b)
    fix_written(b, COMMAND, "put-up", refused.err)
    cut_path = b.ran(*cut_move(b, "fixer", COMMAND)).strip()
    words = (
        "The check wants no trailing space, but N1 decides the command's lines as the user wrote"
    )
    decision_named(b, cut_path, words)
    waiting = "waits on the pruner, to weigh the decision its fixer named"
    early = b.script(*cut_move(b, "generator", COMMAND))
    assert early.code == 1
    assert waiting in early.err
    again = b.script("tree", "fix", b.run, COMMAND, "put-up", given=refused.err)
    assert again.code == 1
    assert waiting in again.err
    weighed = rn_files.decision("a line's trailing space", "Strip it, as the check asks.", "maker")
    design_tree = held(b, COMMAND, ["N2", "N3"], {"N1": [weighed]})
    generator = reviewed(
        b, design_tree, "The fixer's decision.", [cut_move(b, "generator", COMMAND)]
    )[0].strip()
    third = rn_files.round_of(b.folder, COMMAND, "content", 3)
    assert os.path.join(b.repo, generator) == os.path.join(third, "generator-cut.json")
    given = cut_of(b, generator)
    assert (given["stage"], given["number"]) == ("content", 3)
    assert weighed in given["deliverable"]["necessary_conditions"][0]["decisions"]


@pytest.mark.supports("S1", "fixer", "Fix")
def test_a_final_checks_finding_within_the_decisions_is_mended_by_a_fix_of_the_done_deliverable(
    b: Bench,
):
    """Given a run whose plan and command are done, and whose guide was refactored, put up, signed
    off, and checked whole by the final check's subagent
    When the orchestrator judges that a finding of the guide keeps each of its decisions, writes
    the guide's Fix by tree.py fix with the finding's words, and writes the fixer's Cut; the fixer
    mends the guide and ends with fixed; and the orchestrator puts the guide up again
    Then the Fix lies in the guide's fix-3, after its two Rounds, the fixer's Cut holding the
    guide's done node with its decisions; the put-up gives 0; and the guide is done still, its
    node as the sign-off left it"""
    refactored(b)
    signed(b)
    checked_whole(b)
    done = next(each for each in b.tree()["deliverables"] if each["path"] == GUIDE)
    words = "The guide's walkthrough names the command by its old path."
    fix = fix_written(b, GUIDE, "final-check", words)
    assert fix == rn_files.round_of(b.folder, GUIDE, "fix", 3)
    cut_path = b.ran(*cut_move(b, "fixer", GUIDE)).strip()
    assert cut_of(b, cut_path)["deliverable"] == done
    fixed(b, cut_path, {GUIDE: GUIDE_TEXT + "\nThe command lies at invoicer/__main__.py.\n"})
    assert b.script("repository", "put-up", b.run, GUIDE).code == 0
    assert done in b.tree()["deliverables"]
