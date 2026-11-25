"""The unit cases of tree/command.py, tree's command line, through `main`: `touched` with a
pointer and without, of none, one, and two changes; `check` of a tree in form, as committed,
changed, or as a run starts, of one with faults, out of its schema, and of none; `commit` of a
change in form, of one out of it, and of none, of the tree a run starts from, refused by a commit
check, with no pruner's result or one out of its form, of an open plan asking nothing or asking,
with a stray git holds, as the tree changed or not, and one it doesn't or outside the worktree, and
after a Round's point or findings, which it marks weighed; `next` while the goal is open, of an
open plan, of open decisions, of the first generator, of a deliverable whose input is done, after
a made, of a point open, unweighed, and weighed, of a judged Round unweighed and weighed, of a
Round and an evaluator a pause stopped, with --restart and without, past the limit with no
decision open, with a proposal before its put-up and after, and with a point of a good condition,
of each deliverable done, and with more than --restart; `fix` of a deliverable whose Rounds are
over, a Fix after a Fix fixed, and refused where its Rounds aren't over, a Fix waits on its fixer
or on the pruner, the source or the words are wrong, or the path is of no deliverable; `next`
after a Fix, of a fixer a pause stopped, of a Fix fixed, and of a done deliverable's Fix; `commit`
after a fixer's decision, and of a Fix that waits on no pruner; `signoff` of the plan, of a
deliverable with its findings left, leaving a deliverable open and leaving each done, each
committing and asking gh nothing, and of none waiting; a run's folder out of its form or with no
design tree; and arguments other than the usage's. Each runs in the user's repository, the run's
worktree a git worktree on the work's branch, with a host that runs git for real."""

from __future__ import annotations

import json
import os
from typing import Any

import pytest
import rn_files
from gh import gh_double
from repo_files import git
from rn_files import COMMAND, GOAL, GUIDE, RN
from rn_runs import hook
from tree.command import RESTART, USAGE, main

NAME = "20261120-a-command-with-which-the"
BRANCH = f"rn-{NAME}"
TAX = rn_files.decision(rn_files.TAX_ABOUT, rn_files.TAX_ANSWER, "user")


class Run:
    """The user's repository, invoicer, with the walkthrough's run: its worktree on the work's
    branch from main, and its design tree there, committed or not."""

    def __init__(self, tmp: str, design_tree: dict[str, Any], committed: bool = True):
        self.repo = rn_files.repository(os.path.join(tmp, "invoicer"))
        self.worktree = rn_files.worktree_of(self.repo, NAME)
        git(self.repo, "worktree", "add", "-q", "-b", BRANCH, self.worktree, "main")
        self.folder = rn_files.folder_of(self.repo, NAME)
        self.tree_path = os.path.join(self.folder, "design-tree.json")
        self.write(design_tree)
        if committed:
            git(self.worktree, "add", "-A")
            git(self.worktree, "commit", "-q", "-m", "The plan.")

    @property
    def run(self) -> str:
        """The run's folder from the repository's top, as tree takes it."""
        return os.path.relpath(self.folder, self.repo)

    def write(self, design_tree: dict[str, Any]) -> None:
        """Writes the run's design tree."""
        rn_files.write_json(self.tree_path, design_tree)

    def tree(self) -> Any:
        """The run's design tree as it stands."""
        return rn_files.read_json(self.tree_path)

    def head(self) -> str:
        """The work's branch's last commit."""
        return git(self.worktree, "rev-parse", "HEAD").strip()

    def round(self, deliverable: str, stage: str, number: int) -> str:
        """The Round's folder."""
        return rn_files.round_of(self.folder, deliverable, stage, number)

    def main(self, host: Any, *argv: str, stdin: str = "") -> tuple[int, str, str]:
        """tree with the arguments, from the repository's top, given stdin."""
        return main(list(argv), self.repo, RN, host, lambda: stdin)


def walkthrough(**given: Any) -> dict[str, Any]:
    """The walkthrough's tree, the command's N1 holding the user's answer about the tax rate."""
    return rn_files.walkthrough_tree(NAME, command_decisions={"N1": [TAX]}, **given)


def refused(result: tuple[int, str, str], *words: str) -> None:
    """The result is 1 with `tree: ` and each of the words on stderr, and nothing on stdout."""
    code, out, err = result
    assert (code, out) == (1, ""), result
    assert err.startswith("tree: "), err
    for each in words:
        assert each in err, err


# The usage


@pytest.mark.parametrize(
    "argv",
    [
        [],
        ["nothing", "x"],
        ["touched"],
        ["touched", "x", "/goal", "more"],
        ["check"],
        ["check", "x", "more"],
        ["commit"],
        ["commit", "x", "a ground"],
        ["next"],
        ["next", "x", "--restart", "more"],
        ["fix", "x", COMMAND],
        ["fix", "x", COMMAND, "put-up", "more"],
        ["signoff"],
    ],
)
def test_arguments_other_than_the_usages_give_2_with_it(tmp_path: Any, host: Any, argv: list[str]):
    """Given the walkthrough's run
    When tree runs with no arguments, an unknown subcommand, or a subcommand short of or past
    its arguments
    Then it gives 2 with the usage, and changes nothing"""
    r = Run(str(tmp_path), walkthrough())
    head = r.head()
    code, out, err = r.main(host, *argv)
    assert code == 2
    assert USAGE in out + err
    assert r.head() == head


# touched


def test_touched_with_a_pointer_prints_each_node_it_touches_a_line(tmp_path: Any, host: Any):
    """Given the walkthrough's run
    When tree touched runs with the pointer of the command's N1's decision
    Then it gives 0 printing the goal, the command, its N1, and the guide, from the goal down, a
    pointer a line"""
    r = Run(str(tmp_path), walkthrough())
    got = r.main(host, "touched", r.run, "/deliverables/1/necessary_conditions/0/decisions/0")
    lines = [
        "/goal",
        "/deliverables/1",
        "/deliverables/1/necessary_conditions/0",
        "/deliverables/2",
    ]
    assert got == (0, "".join(f"{each}\n" for each in lines), "")


