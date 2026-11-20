"""The unit cases of what rn gives Lane: lane/adapters/starts_due.py's main, one for each class of
the run that Lane gives it and of the run's folder, the commands typed and the starts that run
among them, and one for each combination of the words and the commands that decides whether the
run waits, goes on, or ends; and lane/adapters/rules.py's main, one for each role's steps, a
deliverable with more_paths, a Cut in a later slot, the generators of other Rounds an evaluator may
read, and each refusal. A start in a later slot, a result among the moves, and a Cut named from
rn's worktree stand beside the starts that run, and each Then names the whole of what an adapter
prints. Each adapter lies in a file that Lane runs as a command, so each is loaded from its
path."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Any

import pytest
from repo_files import write_files
from rn_bench import COMMAND, GUIDE, RN, RUN, command, plan, started, typed, worktree

CUT = f"{RUN}/rounds/1/generator.cut.json"
RESULT = f"{RUN}/rounds/1/generator.json"
MADE = {"result": "made", "carried_out": []}
REQUEST = "a command with which the accounting team prints an invoice from its lines"


def generator_cut(path: str = COMMAND, kind: str = "code") -> dict[str, Any]:
    """The generator's Cut of the deliverable, with no decision."""
    return {
        "role": "generator",
        "deliverable": {"name": "n", "path": path, "kind": kind},
        "best_practice": kind,
        "goal": "g",
        "decisions": [],
    }


def evaluator_cut(group: str = "C1", conditions: Any = ("N1", "N2", "N3")) -> dict[str, Any]:
    """An evaluator's Cut of the command's group."""
    return {
        "role": "evaluator",
        "deliverable": {"name": "n", "path": COMMAND, "kind": "code"},
        "best_practice": "code",
        "goal": "g",
        "group": group,
        "conditions": list(conditions),
    }


def evaluator(group: str, slot: str = "") -> str:
    """The path of the Cut of round 1's evaluator of the group, in the slot given."""
    return f"{RUN}/rounds/1/evaluator-{group}{slot}.cut.json"


def made_files() -> dict[str, Any]:
    """Round 1 of the command, its generator made."""
    return {CUT: generator_cut(), RESULT: MADE}


def starts_due(
    top: str, words: str = "", moves: list[dict[str, Any]] | None = None
) -> tuple[int, Any, str]:
    """starts_due.py's main for a run of /rn:up with the words and the moves, rn:up alone by
    default, in the worktree; what it printed as JSON where it's JSON."""
    run = {"skill": "rn:up", "words": words, "moves": [typed("rn:up")] if moves is None else moves}
    code, printed, said = command("lane/adapters/starts_due.py").main(json.dumps({"run": run}), top)
    return code, json.loads(printed) if printed else printed, said


def counts(top: str, words: str = "", moves: list[dict[str, Any]] | None = None) -> Any:
    """Each role that starts_due.py gives due with its count, or what it gave otherwise."""
    code, printed, said = starts_due(top, words, moves)
    assert code == 0, said
    if set(printed) != {"starts"}:
        return printed
    return {s["role"]: s["count"] for s in printed["starts"]}


@pytest.mark.supports("test_a_plan_signed_off_gives_lane_the_generator_of_its_first_deliverable")
@pytest.mark.parametrize(
    ("words", "moves", "due"),
    [
        (REQUEST, ["rn:up"], {}),
        (REQUEST, ["rn:up", "rn:gm"], {}),
        (REQUEST, ["rn:up", "rn:ty"], {"rn:generator": 1}),
        (REQUEST, ["rn:up", "rn:ty", "rn:gm"], {"rn:generator": 1}),
        ("", ["rn:up"], {"rn:generator": 1}),
        ("", ["rn:up", "rn:dn"], {}),
    ],
    ids=[
        "a request",
        "a request sent back",
        "a request signed off",
        "a request signed off and then sent back",
        "a pick-up",
        "a pause",
    ],
)
def test_starts_due_wait_for_the_sign_off_of_a_new_runs_plan(
    tmp_path: Any, words: str, moves: list[str], due: dict[str, int]
):
    """Given the plan with no Round, and a run with words or none, and the commands typed
    When starts_due.py runs
    Then it gives no start where the words ask for a new run and no /rn:ty is typed yet, or where
    the latest command is /rn:dn, and the command's generator otherwise"""
    top = worktree(str(tmp_path))
    assert counts(top, words, [typed(m) for m in moves]) == due


