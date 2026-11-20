"""The unit cases of lane/adapters/starts_due.py, rn's order as Lane asks it: `due`, one for each
combination that its contract lists, the latest command `rn:dn` or another, each deliverable done,
no worktree, the plan open, a deliverable with no item `make` or with an input not done, the roles
that a deliverable's Rounds wait on, a Round that a pause stopped before a role's result, a
deliverable past its Rounds whose findings wait as proposals for its sign-off, an open decision,
a start with no result yet among the moves, another plugin's start, none, one, and two
deliverables due at once, and the run named by the latest start's prompt among several; each
refusal; and `main`, for each exit it gives.

Each input is in the form of Lane's starts_due.in.schema.json, read from the JSON of its text, and
the run's files in the forms that the architecture's Directory structure names. The starts are
taken in any order, as the contract orders none."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from typing import Any

import pytest
import rn_files
from fault import Wrong
from rn_adapters import adapter
from rn_files import COMMAND, GUIDE

pytestmark = pytest.mark.xfail(
    strict=True, reason="starts_due.py's bodies raise NotImplementedError"
)


ADAPTER = adapter("starts_due")
NAME = "20261120-invoices"
CHANGELOG = "CHANGELOG.md"


def command(name: str) -> dict[str, Any]:
    return {"kind": "command", "command": name}


def start(role: str, prompt: str) -> dict[str, Any]:
    return {"kind": "start", "role": role, "prompt": prompt}


def result(role: str, given: str) -> dict[str, Any]:
    return {"kind": "result", "role": role, "result": given}


def run(*moves: Mapping[str, Any], words: str = "") -> dict[str, Any]:
    """What Lane gives the adapter, read from the JSON of its text."""
    text = json.dumps({"run": {"skill": "rn:up", "words": words, "moves": list(moves)}})
    return json.loads(text)


def starts(out: Mapping[str, Any]) -> Any:
    """The output with its starts in the order of their roles."""
    if "starts" not in out:
        return dict(out)
    return {"starts": sorted(out["starts"], key=lambda each: each["role"])}


def due(*roles: tuple[str, int]) -> dict[str, Any]:
    """The starts due of the roles, each with its count, in the order of their roles."""
    return {"starts": [{"role": r, "count": n} for r, n in sorted(roles)]}


def a_run(cwd: str, tree: Mapping[str, Any], name: str = NAME) -> str:
    """Writes the run's design tree and invoicer's lines in its worktree; gives its folder."""
    folder = rn_files.run_folder(cwd, name, tree)
    lines = os.path.join(rn_files.worktree_of(cwd, name), "invoicer", "lines.py")
    os.makedirs(os.path.dirname(lines), exist_ok=True)
    with open(lines, "w", encoding="utf-8") as f:
        f.write("def parse_lines(text):\n    return []\n")
    return folder


def walkthrough(**kwargs: Any) -> dict[str, Any]:
    """The walkthrough's tree of the run, its plan done, the command and the guide open."""
    return rn_files.walkthrough_tree(NAME, **kwargs)


def with_changelog(tree: Mapping[str, Any]) -> dict[str, Any]:
    """The tree with a changelog that rests on none, and its item `make` in the work."""
    more = json.loads(json.dumps(tree))
    more["deliverables"].append(rn_files.open_node("The changes of 1.5.0", CHANGELOG, "light"))
    more["work"].append(rn_files.work("make", CHANGELOG))
    return more


def cut_prompt(cwd: str, folder: str, deliverable: str, role: str = "generator") -> str:
    """Writes an empty Cut of the role in the deliverable's Round content-1, and gives its path
    from cwd, as the orchestrator gives it as the start's prompt."""
    path = os.path.join(rn_files.round_of(folder, deliverable, "content", 1), f"{role}-cut.json")
    rn_files.write_json(path, {})
    return os.path.relpath(path, cwd)


ALL_GOOD = [("N1", ["x"]), ("N2", ["x"]), ("N3", ["x"])]


@pytest.fixture
def cwd(tmp_path: Any) -> str:
    """The top of the user's repository, with no run."""
    folder = os.path.join(str(tmp_path), "repo")
    os.makedirs(folder)
    return os.path.realpath(folder)


# The run's end.


