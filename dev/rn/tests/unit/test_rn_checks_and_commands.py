"""The unit cases of the checks of a role's result and of each command's main: check/'s
generator.faults and evaluator.faults, and scripts/tree.py's, scripts/check.py's, and
scripts/cut.py's main, one for each class of what each takes and gives, its refusals among them,
with several decisions, conditions, faults, and deliverables due among them, a place or a name that
nearly matches beside each that matches, and each line that a check gives named. Each command lies
in a file that shares its name with a package of domain/, so each is loaded from its path."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Any

import pytest
from check import evaluator, generator
from fault import Wrong
from repo_files import git, write_files
from rn_bench import COMMAND, GUIDE, RN, RUN, command, plan, worktree

TAX = {
    "path": COMMAND,
    "condition": "N1",
    "about": "The tax rate",
    "decided": "--rate",
    "by": "user",
}
LINES = {"path": COMMAND, "condition": "N1", "about": "The lines", "decided": "a;b;c", "by": "user"}


def run_with(tmp: str, files: dict[str, Any]) -> str:
    """invoicer's worktree with the plan and each file in it."""
    return worktree(tmp, files)


def generator_cut(path: str = COMMAND, kind: str = "code") -> dict[str, Any]:
    """The generator's Cut of the deliverable, with the command's two decisions."""
    return {
        "role": "generator",
        "deliverable": {"name": "n", "path": path, "kind": kind},
        "best_practice": kind,
        "goal": plan()["goal"]["decided"],
        "decisions": [TAX, LINES] if path == COMMAND else [],
    }


CUT = f"{RUN}/rounds/1/generator.cut.json"
RESULT = f"{RUN}/rounds/1/generator.json"
EVALUATOR_CUT = f"{RUN}/rounds/1/evaluator-C1.cut.json"
EVALUATOR = f"{RUN}/rounds/1/evaluator-C1.json"
C1 = {
    "role": "evaluator",
    "deliverable": {"name": "n", "path": COMMAND, "kind": "code"},
    "best_practice": "code",
    "goal": "g",
    "group": "C1",
    "conditions": ["N1", "N2", "N3"],
}


def at(decision: dict[str, Any]) -> dict[str, str]:
    """The place where a result carries the decision out."""
    keys = ("path", "condition", "about")
    return {**{k: decision[k] for k in keys}, "at": f"{COMMAND}:1"}


@pytest.mark.supports("test_a_generators_result_that_carries_out_each_decision_passes_its_check")
def test_a_made_result_with_each_decision_carried_out_has_no_fault(tmp_path: Any):
    """Given the generator's Cut, and its result made with a place for each decision
    When generator.faults checks it
    Then it gives none"""
    made = {"result": "made", "carried_out": [at(TAX), at(LINES)]}
    top = run_with(str(tmp_path), {CUT: generator_cut(), RESULT: made, COMMAND: "x\n"})
    assert generator.faults(os.path.join(top, RUN), CUT, RN, top) == []


@pytest.mark.supports("test_a_generators_point_passes_its_check_and_starts_no_evaluator")
def test_a_point_needs_no_decision_carried_out(tmp_path: Any):
    """Given the generator's Cut, and its result point
    When generator.faults checks it
    Then it gives none"""
    point = {"result": "point", "point": "EUR alone?"}
    top = run_with(str(tmp_path), {CUT: generator_cut(), RESULT: point})
    assert generator.faults(os.path.join(top, RUN), CUT, RN, top) == []


@pytest.mark.supports("test_a_generators_point_passes_its_check_and_starts_no_evaluator")
def test_a_point_with_no_text_is_a_fault(tmp_path: Any):
    """Given the generator's Cut, and its result point with no point's text
    When generator.faults checks it
    Then it names the point"""
    top = run_with(str(tmp_path), {CUT: generator_cut(), RESULT: {"result": "point"}})
    faults = generator.faults(os.path.join(top, RUN), CUT, RN, top)
    assert len(faults) == 1 and "point" in faults[0]


