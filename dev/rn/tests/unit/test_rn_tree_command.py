"""The unit cases of tree/command.py, tree.py's command line: what each command takes and gives with
its exit code. The cases take each command that a role or the orchestrator runs, through `main`,
with its input in form, a refusal of the input, something outside the work missing, a check that
can't run, and a command line out of form."""

from __future__ import annotations

import io
import json
import os
from typing import Any

import pytest
from tree import practices, rounds
from tree.command import main

from dev.rn.tests.unit import rn_data as d

CHANGE = pytest.mark.xfail(
    strict=True, raises=NotImplementedError, reason="tree.py write's change has an empty body"
)
ROUND = pytest.mark.xfail(
    strict=True, raises=NotImplementedError, reason="tree.py round has an empty body"
)


def run(argv: list[str], cwd: str, given: Any = "") -> tuple[int, str, str]:
    """tree.py with the arguments, in the folder, with the JSON or text given on its standard
    input."""
    text = given if isinstance(given, str) else json.dumps(given)
    return main(argv, io.StringIO(text), cwd, d.RN)


def started(tmp: Any) -> tuple[str, dict[str, Any]]:
    """A repository with a run started by tree.py start; gives the repository, and what tree.py
    start printed."""
    repo = d.repository(str(tmp))
    code, out, err = run(["start", "type hints for invoicer"], repo)
    assert code == 0, err
    return repo, json.loads(out)


@pytest.mark.supports("test_a_request_starts_a_run_anew_with_the_tree_keepers_start_first")
def test_start_gives_the_worktree_the_folder_and_the_orchestrators_record(tmp_path: Any) -> None:
    """Given: a repository with no run.
    When: tree.py start "type hints for invoicer" runs at its root.
    Then: it gives 0 and the run's worktree, its folder, and the orchestrator's record, each
    there."""
    repo, printed = started(tmp_path)
    assert set(printed) == {"worktree", "folder", "record"}
    assert os.path.isdir(os.path.join(printed["worktree"], printed["folder"]))
    assert os.path.dirname(printed["worktree"]) == os.path.join(repo, ".claude", "worktrees")


@CHANGE
@pytest.mark.supports("test_the_goal_and_the_plan_reach_the_design_tree_through_the_tree_keeper")
def test_write_takes_a_change_and_gives_what_changed_touched_and_doing(tmp_path: Any) -> None:
    """Given: a run started.
    When: tree.py write runs in its worktree with the walkthrough's tree as the change.
    Then: it gives 0 with what changed, each node touched, and no deliverable doing, and commits
    the design tree."""
    _, printed = started(tmp_path)
    change = {"nodes": d.walkthrough_tree(), "more": []}
    code, out, err = run(["write", printed["record"], "The plan."], printed["worktree"], change)
    assert code == 0, err
    wrote = json.loads(out)
    assert set(wrote) == {"changed", "touched", "doing"} and wrote["doing"] == []
    assert "design-tree.json" in d.git(printed["worktree"], "show", "--name-only", "HEAD")


@CHANGE
@pytest.mark.supports("test_a_settled_decisions_ground_is_the_message_of_its_commit")
def test_write_commits_the_change_with_its_ground_as_the_message(tmp_path: Any) -> None:
    """Given: a run started.
    When: tree.py write runs with the walkthrough's tree as the change and a ground of two lines.
    Then: it gives 0, and the worktree's last commit holds the design tree with the ground word
    for word as its message."""
    _, printed = started(tmp_path)
    ground = "The user confirmed the goal.\nThe plan follows the user's answer on which files."
    change = {"nodes": d.walkthrough_tree(), "more": []}
    code, _, err = run(["write", printed["record"], ground], printed["worktree"], change)
    assert code == 0, err
    assert d.git(printed["worktree"], "log", "-1", "--format=%B").strip() == ground
    assert "design-tree.json" in d.git(printed["worktree"], "show", "--name-only", "HEAD")


@pytest.mark.supports("test_a_settled_decisions_ground_is_the_message_of_its_commit")
@pytest.mark.parametrize("ground", ["", "   "])
def test_write_with_no_ground_gives_1_and_commits_nothing(tmp_path: Any, ground: str) -> None:
    """Given: a run started.
    When: tree.py write runs with the walkthrough's tree as the change and an empty ground, or one
    of spaces alone.
    Then: it gives 1 with what's wrong, and makes no commit."""
    _, printed = started(tmp_path)
    head = d.git(printed["worktree"], "rev-parse", "HEAD")
    change = {"nodes": d.walkthrough_tree(), "more": []}
    code, out, err = run(["write", printed["record"], ground], printed["worktree"], change)
    assert (code, out) == (1, "") and err
    assert d.git(printed["worktree"], "rev-parse", "HEAD") == head