@pytest.mark.supports("test_the_sign_off_of_the_pull_request_ends_the_run")
@pytest.mark.parametrize(
    ("work", "moves", "given"),
    [
        (False, ["rn:up", "rn:ty"], {"ends": True}),
        (False, ["rn:up", "rn:ty", "rn:gm"], {}),
        (False, ["rn:up"], {}),
        (True, ["rn:up", "rn:ty"], {"rn:generator": 1}),
    ],
    ids=[
        "signed off, no work left",
        "sent back after, no work left",
        "no sign-off, no work left",
        "signed off, work left",
    ],
)
def test_starts_due_end_the_run_on_a_sign_off_with_no_work_left(
    tmp_path: Any, work: bool, moves: list[str], given: Any
):
    """Given the run's design tree with work left or none, and the commands typed
    When starts_due.py runs
    Then it gives the run's end only where the latest command is /rn:ty and no work is left"""
    tree = plan()
    if not work:
        tree["work"] = []
    top = worktree(str(tmp_path), {f"{RUN}/design-tree.json": tree})
    assert counts(top, "", [typed(m) for m in moves]) == given


@pytest.mark.supports("test_up_alone_with_no_run_starts_no_role")
def test_starts_due_with_no_runs_folder_give_none(tmp_path: Any):
    """Given a folder that holds no run's folder
    When starts_due.py runs for /rn:up alone
    Then it gives no start"""
    assert counts(str(tmp_path)) == {}


@pytest.mark.supports("test_a_pick_up_from_the_repositorys_root_finds_the_run_in_rns_worktree")
def test_starts_due_from_the_root_read_the_run_in_rns_worktree(tmp_path: Any):
    """Given the repository's root with no run's folder, and rn's worktree of the run holding the
    plan
    When starts_due.py runs at the root
    Then it gives the command's generator"""
    top = str(tmp_path)
    run = ".claude/worktrees/rn-20261119-invoices"
    docs = ("architecture", "software-design", "test-design", "product-vision")
    inputs = {f"{run}/docs/{name}.md": f"# {name}\n" for name in docs}
    write_files(top, {f"{run}/{RUN}/design-tree.json": json.dumps(plan()), **inputs})
    assert counts(top) == {"rn:generator": 1}


@pytest.mark.supports("test_a_generator_running_gets_no_second_start_of_its_deliverable")
@pytest.mark.parametrize(
    ("files", "moves", "due"),
    [
        ({CUT: generator_cut()}, [started(CUT)], {}),
        ({CUT: generator_cut()}, [], {"rn:generator": 1}),
        (made_files(), [started(CUT)], {"rn:evaluator": 3}),
        (
            {**made_files(), evaluator("C1"): evaluator_cut()},
            [started(evaluator("C1"))],
            {"rn:evaluator": 2},
        ),
    ],
    ids=[
        "a generator that runs",
        "a generator that didn't end",
        "a generator that ended",
        "an evaluator that runs",
    ],
)
def test_starts_due_leave_out_each_start_that_runs(
    tmp_path: Any, files: dict[str, Any], moves: list[dict[str, Any]], due: dict[str, int]
):
    """Given round 1's Cuts, and the starts among the run's moves
    When starts_due.py runs
    Then it leaves out each start whose prompt names a Cut with no result beside it, and counts a
    Cut with no result that no prompt names, or one with a result, as no start that runs"""
    top = worktree(str(tmp_path), files)
    assert counts(top, "", [typed("rn:up"), *moves]) == due


@pytest.mark.supports("test_deliverables_that_rest_on_none_being_made_give_lane_a_generator_each")
def test_starts_due_give_each_role_due_with_its_count(tmp_path: Any):
    """Given the plan in which the guide rests on the product vision alone, and the command's
    round 1 made
    When starts_due.py runs
    Then it gives three starts of rn:evaluator for the command and one of rn:generator for the
    guide"""
    tree = plan()
    tree["deliverables"][1]["inputs"] = ["docs/product-vision.md"]
    top = worktree(str(tmp_path), {f"{RUN}/design-tree.json": tree, **made_files()})
    starts = [{"role": "rn:evaluator", "count": 3}, {"role": "rn:generator", "count": 1}]
    assert starts_due(top) == (0, {"starts": starts}, "")