@pytest.mark.supports("test_a_generators_result_that_carries_out_each_decision_passes_its_check")
def test_a_made_result_with_no_deliverable_at_its_path_is_a_fault(tmp_path: Any):
    """Given the generator's Cut, and its result made with a place for each decision, and no file
    at the command's path
    When generator.faults checks it
    Then it names the command's path"""
    made = {"result": "made", "carried_out": [at(TAX), at(LINES)]}
    top = run_with(str(tmp_path), {CUT: generator_cut(), RESULT: made})
    faults = generator.faults(os.path.join(top, RUN), CUT, RN, top)
    assert len(faults) == 1 and COMMAND in faults[0]


@pytest.mark.supports("test_a_generators_result_that_carries_out_each_decision_passes_its_check")
def test_a_point_still_open_in_the_cut_needs_no_place(tmp_path: Any):
    """Given the generator's Cut with a point still open beside the two decisions, and its result
    made with a place for the two
    When generator.faults checks it
    Then it gives none"""
    held = generator_cut()
    held["decisions"].append({**TAX, "about": "The currency", "decided": None})
    made = {"result": "made", "carried_out": [at(TAX), at(LINES)]}
    top = run_with(str(tmp_path), {CUT: held, RESULT: made, COMMAND: "x\n"})
    assert generator.faults(os.path.join(top, RUN), CUT, RN, top) == []


@pytest.mark.supports("test_a_generators_result_that_leaves_a_decision_out_is_held_naming_it")
def test_a_made_result_leaving_a_decision_out_names_it(tmp_path: Any):
    """Given the generator's Cut, and its result made with a place for the lines alone
    When generator.faults checks it
    Then it names the tax rate"""
    made = {"result": "made", "carried_out": [at(LINES)]}
    top = run_with(str(tmp_path), {CUT: generator_cut(), RESULT: made, COMMAND: "x\n"})
    faults = generator.faults(os.path.join(top, RUN), CUT, RN, top)
    assert len(faults) == 1 and "The tax rate" in faults[0]


@pytest.mark.supports("test_a_generators_result_that_leaves_a_decision_out_is_held_naming_it")
def test_a_made_result_leaving_each_decision_out_names_each(tmp_path: Any):
    """Given the generator's Cut with its two decisions, and its result made with no place
    When generator.faults checks it
    Then it gives two lines, the first naming the tax rate and the second the lines"""
    made = {"result": "made", "carried_out": []}
    top = run_with(str(tmp_path), {CUT: generator_cut(), RESULT: made, COMMAND: "x\n"})
    faults = generator.faults(os.path.join(top, RUN), CUT, RN, top)
    assert len(faults) == 2
    assert "The tax rate" in faults[0] and "The lines" in faults[1]


@pytest.mark.supports("test_a_generators_result_that_leaves_a_decision_out_is_held_naming_it")
@pytest.mark.parametrize(
    "place",
    [{**at(TAX), "condition": "N2"}, {**at(TAX), "path": GUIDE}, {**at(TAX), "about": "The tax"}],
    ids=["another condition", "another node", "an about that nearly matches"],
)
def test_a_place_that_nearly_matches_a_decision_doesnt_carry_it_out(
    tmp_path: Any, place: dict[str, str]
):
    """Given the generator's Cut, and its result made with a place for the lines, and one for
    the tax rate under another condition, of another node, or by an about that nearly matches
    When generator.faults checks it
    Then it gives one line, naming the tax rate"""
    made = {"result": "made", "carried_out": [at(LINES), place]}
    top = run_with(str(tmp_path), {CUT: generator_cut(), RESULT: made, COMMAND: "x\n"})
    faults = generator.faults(os.path.join(top, RUN), CUT, RN, top)
    assert len(faults) == 1 and "The tax rate" in faults[0]


@pytest.mark.supports("test_a_generators_point_passes_its_check_and_starts_no_evaluator")
def test_a_point_of_blanks_alone_is_a_fault(tmp_path: Any):
    """Given the generator's Cut, and its result point whose text is blanks alone
    When generator.faults checks it
    Then it gives one line, naming the point"""
    point = {"result": "point", "point": " \n"}
    top = run_with(str(tmp_path), {CUT: generator_cut(), RESULT: point})
    faults = generator.faults(os.path.join(top, RUN), CUT, RN, top)
    assert len(faults) == 1 and "point" in faults[0]


