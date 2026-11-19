"""The unit cases of the design tree's check and commit: schemas/form.py's load and hold, and
tree/'s design.read, inputs.faults, work.faults, status.faults, git.commit, and commit.commit, one
for each class of what each takes and gives, its refusals among them."""

from __future__ import annotations

import json
import os
from typing import Any

import pytest
from fault import CantRun, Missing, Wrong
from repo_files import git, write_files
from rn_bench import COMMAND, GUIDE, RN, RUN, plan, worktree
from schemas import form
from tree import commit, design, inputs, status, work
from tree import git as tree_git

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts have empty bodies")

SCHEMA = os.path.join(RN, "domain", "best-practices", "design-tree", "design-tree.schema.json")
PRACTICES = os.path.join(RN, "domain", "best-practices")


def repo(tmp: str, tree: dict[str, Any] | None = None) -> str:
    """invoicer's worktree with the tree, the plan by default, in the run's folder."""
    return worktree(tmp, {f"{RUN}/design-tree.json": tree} if tree else None)


@pytest.mark.supports("test_an_edit_out_of_form_is_refused_before_its_commit")
def test_load_gives_the_schema_of_a_file():
    """Given the design tree best practice's schema
    When form.load reads it
    Then it gives the schema, titled design tree"""
    assert form.load(SCHEMA)["title"] == "design tree"


@pytest.mark.supports("test_an_edit_out_of_form_is_refused_before_its_commit")
@pytest.mark.parametrize("text", [None, "{"])
def test_load_of_a_file_missing_or_not_json_cant_run(tmp_path: Any, text: str | None):
    """Given no file, or a file that isn't JSON
    When form.load reads it
    Then it refuses with CantRun, as rn's own file is at fault"""
    path = os.path.join(str(tmp_path), "s.json")
    if text is not None:
        write_files(str(tmp_path), {"s.json": text})
    with pytest.raises(CantRun):
        form.load(path)


@pytest.mark.supports("test_an_edit_out_of_form_is_refused_before_its_commit")
def test_hold_passes_a_value_in_its_form():
    """Given the plan and the design tree's schema
    When form.hold holds the plan to it
    Then it gives nothing"""
    assert form.hold(plan(), form.load(SCHEMA), "design-tree.json") is None


@pytest.mark.supports("test_an_edit_out_of_form_is_refused_before_its_commit")
@pytest.mark.parametrize(
    ("change", "path"),
    [
        (lambda t: t["goal"].pop("by"), "goal"),
        (lambda t: t["deliverables"][0].update(status="late"), "deliverables/0"),
        (lambda t: t["work"].append({"do": "make"}), "work/2"),
        (lambda t: t.update(extra=1), "extra"),
        (lambda t: t["goal"].update(decided=1), "goal/decided"),
    ],
    ids=["required", "anyOf", "array item", "additional", "type"],
)
def test_hold_refuses_a_value_out_of_its_form_naming_the_place(change: Any, path: str):
    """Given the plan changed out of its form: a field required left out, a deliverable of no form,
    an item of work without its path, a field the schema doesn't name, or text given a number
    When form.hold holds it to the schema
    Then it refuses with Wrong, naming the file and the place"""
    tree = plan()
    change(tree)
    with pytest.raises(Wrong) as refused:
        form.hold(tree, form.load(SCHEMA), "design-tree.json")
    assert "design-tree.json" in str(refused.value)
    assert path in str(refused.value)


@pytest.mark.supports("test_an_evaluators_answer_beside_good_and_more_is_held")
def test_hold_refuses_a_value_of_no_enum_naming_the_values():
    """Given a generator's result whose result is neither made nor point
    When form.hold holds it to the generator's schema
    Then it refuses with Wrong, naming made and point"""
    schema = form.load(os.path.join(RN, "domain", "schemas", "generator.schema.json"))
    with pytest.raises(Wrong) as refused:
        form.hold({"result": "done"}, schema, "generator.json")
    assert "made" in str(refused.value) and "point" in str(refused.value)


@pytest.mark.supports("test_an_edit_of_the_design_tree_is_committed_with_its_ground")
def test_read_gives_the_tree_in_form(tmp_path: Any):
    """Given the run's folder with the plan
    When design.read reads it
    Then it gives the plan"""
    top = repo(str(tmp_path))
    assert design.read(os.path.join(top, RUN), RN) == plan()


@pytest.mark.supports("test_an_edit_out_of_form_is_refused_before_its_commit")
@pytest.mark.parametrize("text", [None, "{", '{"goal": {}}'])
def test_read_refuses_a_tree_missing_not_json_or_out_of_its_schema(tmp_path: Any, text: Any):
    """Given the run's folder with no design-tree.json, one that isn't JSON, or one out of its
    schema
    When design.read reads it
    Then it refuses with Wrong, naming design-tree.json"""
    run = os.path.join(str(tmp_path), RUN)
    os.makedirs(run)
    if text is not None:
        write_files(run, {"design-tree.json": text})
    with pytest.raises(Wrong) as refused:
        design.read(run, RN)
    assert "design-tree.json" in str(refused.value)