@pytest.mark.supports("test_a_pause_stops_the_generator_and_pushes_the_runs_work_so_far")
def test_a_run_whose_latest_command_is_a_pause_ends(cwd: str):
    """Given a run whose command is due, and the moves /rn:up then /rn:dn
    When the adapter gives the starts due
    Then the run ends"""
    a_run(cwd, walkthrough())
    assert ADAPTER.due(run(command("rn:up"), command("rn:dn")), cwd) == {"ends": True}


@pytest.mark.supports(
    "test_a_pick_up_starts_the_stopped_generator_again_in_its_round_with_a_fresh_cut"
)
def test_a_run_picked_up_after_a_pause_goes_on(cwd: str):
    """Given a run whose command is due, and the moves /rn:dn then /rn:up
    When the adapter gives the starts due
    Then the command's generator is due once"""
    a_run(cwd, walkthrough())
    out = ADAPTER.due(run(command("rn:dn"), command("rn:up")), cwd)
    assert starts(out) == due(("rn:generator", 1))


@pytest.mark.supports(
    "test_the_last_signoff_ends_the_run_with_each_deliverable_on_the_pull_requests_branch"
)
def test_a_run_whose_deliverables_are_each_done_ends(cwd: str):
    """Given a run whose plan, command, and guide are each done
    When the adapter gives the starts due
    Then the run ends"""
    tree = rn_files.tree(
        [
            rn_files.done_node(rn_files.GOAL, rn_files.plan_path(NAME), "design-tree"),
            rn_files.done_node(rn_files.COMMAND_NAME, COMMAND, "light"),
            rn_files.done_node(rn_files.GUIDE_NAME, GUIDE, "readme"),
        ]
    )
    a_run(cwd, tree)
    assert ADAPTER.due(run(command("rn:ty")), cwd) == {"ends": True}


# No start while the run waits.


@pytest.mark.supports("test_a_turn_with_the_plan_open_starts_no_role")
def test_a_run_with_no_worktree_yet_starts_none(cwd: str):
    """Given a repository with no run, and the move /rn:up with words
    When the adapter gives the starts due
    Then none is due"""
    out = ADAPTER.due(run(command("rn:up"), words=rn_files.WORDS), cwd)
    assert out == {"starts": []}


@pytest.mark.supports("test_no_generator_starts_before_the_plan_is_signed_off")
@pytest.mark.parametrize("good", [False, True], ids=["plan-short", "plan-waiting-signoff"])
def test_a_run_whose_plan_isnt_done_starts_none(cwd: str, good: bool):
    """Given a run whose plan is open, short or with each condition good, and its command in the
    work with its inputs done
    When the adapter gives the starts due
    Then none is due"""
    tree = walkthrough(plan_done=False)
    tree["deliverables"][0] = rn_files.plan(NAME, good=good)
    a_run(cwd, tree)
    assert ADAPTER.due(run(command("rn:up")), cwd) == {"starts": []}


@pytest.mark.supports(
    "test_a_signoff_of_the_plan_makes_it_done_and_starts_the_generator_of_each_deliverable_due"
)
def test_the_deliverable_whose_inputs_are_done_is_due_and_the_one_resting_on_it_isnt(cwd: str):
    """Given a run whose plan is done, its command resting on invoicer's lines and its guide on the
    command, each in the work
    When the adapter gives the starts due
    Then the command's generator alone is due, once"""
    a_run(cwd, walkthrough())
    assert starts(ADAPTER.due(run(command("rn:ty")), cwd)) == due(("rn:generator", 1))


@pytest.mark.supports("test_a_deliverable_signed_off_is_done_and_the_one_resting_on_it_starts")
def test_a_deliverable_whose_input_is_done_is_due(cwd: str):
    """Given a run whose command is done and whose guide, resting on it, is in the work
    When the adapter gives the starts due
    Then the guide's generator is due once"""
    tree = walkthrough()
    tree["deliverables"][1] = rn_files.done_node(rn_files.COMMAND_NAME, COMMAND, "light")
    tree["work"] = [rn_files.work("make", GUIDE)]
    a_run(cwd, tree)
    assert starts(ADAPTER.due(run(command("rn:ty")), cwd)) == due(("rn:generator", 1))


