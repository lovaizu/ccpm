"""The integration cases of each principle item of rn's architecture: each where the parts keep it,
running rn and Lane through the double of Claude Code, and each with the fixture `broken`, which
takes the part that holds the item out of the bench's copy of rn where TRACE_BROKEN is 1, as the
plugin guide's A principle's test seen to fail says. A part taken out is an interface given again
at the end of its module, wrapping or replacing the one before, so the copy runs without what holds
the item."""

from __future__ import annotations

import json
import os
from collections.abc import Callable

import pytest
import rn_files
from repo_files import git
from rn_bench import (
    Bench,
    cut_of,
    decided_command,
    ended,
    evaluator_started,
    generated,
    held,
    listed,
    marked,
    pointed,
    ran,
    read_step,
    requested,
    shared_steps,
    short_twice,
    signed,
    signed_plan,
    started,
    to_plan_signoff,
    touched_items,
    trial_made,
)
from rn_files import COMMAND


def given_again(b: Bench, module: str, code: str) -> None:
    """Gives an interface of the module of the bench's copy of rn again, at the end of its code:
    before the block that runs a script's main, where the module holds one, so that the interface
    given again is the one the main calls, else at the end of its file."""
    path = os.path.join(b.rn, module)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    main = 'if __name__ == "__main__":'
    at = text.find(main)
    at = len(text) if at < 0 else at
    with open(path, "w", encoding="utf-8") as f:
        f.write(text[:at] + "\n\n" + code + "\n\n" + text[at:])


def steps_without(b: Bench, kept: str) -> None:
    """The adapter of the rules gives each step with only the rules that `kept`, a Python test of
    a rule `r` and its step `s`, keeps."""
    given_again(
        b,
        "lane/adapters/rules.py",
        "_given_steps = steps\n\n\n"
        "def steps(given, cwd, plugin_root):\n"
        "    out = _given_steps(given, cwd, plugin_root)\n"
        "    for s in out['steps']:\n"
        f"        s['rules'] = [r for r in s['rules'] if {kept}]\n"
        "    return out\n",
    )


def no_shared_steps(b: Bench) -> None:
    """The orchestrator's turn takes only its event's own steps, none that every event shares."""
    given_again(
        b,
        "lane/adapters/rules.py",
        "_given_steps = steps\n\n\n"
        "def steps(given, cwd, plugin_root):\n"
        "    out = _given_steps(given, cwd, plugin_root)\n"
        "    shared = ('review', 'touched', 'commit', 'move')\n"
        "    out['steps'] = [s for s in out['steps'] if s['name'] not in shared]\n"
        "    return out\n",
    )


def open_decisions_unread(b: Bench) -> None:
    """What a deliverable waits on is decided as if none of its decisions were open."""
    given_again(
        b,
        "domain/rounds/course.py",
        "_given_next_of = next_of\n\n\n"
        "def next_of(deliverable, rounds, refactors):\n"
        "    import copy\n"
        "    shown = copy.deepcopy(deliverable)\n"
        "    for c in shown['necessary_conditions']:\n"
        "        c['decisions'] = [d for d in c['decisions'] if d.get('decided') is not None]\n"
        "    return _given_next_of(shown, rounds, refactors)\n",
    )


def generator_always_due(b: Bench) -> None:
    """The starts due give a generator at every move, whatever the design tree holds."""
    given_again(
        b,
        "lane/adapters/starts_due.py",
        "def due(given, cwd):\n    return {'starts': [{'role': 'rn:generator', 'count': 1}]}\n",
    )


def trial_of_the_worktree(b: Bench) -> None:
    """The people's starting state is a copy of the run's worktree whole, rn's folder among it."""
    given_again(
        b,
        "domain/repository/trial.py",
        "def starting_state(run, round_, host):\n"
        "    import shutil\n"
        "    target = folder(run, round_)\n"
        "    shutil.rmtree(target, ignore_errors=True)\n"
        "    shutil.copytree(run.worktree, target)\n"
        "    return target\n",
    )


def result_unchecked(b: Bench) -> None:
    """A role's result is taken whatever it holds."""
    given_again(
        b, "domain/check/result.py", "def faults(role, cut, result, worktree):\n    return []\n"
    )


def items_left_out(b: Bench) -> None:
    """A best practice gives a maker no item at any stage."""
    given_again(b, "domain/practice.py", "def items(practice, at):\n    return []\n")


def no_limit(b: Bench) -> None:
    """A deliverable takes as many Rounds of a stage as its findings ask."""
    given_again(b, "domain/rounds/course.py", "LIMIT = 99\n")


