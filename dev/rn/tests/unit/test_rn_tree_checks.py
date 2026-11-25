"""The unit cases of tree/checks.py, the faults that keep a change of the design tree from its
commit: a tree in form, the tree a run starts from with its goal open, a done deliverable with its
conditions, and each fault the contract names, one at a time and two at once: a place out of the
schema, a goal with `by` but no sentence or a sentence but no `by`, a done deliverable in one line
without its conditions, a kind with no best practice, an open deliverable's conditions out of its
best practice's set or order, an input that names neither a deliverable nor a file of the worktree,
a deliverable resting on itself directly or through another, an open Markdown deliverable lacking a
figure that its kind's template has it keep, and steps that put a deliverable before one of a kind
that its kind's best practice takes as an input; with a near match beside each."""

from __future__ import annotations

import copy
import os
from typing import Any

import pytest
import rn_files
from repo_files import write_files
from rn_files import COMMAND, GUIDE
from tree.checks import faults as tree_faults

NAME = "20261120-a-command-with-which-the"
KINDS = ("design-tree", "light", "readme", "code", "product-vision", "architecture")
# The figure that the readme template has a guide keep of its own, from the guide's folder.
HOW_IT_WORKS = "images/how-it-works.svg"


def practices() -> dict[str, Any]:
    """The best practice of each kind the cases use, by its name, read from its JSON."""
    return {kind: rn_files.practice(kind) for kind in KINDS}


def figures() -> dict[str, list[str]]:
    """The figures that the template of each kind the cases use has a document keep of its own,
    as rn's templates name them: the readme's one and the architecture's three."""
    return {
        "readme": [HOW_IT_WORKS],
        "architecture": [
            "images/concept-model.svg",
            "images/components.svg",
            "images/deployment.svg",
        ],
    }


def faults(tree: Any, given: Any, worktree: str) -> list[str]:
    """The tree's faults, by the best practices given and the figures of their templates."""
    return tree_faults(tree, given, worktree, figures())


@pytest.fixture
def worktree(tmp_path: Any) -> str:
    """The run's worktree, holding invoicer's lines."""
    folder = os.path.join(str(tmp_path), "worktree")
    write_files(folder, {"invoicer/lines.py": "LINES = []\n", "docs/old.md": "# Old\n"})
    return folder


def the_tree() -> dict[str, Any]:
    """The walkthrough's tree with the plan done and a settled decision of the command's N1."""
    tax = rn_files.decision(rn_files.TAX_ABOUT, rn_files.TAX_ANSWER, "user")
    the = rn_files.walkthrough_tree(NAME, command_decisions={"N1": [tax]})
    return the


def one_fault(found: list[str], pointer: str) -> None:
    """The faults are one line, naming the pointer."""
    assert len(found) == 1, found
    assert pointer in found[0]


def test_a_tree_in_form_has_no_fault(worktree: str):
    """Given the walkthrough's tree, each input a deliverable's path or a file of the worktree
    When its faults are found
    Then there is none"""
    assert faults(the_tree(), practices(), worktree) == []


def test_the_plan_open_with_its_conditions_in_order_has_no_fault(worktree: str):
    """Given the tree a run starts from, its goal open and the plan open, unnamed, with
    design-tree's conditions in order
    When its faults are found
    Then there is none, as the goal waits open for the pruner to write it"""
    assert faults(rn_files.started(NAME), practices(), worktree) == []


