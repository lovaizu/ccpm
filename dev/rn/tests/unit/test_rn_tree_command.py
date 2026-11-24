"""The unit cases of tree/command.py, tree.py's command line, through `main`: `touched` with a
pointer and without, of none, one, and two changes; `check` of a tree in form, as committed,
changed, or as a run starts, of one with faults, out of its schema, and of none; `commit` of a
change in form, of one out of it, and of none; `cut` while the goal is open, and for each role and
each thing a deliverable waits on, a new Round and the last
one again, the Round that a pause stopped, and a stage at its limit with its findings kept;
`signoff` of the plan, of a deliverable with its findings left, of the last, asking gh nothing,
and of none waiting; `commit` of a tree leaving a deliverable open, and of each deliverable done,
each pushing nothing and asking gh nothing; a run's folder out of its form or with no
design tree; and arguments other than the usage's. Each runs in the
user's repository, the run's worktree a git worktree on the work's branch, with a host that runs
git for real."""

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
from tree.command import USAGE, main

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
        """The run's folder from the repository's top, as tree.py takes it."""
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

    def main(self, host: Any, *argv: str) -> tuple[int, str, str]:
        """tree.py with the arguments, from the repository's top."""
        return main(list(argv), self.repo, RN, host)


def walkthrough(**given: Any) -> dict[str, Any]:
    """The walkthrough's tree, the command's N1 holding the user's answer about the tax rate."""
    return rn_files.walkthrough_tree(NAME, command_decisions={"N1": [TAX]}, **given)


def refused(result: tuple[int, str, str], *words: str) -> None:
    """The result is 1 with `tree.py: ` and each of the words on stderr, and nothing on stdout."""
    code, out, err = result
    assert (code, out) == (1, ""), result
    assert err.startswith("tree.py: "), err
    for each in words:
        assert each in err, err


# The usage


@pytest.mark.supports("test_the_pruner_rewrites_each_node_its_change_touches_before_the_commit")
@pytest.mark.parametrize(
    "argv",
    [
        [],
        ["nothing", "x"],
        ["touched"],
        ["touched", "x", "/goal", "more"],
        ["check"],
        ["check", "x", "more"],
        ["commit", "x"],
        ["cut", "x", "generator"],
        ["signoff"],
    ],
)
def test_arguments_other_than_the_usages_give_2_with_it(tmp_path: Any, host: Any, argv: list[str]):
    """Given the walkthrough's run
    When tree.py runs with no arguments, an unknown subcommand, or a subcommand short of or past
    its arguments
    Then it gives 2 with the usage, and changes nothing"""
    r = Run(str(tmp_path), walkthrough())
    head = r.head()
    code, out, err = r.main(host, *argv)
    assert code == 2
    assert USAGE in out + err
    assert r.head() == head


# touched


@pytest.mark.supports("test_the_pruner_rewrites_each_node_its_change_touches_before_the_commit")
def test_touched_with_a_pointer_prints_each_node_it_touches_a_line(tmp_path: Any, host: Any):
    """Given the walkthrough's run
    When tree.py touched runs with the pointer of the command's N1's decision
    Then it gives 0 printing the goal, the command, its N1, the guide, and the work making the
    command, from the goal down, a pointer a line"""
    r = Run(str(tmp_path), walkthrough())
    got = r.main(host, "touched", r.run, "/deliverables/1/necessary_conditions/0/decisions/0")
    lines = [
        "/goal",
        "/deliverables/1",
        "/deliverables/1/necessary_conditions/0",
        "/deliverables/2",
        "/work/0",
    ]
    assert got == (0, "".join(f"{each}\n" for each in lines), "")