@pytest.mark.supports("test_an_evaluator_stopped_starts_again_with_a_fresh_cut_beside_its_first")
def test_starts_due_count_a_start_in_a_later_slot_as_the_one_that_runs(tmp_path: Any):
    """Given the command made, round 1's evaluator of C1 stopped in slot 1 with no result, and
    its start in slot 2 running, its prompt naming slot 2's Cut
    When starts_due.py runs
    Then it gives two starts of rn:evaluator, for C2 and C3"""
    later = evaluator("C1", ".2")
    files = {**made_files(), evaluator("C1"): evaluator_cut(), later: evaluator_cut()}
    top = worktree(str(tmp_path), files)
    moves = [typed("rn:up"), started(CUT), started(evaluator("C1", ".2"))]
    assert counts(top, "", moves) == {"rn:evaluator": 2}


@pytest.mark.supports("test_a_generator_running_gets_no_second_start_of_its_deliverable")
def test_starts_due_leave_alone_the_results_among_the_moves(tmp_path: Any):
    """Given the command made, its evaluator of C1 running, and the run's moves holding the
    generator's start, its result, and the evaluator's start, in the order Lane keeps them
    When starts_due.py runs
    Then it gives two starts of rn:evaluator"""
    top = worktree(str(tmp_path), {**made_files(), evaluator("C1"): evaluator_cut()})
    result = {"kind": "result", "role": "rn:generator", "result": "made"}
    moves = [typed("rn:up"), typed("rn:ty"), started(CUT), result, started(evaluator("C1"))]
    assert counts(top, "", moves) == {"rn:evaluator": 2}


@pytest.mark.supports("test_a_pick_up_from_the_repositorys_root_finds_the_run_in_rns_worktree")
def test_starts_due_from_the_root_count_a_start_whose_prompt_names_its_cut_from_the_worktree(
    tmp_path: Any,
):
    """Given the repository's root, and rn's worktree of the run holding the plan and the
    command's generator of round 1 cut with no result, its start's prompt naming the Cut from the
    worktree's top, as the orchestrator names it
    When starts_due.py runs at the root
    Then it gives no start, as the generator runs"""
    top = str(tmp_path)
    there = ".claude/worktrees/rn-20261119-invoices"
    docs = ("architecture", "software-design", "test-design", "product-vision")
    files = {f"{there}/docs/{name}.md": f"# {name}\n" for name in docs}
    files[f"{there}/{RUN}/design-tree.json"] = json.dumps(plan())
    files[f"{there}/{CUT}"] = json.dumps(generator_cut())
    write_files(top, files)
    assert counts(top, "", [typed("rn:up"), started(CUT)]) == {}


@pytest.mark.supports("test_a_pick_up_in_a_new_conversation_gives_lane_each_role_stopped_again")
@pytest.mark.parametrize(
    ("given", "files", "said"),
    [
        ("{", {}, ""),
        ('{"run": {"skill": "rn:up"}}', {}, ""),
        ('{"run": {"skill": "rn:up", "words": null, "moves": []}}', {}, ""),
        ('{"run": {"skill": "rn:up", "words": "", "moves": {}}}', {}, ""),
        ("[]", {}, ""),
        ("", {RESULT: "{", CUT: generator_cut()}, "generator.json"),
        ("", {f"{RUN}/design-tree.json": {**plan(), "goal": {}}}, "design-tree.json"),
    ],
    ids=[
        "input not JSON",
        "input with no words or moves",
        "words that aren't text",
        "moves that aren't a list",
        "input that isn't an object",
        "a Round not JSON",
        "a tree out of form",
    ],
)
def test_starts_due_refuse_input_or_a_runs_folder_out_of_its_form(
    tmp_path: Any, given: str, files: dict[str, Any], said: str
):
    """Given Lane's input that isn't JSON or leaves its form, with no words or moves, words that
    aren't text, moves that aren't a list, or no object at its top, or a run's folder with a Round
    that isn't JSON or a design tree out of its form
    When starts_due.py runs
    Then it gives 1, printing nothing, naming the file where one is at fault"""
    top = worktree(str(tmp_path), files)
    run = {"run": {"skill": "rn:up", "words": "", "moves": [typed("rn:up")]}}
    code, printed, told = command("lane/adapters/starts_due.py").main(given or json.dumps(run), top)
    assert (code, printed) == (1, "") and told and said in told