@pytest.mark.supports("test_a_deliverable_waits_while_one_it_rests_on_is_being_made")
def test_a_deliverable_resting_on_one_being_made_isnt_due(cwd: str):
    """Given a run whose guide is in the work, resting on the command, which is being made and is
    not in the work
    When the adapter gives the starts due
    Then none is due"""
    tree = walkthrough()
    tree["deliverables"][1]["status"] = "doing"
    tree["work"] = [rn_files.work("make", GUIDE)]
    a_run(cwd, tree)
    assert ADAPTER.due(run(command("rn:ty")), cwd) == {"starts": []}


@pytest.mark.supports(
    "test_a_signoff_of_the_plan_makes_it_done_and_starts_the_generator_of_each_deliverable_due"
)
@pytest.mark.parametrize("order", [[], [("decide", "N1")]], ids=["no-work", "decide-only"])
def test_a_deliverable_that_no_item_make_names_isnt_due(cwd: str, order: list):
    """Given a run whose command's inputs are done, and whose work holds no item, or an item
    `decide` alone of the command
    When the adapter gives the starts due
    Then none is due"""
    tree = walkthrough()
    tree["work"] = [rn_files.work(do, COMMAND, cond, "the tax rate") for do, cond in order]
    a_run(cwd, tree)
    assert ADAPTER.due(run(command("rn:ty")), cwd) == {"starts": []}


# What a deliverable's Rounds wait on.


@pytest.mark.supports("test_a_generators_made_makes_the_evaluator_due_in_the_same_round")
def test_a_round_whose_generator_made_makes_the_evaluator_due(cwd: str):
    """Given a run whose command's Round content-1 holds the generator's made and no evaluator's
    result, and the moves of that start and its result
    When the adapter gives the starts due
    Then the command's evaluator is due once, and no generator"""
    folder = a_run(cwd, walkthrough())
    prompt = cut_prompt(cwd, folder, COMMAND)
    rn_files.a_round(folder, COMMAND, "content", 1, {"generator": rn_files.made(ALL_GOOD)})
    moves = run(command("rn:ty"), start("rn:generator", prompt), result("rn:generator", "made"))
    assert starts(ADAPTER.due(moves, cwd)) == due(("rn:evaluator", 1))


@pytest.mark.supports("test_a_deliverable_whose_point_waits_on_the_user_gets_no_cut")
def test_a_deliverable_with_an_open_decision_waits_on_the_answer_and_no_role(cwd: str):
    """Given a run whose command's generator gave a point in Round content-1, kept as an open
    decision of its N1
    When the adapter gives the starts due
    Then none is due"""
    point = rn_files.decision("a line's quantity", None)
    folder = a_run(cwd, walkthrough(command_decisions={"N1": [point]}))
    rn_files.a_round(folder, COMMAND, "content", 1, {"generator": rn_files.point()})
    assert ADAPTER.due(run(command("rn:up")), cwd) == {"starts": []}


@pytest.mark.supports(
    "test_a_resumed_generator_after_its_answer_ends_with_made_and_the_evaluator_is_due"
)
def test_a_point_answered_makes_the_generator_due_again(cwd: str):
    """Given a run whose command's generator gave a point in Round content-1, answered by the user
    in the decision of its N1
    When the adapter gives the starts due
    Then the command's generator is due once"""
    answer = rn_files.decision("a line's quantity", "yes, 1", "user")
    folder = a_run(cwd, walkthrough(command_decisions={"N1": [answer]}))
    rn_files.a_round(folder, COMMAND, "content", 1, {"generator": rn_files.point()})
    assert starts(ADAPTER.due(run(command("rn:up")), cwd)) == due(("rn:generator", 1))


@pytest.mark.supports("test_a_deliverable_short_after_two_content_rounds_gets_no_third")
def test_a_deliverable_past_two_content_rounds_waits_on_the_orchestrator(cwd: str):
    """Given a run whose command's N1 the evaluator found short in Rounds content-1 and content-2,
    the tree holding N1 not good
    When the adapter gives the starts due
    Then none is due"""
    short_twice(a_run(cwd, walkthrough(command_good=["N2", "N3"])))
    assert ADAPTER.due(run(command("rn:up")), cwd) == {"starts": []}