@pytest.mark.supports("test_a_generators_result_that_carries_out_each_decision_passes_its_check")
def test_a_deliverable_of_many_files_is_at_its_folder(tmp_path: Any):
    """Given the generator's Cut of the folder invoicer/, its result made with a place for each
    decision, and a file in that folder
    When generator.faults checks it
    Then it gives none, as a deliverable of many files lies at its folder"""
    held = {**generator_cut(), "deliverable": {"name": "n", "path": "invoicer", "kind": "code"}}
    made = {"result": "made", "carried_out": [at(TAX), at(LINES)]}
    top = run_with(str(tmp_path), {CUT: held, RESULT: made, COMMAND: "x\n"})
    assert generator.faults(os.path.join(top, RUN), CUT, RN, top) == []


@pytest.mark.supports("test_a_role_that_ends_with_no_result_in_its_file_is_held")
@pytest.mark.parametrize("result", [None, {"result": "done"}, "{"], ids=["none", "form", "json"])
def test_a_result_missing_out_of_form_or_not_json_is_a_fault(tmp_path: Any, result: Any):
    """Given the generator's Cut, and no result, one out of its form, or one that isn't JSON
    When generator.faults checks it
    Then it names generator.json"""
    files: dict[str, Any] = {CUT: generator_cut()}
    if result is not None:
        files[RESULT] = result
    top = run_with(str(tmp_path), files)
    faults = generator.faults(os.path.join(top, RUN), CUT, RN, top)
    assert len(faults) == 1 and "generator.json" in faults[0]


# A guide that holds the readme best practice's template: its title, what it is, and who it's for.
IN_FORM = (
    "# Invoicer\n\nInvoicer is a command that prints an invoice.\n\nInvoicer is for you when you"
    " keep lines in a spreadsheet. With it, you print each invoice.\n"
)


@pytest.mark.supports("test_a_generators_end_with_its_deliverable_off_its_template_is_held")
@pytest.mark.parametrize(
    ("path", "kind", "text", "faults"),
    [
        (GUIDE, "readme", f"{IN_FORM}\n## FAQ\n", 1),
        (GUIDE, "readme", IN_FORM, 0),
        ("docs/notes.md", "light", "## FAQ\n", 0),
        ("docs/notes.txt", "readme", "## FAQ\n", 0),
        (COMMAND, "code", "x\n", 0),
    ],
    ids=[
        "off its template",
        "in its template",
        "a Markdown document of a kind with no template",
        "a kind with a template, at a path that isn't Markdown",
        "code",
    ],
)
def test_a_document_is_held_to_its_kinds_template_where_one_exists(
    tmp_path: Any, path: str, kind: str, text: str, faults: int
):
    """Given a guide of readme off its template or in it, a Markdown document of a kind with no
    template, a document of readme at a path that isn't Markdown, or the command, of code, each
    made
    When generator.faults checks it
    Then it gives one line for the guide off its template, naming its line of FAQ, and none for
    each other"""
    made = {"result": "made", "carried_out": [at(TAX), at(LINES)] if path == COMMAND else []}
    files = {CUT: generator_cut(path, kind), RESULT: made, path: text}
    top = run_with(str(tmp_path), files)
    found = generator.faults(os.path.join(top, RUN), CUT, RN, top)
    assert len(found) == faults
    assert not faults or f'{GUIDE}:7: "## FAQ" lies beside the template' in found[0]


@pytest.mark.supports("test_a_generators_end_with_its_deliverable_off_its_template_is_held")
def test_a_document_off_its_template_and_a_decision_left_out_give_both(tmp_path: Any):
    """Given a guide of readme off its template, and its Cut with a decision of its own that the
    result names nowhere
    When generator.faults checks it
    Then it gives two lines: one naming the decision, and one naming the guide's line of FAQ"""
    held = generator_cut(GUIDE, "readme")
    held["decisions"] = [{**TAX, "path": GUIDE, "about": "The steps"}]
    made = {"result": "made", "carried_out": []}
    files = {CUT: held, RESULT: made, GUIDE: f"{IN_FORM}\n## FAQ\n"}
    top = run_with(str(tmp_path), files)
    found = generator.faults(os.path.join(top, RUN), CUT, RN, top)
    assert len(found) == 2 and "The steps" in found[0]
    assert f'{GUIDE}:7: "## FAQ" lies beside the template' in found[1]