@CHANGE
@pytest.mark.supports("test_tree_py_refuses_a_change_that_leaves_the_design_trees_form")
@pytest.mark.parametrize(
    "given",
    [
        "not JSON",
        {"nodes": {}},
        {"nodes": {"goals": 1}, "more": []},
        {"nodes": [], "more": []},
        {"nodes": {}, "more": [{"deliverable": "invoicer"}]},
        {
            "nodes": {},
            "more": [{"deliverable": "invoicer", "condition": "N2", "good_when": "Typed."}],
        },
    ],
)
def test_write_out_of_form_gives_1_with_whats_wrong(tmp_path: Any, given: Any) -> None:
    """Given: a run started.
    When: tree.py write runs with input that isn't JSON, lacks more, names no node, holds nodes
    that aren't an object, a more without its condition and good_when, or one without its best
    practice and decision.
    Then: it gives 1 with what's wrong, and prints nothing on standard output."""
    _, printed = started(tmp_path)
    code, out, err = run(["write", printed["record"], "The plan."], printed["worktree"], given)
    assert (code, out) == (1, "") and err


@pytest.mark.supports("test_each_steps_end_commits_the_work_with_its_place")
def test_commit_keeps_the_place_and_commits(tmp_path: Any) -> None:
    """Given: a run started, and a new file in its worktree.
    When: tree.py commit runs with the orchestrator's record and step 1.
    Then: it gives 0, and the worktree's last commit holds the file, with a message naming the
    record and step 1."""
    _, printed = started(tmp_path)
    open(os.path.join(printed["worktree"], "invoicer", "py.typed"), "w").close()
    code, _, err = run(["commit", printed["record"], "1"], printed["worktree"])
    assert code == 0, err
    assert "invoicer/py.typed" in d.git(printed["worktree"], "show", "--name-only", "HEAD")
    message = d.git(printed["worktree"], "log", "-1", "--format=%B")
    assert printed["record"] in message and "1" in message


@pytest.mark.supports("test_each_steps_end_commits_the_work_with_its_place")
@pytest.mark.parametrize(
    ("argv", "at_root"),
    [
        (["commit", "{record}", "one"], False),
        (["put-up", "nothing"], False),
        (["put-up", "plan", "more"], False),
        (["approve"], True),
    ],
)
def test_arguments_out_of_form_or_a_folder_in_no_run_give_1(
    tmp_path: Any, argv: list[str], at_root: bool
) -> None:
    """Given: a run started.
    When: tree.py commit runs with a step that isn't a number, put-up with a kind it doesn't take
    or a word too many, or approve at the repository's root, which lies in no run's worktree.
    Then: it gives 1 with what's wrong, and prints nothing on standard output."""
    repo, printed = started(tmp_path)
    given = [each.format(record=printed["record"]) for each in argv]
    code, out, err = run(given, repo if at_root else printed["worktree"])
    assert (code, out) == (1, "") and err


@pytest.mark.supports("test_up_alone_with_no_run_left_says_so_and_starts_no_role")
@pytest.mark.parametrize("count", [0, 1])
def test_runs_gives_each_run_left(tmp_path: Any, count: int) -> None:
    """Given: a repository with no run, or one.
    When: tree.py runs runs at its root.
    Then: it gives 0 and each run left, with its name, worktree, and record."""
    repo = d.repository(str(tmp_path)) if count == 0 else started(tmp_path)[0]
    code, out, err = run(["runs"], repo)
    assert code == 0, err
    left = json.loads(out)
    assert len(left) == count and all(set(r) == {"name", "worktree", "record"} for r in left)


@pytest.mark.supports("test_a_push_without_a_remote_says_what_is_missing")
def test_push_with_no_remote_gives_1_with_whats_missing(tmp_path: Any) -> None:
    """Given: a run started in a repository with no remote.
    When: tree.py push runs.
    Then: it gives 1, naming the remote."""
    _, printed = started(tmp_path)
    code, _, err = run(["push"], printed["worktree"])
    assert code == 1 and "remote" in err


@CHANGE
@pytest.mark.supports("test_a_sign_off_pushes_the_work_and_keeps_a_draft_pull_request")
def test_put_up_plan_and_approve_give_the_sign_off(tmp_path: Any) -> None:
    """Given: a run started with the walkthrough's tree.
    When: tree.py put-up plan runs, then tree.py approve, then tree.py approve again.
    Then: the first two give 0 with the plan waiting and then signed off, and the third gives 1,
    as no sign-off waits."""
    _, printed = started(tmp_path)
    run(
        ["write", printed["record"], "The plan."],
        printed["worktree"],
        {"nodes": d.walkthrough_tree(), "more": []},
    )
    code, out, _ = run(["put-up", "plan"], printed["worktree"])
    assert code == 0 and json.loads(out)["state"] == "waiting"
    code, out, _ = run(["approve"], printed["worktree"])
    assert code == 0 and json.loads(out)["state"] == "signed off"
    assert run(["approve"], printed["worktree"])[0] == 1