def any_end_passes(b: Bench) -> None:
    """check.py passes each end, a role's result written or not."""
    given_again(
        b, "domain/check/command.py", "def main(argv, cwd, plugin_root):\n    return 0, '', ''\n"
    )


def no_parallel(b: Bench) -> None:
    """The starts due give one start at a time: none while a start of rn's subagents has no
    result yet, and else at most one of a role."""
    given_again(
        b,
        "lane/adapters/starts_due.py",
        "_given_due = due\n\n\n"
        "def due(given, cwd):\n"
        "    out = _given_due(given, cwd)\n"
        "    moves = given['run']['moves']\n"
        "    started = sum(1 for m in moves if m['kind'] == 'start')\n"
        "    if started > sum(1 for m in moves if m['kind'] == 'result'):\n"
        "        return {'starts': []}\n"
        "    for s in out.get('starts', []):\n"
        "        s['count'] = min(s['count'], 1)\n"
        "    return out\n",
    )


def no_run_found(b: Bench) -> None:
    """No run is found among the worktrees of the repository."""
    given_again(b, "domain/repository/worktree.py", "def paused(repository):\n    return []\n")


def signoff_unrecorded(b: Bench) -> None:
    """A sign-off leaves the design tree as it was."""
    given_again(
        b, "domain/tree/signoff.py", "def signed_off(tree, deliverable):\n    return tree\n"
    )


def checks_unasked(b: Bench) -> None:
    """A change of the design tree is committed whatever its form."""
    given_again(
        b, "domain/tree/checks.py", "def faults(tree, practices, worktree):\n    return []\n"
    )


BREAKS: dict[str, Callable[[Bench], None]] = {
    "test_an_orchestrators_turn_ended_before_its_review_is_stopped": no_shared_steps,
    "test_a_tree_change_out_of_form_is_refused_at_its_commit": checks_unasked,
    "test_a_deliverable_whose_point_waits_on_the_user_gets_no_cut": open_decisions_unread,
    "test_no_generator_starts_before_the_plan_is_signed_off": generator_always_due,
    "test_a_signoff_of_the_plan_makes_its_deliverables_generator_due": signoff_unrecorded,
    "test_the_people_start_from_the_branch_without_rns_folder": trial_of_the_worktree,
    "test_an_evaluators_end_leaving_a_condition_unanswered_is_stopped": result_unchecked,
    "test_the_orchestrator_writing_a_deliverable_is_stopped": lambda b: steps_without(
        b, "r['type'] != 'writes'"
    ),
    "test_the_orchestrators_review_writing_the_tree_by_bash_is_stopped": lambda b: steps_without(
        b, "r['type'] != 'commands'"
    ),
    "test_the_generators_make_is_held_to_its_best_practices_make_items": items_left_out,
    "test_a_deliverable_short_after_two_content_rounds_gets_no_third": no_limit,
    "test_the_evaluator_reading_the_design_tree_is_stopped": lambda b: steps_without(
        b, "r['type'] != 'reads_none'"
    ),
    "test_a_generators_end_with_no_result_written_is_stopped": any_end_passes,
    "test_the_orchestrators_commit_by_git_in_place_of_tree_py_is_stopped": lambda b: steps_without(
        b, "r['type'] != 'commands'"
    ),
    "test_a_generator_marking_make_before_decide_is_stopped": lambda b: steps_without(
        b, "r['type'] != 'order'"
    ),
    "test_two_deliverables_resting_on_none_start_together": no_parallel,
    "test_a_new_conversation_picks_up_the_run_from_its_files": no_run_found,
}


@pytest.fixture
def broken(b: Bench, request: pytest.FixtureRequest) -> None:
    """Takes out the part that holds the case's principle item where TRACE_BROKEN is 1."""
    if os.environ.get("TRACE_BROKEN") == "1":
        BREAKS[request.node.originalname](b)


# P1: toward the people's aim.


@pytest.mark.supports("P1.1", "orchestrator")
def test_an_orchestrators_turn_ended_before_its_review_is_stopped(b: Bench, broken: None):
    """Given a run whose command's generator ended with made
    When the orchestrator ends its turn at once
    Then Lane stops the end, naming the step `review`"""
    c, generator = signed_plan(b)
    generated(b, c, generator)
    answer = c.stop("Going on.")
    assert answer.blocked
    assert "`review`" in answer.said


