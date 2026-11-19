"""The unit cases of the checks of a role's result and of each command's and adapter's main:
check/'s generator.faults and evaluator.faults, scripts/tree.py's and scripts/check.py's main, and
hooks/adapters/'s start.py, items.py, and results.py main, one for each class of what each takes
and gives, its refusals among them. Each command lies in a file that shares its name with a
package of domain/, so each is loaded from its path."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from typing import Any

import pytest
from check import evaluator, generator
from fault import Wrong
from repo_files import git, write_files
from rn_bench import COMMAND, GUIDE, RN, RUN, plan, worktree

TAX = {
    "path": COMMAND,
    "condition": "N1",
    "about": "The tax rate",
    "decided": "--rate",
    "by": "user",
}
LINES = {"path": COMMAND, "condition": "N1", "about": "The lines", "decided": "a;b;c", "by": "user"}


def command(path: str) -> Any:
    """The module of the command or adapter at the path under rn's folder."""
    spec = importlib.util.spec_from_file_location("rn_command", os.path.join(RN, path))
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


@pytest.mark.supports("test_a_generators_point_starts_no_evaluator")
def test_a_point_needs_no_decision_carried_out(tmp_path: Any):
    """Given the generator's Cut, and its result point
    When generator.faults checks it
    Then it gives none"""
    point = {"result": "point", "point": "EUR alone?"}
    top = run_with(str(tmp_path), {CUT: generator_cut(), RESULT: point})
    assert generator.faults(os.path.join(top, RUN), CUT, RN, top) == []


@pytest.mark.supports("test_a_generators_point_starts_no_evaluator")
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
    assert faults and all("generator.json" in f for f in faults)


@pytest.mark.supports("test_a_generators_end_with_its_deliverable_off_its_template_is_held")
@pytest.mark.parametrize(
    ("text", "faults"),
    [("# Printing an invoice\n\n## FAQ\n", 1), ("", 0)],
    ids=["off its template", "a kind with no template"],
)
def test_a_document_is_held_to_its_kinds_template_where_one_exists(
    tmp_path: Any, text: str, faults: int
):
    """Given a guide of readme off its template, or the command, of code, which has no Markdown
    template beside its own, each made
    When generator.faults checks it
    Then it names the guide's line of FAQ, and nothing for the command"""
    path, kind = (GUIDE, "readme") if text else (COMMAND, "code")
    made = {"result": "made", "carried_out": [at(TAX), at(LINES)] if kind == "code" else []}
    files = {CUT: generator_cut(path, kind), RESULT: made, path: text or "x\n"}
    top = run_with(str(tmp_path), files)
    found = generator.faults(os.path.join(top, RUN), CUT, RN, top)
    assert len(found) == faults
    assert not faults or f'{GUIDE}:3: "## FAQ" lies beside the template' in found[0]


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
        (["N1", "N2", "N3"], ["N3"], "N3"),
        (["N1", "N2", "N3", "N4"], [], "N4"),
    ],
    ids=["left out", "twice", "outside the group"],
)
def test_a_condition_left_out_answered_twice_or_outside_the_group_is_named(
    tmp_path: Any, good: list[str], more: list[str], named: str
):
    """Given the evaluator's Cut of C1, and its result leaving N3 out, answering it twice, or
    answering N4, which C1 doesn't hold
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
    assert faults and all("evaluator-C1.json" in f for f in faults)


@pytest.mark.supports(
    "test_an_evaluators_result_that_answers_each_condition_of_its_group_passes_its_check"
)
def test_an_evaluators_cut_missing_is_refused(tmp_path: Any):
    """Given no Cut of the evaluator
    When evaluator.faults checks a result beside it
    Then it refuses with Wrong, naming evaluator-C1.cut.json"""
    top = run_with(str(tmp_path), {})
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
    [([], 2), (["commit", RUN], 2), (["push", RUN, "g"], 2), (["commit", RUN, "g"], 1)],
    ids=["none", "no ground", "no such command", "no change"],
)
def test_tree_with_other_arguments_or_a_refusal_gives_its_code(
    tmp_path: Any, argv: list[str], code: int
):
    """Given no argument, no ground, a command other than commit, or a commit with no change
    When tree.py runs
    Then it gives 2 with the usage, or 1 with what the refusal says"""
    top = run_with(str(tmp_path), {})
    got, printed, said = command("scripts/tree.py").main(argv, top, RN)
    assert (got, printed) == (code, "")
    assert said


@pytest.mark.supports("test_a_generators_result_that_carries_out_each_decision_passes_its_check")
@pytest.mark.parametrize(
    ("argv", "code"),
    [(["generator", CUT], 0), (["generator", CUT, "x"], 2), (["planner", CUT], 2)],
    ids=["a result that holds", "three arguments", "no such role"],
)
def test_check_gives_0_for_a_result_that_holds_and_2_with_the_usage(
    tmp_path: Any, argv: list[str], code: int
):
    """Given the generator's Cut and its result that holds
    When check.py runs with the role and the Cut, three arguments, or a role rn doesn't have
    Then it gives 0, or 2 with the usage"""
    made = {"result": "made", "carried_out": [at(TAX), at(LINES)]}
    top = run_with(str(tmp_path), {CUT: generator_cut(), RESULT: made, COMMAND: "x\n"})
    got, _, said = command("scripts/check.py").main(argv, top, RN)
    assert got == code and (code == 0) == (said == "")


@pytest.mark.supports("test_a_generators_result_that_leaves_a_decision_out_is_held_naming_it")
def test_check_gives_1_with_each_fault_a_line(tmp_path: Any):
    """Given the generator's result with a place for the lines alone
    When check.py runs
    Then it gives 1 with the fault naming the tax rate"""
    made = {"result": "made", "carried_out": [at(LINES)]}
    top = run_with(str(tmp_path), {CUT: generator_cut(), RESULT: made, COMMAND: "x\n"})
    code, _, said = command("scripts/check.py").main(["generator", CUT], top, RN)
    assert code == 1 and "The tax rate" in said


@pytest.mark.supports("test_the_first_deliverable_of_the_work_gets_a_generator_with_its_cut")
def test_start_gives_the_text_and_the_cut_of_the_start_due(tmp_path: Any):
    """Given the plan, and no start running
    When start.py runs for the generator
    Then it gives 0 with a text that names the Cut, and the Cut's path as the value cut"""
    top = run_with(str(tmp_path), {})
    code, printed, _ = command("hooks/adapters/start.py").main(
        ["generator"], '{"running": []}', top
    )
    given = json.loads(printed)
    assert code == 0 and given["values"] == {"cut": CUT}
    assert CUT in given["text"]