@pytest.mark.supports("test_a_generators_result_that_carries_out_each_decision_passes_its_check")
@pytest.mark.parametrize("cut", [None, {"role": "generator"}], ids=["none", "out of form"])
def test_a_cut_missing_or_out_of_form_is_refused(tmp_path: Any, cut: Any):
    """Given no Cut, or one out of its form
    When generator.faults checks a result beside it
    Then it refuses with Wrong, naming generator.cut.json"""
    top = run_with(str(tmp_path), {CUT: cut} if cut else {})
    with pytest.raises(Wrong) as refused:
        generator.faults(os.path.join(top, RUN), CUT, RN, top)
    assert "generator.cut.json" in str(refused.value)


@pytest.mark.supports(
    "test_an_evaluators_result_that_answers_each_condition_of_its_group_passes_its_check"
)
def test_each_condition_of_the_group_answered_once_has_no_fault(tmp_path: Any):
    """Given the evaluator's Cut of C1, and its result with N1 and N2 good and N3 more
    When evaluator.faults checks it
    Then it gives none"""
    result = {
        "good": [{"condition": c, "lines": ["x:1"]} for c in ("N1", "N2")],
        "more": [{"condition": "N3", "good_when": "w"}],
    }
    top = run_with(str(tmp_path), {EVALUATOR_CUT: C1, EVALUATOR: result})
    assert evaluator.faults(os.path.join(top, RUN), EVALUATOR_CUT, RN) == []


@pytest.mark.supports(
    "test_an_evaluators_result_that_leaves_a_condition_unanswered_is_held_naming_it"
)
@pytest.mark.parametrize(
    ("good", "more", "named"),
    [
        (["N1", "N2"], [], "N3"),
        (["N2", "N3"], [], "N1"),
        (["N1", "N2", "N3"], ["N3"], "N3"),
        (["N1", "N2", "N2", "N3"], [], "N2"),
        (["N1", "N2", "N3", "N4"], [], "N4"),
    ],
    ids=["last left out", "first left out", "twice", "twice as good", "outside the group"],
)
def test_a_condition_left_out_answered_twice_or_outside_the_group_is_named(
    tmp_path: Any, good: list[str], more: list[str], named: str
):
    """Given the evaluator's Cut of C1, and its result leaving N3 or N1 out, answering N3 good
    and more, answering N2 good twice, or answering N4, which C1 doesn't hold
    When evaluator.faults checks it
    Then it names that condition"""
    result = {
        "good": [{"condition": c, "lines": ["x:1"]} for c in good],
        "more": [{"condition": c, "good_when": "w"} for c in more],
    }
    top = run_with(str(tmp_path), {EVALUATOR_CUT: C1, EVALUATOR: result})
    faults = evaluator.faults(os.path.join(top, RUN), EVALUATOR_CUT, RN)
    assert len(faults) == 1 and named in faults[0]


@pytest.mark.supports("test_an_evaluators_answer_beside_good_and_more_is_held")
@pytest.mark.parametrize(
    "result",
    [
        None,
        {"good": [], "more": [], "fix": "x"},
        {"good": [{"condition": "N1", "lines": []}], "more": []},
    ],
    ids=["none", "beside", "good with no line"],
)
def test_a_result_missing_or_out_of_its_form_is_a_fault(tmp_path: Any, result: Any):
    """Given the evaluator's Cut of C1, and no result, one with a field beside good and more, or a
    good with no line that meets it
    When evaluator.faults checks it
    Then it names evaluator-C1.json"""
    files: dict[str, Any] = {EVALUATOR_CUT: C1}
    if result is not None:
        files[EVALUATOR] = result
    top = run_with(str(tmp_path), files)
    faults = evaluator.faults(os.path.join(top, RUN), EVALUATOR_CUT, RN)
    assert len(faults) == 1 and "evaluator-C1.json" in faults[0]