@pytest.mark.supports(
    "test_a_finding_the_people_would_never_meet_is_dropped_by_holding_its_condition_good"
)
def test_a_deliverable_waiting_for_its_signoff_starts_none(cwd: str):
    """Given a run whose command, of the kind light, holds each condition good after its judged
    Round content-1
    When the adapter gives the starts due
    Then none is due"""
    folder = a_run(cwd, walkthrough(command_good=True))
    results = {"generator": rn_files.made(ALL_GOOD), "evaluator": rn_files.judged(ALL_GOOD)}
    rn_files.a_round(folder, COMMAND, "content", 1, results)
    assert ADAPTER.due(run(command("rn:up")), cwd) == {"starts": []}


def short_twice(folder: str) -> None:
    """Writes the command's Rounds content-1 and content-2, each made and judged with N1 short."""
    for number in (1, 2):
        results = {
            "generator": rn_files.made(ALL_GOOD),
            "evaluator": rn_files.judged(ALL_GOOD[1:], [("N1", "a comma in a line")]),
        }
        rn_files.a_round(folder, COMMAND, "content", number, results)


@pytest.mark.supports("test_a_finding_left_past_two_content_rounds_goes_to_the_user_as_a_proposal")
def test_a_deliverable_past_its_rounds_with_its_finding_kept_waits_for_signoff_and_no_role(
    cwd: str,
):
    """Given a run whose command's N1 the evaluator found short in Rounds content-1 and content-2,
    and the orchestrator kept the finding as an open decision of N1
    When the adapter gives the starts due
    Then none is due, and the run doesn't end"""
    proposal = rn_files.decision("a comma in a line", None)
    folder = a_run(
        cwd, walkthrough(command_good=["N2", "N3"], command_decisions={"N1": [proposal]})
    )
    short_twice(folder)
    assert ADAPTER.due(run(command("rn:up")), cwd) == {"starts": []}


@pytest.mark.supports(
    "test_a_pick_up_starts_the_stopped_generator_again_in_its_round_with_a_fresh_cut"
)
def test_a_round_that_a_pause_stopped_before_its_generators_result_makes_it_due_again(cwd: str):
    """Given a run picked up in a new conversation, whose command's Round content-1 holds the
    generator's Cut and no result, as a pause stopped it
    When the adapter gives the starts due
    Then the command's generator is due once"""
    folder = a_run(cwd, walkthrough())
    cut_prompt(cwd, folder, COMMAND)
    assert starts(ADAPTER.due(run(command("rn:up")), cwd)) == due(("rn:generator", 1))


@pytest.mark.supports(
    "test_a_pick_up_starts_the_stopped_generator_again_in_its_round_with_a_fresh_cut"
)
def test_a_pause_in_the_last_round_a_stage_allows_spends_none_of_it(cwd: str):
    """Given a run picked up, whose command's N1 the evaluator found short in Round content-1, and
    whose Round content-2 holds the generator's Cut and no result, as a pause stopped it
    When the adapter gives the starts due
    Then the command's generator is due once, not the orchestrator's keeping of the finding"""
    folder = a_run(cwd, walkthrough(command_good=["N2", "N3"]))
    results = {
        "generator": rn_files.made(ALL_GOOD),
        "evaluator": rn_files.judged(ALL_GOOD[1:], [("N1", "a comma in a line")]),
    }
    rn_files.a_round(folder, COMMAND, "content", 1, results)
    path = os.path.join(rn_files.round_of(folder, COMMAND, "content", 2), "generator-cut.json")
    rn_files.write_json(path, {})
    assert starts(ADAPTER.due(run(command("rn:up")), cwd)) == due(("rn:generator", 1))


@pytest.mark.supports("test_a_pick_up_starts_the_stopped_evaluator_again_in_its_round")
def test_a_round_that_a_pause_stopped_before_its_evaluators_result_makes_it_due_again(cwd: str):
    """Given a run picked up in a new conversation, whose command's Round content-1 holds the
    generator's made and the evaluator's Cut with no result, as a pause stopped it
    When the adapter gives the starts due
    Then the command's evaluator is due once, and no generator"""
    folder = a_run(cwd, walkthrough())
    cut_prompt(cwd, folder, COMMAND, "evaluator")
    rn_files.a_round(folder, COMMAND, "content", 1, {"generator": rn_files.made(ALL_GOOD)})
    assert starts(ADAPTER.due(run(command("rn:up")), cwd)) == due(("rn:evaluator", 1))