@pytest.mark.supports("test_an_item_of_work_before_an_input_not_done_is_refused")
def test_read_refuses_a_tree_that_fails_a_check(tmp_path: Any):
    """Given the plan with the guide first in the work
    When design.read reads it
    Then it refuses with Wrong, naming the guide"""
    tree = plan()
    tree["work"].reverse()
    top = repo(str(tmp_path), tree)
    with pytest.raises(Wrong) as refused:
        design.read(os.path.join(top, RUN), RN)
    assert GUIDE in str(refused.value)


@pytest.mark.supports(
    "test_a_deliverable_whose_inputs_leave_out_a_kind_its_best_practice_takes_is_refused"
)
def test_inputs_of_each_kind_a_best_practice_takes_have_no_fault(tmp_path: Any):
    """Given the plan, its inputs files of the repository or a node
    When inputs.faults checks it
    Then it gives none"""
    assert inputs.faults(plan(), PRACTICES, repo(str(tmp_path))) == []


@pytest.mark.supports(
    "test_a_deliverable_whose_inputs_leave_out_a_kind_its_best_practice_takes_is_refused"
)
def test_a_kind_that_names_no_best_practice_is_a_fault(tmp_path: Any):
    """Given the plan with the command of the kind cli
    When inputs.faults checks it
    Then it names the command and cli"""
    tree = plan()
    tree["deliverables"][0]["kind"] = "cli"
    faults = inputs.faults(tree, PRACTICES, repo(str(tmp_path)))
    assert len(faults) == 1 and COMMAND in faults[0] and "cli" in faults[0]


@pytest.mark.supports(
    "test_a_deliverable_whose_inputs_leave_out_a_kind_its_best_practice_takes_is_refused"
)
@pytest.mark.parametrize("kind", ["specific", "meta"])
def test_a_specific_or_meta_kind_takes_no_input(tmp_path: Any, kind: str):
    """Given the plan with the command of the kind specific or meta, and no input
    When inputs.faults checks it
    Then it gives none"""
    tree = plan()
    tree["deliverables"][0].update(kind=kind, inputs=[])
    if kind == "specific":
        tree["deliverables"][0].update(check="python3 -m invoicer runs", good=False, decisions=[])
        tree["deliverables"][0].pop("necessary_conditions")
    assert inputs.faults(tree, PRACTICES, repo(str(tmp_path))) == []


@pytest.mark.supports(
    "test_a_deliverable_whose_inputs_leave_out_a_kind_its_best_practice_takes_is_refused"
)
def test_inputs_leaving_out_a_kind_are_a_fault_naming_it(tmp_path: Any):
    """Given the plan with docs/test-design.md out of the command's inputs
    When inputs.faults checks it
    Then it names the command and test-design"""
    tree = plan()
    tree["deliverables"][0]["inputs"].remove("docs/test-design.md")
    faults = inputs.faults(tree, PRACTICES, repo(str(tmp_path)))
    assert len(faults) == 1 and COMMAND in faults[0] and "test-design" in faults[0]


@pytest.mark.supports(
    "test_a_deliverable_whose_inputs_leave_out_a_kind_its_best_practice_takes_is_refused"
)
def test_an_input_file_that_isnt_there_counts_for_no_kind(tmp_path: Any):
    """Given the plan with docs/test-design.md in the inputs but not in the repository
    When inputs.faults checks it
    Then it names the command"""
    top = repo(str(tmp_path))
    git(top, "rm", "-q", "docs/test-design.md")
    faults = inputs.faults(plan(), PRACTICES, top)
    assert len(faults) == 1 and COMMAND in faults[0]


@pytest.mark.supports("test_an_item_of_work_before_an_input_not_done_is_refused")
def test_work_in_the_order_of_the_inputs_has_no_fault():
    """Given the plan
    When work.faults checks it
    Then it gives none"""
    assert work.faults(plan()) == []


@pytest.mark.supports("test_an_item_of_work_before_an_input_not_done_is_refused")
def test_an_item_that_names_no_node_is_a_fault():
    """Given the plan with an item of work naming docs/faq.md, which no node is
    When work.faults checks it
    Then it names docs/faq.md"""
    tree = plan()
    tree["work"].append({"do": "make", "path": "docs/faq.md"})
    assert [f for f in work.faults(tree) if "docs/faq.md" in f]