@pytest.mark.supports(
    "test_an_evaluators_result_that_leaves_a_condition_unanswered_is_held_naming_it"
)
def test_a_result_with_several_faults_names_each(tmp_path: Any):
    """Given the evaluator's Cut of C1, and its result leaving N3 out and answering N4, which C1
    doesn't hold
    When evaluator.faults checks it
    Then it gives two lines, one naming N3 and one naming N4"""
    result = {
        "good": [{"condition": c, "lines": ["x:1"]} for c in ("N1", "N2")],
        "more": [{"condition": "N4", "good_when": "w"}],
    }
    top = run_with(str(tmp_path), {EVALUATOR_CUT: C1, EVALUATOR: result})
    faults = evaluator.faults(os.path.join(top, RUN), EVALUATOR_CUT, RN)
    assert len(faults) == 2 and "N3" in faults[0] and "N4" in faults[1]


@pytest.mark.supports(
    "test_an_evaluators_result_that_answers_each_condition_of_its_group_passes_its_check"
)
@pytest.mark.parametrize("cut", [None, {"role": "evaluator"}], ids=["none", "out of form"])
def test_an_evaluators_cut_missing_or_out_of_form_is_refused(tmp_path: Any, cut: Any):
    """Given no Cut of the evaluator, or one out of its form
    When evaluator.faults checks a result beside it
    Then it refuses with Wrong, naming evaluator-C1.cut.json"""
    top = run_with(str(tmp_path), {EVALUATOR_CUT: cut} if cut else {})
    with pytest.raises(Wrong) as refused:
        evaluator.faults(os.path.join(top, RUN), EVALUATOR_CUT, RN)
    assert "evaluator-C1.cut.json" in str(refused.value)


@pytest.mark.supports("test_an_edit_of_the_design_tree_is_committed_with_its_ground")
def test_tree_commit_gives_0_with_the_hash(tmp_path: Any):
    """Given the plan with its goal changed
    When tree.py commit runs with a ground
    Then it gives 0 with the commit's hash"""
    top = run_with(str(tmp_path), {})
    tree = plan()
    tree["goal"]["decided"] += " Soon."
    write_files(top, {f"{RUN}/design-tree.json": json.dumps(tree)})
    code, printed, said = command("scripts/tree.py").main(["commit", RUN, "Soon"], top, RN)
    assert (code, said) == (0, "")
    assert printed.strip() == git(top, "rev-parse", "HEAD").strip()


@pytest.mark.supports("test_an_edit_of_the_design_tree_is_committed_with_its_ground")
@pytest.mark.parametrize(
    ("argv", "code"),
    [
        ([], 2),
        (["commit", RUN], 2),
        (["commit", RUN, "g", "h"], 2),
        (["push", RUN, "g"], 2),
        (["commit", RUN, "g"], 1),
    ],
    ids=["none", "no ground", "four arguments", "no such command", "no change"],
)
def test_tree_with_other_arguments_or_a_refusal_gives_its_code(
    tmp_path: Any, argv: list[str], code: int
):
    """Given no argument, no ground, an argument past the ground, a command other than commit, or
    a commit with no change
    When tree.py runs
    Then it gives 2 with the usage, or 1 with what the refusal says, printing nothing"""
    top = run_with(str(tmp_path), {})
    got, printed, said = command("scripts/tree.py").main(argv, top, RN)
    assert (got, printed) == (code, "")
    assert said.startswith("usage: tree.py commit" if code == 2 else "tree.py: ")


@pytest.mark.supports("test_an_edit_of_the_design_tree_is_committed_with_its_ground")
def test_tree_outside_a_repository_gives_1_saying_what_is_missing(tmp_path: Any):
    """Given the plan in a folder that no git repository holds
    When tree.py commit runs with a ground
    Then it gives 1, printing nothing, with what Missing says"""
    top = str(tmp_path)
    write_files(top, {f"{RUN}/design-tree.json": json.dumps(plan())})
    for name in ("architecture", "software-design", "test-design", "product-vision"):
        write_files(top, {f"docs/{name}.md": f"# {name}\n"})
    got, printed, said = command("scripts/tree.py").main(["commit", RUN, "g"], top, RN)
    assert (got, printed) == (1, "")
    assert said.startswith("tree.py: ") and "git repository" in said