@pytest.mark.supports("P1.1", "Design tree")
def test_a_tree_change_out_of_form_is_refused_at_its_commit(b: Bench, broken: None):
    """Given a run whose goal the orchestrator put, and a change of its design tree that gives the
    command a kind of no best practice, its review and touched done
    When the orchestrator commits it by tree.py commit
    Then it gives 1 naming /deliverables/1/kind, and the work's branch holds no new commit"""
    c = requested(b)
    c.type("yes")
    design_tree = rn_files.walkthrough_tree(b.name(), plan_done=False)
    design_tree["deliverables"][1]["kind"] = "no-such-kind"
    answer = c.write(None, b.tree_path, json.dumps(design_tree, indent=1) + "\n")
    assert not answer.blocked, answer.said
    marked(c, "review")
    touched_items(b, c)
    marked(c, "touched")
    branch = f"rn-{b.name()}"
    before = git(b.repo, "rev-parse", branch).strip()
    refused = c.bash(b.script("tree", "commit", b.run, "The plan."))
    assert refused.exit_code == 1
    assert "/deliverables/1/kind" in refused.output
    assert git(b.repo, "rev-parse", branch).strip() == before


@pytest.mark.supports("P1.2", "Round")
def test_a_deliverable_whose_point_waits_on_the_user_gets_no_cut(b: Bench, broken: None):
    """Given a run whose command's generator ended with a point, kept by the orchestrator as an
    open decision of N1
    When the orchestrator writes the generator's Cut, then puts the point to the user
    Then tree.py cut gives 1 saying the command waits on the user, and the turn ends, Lane stopping
    no move"""
    c, generator = signed_plan(b)
    pointed(b, c, generator, "Should a line's quantity default to 1?")
    point = rn_files.decision("a line's quantity", None)
    shared_steps(b, c, held(b, COMMAND, [], {"N1": [point]}), "The generator's point.")
    refused = c.bash(b.script("tree", "cut", b.run, "generator", COMMAND))
    assert refused.exit_code == 1
    assert "user" in refused.output
    ended(c, "A question that's yours:\n  Should a line's quantity default to 1?")


@pytest.mark.supports("P1.3", "orchestrator")
def test_no_generator_starts_before_the_plan_is_signed_off(b: Bench, broken: None):
    """Given a run whose plan is put up for the user's sign-off
    When the orchestrator starts rn:generator
    Then Lane stops the start, as no start of rn's subagents is due"""
    c = to_plan_signoff(b)
    answer, agent = c.start("rn:generator", "Make the command.", "Run rn:generator")
    assert agent is None
    assert "No start of rn's subagents is due now." in answer.said


@pytest.mark.supports("P1.3", "Design tree")
def test_a_signoff_of_the_plan_makes_its_deliverables_generator_due(b: Bench, broken: None):
    """Given a run whose plan is put up for the user's sign-off
    When the user types /rn:ty and the orchestrator records it by tree.py signoff
    Then the plan is done, and Lane gives rn:generator as due at the turn's next start"""
    c = to_plan_signoff(b)
    c.type("/rn:ty")
    ran(c, b.script("tree", "signoff", b.run))
    assert b.tree()["deliverables"][0]["status"] == "done"
    marked(c, "record")
    cut_path = shared_steps(
        b, c, ground="Signed off.", moves=[b.script("tree", "cut", b.run, "generator", COMMAND)]
    )[0].strip()
    assert started(c, "rn:generator", cut_path) is not None


# P2: judged by the people's aim.


@pytest.mark.supports("P2.1", "evaluator")
def test_the_people_start_from_the_branch_without_rns_folder(b: Bench, broken: None):
    """Given a run whose command's evaluator started, the command written but not committed
    When the evaluator runs repository.py trial for its Round
    Then the folder it prints holds the command and invoicer's files, and no .rn"""
    _, _, given, trial = trial_made(b)
    assert trial == given["trial"] or os.path.samefile(trial, given["trial"])
    assert os.path.isfile(os.path.join(trial, COMMAND))
    assert os.path.isfile(os.path.join(trial, "invoicer", "lines.py"))
    assert not os.path.exists(os.path.join(trial, ".rn"))