@pytest.mark.parametrize(
    ("change", "pointer"),
    [
        (lambda t: t["goal"].update(by="nobody"), "/goal/by"),
        (lambda t: t["goal"].pop("by"), "/goal"),
        (lambda t: t["goal"].update(decided=None), "/goal"),
        (
            lambda t: t["deliverables"][0].pop("necessary_conditions"),
            "/deliverables/0/necessary_conditions",
        ),
        (lambda t: t["deliverables"][1].pop("inputs"), "/deliverables/1"),
        (lambda t: t["deliverables"][1].update(status="done"), "/deliverables/1"),
        (lambda t: t["deliverables"][1].update(status="doing"), "/deliverables/1"),
        (
            lambda t: t["deliverables"][1]["necessary_conditions"][0]["decisions"][0].update(
                by="maker"
            ),
            "/deliverables/1/necessary_conditions/0/decisions/0",
        ),
        (
            lambda t: t["deliverables"][1]["necessary_conditions"][0]["decisions"][0].update(
                decided="The rate, as the user decided."
            ),
            "/deliverables/1/necessary_conditions/0/decisions/0",
        ),
        (
            lambda t: t["deliverables"][2]["necessary_conditions"][0].update(good="yes"),
            "/deliverables/2/necessary_conditions/0/good",
        ),
    ],
)
def test_a_place_out_of_the_schema_is_a_fault_naming_its_pointer(
    worktree: str, change: Any, pointer: str
):
    """Given the walkthrough's tree with one place out of design-tree.schema.json: a goal's by of no
    one, an open deliverable lacking its inputs, done with its conditions kept, or of a status
    neither open nor done, a decision by its deliverable's maker or whose decided says the user
    decided it, or a good that isn't a boolean
    When its faults are found
    Then they are one line, naming the place's pointer"""
    the = the_tree()
    change(the)
    one_fault(faults(the, practices(), worktree), pointer)


def test_a_kind_with_no_best_practice_is_a_fault(worktree: str):
    """Given the walkthrough's tree whose command's kind is `lights`, near light, which no best
    practice has
    When its faults are found
    Then they are one line, naming /deliverables/1/kind"""
    the = the_tree()
    the["deliverables"][1]["kind"] = "lights"
    one_fault(faults(the, practices(), worktree), "/deliverables/1/kind")


def test_a_done_deliverables_kind_is_held_to_the_best_practices_too(worktree: str):
    """Given the walkthrough's tree whose done plan is of the kind `plan`, which no best practice
    has
    When its faults are found
    Then they are one line, naming /deliverables/0/kind"""
    the = the_tree()
    the["deliverables"][0]["kind"] = "plan"
    one_fault(faults(the, practices(), worktree), "/deliverables/0/kind")


@pytest.mark.parametrize(
    "ids",
    [
        ["N2", "N1", "N3"],
        ["N1", "N2"],
        ["N1", "N2", "N3", "N4"],
        ["N1", "N2", "N4"],
    ],
)
def test_an_open_deliverables_conditions_other_than_its_best_practices_in_order_are_a_fault(
    worktree: str, ids: list[str]
):
    """Given the walkthrough's tree whose command, of the kind light of N1, N2, and N3, holds its
    conditions swapped, one short, one past, or one other
    When its faults are found
    Then they are one line, naming /deliverables/1/necessary_conditions"""
    the = the_tree()
    held = {each["id"]: each for each in the["deliverables"][1]["necessary_conditions"]}
    the["deliverables"][1]["necessary_conditions"] = [
        held.get(each, rn_files.condition(each)) for each in ids
    ]
    one_fault(faults(the, practices(), worktree), "/deliverables/1/necessary_conditions")


def test_a_done_node_with_no_file_keeps_its_conditions_without_a_fault(worktree: str):
    """Given the walkthrough's tree beside a done node with no file of the kind light, holding its
    conditions good
    When its faults are found
    Then there is none"""
    the = the_tree()
    the["deliverables"].append(
        {
            "name": "The invoices' people",
            "path": "docs/people.md",
            "kind": "light",
            "status": "done",
            "file": False,
            "necessary_conditions": [
                rn_files.condition(each, True) for each in rn_files.conditions("light")
            ],
        }
    )
    assert faults(the, practices(), worktree) == []


@pytest.mark.parametrize(
    "named", ["invoicer/nothing.py", "invoicer/lines", "invoicer/lines.py.bak"]
)
def test_an_input_naming_neither_a_deliverable_nor_a_file_of_the_worktree_is_a_fault(
    worktree: str, named: str
):
    """Given the walkthrough's tree whose command names as its input a file the worktree lacks, or
    one short of or past invoicer/lines.py, which it holds
    When its faults are found
    Then they are one line, naming /deliverables/1/inputs/0"""
    the = the_tree()
    the["deliverables"][1]["inputs"] = [named]
    one_fault(faults(the, practices(), worktree), "/deliverables/1/inputs/0")


