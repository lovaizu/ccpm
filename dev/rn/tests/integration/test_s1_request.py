"""The integration cases of S1, a request and a deliverable made in rounds: the user types `/rn:up`
with what they want, tree.py makes the run's worktree, the tree-keeper writes the goal and the
plan, and each deliverable whose turn has come is made by a generator, tried in a throwaway copy,
and judged by an evaluator for each group of its necessary conditions, round after round. The test
plays the user, the orchestrator, and each role."""

from __future__ import annotations

import json
import os

import pytest
from claude_code import Conversation
from rn_example import (
    ANSWERED,
    CODE_GROUPS,
    DECIMAL,
    GOAL,
    HINTS,
    POINT,
    SETTLED,
    TYPED,
    WITH_POINT,
    WORDS,
    Repo,
    Run,
    condition,
    conversation,
    decided,
    git,
    gives,
    keeper_done_and_paused,
    keeper_writes,
    plan,
    records_all,
    started,
    text_of,
    throwaway,
    tree,
    write,
)

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")


def signed_plan(conv: Conversation, repo: Repo, run: Run) -> None:
    """The plan of the walkthrough, its point answered, put up and signed off by the user's
    /rn:ty, and the tree-keeper's write of the sign-off, which marks the hints doing."""
    _, keeper = started(conv, repo, run, "tree-keeper")
    keeper_writes(keeper, repo, run, ANSWERED, "The user answered each file.")
    put_up(conv, repo, run, "plan")
    conv.type("/rn:ty")
    keeper_writes(keeper, repo, run, ANSWERED, "The user signed the plan off.")


def put_up(conv: Conversation, repo: Repo, run: Run, of: str) -> None:
    """The orchestrator puts the plan or the deliverable at the path up for the user's sign-off."""
    path = os.path.join(repo.temp, f"sign-off-{len(os.listdir(repo.temp))}.json")
    sign_off = {"of": of, "can_do": "", "decisions": [], "words": ""}
    conv.write(None, path, json.dumps(sign_off))
    done = conv.bash(tree(repo, "sign-off", run.folder, path))
    assert done.exit_code == 0, done.output


@pytest.mark.supports("S1", "orchestrator", "tree.py")
def test_up_with_a_request_makes_the_runs_worktree_on_its_branch_with_its_folder(
    conv: Conversation, repo: Repo
):
    """Given the repository of invoicer with rn installed
    When the user types `/rn:up` with the walkthrough's request, and the orchestrator runs
    `tree.py begin type hints for invoicer`
    Then tree.py prints a worktree under .claude/worktrees/ on the branch rn/<run>, whose .rn/<run>/
    holds records/ and rounds/, committed, and the user's checkout is left as it was"""
    conv.type("/rn:up type hints for invoicer, so that the people who call it see each type")
    made = conv.bash(tree(repo, "begin", WORDS))
    worktree = made.output.strip()
    name = os.path.basename(worktree).removeprefix("rn-")
    assert made.exit_code == 0 and name.endswith("-type-hints-for-invoicer")
    assert worktree == os.path.join(repo.root, ".claude", "worktrees", f"rn-{name}")
    assert git(worktree, "branch", "--show-current").strip() == f"rn/{name}"
    assert git(worktree, "status", "--porcelain") == ""
    assert os.path.isdir(os.path.join(worktree, ".rn", name, "records"))
    assert git(repo.root, "status", "--porcelain") == ""