@pytest.mark.supports("test_a_generators_result_that_carries_out_each_decision_passes_its_check")
@pytest.mark.parametrize(
    ("argv", "code"),
    [
        (["generator", CUT], 0),
        (["generator"], 2),
        (["generator", CUT, "x"], 2),
        (["planner", CUT], 2),
    ],
    ids=["a result that holds", "one argument", "three arguments", "no such role"],
)
def test_check_gives_0_for_a_result_that_holds_and_2_with_the_usage(
    tmp_path: Any, argv: list[str], code: int
):
    """Given the generator's Cut and its result that holds
    When check.py runs with the role and the Cut, one argument, three arguments, or a role rn
    doesn't have
    Then it gives 0 saying nothing, or 2 with the usage, printing nothing each time"""
    made = {"result": "made", "carried_out": [at(TAX), at(LINES)]}
    top = run_with(str(tmp_path), {CUT: generator_cut(), RESULT: made, COMMAND: "x\n"})
    got, printed, said = command("scripts/check.py").main(argv, top, RN)
    assert (got, printed) == (code, "")
    assert said == ("" if code == 0 else "usage: check.py generator|evaluator <cut>\n")


@pytest.mark.supports("test_a_generators_result_that_leaves_a_decision_out_is_held_naming_it")
def test_check_gives_1_with_each_fault_a_line(tmp_path: Any):
    """Given the generator's result with no place for either decision
    When check.py runs
    Then it gives 1, printing nothing, with two lines, the first naming the tax rate and the
    second the lines"""
    made = {"result": "made", "carried_out": []}
    top = run_with(str(tmp_path), {CUT: generator_cut(), RESULT: made, COMMAND: "x\n"})
    code, printed, said = command("scripts/check.py").main(["generator", CUT], top, RN)
    assert (code, printed) == (1, "")
    told = said.splitlines()
    assert said.endswith("\n") and len(told) == 2
    assert "The tax rate" in told[0] and "The lines" in told[1]


@pytest.mark.supports(
    "test_an_evaluators_result_that_answers_each_condition_of_its_group_passes_its_check"
)
@pytest.mark.parametrize(
    ("good", "code"), [(["N1", "N2", "N3"], 0), (["N1", "N2"], 1)], ids=["holds", "N3 left out"]
)
def test_check_of_an_evaluator_checks_its_answers(tmp_path: Any, good: list[str], code: int):
    """Given the evaluator's Cut of C1, and its result answering each condition, or leaving N3 out
    When check.py runs for the evaluator
    Then it gives 0 saying nothing, or 1 naming N3, printing nothing each time"""
    result = {"good": [{"condition": c, "lines": ["x:1"]} for c in good], "more": []}
    top = run_with(str(tmp_path), {EVALUATOR_CUT: C1, EVALUATOR: result})
    got, printed, said = command("scripts/check.py").main(["evaluator", EVALUATOR_CUT], top, RN)
    assert (got, printed) == (code, "")
    assert (said == "") if code == 0 else (len(said.splitlines()) == 1 and "N3" in said)


def cut_main(top: str, role: str) -> tuple[int, str, str]:
    """cut.py's main for the role, run in the worktree."""
    return command("scripts/cut.py").main([role], top)


@pytest.mark.supports("test_the_first_deliverable_of_the_work_gets_a_generator_with_its_cut")
def test_cut_gives_the_path_of_a_fresh_cut_of_the_start_due(tmp_path: Any):
    """Given the plan, and no Round
    When cut.py runs for the generator
    Then it gives 0 with the path of round 1's Cut from the worktree's top, and writes the Cut"""
    top = run_with(str(tmp_path), {})
    assert cut_main(top, "generator") == (0, f"{CUT}\n", "")
    with open(os.path.join(top, CUT), encoding="utf-8") as f:
        held = json.load(f)
    assert (held["role"], held["deliverable"]["path"], held["best_practice"]) == (
        "generator",
        COMMAND,
        "code",
    )