def test_an_input_is_looked_for_in_the_worktree_not_the_folder_it_runs_in(
    worktree: str, tmp_path: Any, monkeypatch: pytest.MonkeyPatch
):
    """Given the walkthrough's tree whose command names docs/new.md, which the folder the check
    runs in holds and the worktree doesn't
    When its faults are found
    Then they are one line, naming /deliverables/1/inputs/0"""
    write_files(str(tmp_path), {"docs/new.md": "# New\n"})
    monkeypatch.chdir(str(tmp_path))
    the = the_tree()
    the["deliverables"][1]["inputs"] = ["docs/new.md"]
    one_fault(faults(the, practices(), worktree), "/deliverables/1/inputs/0")


def test_inputs_of_none_one_and_several_each_named_hold(worktree: str):
    """Given the walkthrough's tree whose command rests on none, and whose guide rests on the
    command, invoicer's lines, and an old document of the worktree
    When its faults are found
    Then there is none"""
    the = the_tree()
    the["deliverables"][1]["inputs"] = []
    the["deliverables"][2]["inputs"] = [COMMAND, "invoicer/lines.py", "docs/old.md"]
    assert faults(the, practices(), worktree) == []


def test_a_deliverable_resting_on_itself_is_a_fault(worktree: str):
    """Given the walkthrough's tree whose command names its own path in its inputs
    When its faults are found
    Then they are one line, naming /deliverables/1"""
    the = the_tree()
    the["deliverables"][1]["inputs"] = [COMMAND]
    one_fault(faults(the, practices(), worktree), "/deliverables/1")


def test_two_deliverables_resting_on_each_other_are_each_a_fault(worktree: str):
    """Given the walkthrough's tree whose command rests on the guide, which rests on the command
    When its faults are found
    Then they are two lines, one naming /deliverables/1 and one /deliverables/2"""
    the = the_tree()
    the["deliverables"][1]["inputs"] = [GUIDE]
    found = faults(the, practices(), worktree)
    assert len(found) == 2, found
    assert any("/deliverables/1" in each for each in found)
    assert any("/deliverables/2" in each for each in found)


def test_a_deliverable_resting_on_one_twice_rests_on_nothing_of_itself(worktree: str):
    """Given the walkthrough's tree with a changelog resting on both the command and the guide,
    which rests on the command
    When its faults are found
    Then there is none, as no deliverable rests on itself"""
    the = the_tree()
    the["deliverables"].append(
        rn_files.open_node("The changes", "CHANGELOG.md", "light", [COMMAND, GUIDE])
    )
    assert faults(the, practices(), worktree) == []


def test_each_fault_of_a_tree_is_given_not_only_the_first(worktree: str):
    """Given the walkthrough's tree whose done plan's kind is `plan`, which no best practice has,
    and whose command names as its input a file the worktree lacks
    When its faults are found
    Then they are two lines, naming /deliverables/0/kind and /deliverables/1/inputs/0"""
    the = copy.deepcopy(the_tree())
    the["deliverables"][0]["kind"] = "plan"
    the["deliverables"][1]["inputs"] = ["invoicer/cli.py"]
    found = faults(the, practices(), worktree)
    assert len(found) == 2, found
    assert any("/deliverables/0/kind" in each for each in found)
    assert any("/deliverables/1/inputs/0" in each for each in found)


# The steps of the way to the goal.


def stepped(*steps: dict[str, Any]) -> dict[str, Any]:
    """The walkthrough's tree with the steps given."""
    the = the_tree()
    the["steps"] = [copy.deepcopy(each) for each in steps]
    return the