# The starts already made, among the moves.


@pytest.mark.supports(
    "test_a_signoff_of_the_plan_makes_it_done_and_starts_the_generator_of_each_deliverable_due"
)
def test_a_start_with_no_result_yet_counts_against_its_deliverable(cwd: str):
    """Given a run whose command's generator is due, and a start of rn:generator whose prompt
    names the command's Cut, with no result after it
    When the adapter gives the starts due
    Then none is due"""
    folder = a_run(cwd, walkthrough())
    prompt = cut_prompt(cwd, folder, COMMAND)
    out = ADAPTER.due(run(command("rn:ty"), start("rn:generator", prompt)), cwd)
    assert out == {"starts": []}


@pytest.mark.supports("test_two_deliverables_resting_on_none_start_together")
def test_two_deliverables_resting_on_none_are_due_at_once(cwd: str):
    """Given a run whose command and changelog rest on nothing still being made, each in the work
    When the adapter gives the starts due
    Then rn:generator is due twice"""
    a_run(cwd, with_changelog(walkthrough()))
    assert starts(ADAPTER.due(run(command("rn:ty")), cwd)) == due(("rn:generator", 2))


@pytest.mark.supports("test_two_deliverables_resting_on_none_start_together")
def test_a_start_of_one_of_two_leaves_the_other_due(cwd: str):
    """Given a run whose command and changelog are due, and a start of rn:generator whose prompt
    names the changelog's Cut, with no result yet
    When the adapter gives the starts due
    Then rn:generator is due once, for the command"""
    folder = a_run(cwd, with_changelog(walkthrough()))
    prompt = cut_prompt(cwd, folder, CHANGELOG)
    out = ADAPTER.due(run(command("rn:ty"), start("rn:generator", prompt)), cwd)
    assert starts(out) == due(("rn:generator", 1))


@pytest.mark.supports("test_two_deliverables_resting_on_none_start_together")
def test_a_generator_and_an_evaluator_are_due_at_once_for_two_deliverables(cwd: str):
    """Given a run whose command's Round content-1 waits on its evaluator and whose changelog
    waits on its first generator
    When the adapter gives the starts due
    Then rn:generator and rn:evaluator are each due once"""
    folder = a_run(cwd, with_changelog(walkthrough()))
    rn_files.a_round(folder, COMMAND, "content", 1, {"generator": rn_files.made(ALL_GOOD)})
    out = ADAPTER.due(run(command("rn:up")), cwd)
    assert starts(out) == due(("rn:evaluator", 1), ("rn:generator", 1))


@pytest.mark.supports(
    "test_a_signoff_of_the_plan_makes_it_done_and_starts_the_generator_of_each_deliverable_due"
)
@pytest.mark.parametrize("role", ["log:generator", "rn:generators"])
def test_another_plugins_start_naming_the_cut_counts_for_nothing(cwd: str, role: str):
    """Given a run whose command's generator is due, and a start of another plugin's role, or of
    one that nearly matches rn's, whose prompt names the command's Cut, with no result
    When the adapter gives the starts due
    Then the command's generator is still due once"""
    folder = a_run(cwd, walkthrough())
    prompt = cut_prompt(cwd, folder, COMMAND)
    out = ADAPTER.due(run(command("rn:ty"), start(role, prompt)), cwd)
    assert starts(out) == due(("rn:generator", 1))


# The run among several.


@pytest.mark.supports("test_a_new_conversation_picks_up_the_run_from_its_files")
def test_the_run_is_the_one_the_latest_starts_prompt_names(cwd: str):
    """Given run 20261120-invoices, whose command waits on its evaluator, and a newer run
    20261121-changes, whose changelog waits on its generator, and the moves of a start of the older
    run's generator with its result
    When the adapter gives the starts due
    Then the older run's evaluator alone is due"""
    folder = a_run(cwd, walkthrough())
    rn_files.a_round(folder, COMMAND, "content", 1, {"generator": rn_files.made(ALL_GOOD)})
    prompt = cut_prompt(cwd, folder, COMMAND)
    newer = "20261121-changes"
    a_run(cwd, with_changelog(rn_files.walkthrough_tree(newer)), newer)
    moves = run(command("rn:up"), start("rn:generator", prompt), result("rn:generator", "made"))
    assert starts(ADAPTER.due(moves, cwd)) == due(("rn:evaluator", 1))