@pytest.mark.supports("test_a_lesson_sent_back_opens_no_issue")
def test_put_up_lesson_takes_its_words_from_standard_input(tmp_path: Any) -> None:
    """Given: a run started.
    When: tree.py put-up lesson runs with the lesson's words on standard input, then send-back.
    Then: each gives 0, with the lesson's words word for word, waiting and then sent back."""
    _, printed = started(tmp_path)
    lesson = "The code best practice says nothing of py.typed."
    code, out, _ = run(["put-up", "lesson"], printed["worktree"], lesson)
    assert code == 0 and json.loads(out)["what"] == lesson
    code, out, _ = run(["send-back"], printed["worktree"])
    assert code == 0 and json.loads(out)["state"] == "sent back"


@pytest.mark.supports("test_dn_where_git_cant_push_commits_and_says_what_is_missing")
def test_pause_with_no_remote_commits_and_says_it_didnt_push(tmp_path: Any) -> None:
    """Given: a run started in a repository with no remote.
    When: tree.py pause runs with the orchestrator standing at step 1.
    Then: it gives 1, saying it committed but didn't push, and naming the remote."""
    _, printed = started(tmp_path)
    stood = {"stood": [{"record": printed["record"], "step": 1}]}
    code, _, err = run(["pause"], printed["worktree"], stood)
    assert code == 1 and "committed" in err and "remote" in err


@CHANGE
@pytest.mark.supports("test_the_round_gives_each_evaluators_answers_and_what_the_generator_made")
def test_round_of_a_deliverable_with_no_round_gives_1(tmp_path: Any) -> None:
    """Given: a run started with the walkthrough's tree.
    When: tree.py round invoicer runs, which has no round.
    Then: it gives 1 with what's wrong."""
    _, printed = started(tmp_path)
    run(
        ["write", printed["record"], "The plan."],
        printed["worktree"],
        {"nodes": d.walkthrough_tree(), "more": []},
    )
    code, out, err = run(["round", "invoicer"], printed["worktree"])
    assert (code, out) == (1, "") and err


@ROUND
@pytest.mark.supports("test_the_round_gives_each_evaluators_answers_and_what_the_generator_made")
def test_a_design_tree_that_cant_be_read_gives_2(tmp_path: Any) -> None:
    """Given: a run started whose design-tree.json is a folder.
    When: tree.py round invoicer runs.
    Then: it gives 2 with why it couldn't run."""
    _, printed = started(tmp_path)
    os.makedirs(os.path.join(printed["worktree"], printed["folder"], "design-tree.json"))
    code, _, err = run(["round", "invoicer"], printed["worktree"])
    assert code == 2 and err


@ROUND
@pytest.mark.supports("test_the_round_gives_each_evaluators_answers_and_what_the_generator_made")
def test_round_names_the_best_practice_of_each_answers(tmp_path: Any) -> None:
    """Given: a run whose invoicer has one round, with its Made and the Answers of its first group
    and of its last, committed.
    When: tree.py round invoicer runs.
    Then: it gives 0 with the round, its Made, and each Answers in the form the evaluator wrote,
    the first naming the code best practice and the last refactor-code."""
    run_ = d.run_of(d.repository(str(tmp_path)))
    d.tree_written(run_, d.with_status(d.walkthrough_tree(), "doing", "doing"))
    d.write_json(os.path.join(run_.worktree, rounds.made_path(run_, "invoicer", True)), d.made())
    last = len(practices.judged_by(run_, d.RN, "code")) - 1
    for group in (0, last):
        path = os.path.join(run_.worktree, rounds.answers_path(run_, "invoicer", group))
        d.write_json(path, d.answers(["N1"]))
    d.git(run_.worktree, "add", "-A")
    d.git(run_.worktree, "commit", "-q", "-m", "A round")
    code, out, err = run(["round", "invoicer"], run_.worktree)
    assert code == 0, err
    (given,) = json.loads(out)
    assert given["number"] == 1 and given["made"]["decisions"] == d.made()["decisions"]
    assert [a["best_practice"] for a in given["answers"]] == ["code", "refactor-code"]
    assert all(a["good"] == d.answers(["N1"])["good"] for a in given["answers"])


@pytest.mark.supports("test_a_request_starts_a_run_anew_with_the_tree_keepers_start_first")
@pytest.mark.parametrize(
    "argv", [[], ["unknown"], ["start"], ["commit", "record.json"], ["write", "record.json"]]
)
def test_a_command_line_out_of_form_gives_2_with_the_usage(tmp_path: Any, argv: list[str]) -> None:
    """Given: a repository.
    When: tree.py runs with no command, one it doesn't know, or one lacking its arguments.
    Then: it gives 2 with the usage."""
    code, out, err = run(argv, d.repository(str(tmp_path)))
    assert (code, out) == (2, "") and "usage" in err