@pytest.mark.supports("test_deliverables_that_rest_on_none_being_made_start_at_once")
@pytest.mark.parametrize(
    ("waiting", "taken"),
    [([], "1/generator.cut.json"), ([CUT], "3/generator.cut.json")],
    ids=["none waiting", "the command's waiting"],
)
def test_cut_takes_the_generator_of_the_deliverable_with_the_fewest_cuts_with_no_result(
    tmp_path: Any, waiting: list[str], taken: str
):
    """Given the plan in which the guide rests on the product vision alone, so that a generator of
    each is due, and no Cut, or the command's Cut of round 1 with no result
    When cut.py runs for the generator
    Then it takes the command's of round 1, the first, or the guide's of round 3, whose
    deliverable holds no Cut with no result, and writes the Cut of that deliverable"""
    tree = plan()
    tree["deliverables"][1]["inputs"] = ["docs/product-vision.md"]
    cuts = {each: generator_cut() for each in waiting}
    top = run_with(str(tmp_path), {f"{RUN}/design-tree.json": tree, **cuts})
    assert cut_main(top, "generator") == (0, f"{RUN}/rounds/{taken}\n", "")
    with open(os.path.join(top, RUN, "rounds", taken), encoding="utf-8") as f:
        held = json.load(f)
    assert held["deliverable"]["path"] == (GUIDE if waiting else COMMAND)


@pytest.mark.supports("test_an_evaluator_stopped_starts_again_with_a_fresh_cut_beside_its_first")
@pytest.mark.parametrize(
    ("waiting", "taken"),
    [
        ([], "evaluator-C1.cut.json"),
        (["C1"], "evaluator-C2.cut.json"),
        (["C1", "C2"], "evaluator-C3.cut.json"),
        (["C1", "C2", "C3"], "evaluator-C1.2.cut.json"),
    ],
    ids=["none waiting", "C1 waiting", "C1 and C2 waiting", "each waiting"],
)
def test_cut_takes_the_start_due_with_the_fewest_cuts_with_no_result(
    tmp_path: Any, waiting: list[str], taken: str
):
    """Given the command made, and a Cut with no result of none, some, or each group of code
    When cut.py runs for an evaluator
    Then it takes the first group in the course's order of those with the fewest Cuts with no
    result, in a slot of its own"""
    made = {"result": "made", "carried_out": []}
    cuts = {f"{RUN}/rounds/1/evaluator-{g}.cut.json": {**C1, "group": g} for g in waiting}
    top = run_with(str(tmp_path), {CUT: generator_cut(), RESULT: made, **cuts})
    assert cut_main(top, "evaluator") == (0, f"{RUN}/rounds/1/{taken}\n", "")


@pytest.mark.supports("test_the_first_deliverable_of_the_work_gets_a_generator_with_its_cut")
@pytest.mark.parametrize(
    ("argv", "code", "said"),
    [
        ([], 2, "usage"),
        (["planner"], 2, "usage"),
        (["generator"], 1, "design-tree.json"),
        (["generator"], 1, "/rn:up"),
        (["evaluator"], 1, "no start of the evaluator is due"),
    ],
    ids=["no role", "no such role", "tree out of form", "no run", "none due"],
)
def test_cut_with_no_role_a_tree_out_of_form_no_run_or_none_due_gives_its_code(
    request: Any, tmp_path: Any, argv: list[str], code: int, said: str
):
    """Given no role or one rn doesn't have, a design tree out of form, a worktree with no run's
    folder, or no start of the role due
    When cut.py runs
    Then it gives 2 with the usage, or 1 naming the fault, and writes no Cut"""
    top = run_with(str(tmp_path), {})
    if request.node.callspec.id == "tree out of form":
        write_files(top, {f"{RUN}/design-tree.json": json.dumps({**plan(), "goal": {}})})
    if request.node.callspec.id == "no run":
        os.remove(os.path.join(top, RUN, "design-tree.json"))
    got, printed, told = command("scripts/cut.py").main(argv, top)
    assert (got, printed) == (code, "") and said in told
    assert not os.path.isdir(os.path.join(top, RUN, "rounds"))


@pytest.mark.supports("test_a_generators_result_that_carries_out_each_decision_passes_its_check")
def test_check_run_with_no_argument_exits_2_with_its_usage(tmp_path: Any):
    """Given no argument
    When check.py runs as a command, as a role runs it
    Then it exits 2, printing nothing and saying its usage"""
    done = subprocess.run(
        [sys.executable, os.path.join(RN, "scripts", "check.py")],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
        check=False,
    )
    assert (done.returncode, done.stdout) == (2, "")
    assert "usage" in done.stderr.lower()