def rules_of(top: str, role: str, cut: str) -> tuple[int, Any, str]:
    """rules.py's main for a start of the role whose prompt names the Cut, in the worktree; what it
    printed as JSON where it's JSON."""
    given = {"run": {"skill": "rn:up", "words": ""}, **started(cut), "role": role}
    given.pop("kind")
    code, printed, said = command("lane/adapters/rules.py").main(json.dumps(given), top, RN)
    return code, json.loads(printed) if printed else printed, said


def practices(kind: str, at: str) -> list[str]:
    """Each practice of the kind's best practice that its maker takes at `decide` or `make`, as
    N<n>.<m>, the m-th practice of the condition N<n>."""
    path = os.path.join(RN, "domain", "best-practices", kind, "best-practice.json")
    with open(path, encoding="utf-8") as f:
        factors = json.load(f)["goal"]["critical_success_factors"]
    return [
        f"{n['id']}.{m}"
        for c in factors
        for n in c["necessary_conditions"]
        for m, item in enumerate(n["items"], 1)
        if item["at"] == at
    ]


def steps_of(*rules: list[dict[str, Any]]) -> dict[str, Any]:
    """Steps 1 onward, each with order before the rules given, as rules.py prints them."""
    return {
        "steps": [
            {"name": str(n), "rules": [{"type": "order"}, *each]} for n, each in enumerate(rules, 1)
        ]
    }


def end_of(role: str, cut: str, result: str) -> list[dict[str, Any]]:
    """The last step's rules of the role's start from the Cut: the writes of the result beside the
    Cut, rn's check of the role, and the result that ends it."""
    return [
        {"type": "writes", "paths": [cut.removesuffix(".cut.json") + ".json"]},
        {"type": "check", "check": f"python3 {RN}/scripts/check.py {role} {cut}"},
        {"type": "result", "results": [result]},
    ]


def generator_steps(practice: str, *deliverable: str) -> dict[str, Any]:
    """The steps of round 1's generator, by the best practice, of the deliverable's paths."""
    return steps_of(
        [{"type": "writes", "paths": []}],
        [
            {"type": "checklist", "items": practices(practice, "decide")},
            {"type": "writes", "paths": [RESULT]},
            {"type": "result", "ends": ["point"]},
        ],
        [
            {"type": "checklist", "items": practices(practice, "make")},
            {"type": "writes", "paths": [*deliverable, RESULT]},
        ],
        end_of("generator", CUT, "made"),
    )


@pytest.mark.supports("test_a_role_that_writes_beside_its_deliverable_is_told_its_step")
def test_rules_give_the_generator_its_steps_from_its_cut(tmp_path: Any):
    """Given the generator's Cut of the command by code
    When rules.py runs for a start of rn:generator whose prompt names the Cut
    Then it gives 0, saying nothing, with steps 1 to 4 in order, each with order: step 1 writes
    nothing, step 2 the checklist of code's decide practices, the writes of the result alone, and
    a result that ends on point, step 3 that of its make practices and the writes of the command
    and the result, and step 4 the writes of the result, rn's check of the generator, and the
    result made, and nothing else"""
    top = worktree(str(tmp_path), {CUT: generator_cut()})
    assert rules_of(top, "rn:generator", CUT) == (0, generator_steps("code", COMMAND), "")


@pytest.mark.supports("test_a_role_that_writes_beside_its_deliverable_is_told_its_step")
@pytest.mark.parametrize(
    "more",
    [["tests/test_main.py"], ["tests/test_main.py", "tests/fixtures/"]],
    ids=["a file", "a file and a folder"],
)
def test_rules_let_the_generator_make_each_more_path_of_its_deliverable(
    tmp_path: Any, more: list[str]
):
    """Given the generator's Cut of the command by code, its deliverable with more_paths of one
    file, and of a file and a folder, as the case of its steps holds one with none
    When rules.py runs for its start
    Then it gives the generator's steps whole, step 3 the writes of the command, each of its
    more_paths in their order, and the result"""
    held = generator_cut()
    held["deliverable"]["more_paths"] = more
    top = worktree(str(tmp_path), {CUT: held})
    assert rules_of(top, "rn:generator", CUT) == (0, generator_steps("code", COMMAND, *more), "")