@pytest.mark.supports("P2.2", "evaluator", "Round")
def test_an_evaluators_end_leaving_a_condition_unanswered_is_stopped(b: Bench, broken: None):
    """Given a run whose command's evaluator kept its steps but wrote answers of N1 and N2 alone
    When it ends with judged
    Then Lane stops the end with check.py's fault naming N3"""
    c, evaluator = evaluator_started(b)
    given = cut_of(c, evaluator)
    evaluator.read(os.path.join(c.cwd, evaluator.start_use["tool_input"]["prompt"]))
    marked(c, "read", evaluator)
    ran(c, b.script("repository", "trial", b.run, given["round"]), evaluator)
    marked(c, "start", evaluator)
    marked(c, "try", evaluator)
    for each in rn_files.conditions("light"):
        evaluator.bash(f"lane-item judge {each}")
    with open(os.path.join(b.worktree, COMMAND), encoding="utf-8") as f:
        first = f.read().splitlines()[0]
    partial = rn_files.judged([("N1", [first]), ("N2", [first])])
    evaluator.write(os.path.join(c.cwd, given["round"], "evaluator.json"), json.dumps(partial))
    evaluator.bash("lane-result judged")
    marked(c, "judge", evaluator)
    stopped, _ = evaluator.end("2 good, 0 more")
    assert stopped.blocked
    assert "N3" in stopped.said


# P3: made the field's established way.


@pytest.mark.supports("P3.1", "orchestrator")
def test_the_orchestrator_writing_a_deliverable_is_stopped(b: Bench, broken: None):
    """Given a run whose plan the user signed off
    When the orchestrator writes the command's file in its review
    Then Lane stops the write, as the step `review` writes only the run's design tree"""
    c = to_plan_signoff(b)
    c.type("/rn:ty")
    ran(c, b.script("tree", "signoff", b.run))
    marked(c, "record")
    answer = c.write(None, os.path.join(b.worktree, COMMAND), "print('invoice')\n")
    assert answer.blocked
    assert "`review`" in answer.said


@pytest.mark.supports("P3.1", "orchestrator")
def test_the_orchestrators_review_writing_the_tree_by_bash_is_stopped(b: Bench, broken: None):
    """Given a run whose plan the user signed off, its sign-off recorded
    When the orchestrator lists the repository by `ls` in its review, and then writes the run's
    design tree by a Bash command other than `ls` and `grep`
    Then the first goes through, and Lane stops the second, as the step `review` runs only `ls`
    and `grep`, and the tree is as it was"""
    c = to_plan_signoff(b)
    c.type("/rn:ty")
    ran(c, b.script("tree", "signoff", b.run))
    marked(c, "record")
    before = b.tree()
    assert not c.bash("ls").blocked
    answer = c.bash(f"printf '%s\\n' '{{}}' > {b.tree_path}")
    assert answer.blocked
    assert "You're at the step `review` of rn:ty, which runs only ls and grep." in answer.said
    assert b.tree() == before


@pytest.mark.supports("P3.2", "generator", "Best practice")
def test_the_generators_make_is_held_to_its_best_practices_make_items(b: Bench, broken: None):
    """Given a run whose command's generator read its inputs and decided, each decide item done
    When it writes the command and reports `make` done with no make item reported
    Then Lane stops the mark, naming the light best practice's make items, N1.4 among them"""
    _, generator = decided_command(b)
    generator.write(os.path.join(b.worktree, COMMAND), "print('invoice')\n")
    answer = generator.bash("lane-step make")
    left = rn_files.items_at("light", "make")
    assert "N1.4" in left
    assert answer.said == (
        f"You're at the step `make` of rn:generator, whose checklist isn't done: {listed(left)}.\n"
        "Do each and mark it done with lane-item make <item> first."
    )


@pytest.mark.supports("P3.3", "Round")
def test_a_deliverable_short_after_two_content_rounds_gets_no_third(b: Bench, broken: None):
    """Given a run whose command's N1 the evaluator found short in Rounds content-1 and content-2,
    its second evaluator's end reaching the main conversation
    When the orchestrator holds N2 and N3 good, keeps the shared steps, and writes the generator's
    Cut at the step `move`
    Then tree.py cut gives 1 saying the command waits on the orchestrator, and the turn ends, Lane
    stopping no move"""
    c = short_twice(b)
    shared_steps(b, c, held(b, COMMAND, ["N2", "N3"]), "The Round's findings.")
    refused = c.bash(b.script("tree", "cut", b.run, "generator", COMMAND))
    assert refused.exit_code == 1
    assert "orchestrator" in refused.output
    ended(c, "Its Rounds are spent.")


# P4: each role on its own work.


@pytest.mark.supports("P4.1", "evaluator", "Cut")
def test_the_evaluator_reading_the_design_tree_is_stopped(b: Bench, broken: None):
    """Given a run whose command's evaluator started
    When it reads the run's design tree
    Then Lane stops the read"""
    _, evaluator = evaluator_started(b)
    answer = evaluator.read(b.tree_path)
    assert answer.blocked
    assert "design-tree.json" in answer.said