@pytest.mark.supports("test_an_item_of_work_before_an_input_not_done_is_refused")
def test_an_item_before_an_input_not_done_is_a_fault_and_after_one_done_is_none():
    """Given the plan with the guide first in the work, and then the command done and out of the
    work
    When work.faults checks each
    Then it names the guide and the command, and then nothing"""
    tree = plan()
    tree["work"].reverse()
    faults = work.faults(tree)
    assert len(faults) == 1 and GUIDE in faults[0] and COMMAND in faults[0]
    tree = plan()
    tree["deliverables"][0] = {"name": "c", "path": COMMAND, "kind": "code", "status": "done"}
    tree["work"] = tree["work"][1:]
    assert work.faults(tree) == []


@pytest.mark.supports("test_a_deliverable_done_with_a_condition_not_good_is_refused")
def test_status_open_or_done_with_each_condition_good_has_no_fault():
    """Given the plan, and the plan with the command done with each condition good
    When status.faults checks each
    Then it gives none"""
    assert status.faults(plan()) == []
    tree = plan()
    for condition in tree["deliverables"][0]["necessary_conditions"]:
        condition["good"] = True
    tree["deliverables"][0]["status"] = "done"
    assert status.faults(tree) == []


@pytest.mark.supports("test_a_deliverable_done_with_a_condition_not_good_is_refused")
def test_done_with_a_condition_not_good_is_a_fault():
    """Given the plan with the command doing while N1 isn't good, then done
    When status.faults checks each
    Then it gives none for doing, and names the command for done"""
    tree = plan()
    tree["deliverables"][0]["status"] = "doing"
    assert status.faults(tree) == []
    tree["deliverables"][0]["status"] = "done"
    faults = status.faults(tree)
    assert len(faults) == 1 and COMMAND in faults[0]


@pytest.mark.supports("test_an_edit_of_the_design_tree_is_committed_with_its_ground")
def test_git_commit_commits_the_runs_folder_with_the_ground(tmp_path: Any):
    """Given the plan with a decision added, and a file changed outside the run's folder
    When git.commit commits with a ground
    Then the commit holds the run's folder alone, with the ground as its message, and its hash is
    given"""
    top = repo(str(tmp_path))
    tree = plan()
    tree["goal"]["decided"] += " Soon."
    write_files(top, {f"{RUN}/design-tree.json": json.dumps(tree), "docs/architecture.md": "x"})
    hash_ = tree_git.commit(top, RUN, "The goal says when")
    assert git(top, "log", "-1", "--format=%H %s").strip() == f"{hash_} The goal says when"
    assert git(top, "status", "--porcelain").strip() == "M docs/architecture.md"


@pytest.mark.supports("test_an_edit_of_the_design_tree_is_committed_with_its_ground")
@pytest.mark.parametrize(
    ("ground", "change", "refusal"),
    [("", True, Wrong), ("A ground", False, Wrong)],
    ids=["empty ground", "no change"],
)
def test_git_commit_refuses_an_empty_ground_or_no_change(
    tmp_path: Any, ground: str, change: bool, refusal: type
):
    """Given an empty ground with a change, or a ground with no change
    When git.commit commits
    Then it refuses with Wrong, and the branch keeps its commit"""
    top = repo(str(tmp_path))
    if change:
        write_files(top, {f"{RUN}/design-tree.json": "{}"})
    with pytest.raises(refusal):
        tree_git.commit(top, RUN, ground)
    assert git(top, "log", "-1", "--format=%s").strip() == "The plan"


@pytest.mark.supports("test_an_edit_of_the_design_tree_is_committed_with_its_ground")
def test_git_commit_outside_a_repository_is_missing(tmp_path: Any):
    """Given a folder that no git repository holds
    When git.commit commits
    Then it refuses with Missing"""
    with pytest.raises(Missing):
        tree_git.commit(str(tmp_path), RUN, "A ground")


@pytest.mark.supports("test_an_edit_out_of_form_is_refused_before_its_commit")
def test_commit_refuses_a_tree_out_of_form_before_git(tmp_path: Any):
    """Given the plan with a decision that has no by
    When commit.commit commits it
    Then it refuses with Wrong, and the branch keeps its commit"""
    top = repo(str(tmp_path))
    tree = plan()
    tree["deliverables"][0]["necessary_conditions"][0]["decisions"].append({"about": "x"})
    write_files(top, {f"{RUN}/design-tree.json": json.dumps(tree)})
    with pytest.raises(Wrong):
        commit.commit(top, RUN, RN, "Out of form")
    assert git(top, "log", "-1", "--format=%s").strip() == "The plan"


@pytest.mark.supports("test_an_edit_of_the_design_tree_is_committed_with_its_ground")
def test_commit_of_a_tree_in_form_gives_the_hash(tmp_path: Any):
    """Given the plan with its goal changed, in form
    When commit.commit commits it
    Then the branch's latest commit is the one whose hash it gives"""
    top = repo(str(tmp_path))
    tree = plan()
    tree["goal"]["decided"] += " Soon."
    write_files(top, {f"{RUN}/design-tree.json": json.dumps(tree)})
    assert commit.commit(top, RUN, RN, "Soon") == git(top, "rev-parse", "HEAD").strip()