@pytest.mark.supports("test_a_generators_point_starts_no_evaluator")
def test_start_gives_why_no_work_waits(tmp_path: Any):
    """Given the generator's point
    When start.py runs for an evaluator
    Then it gives 0 with why no work waits"""
    top = run_with(str(tmp_path), {CUT: generator_cut(), RESULT: {"result": "point", "point": "p"}})
    code, printed, _ = command("hooks/adapters/start.py").main(
        ["evaluator"], '{"running": []}', top
    )
    assert code == 0 and list(json.loads(printed)) == ["none"]


@pytest.mark.supports("test_the_first_deliverable_of_the_work_gets_a_generator_with_its_cut")
@pytest.mark.parametrize(
    ("argv", "given", "code"),
    [
        ([], '{"running": []}', 2),
        (["generator"], "{", 1),
        (["generator"], '{"running": []}', 1),
        (["evaluator"], '{"running": []}', 1),
    ],
    ids=["no role", "input not JSON", "tree out of form", "no run"],
)
def test_start_with_no_role_bad_input_a_tree_out_of_form_or_no_run_gives_its_code(
    request: Any, tmp_path: Any, argv: list[str], given: str, code: int
):
    """Given no role, Lane's input that isn't JSON, a design tree out of form, or a worktree with
    no run's folder
    When start.py runs
    Then it gives 2 with the usage, or 1 naming the fault"""
    top = run_with(str(tmp_path), {})
    if request.node.callspec.id == "tree out of form":
        write_files(top, {f"{RUN}/design-tree.json": "{}"})
    if request.node.callspec.id == "no run":
        os.remove(os.path.join(top, RUN, "design-tree.json"))
    got, printed, said = command("hooks/adapters/start.py").main(argv, given, top)
    assert (got, printed) == (code, "") and said


@pytest.mark.xfail(strict=True, reason="rn's parts have empty bodies")
@pytest.mark.supports("test_a_role_that_writes_beside_its_deliverable_is_told_its_step")
def test_items_gives_each_practice_of_the_cuts_best_practice_in_order(tmp_path: Any):
    """Given the generator's Cut by code
    When items.py runs for its step with the Cut as its run value
    Then it gives 0 with each practice of code, N1.1 first"""
    top = run_with(str(tmp_path), {CUT: generator_cut()})
    given = json.dumps({"values": {"cut": CUT}})
    code, printed, _ = command("hooks/adapters/items.py").main(["generator", "3"], given, top, RN)
    items = json.loads(printed)["items"]
    assert code == 0 and items[0] == "N1.1" and len(items) == len(set(items))