@pytest.mark.supports("S1", "adapters", "guard", "tree-keeper")
def test_up_with_a_request_while_a_run_is_left_starts_a_new_run(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the walkthrough's run paused with the tree-keeper's `done` kept in its record, the one
    run left
    When the user types `/rn:up README for invoicer` in a new conversation at the root of the
    repository
    Then the guard gives the tree-keeper's start, the first move of a new run, and not the
    walkthrough's run picked up, as a request starts a new run whatever runs are left"""
    keeper_done_and_paused(conv, repo, run)
    typed = conversation(repo).type("/rn:up README for invoicer")
    assert "rn:tree-keeper" in typed.said


@pytest.mark.supports("S1", "tree.py")
def test_begin_refuses_a_run_that_already_has_its_worktree(
    conv: Conversation, repo: Repo, run: Run
):
    """Given a run begun on the walkthrough's request today
    When the orchestrator runs `tree.py begin type hints for invoicer` again
    Then tree.py exits 1 naming the run's worktree, and makes nothing"""
    again = conv.bash(tree(repo, "begin", WORDS))
    assert again.exit_code == 1 and run.worktree in again.output
    assert len(git(repo.root, "worktree", "list").splitlines()) == 2


@pytest.mark.supports("S1", "tree-keeper", "Cut", "adapters")
def test_the_tree_keeper_starts_with_its_cut_of_the_run_alone(
    conv: Conversation, repo: Repo, run: Run
):
    """Given a run begun, with no design tree yet
    When the orchestrator has tree.py cut the tree-keeper's cut, and starts it with its run values
    Then the run values name its record, the run, and the run's design-tree.json, and the guard
    lets the start through"""
    given, keeper = started(conv, repo, run, "tree-keeper")
    assert given["run"] == run.folder
    assert given["tree"] == os.path.join(run.folder, "design-tree.json")
    assert given["record"].startswith(os.path.join(run.folder, "records", ""))
    assert keeper.running


@pytest.mark.supports("S1", "tree-keeper", "Design tree", "Decision", "Point")
def test_the_goal_and_the_plan_written_commit_the_design_tree_with_the_point_open(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the tree-keeper started, and the orchestrator's goal drafted, not yet put to the user
    When it writes the goal drafted and the walkthrough's plan, with the point on each file open, by
    `tree.py write` with its ground
    Then tree.py exits 0, prints the goal and both deliverables as changed and none doing, and
    the design tree it committed holds the goal by reasoning and the point with `decided` null,
    before the user sees either"""
    _, keeper = started(conv, repo, run, "tree-keeper")
    drafted = dict(WITH_POINT, goal={"decided": GOAL, "by": "reasoning"})
    wrote = keeper_writes(keeper, repo, run, drafted, "The goal drafted, and the plan.")
    printed = json.loads(wrote.output)
    assert wrote.exit_code == 0 and printed["doing"] == []
    assert {"goal", HINTS, TYPED} <= set(printed["changed"])
    committed = git(run.worktree, "show", f"HEAD:{run.folder}/design-tree.json")
    assert json.loads(committed) == drafted
    assert (
        git(run.worktree, "log", "-1", "--format=%B").strip() == "The goal drafted, and the plan."
    )


@pytest.mark.supports("S1", "tree-keeper", "Design tree", "Decision", "Point", "user")
def test_the_goal_the_user_confirmed_is_written_by_the_user(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the goal drafted and the plan written, and the user's `yes` to the goal put to them
    When the tree-keeper writes the goal by the user
    Then tree.py exits 0, prints the goal as changed, and the design tree holds it by the user"""
    _, keeper = started(conv, repo, run, "tree-keeper")
    drafted = dict(WITH_POINT, goal={"decided": GOAL, "by": "reasoning"})
    keeper_writes(keeper, repo, run, drafted, "The goal drafted, and the plan.")
    wrote = keeper_writes(keeper, repo, run, WITH_POINT, "The user confirmed the goal.")
    committed = json.loads(git(run.worktree, "show", f"HEAD:{run.folder}/design-tree.json"))
    assert wrote.exit_code == 0 and "goal" in json.loads(wrote.output)["changed"]
    assert committed["goal"] == {"decided": GOAL, "by": "user"}


@pytest.mark.supports("S1", "tree.py", "Design tree")
def test_write_refuses_a_deliverable_before_one_it_takes_from_and_leaves_the_tree(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the tree-keeper started, and the walkthrough's plan written
    When it writes the plan again with the typed marker before the hints it takes from
    Then tree.py exits 1 naming both paths, and the run's design tree holds the plan as before"""
    _, keeper = started(conv, repo, run, "tree-keeper")
    keeper_writes(keeper, repo, run, WITH_POINT, "The user confirmed the goal.")
    backwards = dict(WITH_POINT, deliverables=WITH_POINT["deliverables"][::-1])
    refused = keeper_writes(keeper, repo, run, backwards, "Typed first.")
    assert refused.exit_code == 1 and HINTS in refused.output and TYPED in refused.output
    held = text_of(os.path.join(run.worktree, run.folder, "design-tree.json"))
    assert json.loads(held) == WITH_POINT


@pytest.mark.supports("S1", "generator", "Cut", "More kept", "adapters", "Round")
def test_the_hints_once_due_start_a_generator_with_the_cut_of_its_first_round(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the plan signed off, its point answered, so the hints are marked doing
    When the orchestrator has tree.py cut the generator's cut of the hints, and starts it
    Then its run values name the hints, the kind code, round 1, and a cut whose decisions are the
    hints' alone, with no More kept"""
    signed_plan(conv, repo, run)
    given, _ = started(conv, repo, run, "generator", HINTS)
    assert (given["deliverable"], given["kind"], given["round"]) == (HINTS, "code", "1")
    held = json.loads(text_of(os.path.join(run.worktree, given["cut"])))
    assert [each["about"] for each in held["decisions"]] == [POINT]
    assert held["more"] == []


@pytest.mark.supports("S1", "generator", "tree.py", "Place", "Deliverable")
def test_a_generators_place_commits_its_work_with_the_step_it_stands_at(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator running in round 1
    When it writes invoicer/totals.py with hints, and runs
    `tree.py place <run> invoicer/ generator 4`
    Then tree.py exits 0, and the worktree's last commit holds invoicer/totals.py and the round's
    Place of the generator at step 4"""
    signed_plan(conv, repo, run)
    _, generator = started(conv, repo, run, "generator", HINTS)
    generator.write(
        os.path.join(run.worktree, "invoicer", "totals.py"), "def total(lines: list) -> int: ...\n"
    )
    placed = generator.bash(tree(repo, "place", run.folder, HINTS, "generator", "4"))
    committed = git(run.worktree, "show", "--name-only", "--format=", "HEAD").split()
    assert placed.exit_code == 0 and "invoicer/totals.py" in committed
    place = [path for path in committed if path.startswith(f"{run.folder}/rounds/invoicer--/1/")]
    assert place, committed


@pytest.mark.supports("S1", "throwaway.py", "Try record", "generator")
def test_a_try_runs_the_command_in_a_copy_and_keeps_it_in_the_rounds_try_record(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator running in round 1
    When it runs `throwaway.py try <run> invoicer/ 1 'python3 -m pytest -q'`
    Then throwaway.py gives the command's exit code and what it printed, and the round's Try record
    holds the command with both"""
    signed_plan(conv, repo, run)
    _, generator = started(conv, repo, run, "generator", HINTS)
    tried = generator.bash(throwaway(repo, "try", run.folder, HINTS, "1", "python3 -m pytest -q"))
    folder = os.path.join(run.worktree, run.folder, "rounds", "invoicer--", "1")
    kept = json.loads(text_of(os.path.join(folder, "try.json")))
    assert kept["tried"][-1]["command"] == "python3 -m pytest -q"
    assert kept["tried"][-1]["exit_code"] == tried.exit_code


@pytest.mark.supports("S1", "generator", "orchestrator", "Decision")
def test_a_generator_that_asks_ends_with_asks_and_is_resumed_once_the_tree_holds_the_decision(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator running in round 1
    When it gives `asks` on how to type amounts, the tree-keeper writes the decision Decimal, and
    the orchestrator resumes the generator with its ground
    Then the guard lets `asks` end the generator and the resume through, and the run's design tree
    holds the Decimal decision"""
    signed_plan(conv, repo, run)
    _, generator = started(conv, repo, run, "generator", HINTS)
    stopped, reached = gives(generator, repo, "generator", "asks", "How should amounts be typed?")
    assert not stopped.blocked and reached
    _, keeper = started(conv, repo, run, "tree-keeper")
    decimal = decided("How amounts are typed", "Decimal", "maker")
    keeper_writes(
        keeper,
        repo,
        run,
        plan(condition("N3", decided(POINT, "each file", "user"), decimal)),
        "As the code computes with Decimal.",
    )
    resumed = conv.resume(
        generator, "The main conversation's grounds:\nAmounts are Decimal, as the code computes."
    )
    held = json.loads(text_of(os.path.join(run.worktree, run.folder, "design-tree.json")))
    assert not resumed.blocked and generator.running
    assert decimal in held["deliverables"][0]["necessary_conditions"][2]["decisions"]


@pytest.mark.supports("S1", "generator", "orchestrator")
def test_a_generator_that_lacks_a_tool_ends_with_lacks_and_is_resumed_once_cleared(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator running in round 1
    When it gives `lacks` naming mypy, and the orchestrator resumes it once the user installed it
    Then the guard lets `lacks` end it, and lets the resume through"""
    signed_plan(conv, repo, run)
    _, generator = started(conv, repo, run, "generator", HINTS)
    stopped, reached = gives(generator, repo, "generator", "lacks", "mypy isn't installed.")
    resumed = conv.resume(generator, "The main conversation's grounds:\nThe user installed mypy.")
    assert not stopped.blocked and reached and not resumed.blocked


@pytest.mark.supports("S1", "evaluator", "Answers", "Necessary condition", "Round", "adapters")
def test_once_the_generator_is_done_an_evaluator_starts_for_each_group_side_by_side(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator done in round 1, its record and what it made accepted
    When the orchestrator starts an evaluator for each group of the code best practice
    Then each starts beside the others, each with its own group and its own Answers' path in
    round 1"""
    signed_plan(conv, repo, run)
    given, generator = started(conv, repo, run, "generator", HINTS)
    records_all(generator, repo, given, "generator", "code", "refactor-code")
    write(
        run.worktree,
        given["made"],
        json.dumps(
            {"decisions": [{"about": POINT, "where": "invoicer/"}], "more": [], "settled": []}
        ),
    )
    gives(generator, repo, "generator", "done")
    starts = [started(conv, repo, run, "evaluator", HINTS, group) for group in CODE_GROUPS]
    assert [given["group"] for given, _ in starts] == list(CODE_GROUPS)
    assert len({given["answers"] for given, _ in starts}) == 3
    assert all(given["round"] == "1" and agent.running for given, agent in starts)


@pytest.mark.supports("S1", "evaluator", "tree.py", "Place")
def test_an_evaluators_place_commits_its_work_with_its_group_and_step(
    conv: Conversation, repo: Repo, run: Run
):
    """Given an evaluator of the hints' group C1 running, which wrote part of its Answers
    When it keeps its Place at step 2 for its group
    Then tree.py exits 0, and the worktree has nothing left uncommitted"""
    signed_plan(conv, repo, run)
    given, evaluator = started(conv, repo, run, "evaluator", HINTS, "C1")
    evaluator.write(os.path.join(run.worktree, given["answers"]), '{"good": [], "more": []}')
    kept = evaluator.bash(tree(repo, "place", run.folder, HINTS, "evaluator", "2", "C1"))
    assert kept.exit_code == 0 and git(run.worktree, "status", "--porcelain") == ""


@pytest.mark.supports("S1", "orchestrator", "tree.py", "Answers", "Made", "Round", "Sign-off")
def test_the_orchestrator_gets_the_round_and_puts_up_the_points_the_generator_settled(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator done in round 1, what it made naming the point on amounts it
    settled without asking, and the evaluator of C1 done with its Answers
    When the orchestrator runs `tree.py round` on the hints, and puts the hints up with the point
    among the decisions taken without asking
    Then tree.py prints what the generator made with the point settled and the Answers of C1, and
    the run's sign-offs keep the point"""
    signed_plan(conv, repo, run)
    given, generator = started(conv, repo, run, "generator", HINTS)
    records_all(generator, repo, given, "generator", "code", "refactor-code")
    made = {
        "decisions": [{"about": POINT, "where": "invoicer/"}],
        "more": [],
        "settled": [SETTLED],
    }
    write(run.worktree, given["made"], json.dumps(made))
    gives(generator, repo, "generator", "done")
    judged, evaluator = started(conv, repo, run, "evaluator", HINTS, "C1")
    records_all(evaluator, repo, judged, "evaluator")
    met = [{"question": n, "lines": ["invoicer/totals.py:1"]} for n in ("N1", "N2", "N3")]
    write(run.worktree, judged["answers"], json.dumps({"good": met, "more": []}))
    gives(evaluator, repo, "evaluator", "done")
    printed = conv.bash(tree(repo, "round", run.folder, HINTS))
    held = json.loads(printed.output)
    assert printed.exit_code == 0 and held["made"]["settled"] == [SETTLED]
    assert [each["group"] for each in held["answers"]] == ["C1"]
    path = os.path.join(repo.temp, "hints.json")
    sign_off = {"of": HINTS, "can_do": "", "decisions": [DECIMAL], "words": ""}
    conv.write(None, path, json.dumps(sign_off))
    conv.bash(tree(repo, "sign-off", run.folder, path))
    kept = json.loads(text_of(os.path.join(run.worktree, run.folder, "sign-offs.json")))
    assert any(each["of"] == HINTS and DECIMAL in each["decisions"] for each in kept)


@pytest.mark.supports("S1", "orchestrator", "tree-keeper", "More kept", "Round", "Decision")
def test_a_more_the_people_fall_short_by_changes_its_decision_and_reaches_the_next_round(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' round 1 judged, an evaluator naming that callers can't tell a rate from an
    amount
    When the tree-keeper writes the decision it changes and runs `tree.py more` with it, and
    the orchestrator cuts the generator's cut of the hints
    Then the new cut is of round 2, and holds the decision changed and the More kept"""
    signed_plan(conv, repo, run)
    started(conv, repo, run, "generator", HINTS)
    _, keeper = started(conv, repo, run, "tree-keeper")
    rate = decided("How a rate is typed", "a Decimal named Rate", "maker")
    keeper_writes(
        keeper,
        repo,
        run,
        plan(condition("N3", decided(POINT, "each file", "user")), condition("N2", rate)),
        "A rate reads apart from an amount.",
    )
    good_when = "A caller tells a rate by its type."
    kept = keeper.bash(tree(repo, "more", run.folder, HINTS, "N2", good_when))
    given, _ = started(conv, repo, run, "generator", HINTS)
    held = json.loads(text_of(os.path.join(run.worktree, given["cut"])))
    assert kept.exit_code == 0 and given["round"] == "2"
    assert rate in held["decisions"] and held["more"] == [
        {"condition": "N2", "good_when": good_when}
    ]


@pytest.mark.supports("S1", "guard", "generator", "record.py", "Record")
def test_the_guard_holds_a_generators_end_whose_record_lacks_a_step(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator running in round 1, which recorded no step
    When it gives `done`
    Then the guard holds its end, with what rn's check found missing"""
    signed_plan(conv, repo, run)
    _, generator = started(conv, repo, run, "generator", HINTS)
    stopped, reached = gives(generator, repo, "generator", "done")
    assert stopped.blocked and reached is None
    assert "step 1" in stopped.said


@pytest.mark.supports("S1", "orchestrator", "Deliverable")
def test_a_deliverable_the_orchestrator_sends_back_resumes_its_generator(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator done in round 1, what it made naming no place for one decision
    When the orchestrator resumes it with the ground
    Then the guard lets the resume through, and the generator runs again in round 1"""
    signed_plan(conv, repo, run)
    given, generator = started(conv, repo, run, "generator", HINTS)
    records_all(generator, repo, given, "generator", "code", "refactor-code")
    gives(generator, repo, "generator", "done")
    resumed = conv.resume(
        generator, "The main conversation's grounds:\nThe hints of tax.py are missing."
    )
    assert not resumed.blocked and generator.running


@pytest.mark.supports("S1", "evaluator", "Answers")
def test_an_evaluators_end_is_held_until_its_answers_name_each_condition_of_its_group(
    conv: Conversation, repo: Repo, run: Run
):
    """Given an evaluator of the hints' group C1 running, which recorded each step
    When it writes Answers that leave N2 unanswered, and gives `done`
    Then the guard holds its end, naming N2"""
    signed_plan(conv, repo, run)
    given, evaluator = started(conv, repo, run, "evaluator", HINTS, "C1")
    records_all(evaluator, repo, given, "evaluator")
    evaluator.write(
        os.path.join(run.worktree, given["answers"]),
        json.dumps({"good": [{"question": "N1", "lines": ["invoicer/totals.py:1"]}], "more": []}),
    )
    stopped, _ = gives(evaluator, repo, "evaluator", "done")
    assert stopped.blocked and "N2" in stopped.said