@pytest.mark.supports("test_a_round_of_refactoring_comes_only_after_the_content_is_good")
def test_rules_give_a_generator_of_refactoring_the_practices_of_the_refactor_best_practice(
    tmp_path: Any,
):
    """Given the generator's Cut of the guide by refactor-doc
    When rules.py runs for its start
    Then it gives the generator's steps whole, steps 2 and 3 holding the decide and make practices
    of refactor-doc, not of readme, and step 3 the writes of the guide"""
    top = worktree(
        str(tmp_path), {CUT: {**generator_cut(GUIDE, "readme"), "best_practice": "refactor-doc"}}
    )
    assert rules_of(top, "rn:generator", CUT) == (0, generator_steps("refactor-doc", GUIDE), "")


def evaluator_steps(cut: str, unread: list[str], conditions: list[str]) -> dict[str, Any]:
    """The steps of an evaluator from its Cut, never reading the paths, judging the conditions."""
    return steps_of(
        [{"type": "writes", "paths": []}],
        [{"type": "reads_none", "paths": unread}],
        [{"type": "checklist", "items": conditions}, {"type": "writes", "paths": []}],
        end_of("evaluator", cut, "judged"),
    )


@pytest.mark.supports("test_an_evaluator_starts_with_only_what_the_deliverables_people_have")
def test_rules_give_an_evaluator_its_steps_from_its_cut(tmp_path: Any):
    """Given an evaluator's Cut of C2 of the command
    When rules.py runs for a start of rn:evaluator whose prompt names the Cut
    Then it gives 0, saying nothing, with steps 1 to 4 in order, each with order: step 1 writes
    nothing, step 2 never reading the design tree or the generator's Cut and result of the Round,
    and writing what it will, step 3 the checklist of N4 to N7 and writing nothing, and step 4 the
    writes of the result, rn's check of the evaluator, and the result judged, and nothing else"""
    cut = evaluator("C2")
    conditions = ["N4", "N5", "N6", "N7"]
    top = worktree(str(tmp_path), {**made_files(), cut: evaluator_cut("C2", conditions)})
    unread = [f"{RUN}/design-tree.json", CUT, RESULT]
    assert rules_of(top, "rn:evaluator", cut) == (0, evaluator_steps(cut, unread, conditions), "")


@pytest.mark.supports("test_an_evaluator_stopped_starts_again_with_a_fresh_cut_beside_its_first")
def test_rules_of_a_cut_in_a_later_slot_name_the_result_beside_it(tmp_path: Any):
    """Given round 1's evaluator of C1 in slot 2, beside the Cut that a pause left
    When rules.py runs for the start whose prompt names slot 2's Cut
    Then it gives the evaluator's steps, step 4 writing the result of slot 2 alone and checking
    slot 2's Cut"""
    cut = evaluator("C1", ".2")
    files = {**made_files(), evaluator("C1"): evaluator_cut(), cut: evaluator_cut()}
    top = worktree(str(tmp_path), files)
    unread = [f"{RUN}/design-tree.json", CUT, RESULT]
    expected = evaluator_steps(cut, unread, ["N1", "N2", "N3"])
    assert rules_of(top, "rn:evaluator", cut) == (0, expected, "")


@pytest.mark.supports("test_an_evaluator_starts_with_only_what_the_deliverables_people_have")
def test_rules_keep_an_evaluator_from_each_generator_of_its_round_in_any_slot(tmp_path: Any):
    """Given round 1's generator made in slot 2, beside the Cut of slot 1 that a pause left, and
    an evaluator's Cut of C1
    When rules.py runs for the evaluator's start
    Then step 2 never reads the design tree, nor either generator's Cut or result"""
    cut = evaluator("C1")
    second = f"{RUN}/rounds/1/generator.2.cut.json"
    files = {CUT: generator_cut(), second: generator_cut(), cut: evaluator_cut()}
    top = worktree(str(tmp_path), {**files, f"{RUN}/rounds/1/generator.2.json": MADE})
    unread = [
        f"{RUN}/design-tree.json",
        CUT,
        RESULT,
        second,
        f"{RUN}/rounds/1/generator.2.json",
    ]
    expected = evaluator_steps(cut, unread, ["N1", "N2", "N3"])
    assert rules_of(top, "rn:evaluator", cut) == (0, expected, "")