def test_steps_holding_each_deliverable_but_the_plan_once_have_no_fault(worktree: str):
    """Given the walkthrough's tree whose steps hold the command, then the guide, each once
    When its faults are found
    Then there is none"""
    the = stepped(
        rn_files.step("what it does", [COMMAND], True),
        rn_files.step("how it's used", [GUIDE], False),
    )
    assert faults(the, practices(), worktree) == []


def test_a_tree_with_no_steps_has_no_fault_of_them(worktree: str):
    """Given the walkthrough's tree with no steps, as before the plan holds them
    When its faults are found
    Then there is none"""
    assert faults(stepped(), practices(), worktree) == []


@pytest.mark.parametrize(
    ("steps", "pointer", "words"),
    [
        (
            [rn_files.step("what it does", [COMMAND, "docs/none.md", GUIDE], True)],
            "/steps/0/deliverables/1",
            "docs/none.md, which no deliverable but the plan has",
        ),
        (
            [rn_files.step("the plan", [rn_files.plan_path(NAME), COMMAND, GUIDE], True)],
            "/steps/0/deliverables/0",
            "which no deliverable but the plan has",
        ),
        (
            [
                rn_files.step("what it does", [COMMAND, GUIDE], True),
                rn_files.step("how it's used", [GUIDE], False),
            ],
            "/steps/1/deliverables/0",
            f"{GUIDE}, which /steps/0 holds already",
        ),
        (
            [rn_files.step("what it does", [COMMAND], True)],
            "/steps",
            f"{GUIDE}, which no step holds",
        ),
    ],
    ids=["no-deliverable", "the-plan", "two-steps", "no-step"],
)
def test_a_fault_of_the_steps_names_its_place(
    worktree: str, steps: list[dict[str, Any]], pointer: str, words: str
):
    """Given the walkthrough's tree whose steps name a path that no deliverable has, the plan, a
    deliverable twice, or leave a deliverable out
    When its faults are found
    Then the one fault names the place and what's wrong there"""
    found = faults(stepped(*steps), practices(), worktree)
    one_fault(found, pointer)
    assert words in found[0]


def test_a_step_without_its_signoff_is_out_of_the_schema(worktree: str):
    """Given the walkthrough's tree whose one step lacks `signoff`
    When its faults are found
    Then the one fault names the step"""
    lacking = rn_files.step("what it does", [COMMAND, GUIDE], True)
    del lacking["signoff"]
    one_fault(faults(stepped(lacking), practices(), worktree), "/steps/0")


# The figures that a deliverable's kind's template has it keep of its own.

GUIDE_FIGURE = f"docs/{HOW_IT_WORKS}"


def guide_with(more: list[str] | None, status: str = "open") -> dict[str, Any]:
    """The walkthrough's tree whose guide holds the more paths given, open or done."""
    the = the_tree()
    guide = the["deliverables"][2]
    guide.pop("more_paths", None)
    if more is not None:
        guide["more_paths"] = more
    if status == "done":
        the["deliverables"][2] = rn_files.done_node(rn_files.GUIDE_NAME, GUIDE, "readme")
    return the


@pytest.mark.parametrize(
    "more", [[GUIDE_FIGURE], ["docs/images/"], ["docs/images"], ["tests/", GUIDE_FIGURE]]
)
def test_a_guide_holding_its_templates_figure_has_no_fault(worktree: str, more: list[str]):
    """Given the walkthrough's tree whose guide, of the kind readme, holds in its more paths the
    figure that the readme template has it keep, docs/images/how-it-works.svg, by its path or by
    its folder's
    When its faults are found
    Then there is none"""
    assert faults(guide_with(more), practices(), worktree) == []


@pytest.mark.parametrize(
    "more", [None, ["docs/how-it-works.svg"], ["docs/images/how-it-works.png"], ["docs/imag/"]]
)
def test_a_guide_lacking_its_templates_figure_is_a_fault_naming_it(
    worktree: str, more: list[str] | None
):
    """Given the walkthrough's tree whose guide, of the kind readme, holds no more paths, or only
    a path near the figure that the readme template has it keep
    When its faults are found
    Then the one fault names the guide's more paths and the figure's path from the worktree's top,
    so that the pruner writes it in the same weighing"""
    found = faults(guide_with(more), practices(), worktree)
    one_fault(found, "/deliverables/2/more_paths")
    assert f"leaves out {GUIDE_FIGURE}" in found[0], "the figure is named"
    assert "readme" in found[0], "the kind whose template asks it is named"