@pytest.mark.supports("test_a_new_conversation_picks_up_the_run_from_its_files")
def test_with_no_start_the_run_is_the_newest_with_work_left(cwd: str):
    """Given run 20261120-invoices, whose command waits on its evaluator, a newer run
    20261121-changes whose changelog and command wait on their generators, and a newest run
    20261122-done whose deliverables are each done, and no start among the moves
    When the adapter gives the starts due
    Then the generator is due twice, of 20261121-changes"""
    folder = a_run(cwd, walkthrough())
    rn_files.a_round(folder, COMMAND, "content", 1, {"generator": rn_files.made(ALL_GOOD)})
    newer = "20261121-changes"
    a_run(cwd, with_changelog(rn_files.walkthrough_tree(newer)), newer)
    done = "20261122-done"
    plan = rn_files.done_node(rn_files.GOAL, rn_files.plan_path(done), "design-tree")
    a_run(cwd, rn_files.tree([plan]), done)
    assert starts(ADAPTER.due(run(command("rn:up")), cwd)) == due(("rn:generator", 2))


# Refusals, and main.


def broken(cwd: str, which: str) -> None:
    """Writes the run with its design tree, or its Round's generator result, as text that isn't
    JSON."""
    folder = a_run(cwd, walkthrough())
    path = os.path.join(folder, "design-tree.json")
    if which == "round":
        round_ = rn_files.a_round(folder, COMMAND, "content", 1)
        path = os.path.join(round_, "generator.json")
    with open(path, "w", encoding="utf-8") as f:
        f.write('{"result": made\n')


@pytest.mark.supports("test_a_tree_change_out_of_form_is_refused_at_its_commit")
@pytest.mark.parametrize("which", ["tree", "round"])
def test_a_tree_or_a_round_that_cant_be_read_is_refused_naming_its_file(cwd: str, which: str):
    """Given a run whose design tree, or whose command's generator result, isn't JSON
    When the adapter gives the starts due
    Then it raises Wrong, naming the file"""
    broken(cwd, which)
    with pytest.raises(Wrong, match="design-tree.json" if which == "tree" else "generator.json"):
        ADAPTER.due(run(command("rn:up")), cwd)


@pytest.mark.supports(
    "test_a_signoff_of_the_plan_makes_it_done_and_starts_the_generator_of_each_deliverable_due"
)
def test_main_gives_0_with_the_starts_due_as_one_line_of_json(cwd: str):
    """Given Lane's input of a run whose command's generator is due, as JSON on standard input
    When main runs
    Then it gives 0, the starts due as one line of JSON, and nothing on stderr"""
    a_run(cwd, walkthrough())
    code, out, err = ADAPTER.main(json.dumps(run(command("rn:ty"))), cwd)
    assert (code, err) == (0, "")
    assert out.endswith("\n") and out.count("\n") == 1
    assert starts(json.loads(out)) == due(("rn:generator", 1))


@pytest.mark.supports("test_a_tree_change_out_of_form_is_refused_at_its_commit")
@pytest.mark.parametrize("stdin", ["", "{run", "[]"])
def test_main_gives_1_where_its_input_isnt_lanes_json(cwd: str, stdin: str):
    """Given standard input that's empty, not JSON, or JSON of another form
    When main runs
    Then it gives 1, nothing on stdout, and `starts_due.py: ` with what's wrong on stderr"""
    code, out, err = ADAPTER.main(stdin, cwd)
    assert (code, out) == (1, "")
    assert err.startswith("starts_due.py: ")


@pytest.mark.supports("test_a_tree_change_out_of_form_is_refused_at_its_commit")
def test_main_gives_1_where_due_refuses_the_run(cwd: str):
    """Given a run whose design tree isn't JSON
    When main runs
    Then it gives 1, nothing on stdout, and `starts_due.py: ` naming the design tree on stderr"""
    broken(cwd, "tree")
    code, out, err = ADAPTER.main(json.dumps(run(command("rn:up"))), cwd)
    assert (code, out) == (1, "")
    assert err.startswith("starts_due.py: ") and "design-tree.json" in err