@pytest.mark.xfail(strict=True, reason="rn's parts have empty bodies")
@pytest.mark.supports("test_a_role_that_writes_beside_its_deliverable_is_told_its_step")
@pytest.mark.parametrize(
    ("argv", "cut", "code"),
    [
        (["generator"], generator_cut(), 2),
        (["generator", "3"], {**generator_cut(), "best_practice": "x"}, 1),
    ],
    ids=["no step", "no such best practice"],
)
def test_items_with_no_step_or_no_best_practice_gives_its_code(
    tmp_path: Any, argv: list[str], cut: dict[str, Any], code: int
):
    """Given no step, or a Cut whose best practice rn doesn't have
    When items.py runs
    Then it gives 2 with the usage, or 1 naming the best practice"""
    top = run_with(str(tmp_path), {CUT: cut})
    given = json.dumps({"values": {"cut": CUT}})
    got, printed, said = command("hooks/adapters/items.py").main(argv, given, top, RN)
    assert (got, printed) == (code, "") and said


@pytest.mark.supports("test_a_pick_up_in_a_new_conversation_gets_the_results_kept_in_their_order")
def test_results_gives_each_result_in_the_order_of_the_rounds(tmp_path: Any):
    """Given round 1's generator made and its evaluator of C1 judged, and round 2's generator with
    no result
    When results.py runs with no words
    Then it gives 0 with the generator's made and the evaluator's judged"""
    files = {
        CUT: generator_cut(),
        RESULT: {"result": "made", "carried_out": []},
        EVALUATOR_CUT: C1,
        EVALUATOR: {"good": [], "more": []},
        f"{RUN}/rounds/2/generator.cut.json": generator_cut(),
    }
    top = run_with(str(tmp_path), files)
    code, printed, _ = command("hooks/adapters/results.py").main('{"words": ""}', top)
    assert code == 0
    assert json.loads(printed) == {
        "results": [
            {"role": "generator", "result": "made"},
            {"role": "evaluator", "result": "judged"},
        ]
    }


@pytest.mark.supports("test_up_with_a_new_request_picks_up_no_run")
def test_results_gives_none_for_words_of_a_new_request(tmp_path: Any):
    """Given a run with a result
    When results.py runs with the words of a new request
    Then it gives 0 with no result"""
    top = run_with(
        str(tmp_path), {CUT: generator_cut(), RESULT: {"result": "made", "carried_out": []}}
    )
    code, printed, _ = command("hooks/adapters/results.py").main('{"words": "a dashboard"}', top)
    assert (code, json.loads(printed)) == (0, {"results": []})


@pytest.mark.supports("test_up_alone_with_no_run_picks_up_none")
def test_results_gives_none_where_no_run_is(tmp_path: Any):
    """Given a folder with no run's folder
    When results.py runs with no words
    Then it gives 0 with no result"""
    code, printed, _ = command("hooks/adapters/results.py").main('{"words": ""}', str(tmp_path))
    assert (code, json.loads(printed)) == (0, {"results": []})


@pytest.mark.supports("test_a_pick_up_in_a_new_conversation_gets_the_results_kept_in_their_order")
def test_results_of_a_result_not_json_gives_1_naming_it(tmp_path: Any):
    """Given round 1's generator, its result not JSON
    When results.py runs with no words
    Then it gives 1, naming the result's file"""
    top = run_with(str(tmp_path), {CUT: generator_cut(), RESULT: "{"})
    code, printed, said = command("hooks/adapters/results.py").main('{"words": ""}', top)
    assert (code, printed) == (1, "") and "generator.json" in said


@pytest.mark.supports("test_a_pick_up_in_a_new_conversation_gets_the_results_kept_in_their_order")
def test_results_of_input_not_json_gives_1(tmp_path: Any):
    """Given Lane's input that isn't JSON
    When results.py runs
    Then it gives 1, saying so"""
    code, printed, said = command("hooks/adapters/results.py").main("{", str(tmp_path))
    assert (code, printed) == (1, "") and said


@pytest.mark.supports("test_a_generators_result_that_carries_out_each_decision_passes_its_check")
@pytest.mark.parametrize(
    "path",
    [
        "scripts/check.py",
        pytest.param(
            "hooks/adapters/items.py",
            marks=pytest.mark.xfail(strict=True, reason="rn's parts have empty bodies"),
        ),
    ],
)
def test_a_command_run_with_no_argument_exits_2_with_its_usage(tmp_path: Any, path: str):
    """Given no argument
    When check.py, or items.py, runs as a command, as Lane runs it
    Then it exits 2, printing nothing and saying its usage"""
    done = subprocess.run(
        [sys.executable, os.path.join(RN, path)],
        input="{}",
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
        check=False,
    )
    assert (done.returncode, done.stdout) == (2, "")
    assert "usage" in done.stderr.lower()