@pytest.mark.supports("P4.2", "generator", "Round")
def test_a_generators_end_with_no_result_written_is_stopped(b: Bench, broken: None):
    """Given a run whose command's generator kept each step but wrote no result in its Round
    When it ends with made
    Then Lane stops the end, naming the path of generator.json in the Round's folder"""
    c, generator = signed_plan(b)
    given = cut_of(c, generator)
    read_step(b, c, generator, given)
    for each in rn_files.items_at("light", "decide"):
        generator.bash(f"lane-item decide {each}")
    marked(c, "decide", generator)
    generator.write(os.path.join(b.worktree, COMMAND), "print('invoice')\n")
    for each in rn_files.items_at("light", "make"):
        generator.bash(f"lane-item make {each}")
    marked(c, "make", generator)
    marked(c, "try", generator)
    ran(c, b.script("repository", "checks", b.run, COMMAND), generator)
    generator.bash("lane-result made")
    marked(c, "check", generator)
    stopped, _ = generator.end("made")
    assert stopped.blocked
    assert os.path.join(given["round"], "generator.json") in stopped.said


@pytest.mark.supports("P4.3", "scripts", "orchestrator")
def test_the_orchestrators_commit_by_git_in_place_of_tree_py_is_stopped(b: Bench, broken: None):
    """Given a run whose goal the user confirmed, the orchestrator's review and touched done
    When it commits the design tree by git at the step `commit`
    Then Lane stops the call, as the step runs only tree.py commit"""
    c = requested(b)
    c.type("yes")
    marked(c, "review")
    marked(c, "touched")
    answer = c.bash(f"git -C {b.worktree} commit -am 'The goal.'")
    assert answer.blocked
    assert "`commit`" in answer.said


# P5: the shortest path.


@pytest.mark.supports("P5.1", "generator")
def test_a_generator_marking_make_before_decide_is_stopped(b: Bench, broken: None):
    """Given a run whose command's generator read its inputs
    When it reports `make` done before `decide`
    Then Lane stops the mark, naming `decide` as the step before"""
    c, generator = signed_plan(b)
    read_step(b, c, generator, cut_of(c, generator))
    answer = generator.bash("lane-step make")
    assert answer.said == (
        "You're at the step `decide` of rn:generator, which comes before `make`.\n"
        "Do `decide` and mark it done with lane-step decide first."
    )


@pytest.mark.supports("P5.2", "Design tree")
def test_two_deliverables_resting_on_none_start_together(b: Bench, broken: None):
    """Given a run whose plan holds two deliverables that rest on none, the command and a
    changelog, put up for the user's sign-off
    When the user signs the plan off
    Then both generators start, each with its own Cut, as Lane gives rn:generator as due 2 times
    at once"""
    c = requested(b)
    c.type("yes")
    name = b.name()
    design_tree = rn_files.tree(
        [
            rn_files.plan(name),
            rn_files.open_node(rn_files.COMMAND_NAME, COMMAND, "light", ["invoicer/lines.py"]),
            rn_files.open_node("The changes of 1.5.0", "CHANGELOG.md", "light"),
        ],
        [rn_files.work("make", COMMAND), rn_files.work("make", "CHANGELOG.md")],
    )
    shared_steps(
        b,
        c,
        design_tree,
        "The plan.",
        [b.script("repository", "put-up", b.run, rn_files.plan_path(name))],
    )
    ended(c, "The plan, for your sign-off.")
    cuts = signed(
        b,
        c,
        [
            b.script("tree", "cut", b.run, "generator", COMMAND),
            b.script("tree", "cut", b.run, "generator", "CHANGELOG.md"),
        ],
    )
    first, one = c.start("rn:generator", cuts[0].strip(), "Run rn:generator")
    assert one is not None, first.said
    second, other = c.start("rn:generator", cuts[1].strip(), "Run rn:generator")
    assert other is not None, second.said


# P6: nothing lost on a stop.


@pytest.mark.supports("P6.1", "scripts", "Design tree")
def test_a_new_conversation_picks_up_the_run_from_its_files(b: Bench, broken: None):
    """Given a run whose plan is put up, paused by /rn:dn
    When the user types /rn:up alone in a new conversation, and the orchestrator runs
    repository.py find
    Then it prints the run's folder from the repository's top"""
    c = to_plan_signoff(b)
    c.type("/rn:dn")
    marked(c, "stop")
    ran(c, b.script("repository", "pause", b.run))
    marked(c, "pause")
    ended(c, "Paused.")
    later = b.converse()
    later.type("/rn:up")
    assert ran(later, b.script("repository", "find")).split() == [b.run]