def test_an_architecture_lacking_two_of_its_figures_is_a_fault_for_each(worktree: str):
    """Given the walkthrough's tree with an open architecture at dev/architecture.md, of the kind
    architecture, holding only dev/images/components.svg of its template's three figures
    When its faults are found
    Then they are two lines, each naming one figure it lacks"""
    the = guide_with([GUIDE_FIGURE])
    node = rn_files.open_node("the architecture", "dev/architecture.md", "architecture")
    node["more_paths"] = ["dev/images/components.svg"]
    the["deliverables"].append(node)
    the["steps"] = []
    found = faults(the, practices(), worktree)
    assert sorted(found) == sorted(
        f"/deliverables/3/more_paths: leaves out dev/images/{name}.svg, a figure that the"
        " template of its kind architecture has dev/architecture.md keep of its own; add it"
        for name in ("concept-model", "deployment")
    )


def test_a_done_guide_lacking_its_templates_figure_has_no_fault(worktree: str):
    """Given the walkthrough's tree whose guide is done, holding no more paths
    When its faults are found
    Then there is none, as a done deliverable keeps what its Rounds made"""
    assert faults(guide_with(None, "done"), practices(), worktree) == []


def test_a_deliverable_that_isnt_markdown_is_asked_no_figure(worktree: str):
    """Given the walkthrough's tree whose guide, of the kind readme, lies at docs/guide.txt, with
    no more paths
    When its faults are found
    Then there is none, as only a Markdown document holds its template"""
    the = guide_with(None)
    the["deliverables"][2]["path"] = "docs/guide.txt"
    assert faults(the, practices(), worktree) == []


# The order of the steps by what each kind's best practice takes as an input.

VISION = "docs/product-vision.md"


def with_vision(*steps: list[str]) -> dict[str, Any]:
    """The walkthrough's tree, its guide holding its figure, with an open product vision, which
    the readme best practice takes as an input, and a step for each list of paths given."""
    the = guide_with([GUIDE_FIGURE])
    the["deliverables"].append(rn_files.open_node("the product vision", VISION, "product-vision"))
    the["steps"] = [rn_files.step(f"step {n}", each, n == 0) for n, each in enumerate(steps)]
    return the


@pytest.mark.parametrize(
    "steps",
    [
        [[VISION], [COMMAND], [GUIDE]],
        [[VISION, COMMAND], [GUIDE]],
        [[COMMAND, VISION, GUIDE]],
    ],
    ids=["before", "before-with-another", "same-step"],
)
def test_steps_putting_each_input_of_a_kind_no_later_have_no_fault(
    worktree: str, steps: list[list[str]]
):
    """Given the walkthrough's tree with a product vision, which the readme best practice takes
    as an input, in a step before the guide's or in the guide's own
    When its faults are found
    Then there is none"""
    assert faults(with_vision(*steps), practices(), worktree) == []


def test_steps_putting_the_guide_before_the_product_vision_is_a_fault_naming_the_pair(
    worktree: str,
):
    """Given the walkthrough's tree with a product vision, which the readme best practice takes
    as an input, in a step after the guide's
    When its faults are found
    Then the one fault names the guide's place in the steps, the guide, the product vision, and
    the kind that takes it, so that the pruner reorders the steps in the same weighing"""
    found = faults(with_vision([COMMAND], [GUIDE], [VISION]), practices(), worktree)
    assert found == [
        (
            f"/steps/1/deliverables/0: puts {GUIDE} before {VISION}, which the best practice of"
            f" its kind readme takes as an input; put {VISION} in a step no later than {GUIDE}'s"
        )
    ]