@pytest.mark.supports("test_the_pruner_rewrites_each_node_its_change_touches_before_the_commit")
def test_touched_with_a_pointer_of_a_path_changed_since_the_commit_follows_the_old_path(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run whose tree, since its last commit, gives the command the path
    invoicer/cli.py, the guide's input still naming invoicer/__main__.py
    When tree.py touched runs with the pointer of the command's path
    Then it gives 0 printing the goal, the command, the guide by the command's old path, and the
    work making the command, a pointer a line"""
    r = Run(str(tmp_path), walkthrough())
    changed = r.tree()
    changed["deliverables"][1]["path"] = "invoicer/cli.py"
    r.write(changed)
    got = r.main(host, "touched", r.run, "/deliverables/1/path")
    lines = ["/goal", "/deliverables/1", "/deliverables/2", "/work/0"]
    assert got == (0, "".join(f"{each}\n" for each in lines), "")


@pytest.mark.supports("test_the_pruner_rewrites_each_node_its_change_touches_before_the_commit")
def test_touched_with_a_pointer_of_no_node_gives_1_naming_it(tmp_path: Any, host: Any):
    """Given the walkthrough's run, of three deliverables
    When tree.py touched runs with the pointer of a fourth
    Then it gives 1 naming the pointer"""
    r = Run(str(tmp_path), walkthrough())
    refused(r.main(host, "touched", r.run, "/deliverables/3"), "/deliverables/3")


@pytest.mark.supports("test_the_pruner_rewrites_each_node_its_change_touches_before_the_commit")
def test_touched_of_a_change_since_the_commit_prints_what_it_touches(tmp_path: Any, host: Any):
    """Given the walkthrough's run, its tree committed, then the user's answer about the tax rate
    changed in the tree
    When tree.py touched runs with no pointer
    Then it gives 0 printing the goal, the command, its N1, the decision, the guide, and the work
    making the command, the changed decided left out"""
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
        "/work/0",
    ]
    assert r.main(host, "touched", r.run) == (0, "".join(f"{each}\n" for each in lines), "")


@pytest.mark.supports("test_the_pruner_rewrites_each_node_its_change_touches_before_the_commit")
def test_touched_of_two_changes_prints_each_node_once_leaving_each_change_out(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run, its tree committed, then the tax rate's answer and the guide's
    N1's good both changed
    When tree.py touched runs with no pointer
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
            "/work/0",
            "/work/1",
        ]
    )


@pytest.mark.supports("test_the_pruner_rewrites_each_node_its_change_touches_before_the_commit")
def test_touched_of_no_change_since_the_commit_prints_nothing(tmp_path: Any, host: Any):
    """Given the walkthrough's run, its tree as committed
    When tree.py touched runs with no pointer
    Then it gives 0 printing nothing"""
    r = Run(str(tmp_path), walkthrough())
    assert r.main(host, "touched", r.run) == (0, "", "")


# check


@pytest.mark.supports("test_the_pruners_write_passes_the_hook_and_tree_py_check_takes_it")
@pytest.mark.parametrize("committed", [True, False], ids=["committed", "changed"])
def test_check_of_a_tree_in_form_gives_0_printing_nothing(
    tmp_path: Any, host: Any, committed: bool
):
    """Given the walkthrough's run whose tree is as committed, or changed by a decision settled in
    the guide's N1 and not committed
    When tree.py check runs
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


@pytest.mark.supports("test_the_pruners_write_passes_the_hook_and_tree_py_check_takes_it")
def test_check_of_the_tree_a_run_starts_from_gives_0(tmp_path: Any, host: Any):
    """Given a run's worktree whose design tree is as the run starts, its goal open, never
    committed
    When tree.py check runs
    Then it gives 0 printing nothing, as the tree's checks take the goal open"""
    r = Run(str(tmp_path), rn_files.started(NAME), committed=False)
    assert r.main(host, "check", r.run) == (0, "", "")


@pytest.mark.supports(
    "test_tree_py_check_gives_each_fault_of_the_pruners_write_a_line_changing_nothing"
)
def test_check_of_a_tree_with_two_faults_gives_1_with_each_on_a_line(tmp_path: Any, host: Any):
    """Given the walkthrough's run, its tree changed so that the command's kind is `lights` and the
    guide's input names a file that the worktree doesn't hold
    When tree.py check runs
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


@pytest.mark.supports(
    "test_tree_py_check_gives_each_fault_of_the_pruners_write_a_line_changing_nothing"
)
def test_check_of_a_tree_out_of_its_schema_gives_1_with_its_place(tmp_path: Any, host: Any):
    """Given the walkthrough's run, its tree changed so that the goal holds no `by`
    When tree.py check runs
    Then it gives 1 with a line naming /goal"""
    r = Run(str(tmp_path), walkthrough())
    changed = r.tree()
    del changed["goal"]["by"]
    r.write(changed)
    code, out, _ = r.main(host, "check", r.run)
    assert code == 1
    assert "/goal" in out


@pytest.mark.supports(
    "test_tree_py_check_gives_each_fault_of_the_pruners_write_a_line_changing_nothing"
)
def test_check_of_a_run_with_no_design_tree_gives_1_naming_it(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose design tree was deleted
    When tree.py check runs
    Then it gives 1 with `tree.py: ` and that the run's folder holds no design tree on stderr"""
    r = Run(str(tmp_path), walkthrough())
    os.remove(r.tree_path)
    refused(r.main(host, "check", r.run), "holds no design tree")


# commit


@pytest.mark.supports("test_a_point_the_pruner_settles_is_committed_with_its_ground_as_the_message")
def test_commit_of_a_change_in_form_commits_the_tree_alone_with_the_ground(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run, its tree committed, then a decision settled by reasoning in the
    guide's N1, and the guide's file written beside it
    When tree.py commit runs with the ground
    Then it gives 0 printing the new commit's hash, whose message is the ground word for word and
    which holds the tree alone, the guide left uncommitted"""
    r = Run(str(tmp_path), walkthrough())
    changed = r.tree()
    changed["deliverables"][2]["necessary_conditions"][0]["decisions"].append(
        rn_files.decision("its people", "The accounting team.", "reasoning")
    )
    r.write(changed)
    with open(os.path.join(r.worktree, GUIDE), "w", encoding="utf-8") as f:
        f.write("# Print an invoice\n")
    before = r.head()
    code, out, err = r.main(host, "commit", r.run, "The README names its people.")
    assert (code, err) == (0, "")
    assert out.strip() == r.head() != before
    assert git(r.worktree, "log", "-1", "--format=%B").strip() == "The README names its people."
    held = git(r.worktree, "show", "--name-only", "--format=", "HEAD").split()
    assert held == [os.path.relpath(r.tree_path, r.worktree)]
    assert git(r.worktree, "status", "--porcelain").strip() == f"?? {GUIDE}"


@pytest.mark.supports("test_a_tree_change_out_of_form_is_refused_at_its_commit")
def test_commit_of_a_tree_out_of_form_gives_1_with_its_first_fault_leaving_git(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run, its tree committed, then the command's kind made `lights`
    When tree.py commit runs
    Then it gives 1 naming /deliverables/1/kind, the branch's last commit as it was and the tree
    still changed"""
    r = Run(str(tmp_path), walkthrough())
    changed = r.tree()
    changed["deliverables"][1]["kind"] = "lights"
    r.write(changed)
    before = r.head()
    refused(r.main(host, "commit", r.run, "The command."), "/deliverables/1/kind")
    assert r.head() == before
    assert (
        git(r.worktree, "status", "--porcelain").strip()
        == f"M {os.path.relpath(r.tree_path, r.worktree)}"
    )


@pytest.mark.supports("test_a_point_the_pruner_settles_is_committed_with_its_ground_as_the_message")
def test_commit_of_no_change_prints_the_last_commit_committing_nothing(tmp_path: Any, host: Any):
    """Given the walkthrough's run, its tree as committed
    When tree.py commit runs
    Then it gives 0 printing the last commit's hash, and the branch holds no new commit"""
    r = Run(str(tmp_path), walkthrough())
    before = r.head()
    assert r.main(host, "commit", r.run, "Nothing.")[:2] == (0, f"{before}\n")
    assert r.head() == before


@pytest.mark.supports("test_a_point_the_pruner_settles_is_committed_with_its_ground_as_the_message")
def test_commit_of_the_tree_a_run_starts_from_commits_it_first(tmp_path: Any, host: Any):
    """Given a run's worktree whose design tree, as the run starts with its goal open, was never
    committed
    When tree.py commit runs with the ground
    Then it gives 0 printing a new commit's hash, whose message is the ground, as the tree's checks
    take the goal open"""
    r = Run(str(tmp_path), rn_files.started(NAME), committed=False)
    before = r.head()
    code, out, _ = r.main(host, "commit", r.run, "The goal as put.")
    assert code == 0
    assert out.strip() == r.head() != before
    assert git(r.worktree, "log", "-1", "--format=%B").strip() == "The goal as put."


@pytest.mark.supports("test_a_point_the_pruner_settles_is_committed_with_its_ground_as_the_message")
def test_commit_that_a_commit_check_refuses_gives_2_with_what_git_said(tmp_path: Any, host: Any):
    """Given the walkthrough's run, its tree committed, then a decision settled in the guide's N1,
    in a repository whose pre-commit hook refuses each commit saying `tree: no`
    When tree.py commit runs with the ground
    Then it gives 2, nothing on stdout, and stderr naming tree.py and the hook's line, and the
    branch holds no new commit"""
    r = Run(str(tmp_path), walkthrough())
    hook(r.repo, "echo 'tree: no'\nexit 1\n")
    changed = r.tree()
    changed["deliverables"][2]["necessary_conditions"][0]["decisions"].append(
        rn_files.decision("its people", "The accounting team.", "reasoning")
    )
    r.write(changed)
    before = r.head()
    code, out, err = r.main(host, "commit", r.run, "The README names its people.")
    assert (code, out) == (2, "")
    assert err.startswith("tree.py: ") and "tree: no" in err
    assert r.head() == before


# cut


@pytest.mark.supports("test_a_cut_waits_while_the_goal_is_open")
@pytest.mark.parametrize("role", ["generator", "evaluator"])
def test_cut_while_the_goal_is_open_gives_1_making_no_round(tmp_path: Any, host: Any, role: str):
    """Given the walkthrough's run whose goal is open, its decided null
    When tree.py cut runs for the command's generator or evaluator
    Then it gives 1 saying that the goal is open and a new pruner writes it, and makes no Round"""
    the = walkthrough()
    the["goal"] = {"decided": None}
    r = Run(str(tmp_path), the)
    refused(r.main(host, "cut", r.run, role, COMMAND), "goal is open", "a new pruner")
    assert not os.path.exists(os.path.join(r.folder, "rounds"))


@pytest.mark.supports(
    "test_the_generators_cut_holds_its_deliverables_node_inputs_and_best_practice"
)
def test_cut_of_the_first_generator_writes_its_cut_in_round_content_1(tmp_path: Any, host: Any):
    """Given the walkthrough's run, its plan done and no Round yet
    When tree.py cut runs for the command's generator
    Then it gives 0 printing the path of Round content-1's generator-cut.json from the repository's
    top, which holds the command's Cut"""
    r = Run(str(tmp_path), walkthrough())
    code, out, err = r.main(host, "cut", r.run, "generator", COMMAND)
    path = os.path.join(r.round(COMMAND, "content", 1), "generator-cut.json")
    assert (code, err) == (0, "")
    assert os.path.normpath(os.path.join(r.repo, out.strip())) == path
    given = rn_files.read_json(path)
    assert given["goal"] == GOAL
    assert given["deliverable"] == r.tree()["deliverables"][1]
    assert os.path.normpath(os.path.join(r.repo, given["worktree"])) == r.worktree
    assert os.path.normpath(os.path.join(r.repo, given["best_practice"])) == os.path.join(
        RN, "domain", "best-practices", "light"
    )
    assert (given["stage"], given["number"], given["last_good"]) == ("content", 1, None)
    assert "findings" not in given


@pytest.mark.supports("test_a_generators_made_makes_the_evaluator_due_in_the_same_round")
def test_cut_of_the_evaluator_writes_its_cut_in_the_generators_round(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose command's generator made Round content-1
    When tree.py cut runs for the command's evaluator
    Then it gives 0 printing the path of Round content-1's evaluator-cut.json, which holds the
    command's name and path and what light judges by"""
    r = Run(str(tmp_path), walkthrough())
    rn_files.a_round(r.folder, COMMAND, "content", 1, {"generator": rn_files.made([], [COMMAND])})
    code, out, err = r.main(host, "cut", r.run, "evaluator", COMMAND)
    path = os.path.join(r.round(COMMAND, "content", 1), "evaluator-cut.json")
    assert (code, err) == (0, "")
    assert os.path.normpath(os.path.join(r.repo, out.strip())) == path
    given = rn_files.read_json(path)
    assert given["deliverable"] == {"name": rn_files.COMMAND_NAME, "path": COMMAND}
    assert given["judges_by"] == rn_files.judged_by("light")


@pytest.mark.supports("test_a_generators_made_makes_the_evaluator_due_in_the_same_round")
def test_cut_of_the_generator_while_the_evaluator_is_due_gives_1_naming_it(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run whose command's generator made Round content-1
    When tree.py cut runs for the command's generator
    Then it gives 1 saying it waits on the evaluator, and makes no Round content-2"""
    r = Run(str(tmp_path), walkthrough())
    rn_files.a_round(r.folder, COMMAND, "content", 1, {"generator": rn_files.made([], [COMMAND])})
    code, out, err = r.main(host, "cut", r.run, "generator", COMMAND)
    assert code == 1
    assert "evaluator" in out + err
    assert not os.path.exists(r.round(COMMAND, "content", 2))


@pytest.mark.supports("test_a_deliverable_whose_point_waits_on_the_user_gets_no_cut")
def test_cut_of_a_deliverable_with_an_open_point_gives_1_naming_the_user(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose command's generator gave a point in Round content-1, kept
    open in its N1
    When tree.py cut runs for the command's generator
    Then it gives 1 saying it waits on the user, and writes no Cut"""
    the = rn_files.walkthrough_tree(
        NAME, command_decisions={"N1": [rn_files.decision("a line's quantity", None)]}
    )
    r = Run(str(tmp_path), the)
    rn_files.a_round(r.folder, COMMAND, "content", 1, {"generator": rn_files.point()})
    code, out, err = r.main(host, "cut", r.run, "generator", COMMAND)
    assert code == 1
    assert "user" in out + err
    assert not os.path.exists(os.path.join(r.round(COMMAND, "content", 1), "generator-cut.json"))


@pytest.mark.supports("test_a_deliverable_short_after_two_content_rounds_gets_no_third")
def test_cut_after_two_content_rounds_short_gives_1_naming_the_pruner(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose command's evaluators found N1 short in Rounds content-1 and
    content-2, its tree holding N2 and N3 good
    When tree.py cut runs for the command's generator
    Then it gives 1 saying it waits on the pruner, to keep each finding left as an open decision,
    and makes no Round content-3"""
    r = Run(str(tmp_path), walkthrough(command_good=["N2", "N3"]))
    results = {
        "generator": rn_files.made([], [COMMAND]),
        "evaluator": rn_files.judged(
            [("N2", ["a"]), ("N3", ["b"])], [("N1", "It prints a comma.")]
        ),
    }
    for number in (1, 2):
        rn_files.a_round(r.folder, COMMAND, "content", number, results)
    code, out, err = r.main(host, "cut", r.run, "generator", COMMAND)
    assert code == 1
    assert err == (
        f"tree.py: {COMMAND} waits on the pruner, to keep each finding left as an open decision,"
        " not on its generator\n"
    )
    assert out == ""
    assert not os.path.exists(r.round(COMMAND, "content", 3))


@pytest.mark.supports("test_a_generators_point_reaches_the_user_and_their_answer_resumes_it")
def test_cut_after_a_point_answered_writes_the_same_rounds_cut_again(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose command's generator gave a point in Round content-1, which
    the user answered in its N1
    When tree.py cut runs for the command's generator
    Then it gives 0 printing Round content-1's generator-cut.json, holding the answer by user, and
    makes no Round content-2"""
    r = Run(str(tmp_path), walkthrough())
    rn_files.a_round(r.folder, COMMAND, "content", 1, {"generator": rn_files.point()})
    code, out, _ = r.main(host, "cut", r.run, "generator", COMMAND)
    path = os.path.join(r.round(COMMAND, "content", 1), "generator-cut.json")
    assert code == 0
    assert os.path.normpath(os.path.join(r.repo, out.strip())) == path
    assert TAX in rn_files.read_json(path)["deliverable"]["necessary_conditions"][0]["decisions"]
    assert not os.path.exists(r.round(COMMAND, "content", 2))


@pytest.mark.supports("test_the_generators_cut_holds_the_pruners_remedy_and_no_evaluators_finding")
def test_cut_after_a_round_judged_short_makes_the_next_round(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose command's evaluator found N1 short in Round content-1, its
    tree holding N2 and N3 good
    When tree.py cut runs for the command's generator
    Then it gives 0 printing Round content-2's generator-cut.json, which holds none of the
    evaluator's findings, and the generator's good of content-1 as its last good"""
    r = Run(str(tmp_path), walkthrough(command_good=["N2", "N3"]))
    judged = rn_files.judged([("N2", ["a"]), ("N3", ["b"])], [("N1", "It prints a comma.")])
    rn_files.a_round(
        r.folder,
        COMMAND,
        "content",
        1,
        {"generator": rn_files.made([], [COMMAND]), "evaluator": judged},
    )
    code, out, _ = r.main(host, "cut", r.run, "generator", COMMAND)
    path = os.path.join(r.round(COMMAND, "content", 2), "generator-cut.json")
    assert code == 0
    assert os.path.normpath(os.path.join(r.repo, out.strip())) == path
    given = rn_files.read_json(path)
    assert (given["stage"], given["number"]) == ("content", 2)
    assert "findings" not in given
    assert "It prints a comma." not in json.dumps(given)
    assert given["last_good"] == []


@pytest.mark.supports(
    "test_a_pick_up_starts_the_stopped_generator_again_in_its_round_with_a_fresh_cut"
)
def test_cut_of_a_round_a_pause_stopped_writes_a_fresh_cut_in_that_round(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose command's Round content-1 holds the generator's Cut of a
    stale goal and no result, as a pause stopped it
    When tree.py cut runs for the command's generator
    Then it gives 0 printing Round content-1's generator-cut.json, written anew with the tree's
    goal, and makes no Round content-2"""
    r = Run(str(tmp_path), walkthrough())
    first = rn_files.a_round(r.folder, COMMAND, "content", 1)
    rn_files.write_json(os.path.join(first, "generator-cut.json"), {"goal": "stale"})
    code, out, _ = r.main(host, "cut", r.run, "generator", COMMAND)
    path = os.path.join(first, "generator-cut.json")
    assert code == 0
    assert os.path.normpath(os.path.join(r.repo, out.strip())) == path
    assert rn_files.read_json(path)["goal"] == GOAL
    assert (rn_files.read_json(path)["stage"], rn_files.read_json(path)["number"]) == (
        "content",
        1,
    )
    assert not os.path.exists(r.round(COMMAND, "content", 2))


@pytest.mark.supports("test_a_pick_up_starts_the_stopped_evaluator_again_in_its_round")
def test_cut_of_an_evaluator_a_pause_stopped_writes_its_cut_in_that_round(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose command's Round content-1 holds the generator's made and
    the evaluator's Cut with no result, as a pause stopped it
    When tree.py cut runs for the command's evaluator
    Then it gives 0 printing Round content-1's evaluator-cut.json"""
    r = Run(str(tmp_path), walkthrough())
    first = rn_files.a_round(
        r.folder, COMMAND, "content", 1, {"generator": rn_files.made([], [COMMAND])}
    )
    rn_files.write_json(os.path.join(first, "evaluator-cut.json"), {"goal": "stale"})
    code, out, _ = r.main(host, "cut", r.run, "evaluator", COMMAND)
    path = os.path.join(first, "evaluator-cut.json")
    assert code == 0
    assert os.path.normpath(os.path.join(r.repo, out.strip())) == path
    assert rn_files.read_json(path)["goal"] == GOAL


LEFT = rn_files.decision("a comma in a line", None)
SHORT = {
    "generator": rn_files.made([], [COMMAND]),
    "evaluator": rn_files.judged([("N2", ["a"]), ("N3", ["b"])], [("N1", "It prints a comma.")]),
}


def left_past(tmp: str) -> Run:
    """The walkthrough's run whose command's evaluators found N1 short in Rounds content-1 and
    content-2, its tree holding N2 and N3 good and the finding left as an open decision of N1."""
    the = rn_files.walkthrough_tree(
        NAME, command_good=["N2", "N3"], command_decisions={"N1": [TAX, LEFT]}
    )
    r = Run(tmp, the)
    for number in (1, 2):
        rn_files.a_round(r.folder, COMMAND, "content", number, SHORT)
    return r


@pytest.mark.supports("test_a_finding_left_past_two_content_rounds_goes_to_the_user_as_a_proposal")
def test_cut_of_a_deliverable_past_its_rounds_with_its_findings_kept_gives_1_naming_the_signoff(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run whose command is past its two content Rounds, its finding kept
    as an open decision
    When tree.py cut runs for the command's generator
    Then it gives 1 saying it waits on the sign-off, and makes no Round content-3"""
    r = left_past(str(tmp_path))
    code, out, err = r.main(host, "cut", r.run, "generator", COMMAND)
    assert code == 1
    assert "sign-off" in out + err
    assert not os.path.exists(r.round(COMMAND, "content", 3))


# signoff


@pytest.mark.supports(
    "test_a_signoff_of_the_plan_makes_it_done_and_starts_the_generator_of_each_deliverable_due"
)
def test_signoff_of_the_plan_waiting_writes_it_done_and_prints_the_trees_path(
    tmp_path: Any, host: Any
):
    """Given the walkthrough's run whose plan is open with each condition good
    When tree.py signoff runs
    Then it gives 0 printing the design tree's path, whose plan is now done in its one line"""
    r = Run(str(tmp_path), walkthrough(plan_done=False))
    code, out, err = r.main(host, "signoff", r.run)
    assert (code, err) == (0, "")
    assert os.path.normpath(os.path.join(r.repo, out.strip())) == r.tree_path
    assert r.tree()["deliverables"][0] == rn_files.done_node(
        GOAL, rn_files.plan_path(NAME), "design-tree"
    )


@pytest.mark.supports(
    "test_a_signoff_of_the_plan_makes_it_done_and_starts_the_generator_of_each_deliverable_due"
)
def test_signoff_with_none_waiting_gives_1_leaving_the_tree(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose plan is done, and whose command and guide have no Round
    When tree.py signoff runs
    Then it gives 1, and the tree is as it was"""
    r = Run(str(tmp_path), walkthrough())
    before = r.tree()
    code, out, err = r.main(host, "signoff", r.run)
    assert code == 1
    assert out == ""
    assert err.startswith("tree.py: ")
    assert r.tree() == before


@pytest.mark.supports("test_a_finding_left_past_two_content_rounds_goes_to_the_user_as_a_proposal")
def test_signoff_of_a_deliverable_past_its_rounds_writes_it_done(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose command is past its two content Rounds, its finding kept
    as an open decision
    When tree.py signoff runs
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
    the["work"] = [rn_files.work("make", COMMAND)]
    r.write(the)
    return r


def opened_pr(gh_state: str) -> None:
    """Sets the double of gh's state to the pull request that put-up opened."""
    kept = gh_double.state(gh_state)
    kept["pull_request"] = "http://github.com/owner/repo/pull/1"
    gh_double.keep(gh_state, kept)


@pytest.mark.supports(
    "test_the_last_signoff_ends_the_run_with_each_deliverable_on_the_pull_requests_branch"
)
def test_signoff_that_leaves_each_deliverable_done_writes_it_asking_gh_nothing(
    tmp_path: Any, host: Any, gh_state: str
):
    """Given the walkthrough's run whose plan and guide are done, and whose command waits for
    sign-off, its pull request open
    When tree.py signoff runs
    Then it gives 0 printing the tree's path, each deliverable is done, the branch holds no new
    commit, and gh was asked nothing"""
    r = all_but_command(str(tmp_path))
    opened_pr(gh_state)
    before = r.head()
    code, out, err = r.main(host, "signoff", r.run)
    assert (code, err) == (0, "")
    assert os.path.normpath(os.path.join(r.repo, out.strip())) == r.tree_path
    assert [each["status"] for each in r.tree()["deliverables"]] == ["done", "done", "done"]
    assert r.head() == before
    assert gh_double.state(gh_state)["asked"] == []


# commit of each deliverable done


def signed_last(tmp: str, host: Any, gh_state: str) -> Run:
    """The run of `all_but_command` with its command signed off by tree.py signoff, each
    deliverable done in the tree not yet committed, its pull request open, and the repository
    given a remote origin."""
    r = all_but_command(tmp)
    rn_files.with_origin(r.repo, os.path.join(tmp, "origin.git"))
    opened_pr(gh_state)
    assert r.main(host, "signoff", r.run)[0] == 0
    return r


def pushed(tmp: str) -> str:
    """The hash that origin's work branch holds, or the empty string where it holds none."""
    origin = os.path.join(tmp, "origin.git")
    return git(origin, "branch", "--list", "--format=%(objectname)", BRANCH).strip()


def sent(host: Any) -> list[tuple[list[str], str]]:
    """Each push and each command of gh that the host ran, in order, with its folder."""
    return [(argv, cwd) for argv, cwd in host.ran if argv[:2] == ["git", "push"] or argv[0] == "gh"]


@pytest.mark.supports("test_the_pull_request_stays_a_draft_while_a_deliverable_is_left_open")
def test_commit_that_leaves_a_deliverable_open_pushes_nothing_and_asks_gh_nothing(
    tmp_path: Any, host: Any, gh_state: str
):
    """Given the walkthrough's run with a remote origin, whose command was signed off by tree.py
    signoff and whose guide is open, its pull request open
    When tree.py commit runs with the ground
    Then it gives 0 printing the new commit's hash, origin holds no work branch, and gh was asked
    nothing"""
    r = left_past(str(tmp_path))
    rn_files.with_origin(r.repo, os.path.join(str(tmp_path), "origin.git"))
    opened_pr(gh_state)
    assert r.main(host, "signoff", r.run)[0] == 0
    code, out, err = r.main(host, "commit", r.run, "The user signs it off.")
    assert (code, out, err) == (0, f"{r.head()}\n", "")
    assert pushed(str(tmp_path)) == ""
    assert sent(host) == []


@pytest.mark.supports("test_the_pull_request_stays_a_draft_after_the_last_signoff")
def test_commit_that_leaves_each_deliverable_done_commits_it_pushing_nothing_and_asking_gh_nothing(
    tmp_path: Any, host: Any, gh_state: str
):
    """Given the walkthrough's run with a remote origin, whose last deliverable was signed off by
    tree.py signoff, its pull request open
    When tree.py commit runs with the ground
    Then it gives 0 printing the new commit's hash, origin holds no work branch, and the host ran
    no push and no command of gh, as the final check pushes the work and the user marks the pull
    request ready"""
    r = signed_last(str(tmp_path), host, gh_state)
    before = r.head()
    code, out, err = r.main(host, "commit", r.run, "The user signs it off.")
    assert (code, err) == (0, "")
    assert out == f"{r.head()}\n" and r.head() != before
    assert pushed(str(tmp_path)) == ""
    assert sent(host) == []


# The run's folder


@pytest.mark.supports("test_the_pruner_rewrites_each_node_its_change_touches_before_the_commit")
@pytest.mark.parametrize(
    "folder", ["invoicer", ".claude/worktrees/rn-x/.rn/y", f".claude/worktrees/{BRANCH}/.rn"]
)
def test_a_folder_that_isnt_a_runs_gives_1(tmp_path: Any, host: Any, folder: str):
    """Given the walkthrough's run
    When tree.py touched runs with a folder of invoicer, one whose names differ, or the worktree's
    .rn
    Then it gives 1 naming the folder"""
    r = Run(str(tmp_path), walkthrough())
    refused(r.main(host, "touched", folder, "/goal"), folder)


@pytest.mark.supports("test_the_pruner_rewrites_each_node_its_change_touches_before_the_commit")
def test_a_runs_folder_with_no_design_tree_gives_1(tmp_path: Any, host: Any):
    """Given the walkthrough's run whose design tree is taken away
    When tree.py touched runs on its folder
    Then it gives 1 naming the folder"""
    r = Run(str(tmp_path), walkthrough())
    os.remove(r.tree_path)
    refused(r.main(host, "touched", r.run, "/goal"), r.run)


@pytest.mark.supports("test_the_pruner_rewrites_each_node_its_change_touches_before_the_commit")
def test_a_runs_folder_given_whole_is_the_same_run(tmp_path: Any, host: Any):
    """Given the walkthrough's run
    When tree.py touched runs on its folder given as an absolute path
    Then it prints what it prints for the folder from the repository's top"""
    r = Run(str(tmp_path), walkthrough())
    pointer = "/deliverables/2"
    assert r.main(host, "touched", r.folder, pointer) == r.main(host, "touched", r.run, pointer)