@pytest.mark.supports("test_an_evaluator_starts_with_only_what_the_deliverables_people_have")
def test_rules_leave_an_evaluator_free_to_read_the_generators_of_other_rounds(tmp_path: Any):
    """Given round 1's evaluator of C1, with round 1's generator made, and the generators of
    round 10 and round 2, whose numbers start like round 1's or follow it
    When rules.py runs for the evaluator's start
    Then step 2 never reads the design tree nor round 1's generator, and leaves the other rounds'
    alone"""
    cut = evaluator("C1")
    later = {f"{RUN}/rounds/{n}/generator.cut.json": generator_cut() for n in (2, 10)}
    top = worktree(str(tmp_path), {**made_files(), **later, cut: evaluator_cut()})
    unread = [f"{RUN}/design-tree.json", CUT, RESULT]
    expected = evaluator_steps(cut, unread, ["N1", "N2", "N3"])
    assert rules_of(top, "rn:evaluator", cut) == (0, expected, "")


@pytest.mark.supports("test_a_role_that_writes_beside_its_deliverable_is_told_its_step")
@pytest.mark.parametrize(
    ("given", "cut", "said"),
    [
        ("{", generator_cut(), ""),
        ('{"role": "rn:generator"}', generator_cut(), ""),
        (
            '{"run": {"skill": "rn:up", "words": ""}, "role": "rn:generator", "prompt": "Go"}',
            generator_cut(),
            "",
        ),
        (
            json.dumps(
                {
                    "run": {"skill": "rn:up", "words": ""},
                    "role": "rn:generator",
                    "prompt": f"Carry out your steps, from your result at {RESULT}",
                }
            ),
            generator_cut(),
            RESULT,
        ),
        ("", {"role": "generator"}, "generator.cut.json"),
        ("", {**generator_cut(), "best_practice": "x"}, "x"),
        ("", {**generator_cut(), "best_practice": "cod"}, "cod"),
    ],
    ids=[
        "input not JSON",
        "input out of form",
        "a prompt that names no Cut",
        "a prompt that names a result, not a Cut",
        "a Cut out of form",
        "no best practice of rn's",
        "a near match of a best practice",
    ],
)
def test_rules_refuse_input_a_prompt_or_a_cut_out_of_its_form(
    tmp_path: Any, given: str, cut: dict[str, Any], said: str
):
    """Given Lane's input that isn't JSON or leaves its form, a prompt that names no Cut or names
    the result beside one, a Cut out of its form, or one whose best practice rn doesn't have or
    nearly has
    When rules.py runs
    Then it gives 1, printing nothing, naming what's at fault"""
    top = worktree(str(tmp_path), {CUT: cut})
    if given:
        code, printed, told = command("lane/adapters/rules.py").main(given, top, RN)
    else:
        code, printed, told = rules_of(top, "rn:generator", CUT)
    assert (code, printed) == (1, "") and told.startswith("rules.py: ") and said in told


@pytest.mark.supports("test_an_evaluator_starts_with_only_what_the_deliverables_people_have")
def test_rules_refuse_an_evaluator_whose_rounds_generator_cut_isnt_json(tmp_path: Any):
    """Given an evaluator's Cut of C1, and round 1's generator's Cut that isn't JSON
    When rules.py runs for the evaluator's start
    Then it gives 1, printing nothing, naming the generator's Cut"""
    cut = evaluator("C1")
    top = worktree(str(tmp_path), {CUT: "{", cut: evaluator_cut()})
    code, printed, told = rules_of(top, "rn:evaluator", cut)
    assert (code, printed) == (1, "") and "rounds/1/generator.cut.json" in told


@pytest.mark.supports("test_a_role_that_writes_beside_its_deliverable_is_told_its_step")
@pytest.mark.parametrize(
    "adapter",
    ["rules", "starts_due"],
)
def test_an_adapter_run_as_lane_runs_it_ends_with_what_its_main_gives(tmp_path: Any, adapter: str):
    """Given Lane's input that isn't JSON
    When the adapter runs as a command, as Lane runs it, in a worktree
    Then it exits 1, printing nothing and saying why"""
    done = subprocess.run(
        [sys.executable, os.path.join(RN, "lane", "adapters", f"{adapter}.py")],
        input="{",
        capture_output=True,
        text=True,
        cwd=worktree(str(tmp_path)),
        check=False,
    )
    assert (done.returncode, done.stdout) == (1, "")
    assert done.stderr and "Traceback" not in done.stderr