def test_touched_with_a_pointer_of_a_path_changed_since_the_commit_follows_the_old_path(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run whose tree, since its last commit, gives the command the path
    invoicer/cli.py, the guide's input still naming invoicer/__main__.py
    When tree touched runs with the pointer of the command's path
    Then it gives 0 printing the goal, the command, and the guide by the command's old path, a
    pointer a line"""
    r = Run(str(tmp_path), walkthrough())
    changed = r.tree()
    changed["deliverables"][1]["path"] = "invoicer/cli.py"
    r.write(changed)
    got = r.main(host, "touched", r.run, "/deliverables/1/path")
    lines = ["/goal", "/deliverables/1", "/deliverables/2"]
    assert got == (0, "".join(f"{each}\n" for each in lines), "")


def test_touched_with_a_pointer_of_no_node_gives_1_naming_it(tmp_path: Any, host: Any):
    """Given the walkthrough's run, of three deliverables
    When tree touched runs with the pointer of a fourth
    Then it gives 1 naming the pointer"""
    r = Run(str(tmp_path), walkthrough())
    refused(r.main(host, "touched", r.run, "/deliverables/3"), "/deliverables/3")


def test_touched_of_a_change_since_the_commit_prints_what_it_touches(tmp_path: Any, host: Any):
    """Given the walkthrough's run, its tree committed, then the user's answer about the tax rate
    changed in the tree
    When tree touched runs with no pointer
    Then it gives 0 printing the goal, the command, its N1, the decision, and the guide, the changed
    decided left out"""
    r = Run(str(tmp_path), walkthrough())
    changed = r.tree()
    changed["deliverables"][1]["necessary_conditions"][0]["decisions"][0]["decided"] = "Once."
    r.write(changed)
    lines = [
        "/goal",
        "/deliverables/1",
        "/deliverables/1/necessary_conditions/0",
        "/deliverables/1/necessary_conditions/0/decisions/0",
        "/deliverables/2",
    ]
    assert r.main(host, "touched", r.run) == (0, "".join(f"{each}\n" for each in lines), "")


def test_touched_of_a_decision_taken_away_prints_what_its_condition_touches(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run, its tree committed, then the user's answer about the tax rate
    taken out of the tree
    When tree touched runs with no pointer
    Then it gives 0 printing what the command's N1, which held the answer, touches: the goal, the
    command, its N1, and the guide"""
    r = Run(str(tmp_path), walkthrough())
    changed = r.tree()
    del changed["deliverables"][1]["necessary_conditions"][0]["decisions"][0]
    r.write(changed)
    lines = [
        "/goal",
        "/deliverables/1",
        "/deliverables/1/necessary_conditions/0",
        "/deliverables/2",
    ]
    assert r.main(host, "touched", r.run) == (0, "".join(f"{each}\n" for each in lines), "")


def test_touched_of_a_deliverable_taken_away_prints_the_goal(tmp_path: Any, host: Any):
    """Given the walkthrough's run, its tree committed, then the guide, its last deliverable, taken
    out of the tree
    When tree touched runs with no pointer
    Then it gives 0 printing the goal, the nearest node above the guide that the tree still holds"""
    r = Run(str(tmp_path), walkthrough())
    changed = r.tree()
    del changed["deliverables"][2]
    r.write(changed)
    assert r.main(host, "touched", r.run) == (0, "/goal\n", "")


def test_touched_of_two_changes_prints_each_node_once_leaving_each_change_out(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run, its tree committed, then the tax rate's answer and the guide's
    N1's good both changed
    When tree touched runs with no pointer
    Then it gives 0 printing each node that either touches once, and neither change"""
    r = Run(str(tmp_path), walkthrough())
    changed = r.tree()
    changed["deliverables"][1]["necessary_conditions"][0]["decisions"][0]["decided"] = "Once."
    changed["deliverables"][2]["necessary_conditions"][0]["good"] = True
    r.write(changed)
    code, out, err = r.main(host, "touched", r.run)
    printed = out.splitlines()
    assert (code, err) == (0, "")
    assert len(printed) == len(set(printed))
    assert sorted(printed) == sorted(
        [
            "/goal",
            "/deliverables/1",
            "/deliverables/1/necessary_conditions/0",
            "/deliverables/1/necessary_conditions/0/decisions/0",
            "/deliverables/2",
            "/deliverables/2/necessary_conditions/0",
        ]
    )


def test_touched_of_no_change_since_the_commit_prints_nothing(tmp_path: Any, host: Any):
    """Given the walkthrough's run, its tree as committed
    When tree touched runs with no pointer
    Then it gives 0 printing nothing"""
    r = Run(str(tmp_path), walkthrough())
    assert r.main(host, "touched", r.run) == (0, "", "")


# check


@pytest.mark.parametrize("committed", [True, False], ids=["committed", "changed"])
def test_check_of_a_tree_in_form_gives_0_printing_nothing(
    tmp_path: Any, host: Any, committed: bool
):
    """Given the walkthrough's run whose tree is as committed, or changed by a decision settled in
    the guide's N1 and not committed
    When tree check runs
    Then it gives 0 printing nothing, the tree and the branch's last commit as they were"""
    r = Run(str(tmp_path), walkthrough())
    if not committed:
        changed = r.tree()
        changed["deliverables"][2]["necessary_conditions"][0]["decisions"].append(
            rn_files.decision("its people", "The accounting team.", "reasoning")
        )
        r.write(changed)
    before, tree = r.head(), r.tree()
    assert r.main(host, "check", r.run) == (0, "", "")
    assert (r.head(), r.tree()) == (before, tree)


def test_check_of_the_tree_a_run_starts_from_gives_0(tmp_path: Any, host: Any):
    """Given a run's worktree whose design tree is as the run starts, its goal open, never
    committed
    When tree check runs
    Then it gives 0 printing nothing, as the tree's checks take the goal open"""
    r = Run(str(tmp_path), rn_files.started(NAME), committed=False)
    assert r.main(host, "check", r.run) == (0, "", "")


def test_check_of_a_tree_with_two_faults_gives_1_with_each_on_a_line(tmp_path: Any, host: Any):
    """Given the walkthrough's run, its tree changed so that the command's kind is `lights` and the
    guide's input names a file that the worktree doesn't hold
    When tree check runs
    Then it gives 1 printing two lines, the first naming /deliverables/1/kind and the second
    /deliverables/2/inputs/0, nothing on stderr, and the tree and the branch's last commit as they
    were"""
    r = Run(str(tmp_path), walkthrough())
    changed = r.tree()
    changed["deliverables"][1]["kind"] = "lights"
    changed["deliverables"][2]["inputs"] = ["docs/missing.md"]
    r.write(changed)
    before = r.head()
    code, out, err = r.main(host, "check", r.run)
    assert (code, err) == (1, "")
    lines = out.splitlines()
    assert len(lines) == 2 and out.endswith("\n")
    assert lines[0].startswith("/deliverables/1/kind: ")
    assert lines[1].startswith("/deliverables/2/inputs/0: names docs/missing.md")
    assert (r.head(), r.tree()) == (before, changed)


def test_check_of_a_tree_out_of_its_schema_gives_1_with_its_place(tmp_path: Any, host: Any):
    """Given the walkthrough's run, its tree changed so that the goal holds no `by`
    When tree check runs
    Then it gives 1 with a line naming /goal"""
    r = Run(str(tmp_path), walkthrough())
    changed = r.tree()
    del changed["goal"]["by"]
    r.write(changed)
    code, out, _ = r.main(host, "check", r.run)
    assert code == 1
    assert "/goal" in out


def test_check_of_a_run_with_no_design_tree_gives_1_naming_it(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose design tree was deleted
    When tree check runs
    Then it gives 1 with `tree: ` and that the run's folder holds no design tree on stderr"""
    r = Run(str(tmp_path), walkthrough())
    os.remove(r.tree_path)
    refused(r.main(host, "check", r.run), "holds no design tree")


# commit


PRUNER = "pruner.json"
QUESTION = (
    "Should a line with no quantity count once? I recommend counting it once, as the accountant"
    " prints such lines."
)
ASK = {
    "deliverable": COMMAND,
    "condition": "N1",
    "about": "a line's quantity",
    "question": QUESTION,
}


def weighed_by_pruner(r: Run, **given: Any) -> str:
    """Writes the pruner's result in the run's folder, as the pruner writes it as it ends, with
    what's given; gives its path."""
    path = os.path.join(r.folder, PRUNER)
    rn_files.write_json(path, rn_files.pruner_result(**given))
    return path


def guide_decided(r: Run) -> None:
    """Writes the run's tree with a decision settled by reasoning in the guide's N1."""
    changed = r.tree()
    changed["deliverables"][2]["necessary_conditions"][0]["decisions"].append(
        rn_files.decision("its people", "The accounting team.", "reasoning")
    )
    r.write(changed)


def test_commit_of_a_change_in_form_commits_the_tree_alone_with_the_ground_of_kept(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run, its tree committed, then a decision settled by reasoning in the
    guide's N1, the guide's file written beside it, and the pruner's result keeping that node,
    asking nothing
    When tree commit runs
    Then it gives 0 printing the new commit's hash alone, whose message names the run and then
    the node kept, and which holds the tree alone, the guide left uncommitted; pruner.json is
    gone"""
    r = Run(str(tmp_path), walkthrough())
    guide_decided(r)
    with open(os.path.join(r.worktree, GUIDE), "w", encoding="utf-8") as f:
        f.write("# Print an invoice\n")
    path = weighed_by_pruner(r, kept=["docs/guide.md N1: its people"])
    before = r.head()
    code, out, err = r.main(host, "commit", r.run)
    assert (code, err) == (0, "")
    assert out == f"{r.head()}\n" and r.head() != before
    assert git(r.worktree, "log", "-1", "--format=%B").strip() == (
        f"rn: the design tree of {NAME}, weighed\n\n- docs/guide.md N1: its people"
    )
    held = git(r.worktree, "show", "--name-only", "--format=", "HEAD").split()
    assert held == [os.path.relpath(r.tree_path, r.worktree)]
    assert git(r.worktree, "status", "--porcelain").strip() == f"?? {GUIDE}"
    assert not os.path.exists(path)


def test_commit_of_a_tree_out_of_form_gives_1_with_its_first_fault_leaving_git(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run, its tree committed, then the command's kind made `lights`, and
    the pruner's result
    When tree commit runs
    Then it gives 1 naming /deliverables/1/kind, the branch's last commit as it was, the tree
    still changed, and pruner.json still there"""
    r = Run(str(tmp_path), walkthrough())
    changed = r.tree()
    changed["deliverables"][1]["kind"] = "lights"
    r.write(changed)
    path = weighed_by_pruner(r)
    before = r.head()
    refused(r.main(host, "commit", r.run), "/deliverables/1/kind")
    assert r.head() == before
    assert git(r.worktree, "status", "--porcelain").strip().splitlines() == [
        f"M {os.path.relpath(r.tree_path, r.worktree)}",
        f"?? {os.path.relpath(path, r.worktree)}",
    ]


def test_commit_of_no_change_prints_the_last_commit_committing_nothing(tmp_path: Any, host: Any):
    """Given the walkthrough's run, its tree as committed, and the pruner's result, as the pruner
    cut what its unit asked
    When tree commit runs
    Then it gives 0 printing the last commit's hash, the branch holds no new commit, and
    pruner.json is gone"""
    r = Run(str(tmp_path), walkthrough())
    path = weighed_by_pruner(r, kept=[], cut=["a flag for the currency: they never meet it"])
    before = r.head()
    assert r.main(host, "commit", r.run) == (0, f"{before}\n", "")
    assert r.head() == before
    assert not os.path.exists(path)


def test_commit_of_the_tree_a_run_starts_from_commits_it_first_signing_off_nothing(
    tmp_path: Any, host: Any
):
    """Given a run's worktree whose design tree, as the run starts with its goal open, was never
    committed, and the pruner's result keeping nothing and asking nothing
    When tree commit runs
    Then it gives 0 printing a new commit's hash, whose message is its first line alone, as the
    tree's checks take the goal open, and the plan is still open, as its goal is"""
    r = Run(str(tmp_path), rn_files.started(NAME), committed=False)
    weighed_by_pruner(r, kept=[])
    before = r.head()
    code, out, _ = r.main(host, "commit", r.run)
    assert code == 0
    assert out.strip() == r.head() != before
    assert git(r.worktree, "log", "-1", "--format=%B").strip() == (
        f"rn: the design tree of {NAME}, weighed"
    )
    assert r.tree()["deliverables"][0]["status"] == "open"


def test_commit_that_a_commit_check_refuses_gives_2_with_what_git_said(tmp_path: Any, host: Any):
    """Given the walkthrough's run, its tree committed, then a decision settled in the guide's N1,
    and the pruner's result, in a repository whose pre-commit hook refuses each commit saying
    `tree: no`
    When tree commit runs
    Then it gives 2, nothing on stdout, and stderr naming tree and the hook's line; the branch
    holds no new commit, and pruner.json is still there"""
    r = Run(str(tmp_path), walkthrough())
    hook(r.repo, "echo 'tree: no'\nexit 1\n")
    guide_decided(r)
    path = weighed_by_pruner(r)
    before = r.head()
    code, out, err = r.main(host, "commit", r.run)
    assert (code, out) == (2, "")
    assert err.startswith("tree: ") and "tree: no" in err
    assert r.head() == before
    assert os.path.isfile(path)


def test_commit_with_no_pruners_result_gives_1_naming_it(tmp_path: Any, host: Any):
    """Given the walkthrough's run, its tree changed since its commit, and no pruner's result
    When tree commit runs
    Then it gives 1 naming pruner.json and saying the pruner writes it, and the branch holds no
    new commit"""
    r = Run(str(tmp_path), walkthrough())
    guide_decided(r)
    before = r.head()
    refused(r.main(host, "commit", r.run), PRUNER, "the pruner writes it")
    assert r.head() == before


@pytest.mark.parametrize(
    ("written", "said"),
    [
        ("{", "isn't JSON"),
        ('{"kept": []}', "/cut: is required"),
        (
            json.dumps(rn_files.pruner_result(ask=[{**ASK, "question": "Count it once?"}])),
            "/ask/0/question: takes a string that matches",
        ),
        (json.dumps(rn_files.pruner_result(changed=["one\ttwo"])), "/changed/0: takes a string"),
        (json.dumps(rn_files.pruner_result(stray=["a\nb"])), "/stray/0: takes a string"),
    ],
    ids=["not JSON", "a list left out", "no recommendation", "a tab", "a line break"],
)
def test_commit_of_a_pruners_result_out_of_its_form_gives_1_naming_the_place(
    tmp_path: Any, host: Any, written: str, said: str
):
    """Given the walkthrough's run, its tree changed since its commit, and a pruner's result that
    isn't JSON, leaves out a list, asks a question with no recommendation, or holds a tab or a line
    break in a line
    When tree commit runs
    Then it gives 1 naming pruner.json and the place, the branch holds no new commit, and the
    tree and pruner.json are as they were"""
    r = Run(str(tmp_path), walkthrough())
    guide_decided(r)
    before, tree = r.head(), r.tree()
    path = os.path.join(r.folder, PRUNER)
    with open(path, "w", encoding="utf-8") as f:
        f.write(written)
    refused(r.main(host, "commit", r.run), PRUNER, said)
    assert (r.head(), r.tree()) == (before, tree)
    assert os.path.isfile(path)


def test_commit_of_an_open_plan_asking_nothing_signs_it_off_in_the_same_commit(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run whose plan is open, its goal settled, and the pruner's result
    asking nothing
    When tree commit runs
    Then it gives 0 printing the hash; the plan is done in the commit, whose message closes with
    `The plan is signed off.`, and the tree has no change since"""
    r = Run(str(tmp_path), walkthrough(plan_done=False), committed=False)
    weighed_by_pruner(r)
    code, out, _ = r.main(host, "commit", r.run)
    assert (code, out) == (0, f"{r.head()}\n")
    assert r.tree()["deliverables"][0]["status"] == "done"
    assert git(r.worktree, "log", "-1", "--format=%B").strip().endswith("The plan is signed off.")
    assert git(r.worktree, "status", "--porcelain", "--", r.tree_path).strip() == ""


def test_commit_of_an_open_plan_with_a_condition_not_good_leaves_it_open(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose plan is open, its goal settled and its N2 not good, as a
    pause mid-hearing leaves it, and the pruner's result asking nothing
    When tree commit runs
    Then it gives 0 printing the new commit's hash, and the plan stays open, as it waits on more
    of the hearing, not on its sign-off"""
    the = walkthrough(plan_done=False)
    the["deliverables"][0]["necessary_conditions"][1]["good"] = False
    r = Run(str(tmp_path), the, committed=False)
    weighed_by_pruner(r)
    assert r.main(host, "commit", r.run)[:2] == (0, f"{r.head()}\n")
    assert r.tree()["deliverables"][0]["status"] == "open"
    assert not git(r.worktree, "log", "-1", "--format=%B").strip().endswith("signed off.")


def test_commit_of_an_open_plan_asking_prints_each_ask_and_change_leaving_the_plan_open(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run whose plan is open, its command's N1 holding an open decision,
    and the pruner's result asking it and naming two steps of its own that it changed
    When tree commit runs
    Then it gives 0 printing the hash, then the ask, and then each change, a line each, its words
    apart by a tab; and the plan stays open"""
    open_point = rn_files.decision("a line's quantity", None)
    the = rn_files.walkthrough_tree(NAME, plan_done=False, command_decisions={"N1": [open_point]})
    r = Run(str(tmp_path), the, committed=False)
    weighed_by_pruner(r, ask=[ASK], changed=["Step 2: read the guide first", "Step 4: once"])
    code, out, _ = r.main(host, "commit", r.run)
    assert code == 0
    assert out.splitlines() == [
        r.head(),
        f"ask\t{COMMAND}\tN1\ta line's quantity\t{QUESTION}",
        "changed\tStep 2: read the guide first",
        "changed\tStep 4: once",
    ]
    assert r.tree()["deliverables"][0]["status"] == "open"


def tracked(r: Run, path: str) -> None:
    """Writes the file in the run's worktree and commits it, as a deliverable put up was."""
    with open(os.path.join(r.worktree, path), "w", encoding="utf-8") as f:
        f.write("# Notes\n")
    git(r.worktree, "add", path)
    git(r.worktree, "commit", "-q", "-m", "Notes.")


@pytest.mark.parametrize("changed", [True, False], ids=["the tree changed", "the tree as it was"])
def test_commit_with_a_stray_removes_it_in_the_trees_commit(
    tmp_path: Any, host: Any, changed: bool
):
    """Given the walkthrough's run whose worktree holds NOTES.md as committed, the tree changed or
    as committed, and the pruner's result naming NOTES.md a stray
    When tree commit runs
    Then it gives 0 printing a new commit's hash, which removes NOTES.md, with the tree where it
    changed; the file is gone, and the worktree holds no change"""
    r = Run(str(tmp_path), walkthrough())
    tracked(r, "NOTES.md")
    if changed:
        guide_decided(r)
    weighed_by_pruner(r, stray=["NOTES.md"])
    before = r.head()
    code, out, _ = r.main(host, "commit", r.run)
    assert (code, out) == (0, f"{r.head()}\n") and r.head() != before
    shown = git(r.worktree, "show", "--name-status", "--format=", "HEAD").splitlines()
    tree = os.path.relpath(r.tree_path, r.worktree)
    assert sorted(shown) == sorted(["D\tNOTES.md", *([f"M\t{tree}"] if changed else [])])
    assert not os.path.exists(os.path.join(r.worktree, "NOTES.md"))
    assert git(r.worktree, "status", "--porcelain").strip() == ""


@pytest.mark.parametrize(
    ("stray", "said"),
    [("DRAFT.md", "git holds no such file"), ("../outside.md", "lies outside the run's worktree")],
    ids=["one git doesn't hold", "one outside the worktree"],
)
def test_commit_with_a_stray_git_doesnt_hold_gives_1_changing_nothing(
    tmp_path: Any, host: Any, stray: str, said: str
):
    """Given the walkthrough's run whose plan is open, its tree as committed, NOTES.md committed,
    and DRAFT.md written but never committed; and the pruner's result asking nothing, naming as
    strays NOTES.md and DRAFT.md, or a path outside the worktree
    When tree commit runs
    Then it gives 1 naming the stray; the branch holds no new commit, NOTES.md and DRAFT.md stay,
    the plan stays open, and pruner.json is still there"""
    r = Run(str(tmp_path), walkthrough(plan_done=False))
    tracked(r, "NOTES.md")
    with open(os.path.join(r.worktree, "DRAFT.md"), "w", encoding="utf-8") as f:
        f.write("# Draft\n")
    path = weighed_by_pruner(r, stray=["NOTES.md", stray])
    before = r.head()
    refused(r.main(host, "commit", r.run), stray, said)
    assert r.head() == before
    assert os.path.isfile(os.path.join(r.worktree, "NOTES.md"))
    assert os.path.isfile(os.path.join(r.worktree, "DRAFT.md"))
    assert r.tree()["deliverables"][0]["status"] == "open"
    assert os.path.isfile(path)


@pytest.mark.parametrize(
    "results",
    [
        {"generator": rn_files.point()},
        {"generator": rn_files.made([], [COMMAND]), "evaluator": rn_files.judged([("N1", ["a"])])},
    ],
    ids=["a point", "a judged Round"],
)
def test_commit_after_a_rounds_result_marks_it_weighed(
    tmp_path: Any, host: Any, results: dict[str, Any]
):
    """Given the walkthrough's run whose command's Round content-1 holds a generator's point, or a
    made and judged Round, unweighed, and the pruner's result
    When tree commit runs
    Then content-1's weighed.json holds the commit's hash"""
    r = Run(str(tmp_path), walkthrough())
    first = rn_files.a_round(r.folder, COMMAND, "content", 1, results)
    unit = os.path.join(first, "evaluator.json" if "evaluator" in results else "generator.json")
    guide_decided(r)
    weighed_by_pruner(r, units=[unit])
    code, out, _ = r.main(host, "commit", r.run)
    assert code == 0
    assert rn_files.read_json(os.path.join(first, "weighed.json")) == {"commit": out.strip()}


def test_commit_leaves_a_round_its_pruner_didnt_weigh_unweighed(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose command's Round content-1 holds an evaluator's findings,
    unweighed, and the pruner's result of another unit, naming no unit
    When tree commit runs, then tree next
    Then the commit gives 0, content-1 holds no weighed.json, and next prints the command's
    pruner with content-1's evaluator.json still"""
    r = Run(str(tmp_path), walkthrough(command_good=["N2", "N3"]))
    first = rn_files.a_round(r.folder, COMMAND, "content", 1, SHORT)
    guide_decided(r)
    weighed_by_pruner(r)
    assert r.main(host, "commit", r.run)[0] == 0
    assert not os.path.exists(os.path.join(first, "weighed.json"))
    assert next_lines(r, host) == [["pruner", COMMAND, os.path.join(first, "evaluator.json")]]


@pytest.mark.parametrize(
    "unit",
    ["evaluator.json", "generator.json", "nothing.json"],
    ids=["a weighed Round's findings", "a made, no unit", "no file"],
)
def test_commit_of_a_unit_next_doesnt_print_gives_1_changing_nothing(
    tmp_path: Any, host: Any, unit: str
):
    """Given the walkthrough's run whose command's Round content-1, judged short, is weighed, and
    the pruner's result naming as its unit content-1's evaluator.json, its generator.json, a made,
    or a file there that doesn't exist
    When tree commit runs
    Then it gives 1 naming the path; the branch holds no new commit, and the tree and pruner.json
    are as they were"""
    r = Run(str(tmp_path), walkthrough(command_good=["N2", "N3"]))
    first = rn_files.a_round(r.folder, COMMAND, "content", 1, {**SHORT, **rn_files.WEIGHED})
    guide_decided(r)
    path = weighed_by_pruner(r, units=[os.path.join(first, unit)])
    before, tree = r.head(), r.tree()
    refused(r.main(host, "commit", r.run), os.path.join(first, unit), "pruner line")
    assert (r.head(), r.tree()) == (before, tree)
    assert os.path.isfile(path)


def test_commit_of_the_findings_left_past_the_limit_takes_the_unit_marking_nothing_anew(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run whose command's evaluators found N1 short in Rounds content-1
    and content-2, each weighed, so that next prints its pruner with content-2's evaluator.json;
    then the pruner keeping the finding as an open decision of N1, and naming that unit
    When tree commit runs
    Then it gives 0, and content-2's weighed.json holds the commit that weighed it before"""
    r = Run(str(tmp_path), walkthrough(command_good=["N2", "N3"]))
    for number in (1, 2):
        rn_files.a_round(r.folder, COMMAND, "content", number, {**SHORT, **rn_files.WEIGHED})
    second = r.round(COMMAND, "content", 2)
    kept = r.tree()
    kept["deliverables"][1]["necessary_conditions"][0]["decisions"] += [TAX, LEFT]
    r.write(kept)
    weighed_by_pruner(r, units=[os.path.join(second, "evaluator.json")])
    assert r.main(host, "commit", r.run)[0] == 0
    assert rn_files.read_json(os.path.join(second, "weighed.json")) == {"commit": "a1b2c3"}


# next


def next_lines(r: Run, host: Any, *more: str) -> list[list[str]]:
    """What tree next prints, each line split at its tabs; it must give 0 with nothing on
    stderr."""
    code, out, err = r.main(host, "next", r.run, *more)
    assert (code, err) == (0, ""), err
    return [each.split("\t") for each in out.splitlines()]


def cut_at(r: Run, line: list[str]) -> str:
    """The absolute path of the Cut that a `start` line names from the repository's top."""
    return os.path.normpath(os.path.join(r.repo, line[3]))


def test_next_while_the_goal_is_open_prints_the_hearing_alone_making_no_round(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run whose goal is open, its decided null
    When tree next runs
    Then it prints `hearing` alone, and makes no Round"""
    the = walkthrough()
    the["goal"] = {"decided": None}
    r = Run(str(tmp_path), the)
    assert next_lines(r, host) == [["hearing"]]
    assert not os.path.exists(os.path.join(r.folder, "rounds"))


def test_next_of_an_open_plan_prints_its_signoff_and_starts_nothing(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose plan is open with each condition good
    When tree next runs
    Then it prints `sign-off`, `plan` alone, as the work that rests on the plan starts at its
    sign-off, and makes no Round"""
    r = Run(str(tmp_path), walkthrough(plan_done=False))
    assert next_lines(r, host) == [["sign-off", "plan"]]
    assert not os.path.exists(os.path.join(r.folder, "rounds"))


def test_next_of_open_decisions_of_the_plan_and_a_deliverable_prints_an_answer_for_each(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run whose plan is open, its N2 not good holding an open decision of
    the steps, and whose command's N1 holds an open decision of a line's quantity
    When tree next runs
    Then it prints an `answer` for the plan's, then one for the command's, and no sign-off"""
    the = rn_files.walkthrough_tree(
        NAME, plan_done=False, command_decisions={"N1": [rn_files.decision("quantity", None)]}
    )
    plan = the["deliverables"][0]
    plan["necessary_conditions"][1]["good"] = False
    plan["necessary_conditions"][1]["decisions"].append(rn_files.decision("the steps", None))
    r = Run(str(tmp_path), the)
    plan_id = plan["necessary_conditions"][1]["id"]
    assert next_lines(r, host) == [
        ["answer", plan["path"], plan_id, "the steps"],
        ["answer", COMMAND, "N1", "quantity"],
    ]


def test_next_of_the_first_generator_writes_its_cut_in_round_content_1(tmp_path: Any, host: Any):
    """Given the walkthrough's run, its plan done and no Round yet, the guide resting on the
    command
    When tree next runs
    Then it prints one `start` line, of the command's generator, with the path of Round
    content-1's generator-cut.json from the repository's top, which holds the command's Cut; and
    nothing of the guide, whose input isn't done"""
    r = Run(str(tmp_path), walkthrough())
    lines = next_lines(r, host)
    path = os.path.join(r.round(COMMAND, "content", 1), "generator-cut.json")
    assert [each[:3] for each in lines] == [["start", "generator", COMMAND]]
    assert cut_at(r, lines[0]) == path
    given = rn_files.read_json(path)
    assert given["goal"] == GOAL
    assert given["deliverable"] == r.tree()["deliverables"][1]
    assert os.path.normpath(os.path.join(r.repo, given["worktree"])) == r.worktree
    assert os.path.normpath(os.path.join(r.repo, given["best_practice"])) == os.path.join(
        RN, "domain", "best-practices", "light"
    )
    assert (given["stage"], given["number"], given["last_good"]) == ("content", 1, None)
    assert "findings" not in given


def test_next_starts_each_deliverable_whose_inputs_are_done_together(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose command is done, and whose guide rests on it, with no
    Round
    When tree next runs
    Then it prints the guide's generator's `start`, as its input is done"""
    the = walkthrough()
    the["deliverables"][1] = rn_files.done_node(rn_files.COMMAND_NAME, COMMAND, "light")
    r = Run(str(tmp_path), the)
    assert [each[:3] for each in next_lines(r, host)] == [["start", "generator", GUIDE]]


def test_next_after_a_generators_made_writes_the_evaluators_cut_in_its_round(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run whose command's generator made Round content-1
    When tree next runs, and again
    Then the first prints the evaluator's `start` with the path of Round content-1's
    evaluator-cut.json, which holds the command's name and path and what light judges by, making
    no Round content-2; the second prints it `running`"""
    r = Run(str(tmp_path), walkthrough())
    rn_files.a_round(r.folder, COMMAND, "content", 1, {"generator": rn_files.made([], [COMMAND])})
    lines = next_lines(r, host)
    path = os.path.join(r.round(COMMAND, "content", 1), "evaluator-cut.json")
    assert [each[:3] for each in lines] == [["start", "evaluator", COMMAND]]
    assert cut_at(r, lines[0]) == path
    given = rn_files.read_json(path)
    assert given["deliverable"] == {"name": rn_files.COMMAND_NAME, "path": COMMAND}
    assert given["judges_by"] == rn_files.judged_by("light")
    assert not os.path.exists(r.round(COMMAND, "content", 2))
    assert next_lines(r, host) == [["running", "evaluator", COMMAND]]


def test_next_of_a_deliverable_with_an_open_point_prints_the_answer_writing_no_cut(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run whose command's generator gave a point in Round content-1, which
    one pruner weighed and kept open in its N1
    When tree next runs
    Then it prints the `answer` of the command's N1 alone, and writes no Cut"""
    the = rn_files.walkthrough_tree(
        NAME, command_decisions={"N1": [rn_files.decision("a line's quantity", None)]}
    )
    r = Run(str(tmp_path), the)
    rn_files.a_round(
        r.folder, COMMAND, "content", 1, {"generator": rn_files.point(), **rn_files.WEIGHED}
    )
    assert next_lines(r, host) == [["answer", COMMAND, "N1", "a line's quantity"]]
    assert not os.path.exists(os.path.join(r.round(COMMAND, "content", 1), "generator-cut.json"))


def test_next_of_a_point_unweighed_prints_a_pruner_with_its_result_writing_no_cut(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run whose command's generator gave a point in Round content-1, which
    no commit weighed yet
    When tree next runs
    Then it prints the `pruner` of the command with the absolute path of content-1's
    generator.json alone, and writes no Cut"""
    r = Run(str(tmp_path), walkthrough())
    first = rn_files.a_round(r.folder, COMMAND, "content", 1, {"generator": rn_files.point()})
    assert next_lines(r, host) == [["pruner", COMMAND, os.path.join(first, "generator.json")]]
    assert not os.path.exists(os.path.join(first, "generator-cut.json"))


def test_next_after_a_point_weighed_writes_the_same_rounds_cut_again_taking_the_point_out(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run whose command's generator gave a point in Round content-1, which
    a commit weighed, the tree holding the user's answer in its N1
    When tree next runs, and again
    Then the first prints the generator's `start` with content-1's generator-cut.json, holding
    the answer by user; content-1 holds no generator.json and no weighed.json, and no Round
    content-2 is made; the second prints it `running`"""
    r = Run(str(tmp_path), walkthrough())
    first = rn_files.a_round(
        r.folder, COMMAND, "content", 1, {"generator": rn_files.point(), **rn_files.WEIGHED}
    )
    lines = next_lines(r, host)
    path = os.path.join(first, "generator-cut.json")
    assert [each[:3] for each in lines] == [["start", "generator", COMMAND]]
    assert cut_at(r, lines[0]) == path
    assert TAX in rn_files.read_json(path)["deliverable"]["necessary_conditions"][0]["decisions"]
    assert sorted(os.listdir(first)) == ["generator-cut.json"]
    assert not os.path.exists(r.round(COMMAND, "content", 2))
    assert next_lines(r, host) == [["running", "generator", COMMAND]]


def test_next_of_a_judged_round_unweighed_prints_a_pruner_with_the_evaluators_result(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run whose command's evaluator judged Round content-1, which no
    commit weighed yet
    When tree next runs
    Then it prints the `pruner` of the command with the absolute path of content-1's
    evaluator.json alone"""
    r = Run(str(tmp_path), walkthrough(command_good=["N2", "N3"]))
    first = rn_files.a_round(r.folder, COMMAND, "content", 1, SHORT)
    assert next_lines(r, host) == [["pruner", COMMAND, os.path.join(first, "evaluator.json")]]


def test_next_after_a_round_judged_short_and_weighed_makes_the_next_round(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose command's evaluator found N1 short in Round content-1,
    weighed, its tree holding N2 and N3 good
    When tree next runs
    Then it prints the generator's `start` with Round content-2's generator-cut.json, which holds
    none of the evaluator's findings, and the generator's good of content-1 as its last good"""
    r = Run(str(tmp_path), walkthrough(command_good=["N2", "N3"]))
    rn_files.a_round(r.folder, COMMAND, "content", 1, {**SHORT, **rn_files.WEIGHED})
    lines = next_lines(r, host)
    path = os.path.join(r.round(COMMAND, "content", 2), "generator-cut.json")
    assert [each[:3] for each in lines] == [["start", "generator", COMMAND]]
    assert cut_at(r, lines[0]) == path
    given = rn_files.read_json(path)
    assert (given["stage"], given["number"]) == ("content", 2)
    assert "findings" not in given
    assert "It prints a comma." not in json.dumps(given)
    assert given["last_good"] == []


def test_next_of_a_round_a_pause_stopped_prints_it_running_and_restarts_it_with_a_fresh_cut(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run whose command's Round content-1 holds the generator's Cut of a
    stale goal and no result, as a pause stopped it
    When tree next runs, then tree next --restart
    Then the first prints the generator `running`, leaving the Cut; the second prints its `start`
    with content-1's generator-cut.json, written anew with the tree's goal, and makes no Round
    content-2"""
    r = Run(str(tmp_path), walkthrough())
    first = rn_files.a_round(r.folder, COMMAND, "content", 1)
    path = os.path.join(first, "generator-cut.json")
    rn_files.write_json(path, {"goal": "stale"})
    assert next_lines(r, host) == [["running", "generator", COMMAND]]
    assert rn_files.read_json(path) == {"goal": "stale"}
    lines = next_lines(r, host, RESTART)
    assert [each[:3] for each in lines] == [["start", "generator", COMMAND]]
    assert cut_at(r, lines[0]) == path
    given = rn_files.read_json(path)
    assert (given["goal"], given["stage"], given["number"]) == (GOAL, "content", 1)
    assert not os.path.exists(r.round(COMMAND, "content", 2))


def test_next_restart_of_an_evaluator_a_pause_stopped_writes_its_cut_in_that_round(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run whose command's Round content-1 holds the generator's made and
    the evaluator's Cut with no result, as a pause stopped it
    When tree next --restart runs
    Then it prints the evaluator's `start` with content-1's evaluator-cut.json, written anew"""
    r = Run(str(tmp_path), walkthrough())
    first = rn_files.a_round(
        r.folder, COMMAND, "content", 1, {"generator": rn_files.made([], [COMMAND])}
    )
    path = os.path.join(first, "evaluator-cut.json")
    rn_files.write_json(path, {"goal": "stale"})
    lines = next_lines(r, host, RESTART)
    assert [each[:3] for each in lines] == [["start", "evaluator", COMMAND]]
    assert cut_at(r, lines[0]) == path
    assert rn_files.read_json(path)["goal"] == GOAL


def test_next_restart_with_none_at_work_prints_as_next_does(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose command's evaluator judged Round content-1, unweighed
    When tree next --restart runs
    Then it prints what tree next prints, the pruner's line"""
    r = Run(str(tmp_path), walkthrough(command_good=["N2", "N3"]))
    rn_files.a_round(r.folder, COMMAND, "content", 1, SHORT)
    assert next_lines(r, host, RESTART) == next_lines(r, host)


LEFT = rn_files.decision("a comma in a line", None)
SHORT = {
    "generator": rn_files.made([], [COMMAND]),
    "evaluator": rn_files.judged([("N2", ["a"]), ("N3", ["b"])], [("N1", "It prints a comma.")]),
}


def test_next_after_two_content_rounds_short_prints_a_pruner_making_no_third(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run whose command's evaluators found N1 short in Rounds content-1 and
    content-2, each weighed, its tree holding N2 and N3 good and no decision open
    When tree next runs
    Then it prints the `pruner` of the command with content-2's evaluator.json, to keep each
    finding left as an open decision, and makes no Round content-3"""
    r = Run(str(tmp_path), walkthrough(command_good=["N2", "N3"]))
    for number in (1, 2):
        rn_files.a_round(r.folder, COMMAND, "content", number, {**SHORT, **rn_files.WEIGHED})
    second = r.round(COMMAND, "content", 2)
    assert next_lines(r, host) == [["pruner", COMMAND, os.path.join(second, "evaluator.json")]]
    assert not os.path.exists(r.round(COMMAND, "content", 3))


def left_past(tmp: str) -> Run:
    """The walkthrough's run whose command's evaluators found N1 short in Rounds content-1 and
    content-2, each weighed, its tree holding N2 and N3 good and the finding left as an open
    decision of N1."""
    the = rn_files.walkthrough_tree(
        NAME, command_good=["N2", "N3"], command_decisions={"N1": [TAX, LEFT]}
    )
    r = Run(tmp, the)
    for number in (1, 2):
        rn_files.a_round(r.folder, COMMAND, "content", number, {**SHORT, **rn_files.WEIGHED})
    return r


def test_next_of_a_deliverable_past_its_rounds_prints_its_put_up_then_its_signoff(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run whose command is past its two content Rounds, its finding kept
    as an open decision, a proposal
    When tree next runs, before content-2 is marked put up with the command's state, and after
    Then the first prints the command's `put-up` alone, asking no answer of the proposal, and the
    second its `sign-off`, at a step that the user checks, as no step says otherwise; neither
    makes a Round content-3"""
    r = left_past(str(tmp_path))
    assert next_lines(r, host) == [["put-up", COMMAND]]
    mark = {"short": ["N1"], "open": [{"condition": "N1", "about": "a comma in a line"}]}
    rn_files.write_json(os.path.join(r.round(COMMAND, "content", 2), "put-up.json"), mark)
    assert next_lines(r, host) == [["sign-off", COMMAND]]
    assert not os.path.exists(r.round(COMMAND, "content", 3))


def test_next_past_the_limit_answers_only_a_point_of_a_good_condition(tmp_path: Any, host: Any):
    """Given the run of `left_past` whose N2, good, holds an open point too
    When tree next runs
    Then it prints the `answer` of N2's point alone, the finding of N1 left as a proposal"""
    r = left_past(str(tmp_path))
    the = r.tree()
    the["deliverables"][1]["necessary_conditions"][1]["decisions"].append(
        rn_files.decision("the currency", None)
    )
    r.write(the)
    assert next_lines(r, host) == [["answer", COMMAND, "N2", "the currency"]]


def test_next_of_each_deliverable_done_prints_the_final_check(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose plan, command, and guide are done, the command's last
    Round put up
    When tree next runs
    Then it prints `final-check` alone"""
    the = walkthrough()
    the["deliverables"][1] = rn_files.done_node(rn_files.COMMAND_NAME, COMMAND, "light")
    the["deliverables"][2] = rn_files.done_node(rn_files.GUIDE_NAME, GUIDE, "readme")
    r = Run(str(tmp_path), the)
    rn_files.a_round(r.folder, COMMAND, "content", 1, {**JUDGED_GOOD, **rn_files.WEIGHED})
    assert next_lines(r, host) == [["final-check"]]


@pytest.mark.parametrize("more", [["again"], ["--restart", "again"]], ids=["a word", "two"])
def test_next_with_more_than_restart_gives_2_with_the_usage(
    tmp_path: Any, host: Any, more: list[str]
):
    """Given the walkthrough's run
    When tree next runs with a word other than --restart after the run, or with two
    Then it gives 2 with the usage, and makes no Round"""
    r = Run(str(tmp_path), walkthrough())
    code, out, err = r.main(host, "next", r.run, *more)
    assert code == 2 and USAGE in out + err
    assert not os.path.exists(os.path.join(r.folder, "rounds"))


# fix, and the fixer's start

# The words that a put-up refused by the repository's push check printed.
REFUSAL = "repository: git can't push the run's work: lint: a line ends in a space\n"
JUDGED_GOOD = {
    "generator": rn_files.made([], [COMMAND]),
    "evaluator": rn_files.judged([("N1", ["x"]), ("N2", ["x"]), ("N3", ["x"])]),
}


def over(tmp: str) -> Run:
    """The walkthrough's run whose command, each condition good, was made and judged good in Round
    content-1, weighed, its Rounds over."""
    r = Run(tmp, walkthrough(command_good=True))
    rn_files.a_round(r.folder, COMMAND, "content", 1, {**JUDGED_GOOD, **rn_files.WEIGHED})
    return r


def test_fix_of_a_deliverable_whose_rounds_are_over_writes_its_fix_and_prints_its_folder(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run whose command's Rounds are over
    When tree fix runs for the command, from put-up, with the refusal's words on stdin
    Then it gives 0 printing fix-2's folder, absolute, which holds the problem with the words as
    given, and the design tree is as it was"""
    r = over(str(tmp_path))
    before = r.tree()
    code, out, err = r.main(host, "fix", r.run, COMMAND, "put-up", stdin=REFUSAL)
    fix = r.round(COMMAND, "fix", 2)
    assert (code, out, err) == (0, f"{fix}\n", "")
    assert rn_files.read_json(os.path.join(fix, "problem.json")) == {
        "source": "put-up",
        "words": REFUSAL,
    }
    assert r.tree() == before


def test_fix_after_a_fix_fixed_writes_the_next(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose command's Rounds are over, and whose fix-2 its fixer
    fixed, its Cut holding the command's node as it stands
    When tree fix runs for the command, from send-back, with the user's words
    Then it gives 0 printing fix-3's folder"""
    r = over(str(tmp_path))
    fix = r.round(COMMAND, "fix", 2)
    rn_files.write_json(
        os.path.join(fix, "fixer-cut.json"), {"deliverable": r.tree()["deliverables"][1]}
    )
    rn_files.write_json(os.path.join(fix, "fixer.json"), {"result": "fixed", "files": [COMMAND]})
    code, out, err = r.main(host, "fix", r.run, COMMAND, "send-back", stdin="Name the flag.")
    assert (code, out, err) == (0, f"{r.round(COMMAND, 'fix', 3)}\n", "")


def test_fix_of_a_deliverable_whose_rounds_arent_over_gives_1_writing_no_fix(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run whose command's generator made Round content-1, the evaluator
    still due
    When tree fix runs for the command
    Then it gives 1 saying it waits on its evaluator, as its Rounds aren't over yet, and writes no
    Fix"""
    r = Run(str(tmp_path), walkthrough())
    rn_files.a_round(r.folder, COMMAND, "content", 1, {"generator": rn_files.made([], [COMMAND])})
    refused(
        r.main(host, "fix", r.run, COMMAND, "put-up", stdin=REFUSAL),
        f"{COMMAND} waits on its evaluator, as its Rounds aren't over yet",
    )
    assert not os.path.exists(r.round(COMMAND, "fix", 2))


def test_fix_while_a_fix_waits_on_its_fixer_gives_1_writing_no_fix(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose command's Rounds are over, and whose fix-2 holds its
    problem alone
    When tree fix runs for the command
    Then it gives 1 saying it waits on its fixer, as a Fix of it is unfinished, and writes no
    fix-3"""
    r = over(str(tmp_path))
    r.main(host, "fix", r.run, COMMAND, "put-up", stdin=REFUSAL)
    refused(
        r.main(host, "fix", r.run, COMMAND, "put-up", stdin=REFUSAL),
        f"{COMMAND} waits on its fixer, as a Fix of it is unfinished",
    )
    assert not os.path.exists(r.round(COMMAND, "fix", 3))


def test_fix_and_next_while_a_fixs_decision_waits_on_the_pruner(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose command's fix-2 its fixer ended with decision, its Cut
    holding the command's node as it stands
    When tree fix, then tree next, run
    Then the fix gives 1 saying it waits on the pruner, to weigh the decision its fixer named;
    next prints the `pruner` of the command with fix-2's fixer.json; and neither writes a
    folder"""
    r = over(str(tmp_path))
    fix = r.round(COMMAND, "fix", 2)
    rn_files.write_json(
        os.path.join(fix, "fixer-cut.json"), {"deliverable": r.tree()["deliverables"][1]}
    )
    rn_files.write_json(os.path.join(fix, "fixer.json"), {"result": "decision", "decision": "x"})
    waits = f"{COMMAND} waits on the pruner, to weigh the decision its fixer named"
    refused(r.main(host, "fix", r.run, COMMAND, "put-up", stdin=REFUSAL), waits)
    assert next_lines(r, host) == [["pruner", COMMAND, os.path.join(fix, "fixer.json")]]
    assert sorted(os.listdir(os.path.dirname(fix))) == ["content-1", "fix-2"]


def fixer_ended(r: Run, result: Any) -> str:
    """Writes the command's fix-2 with a fixer's Cut holding the command's node as it stands, and
    the fixer's result, None for none; gives the Fix's folder."""
    fix = r.round(COMMAND, "fix", 2)
    rn_files.write_json(os.path.join(fix, "problem.json"), {"source": "put-up", "words": "x"})
    rn_files.write_json(
        os.path.join(fix, "fixer-cut.json"), {"deliverable": r.tree()["deliverables"][1]}
    )
    if result is not None:
        rn_files.write_json(os.path.join(fix, "fixer.json"), result)
    return fix


def test_commit_after_a_fixs_decision_marks_it_weighed_and_the_command_is_put_up_again(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run whose command's fix-2 its fixer ended with decision, the tree as
    committed, as the pruner cut the decision and changed nothing, and the pruner's result
    When tree commit runs, and then tree next
    Then the commit gives 0 printing the last commit's hash, which fix-2's weighed.json holds; and
    next prints the command's `put-up`, as the Fix is over"""
    r = over(str(tmp_path))
    fix = fixer_ended(r, {"result": "decision", "decision": "x"})
    units = [os.path.join(fix, "fixer.json")]
    weighed_by_pruner(r, units=units, kept=[], cut=["the decision: they never meet it"])
    assert r.main(host, "commit", r.run) == (0, f"{r.head()}\n", "")
    assert rn_files.read_json(os.path.join(fix, "weighed.json")) == {"commit": r.head()}
    assert next_lines(r, host) == [["put-up", COMMAND]]


def test_commit_leaves_a_fixs_decision_its_pruner_didnt_weigh_unmarked(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose command's fix-2 its fixer ended with decision, and the
    pruner's result of another unit, naming no unit
    When tree commit runs
    Then it gives 0, and fix-2 holds no weighed.json, its decision still due to a pruner"""
    r = over(str(tmp_path))
    fix = fixer_ended(r, {"result": "decision", "decision": "x"})
    guide_decided(r)
    weighed_by_pruner(r)
    assert r.main(host, "commit", r.run)[0] == 0
    assert not os.path.exists(os.path.join(fix, "weighed.json"))
    assert next_lines(r, host) == [["pruner", COMMAND, os.path.join(fix, "fixer.json")]]


@pytest.mark.parametrize(
    "result", [{"result": "fixed", "files": [COMMAND]}, None], ids=["fixed", "no result"]
)
def test_commit_leaves_a_fix_that_waits_on_no_pruner_unmarked(
    tmp_path: Any, host: Any, result: Any
):
    """Given the walkthrough's run whose command's fix-2 its fixer fixed, or holds no result yet,
    and the pruner's result of another unit
    When tree commit runs
    Then it gives 0, and fix-2 holds no weighed.json, as no pruner weighs it"""
    r = over(str(tmp_path))
    fix = fixer_ended(r, result)
    weighed_by_pruner(r, kept=[])
    assert r.main(host, "commit", r.run)[0] == 0
    assert not os.path.exists(os.path.join(fix, "weighed.json"))


@pytest.mark.parametrize(
    ("source", "words", "said"),
    [
        ("pushed", REFUSAL, "put-up, final-check, send-back"),
        ("put-up", "", "give them on stdin"),
        ("final-check", "  \n", "give them on stdin"),
    ],
    ids=["a source of none", "no words", "only spaces"],
)
def test_fix_with_a_wrong_source_or_no_words_gives_1_writing_no_fix(
    tmp_path: Any, host: Any, source: str, words: str, said: str
):
    """Given the walkthrough's run whose command's Rounds are over
    When tree fix runs for the command with a source of none, or with no words on stdin
    Then it gives 1 saying what it takes, and writes no Fix"""
    r = over(str(tmp_path))
    refused(r.main(host, "fix", r.run, COMMAND, source, stdin=words), said)
    assert not os.path.exists(r.round(COMMAND, "fix", 2))


def test_fix_of_a_path_of_no_deliverable_gives_1_naming_it(tmp_path: Any, host: Any):
    """Given the walkthrough's run
    When tree fix runs for invoicer/cli.py, no deliverable's path
    Then it gives 1 naming the path"""
    r = over(str(tmp_path))
    refused(
        r.main(host, "fix", r.run, "invoicer/cli.py", "put-up", stdin=REFUSAL), "invoicer/cli.py"
    )


def test_next_after_a_fix_writes_the_fixers_cut_in_it(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose command's Rounds are over, and whose fix-2 tree fix
    wrote
    When tree next runs, and again
    Then the first prints the fixer's `start` with the path of fix-2's fixer-cut.json from the
    repository's top, which holds the command's node and the Fix's problem; the second prints it
    `running`"""
    r = over(str(tmp_path))
    r.main(host, "fix", r.run, COMMAND, "put-up", stdin=REFUSAL)
    path = os.path.join(r.round(COMMAND, "fix", 2), "fixer-cut.json")
    assert next_lines(r, host) == [["start", "fixer", COMMAND, os.path.relpath(path, r.repo)]]
    given = rn_files.read_json(path)
    assert given["deliverable"] == r.tree()["deliverables"][1]
    assert given["problem"] == {"source": "put-up", "words": REFUSAL}
    assert next_lines(r, host) == [["running", "fixer", COMMAND]]


def test_next_restart_of_a_fixer_a_pause_stopped_writes_a_fresh_cut_in_its_fix(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run whose command's fix-2 holds a fixer's Cut of an older node and
    no result, as a pause stopped its fixer
    When tree next --restart runs
    Then it prints the fixer's `start`, fix-2's Cut holding the node as the tree holds it now, and
    no fix-3 made"""
    r = over(str(tmp_path))
    r.main(host, "fix", r.run, COMMAND, "put-up", stdin=REFUSAL)
    path = os.path.join(r.round(COMMAND, "fix", 2), "fixer-cut.json")
    rn_files.write_json(path, {"deliverable": {"name": "older"}})
    assert [each[:3] for each in next_lines(r, host, RESTART)] == [["start", "fixer", COMMAND]]
    assert rn_files.read_json(path)["deliverable"] == r.tree()["deliverables"][1]
    assert not os.path.exists(r.round(COMMAND, "fix", 3))


def test_next_of_a_fix_fixed_prints_its_put_up_until_it_is_put_up(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose command's fix-2 its fixer fixed
    When tree next runs, before fix-2 is marked put up with the command's state, and after
    Then the first prints the command's `put-up`, and the second its `sign-off`, as the command
    is open at a step that the user checks"""
    r = over(str(tmp_path))
    fix = fixer_ended(r, {"result": "fixed", "files": []})
    assert next_lines(r, host) == [["put-up", COMMAND]]
    rn_files.write_json(os.path.join(fix, "put-up.json"), {"short": [], "open": []})
    assert next_lines(r, host) == [["sign-off", COMMAND]]


def test_next_of_a_done_deliverables_fix_starts_its_fixer_then_its_put_up(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose plan, command, and guide are done, the command's Round
    content-1 judged good and weighed, and its fix-2 written with its problem
    When tree next runs; then once its fixer fixed it; then once fix-2 is marked put up
    Then it prints the fixer's `start`; then the command's `put-up`; then `final-check`, as the
    command stays done"""
    the = walkthrough()
    the["deliverables"][1] = rn_files.done_node(rn_files.COMMAND_NAME, COMMAND, "light")
    the["deliverables"][2] = rn_files.done_node(rn_files.GUIDE_NAME, GUIDE, "readme")
    r = Run(str(tmp_path), the)
    rn_files.a_round(r.folder, COMMAND, "content", 1, {**JUDGED_GOOD, **rn_files.WEIGHED})
    r.main(host, "fix", r.run, COMMAND, "final-check", stdin="It prints no total.")
    assert [each[:3] for each in next_lines(r, host)] == [["start", "fixer", COMMAND]]
    fix = r.round(COMMAND, "fix", 2)
    rn_files.write_json(os.path.join(fix, "fixer.json"), {"result": "fixed", "files": []})
    assert next_lines(r, host) == [["put-up", COMMAND]]
    rn_files.write_json(os.path.join(fix, "put-up.json"), {"short": [], "open": []})
    assert next_lines(r, host) == [["final-check"]]


def test_next_of_a_done_deliverable_whose_fix_changed_its_decisions_starts_nothing_of_it(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run whose plan, command, and guide are done, and whose command's
    fix-2 its fixer ended with decision, its Cut holding the command with N1 good, which the tree
    now holds not good, as a pruner left the command done
    When tree next runs
    Then it prints `final-check` alone, starting no Round of the done command, so that the final
    check finds the problem again for a pruner, which opens the command for its Rounds"""
    the = walkthrough()
    the["deliverables"][1] = rn_files.done_node(rn_files.COMMAND_NAME, COMMAND, "light", ["N2"])
    the["deliverables"][2] = rn_files.done_node(rn_files.GUIDE_NAME, GUIDE, "readme")
    r = Run(str(tmp_path), the)
    rn_files.a_round(r.folder, COMMAND, "content", 1, {**JUDGED_GOOD, **rn_files.WEIGHED})
    fix = r.round(COMMAND, "fix", 2)
    given = rn_files.done_node(rn_files.COMMAND_NAME, COMMAND, "light")
    rn_files.write_json(os.path.join(fix, "problem.json"), {"source": "final-check", "words": "x"})
    rn_files.write_json(os.path.join(fix, "fixer-cut.json"), {"deliverable": given})
    rn_files.write_json(os.path.join(fix, "fixer.json"), {"result": "decision", "decision": "x"})
    rn_files.write_json(os.path.join(fix, "weighed.json"), {"commit": "a1b2c3"})
    assert next_lines(r, host) == [["final-check"]]
    assert not os.path.exists(r.round(COMMAND, "content", 3))


# signoff


def test_signoff_of_the_plan_waiting_writes_it_done_commits_it_and_prints_the_trees_path(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run whose plan is open with each condition good
    When tree signoff runs
    Then it gives 0 printing the design tree's path, whose plan is now done in its one line, and
    the tree is committed as `rn: <the plan's name>, signed off`, with no change left"""
    r = Run(str(tmp_path), walkthrough(plan_done=False))
    before = r.head()
    code, out, err = r.main(host, "signoff", r.run)
    assert (code, err) == (0, "")
    assert os.path.normpath(os.path.join(r.repo, out.strip())) == r.tree_path
    assert r.tree()["deliverables"][0] == rn_files.done_node(
        GOAL, rn_files.plan_path(NAME), "design-tree"
    )
    assert r.head() != before
    assert git(r.worktree, "log", "-1", "--format=%B").strip() == f"rn: {GOAL}, signed off"
    assert git(r.worktree, "status", "--porcelain", "--", r.tree_path).strip() == ""


def test_signoff_with_none_waiting_gives_1_leaving_the_tree(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose plan is done, and whose command and guide have no Round
    When tree signoff runs
    Then it gives 1, and the tree is as it was"""
    r = Run(str(tmp_path), walkthrough())
    before = r.tree()
    code, out, err = r.main(host, "signoff", r.run)
    assert code == 1
    assert out == ""
    assert err.startswith("tree: ")
    assert r.tree() == before


def test_signoff_of_a_deliverable_past_its_rounds_writes_it_done(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose command is past its two content Rounds, its finding kept
    as an open decision
    When tree signoff runs
    Then it gives 0 printing the design tree's path, whose command is now done, keeping N1 not
    good with the user's answer and the finding left as its decisions, and N2 and N3 good"""
    r = left_past(str(tmp_path))
    code, out, err = r.main(host, "signoff", r.run)
    assert (code, err) == (0, "")
    assert os.path.normpath(os.path.join(r.repo, out.strip())) == r.tree_path
    assert r.tree()["deliverables"][1] == rn_files.done_node(
        rn_files.COMMAND_NAME, COMMAND, "light", ["N2", "N3"], {"N1": [TAX, LEFT]}
    )


def all_but_command(tmp: str) -> Run:
    """The walkthrough's run as `left_past` makes it, but with its guide done, so that the command
    alone waits for the user's sign-off; its pull request open, as put-up opened it."""
    r = left_past(tmp)
    the = r.tree()
    the["deliverables"][2] = rn_files.done_node(rn_files.GUIDE_NAME, GUIDE, "readme")
    r.write(the)
    return r


def opened_pr(gh_state: str) -> None:
    """Sets the double of gh's state to the pull request that put-up opened."""
    kept = gh_double.state(gh_state)
    kept["pull_request"] = "http://github.com/owner/repo/pull/1"
    gh_double.keep(gh_state, kept)


def signed_with_origin(tmp: str, host: Any, gh_state: str, last: bool) -> Run:
    """The run of `all_but_command`, or of `left_past` where `last` is false, whose guide is then
    open, with a remote origin and its pull request open, as put-up opened it."""
    r = all_but_command(tmp) if last else left_past(tmp)
    rn_files.with_origin(r.repo, os.path.join(tmp, "origin.git"))
    opened_pr(gh_state)
    return r


def pushed(tmp: str) -> str:
    """The hash that origin's work branch holds, or the empty string where it holds none."""
    origin = os.path.join(tmp, "origin.git")
    return git(origin, "branch", "--list", "--format=%(objectname)", BRANCH).strip()


def sent(host: Any) -> list[tuple[list[str], str]]:
    """Each push and each command of gh that the host ran, in order, with its folder."""
    return [(argv, cwd) for argv, cwd in host.ran if argv[:2] == ["git", "push"] or argv[0] == "gh"]


def test_signoff_that_leaves_a_deliverable_open_commits_pushing_nothing_and_asking_gh_nothing(
    tmp_path: Any, host: Any, gh_state: str
):
    """Given the walkthrough's run with a remote origin, whose command waits for sign-off and whose
    guide is open, its pull request open
    When tree signoff runs
    Then it gives 0, the branch holds a new commit, origin holds no work branch, and the host ran
    no push and no command of gh"""
    r = signed_with_origin(str(tmp_path), host, gh_state, last=False)
    before = r.head()
    assert r.main(host, "signoff", r.run)[0] == 0
    assert r.head() != before
    assert pushed(str(tmp_path)) == ""
    assert sent(host) == []


def test_signoff_that_leaves_each_deliverable_done_commits_it_pushing_nothing_and_asking_gh_nothing(
    tmp_path: Any, host: Any, gh_state: str
):
    """Given the walkthrough's run with a remote origin, whose plan and guide are done and whose
    command waits for sign-off, its pull request open
    When tree signoff runs
    Then it gives 0 printing the tree's path, each deliverable is done, the branch holds a new
    commit, origin holds no work branch, and the host ran no push and no command of gh, as the
    final check pushes the work and the user marks the pull request ready"""
    r = signed_with_origin(str(tmp_path), host, gh_state, last=True)
    before = r.head()
    code, out, err = r.main(host, "signoff", r.run)
    assert (code, err) == (0, "")
    assert os.path.normpath(os.path.join(r.repo, out.strip())) == r.tree_path
    assert [each["status"] for each in r.tree()["deliverables"]] == ["done", "done", "done"]
    assert r.head() != before
    assert pushed(str(tmp_path)) == ""
    assert sent(host) == []
    assert gh_double.state(gh_state)["asked"] == []


# The run's folder


@pytest.mark.parametrize(
    "folder", ["invoicer", ".claude/worktrees/rn-x/.rn/y", f".claude/worktrees/{BRANCH}/.rn"]
)
def test_a_folder_that_isnt_a_runs_gives_1(tmp_path: Any, host: Any, folder: str):
    """Given the walkthrough's run
    When tree touched runs with a folder of invoicer, one whose names differ, or the worktree's
    .rn
    Then it gives 1 naming the folder"""
    r = Run(str(tmp_path), walkthrough())
    refused(r.main(host, "touched", folder, "/goal"), folder)


def test_a_runs_folder_with_no_design_tree_gives_1(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose design tree is taken away
    When tree touched runs on its folder
    Then it gives 1 naming the folder"""
    r = Run(str(tmp_path), walkthrough())
    os.remove(r.tree_path)
    refused(r.main(host, "touched", r.run, "/goal"), r.run)


def test_a_runs_folder_given_whole_is_the_same_run(tmp_path: Any, host: Any):
    """Given the walkthrough's run
    When tree touched runs on its folder given as an absolute path
    Then it prints what it prints for the folder from the repository's top"""
    r = Run(str(tmp_path), walkthrough())
    pointer = "/deliverables/2"
    assert r.main(host, "touched", r.folder, pointer) == r.main(host, "touched", r.run, pointer)
