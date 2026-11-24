"""What rn's integration cases share: a bench for each case, and the fixture `broken`, which takes
the part that holds a case's principle item out of the bench's copy of rn where TRACE_BROKEN is 1,
as the plugin guide's A principle's test seen to fail says. A part taken out is an interface given
again at the end of its module, wrapping or replacing the one before, so the copy runs without what
holds the item."""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

import pytest
import rn_bench
from rn_bench import Bench


@pytest.fixture
def b(tmp_path: Any) -> Bench:
    """The bench: rn, and invoicer's repository with its remote."""
    return rn_bench.bench(str(tmp_path))


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


def checks_unasked(b: Bench) -> None:
    """A change of the design tree is committed whatever its form."""
    given_again(
        b, "domain/tree/checks.py", "def faults(tree, practices, worktree):\n    return []\n"
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


def signoff_unrecorded(b: Bench) -> None:
    """A sign-off leaves the design tree as it was."""
    given_again(
        b, "domain/tree/signoff.py", "def signed_off(tree, deliverable):\n    return tree\n"
    )


def put_up_unmarked(b: Bench) -> None:
    """A Round put up for the sign-off is left unmarked, so that a send-back after it counts the
    content Rounds before it."""
    given_again(
        b, "domain/rounds/files.py", "def mark(run, deliverable, state):\n    return None\n"
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
        b,
        "domain/check/result.py",
        "def faults(role, cut, result, worktree, cwd):\n    return []\n",
    )


def opened_ready(b: Bench) -> None:
    """The run's pull request opens ready for review, not as a draft."""
    given_again(
        b,
        "domain/repository/push.py",
        "_given_put_up = put_up\n\n\n"
        "def put_up(run, deliverable, host):\n"
        "    def ready(argv, cwd, env=None):\n"
        "        return host([each for each in argv if each != '--draft'], cwd, env)\n\n"
        "    return _given_put_up(run, deliverable, ready)\n",
    )


def judged_before_made(b: Bench) -> None:
    """A deliverable whose Round waits on its generator waits on its evaluator instead."""
    given_again(
        b,
        "domain/rounds/course.py",
        "_given_next_of = next_of\n\n\n"
        "def next_of(deliverable, rounds, refactors):\n"
        "    given = _given_next_of(deliverable, rounds, refactors)\n"
        "    if given.waits_on == 'generator' and given.resumes:\n"
        "        return Next('evaluator', given.stage, True)\n"
        "    return given\n",
    )


def refactoring_judged(b: Bench) -> None:
    """A refactor Round that its generator made waits on its evaluator, as a Round of content
    does."""
    given_again(
        b,
        "domain/rounds/course.py",
        "_given_next_of = next_of\n\n\n"
        "def next_of(deliverable, rounds, refactors):\n"
        "    last = rounds[-1] if rounds else None\n"
        "    if last and last.round.stage == 'refactor' and last.evaluator is None and (\n"
        "        last.generator and last.generator['result'] == 'made'\n"
        "    ):\n"
        "        return Next('evaluator', 'refactor', False)\n"
        "    return _given_next_of(deliverable, rounds, refactors)\n",
    )


def no_limit(b: Bench) -> None:
    """A deliverable takes as many Rounds of a stage as its findings ask."""
    given_again(b, "domain/rounds/course.py", "LIMIT = 99\n")


def cut_of_the_whole_node(b: Bench) -> None:
    """The evaluator's Cut holds the deliverable's whole node, its decisions among it."""
    given_again(
        b,
        "domain/tree/cut.py",
        "_given_evaluator = evaluator\n\n\n"
        "def evaluator(tree, run, round_, practice):\n"
        "    given = _given_evaluator(tree, run, round_, practice)\n"
        "    given['deliverable'] = _open(tree, round_)\n"
        "    return given\n",
    )


def any_end_passes(b: Bench) -> None:
    """check.py passes each end, a role's result written or not."""
    given_again(
        b, "domain/check/command.py", "def main(argv, cwd, plugin_root):\n    return 0, '', ''\n"
    )


def checks_in_place(b: Bench) -> None:
    """The repository's commit checks run on the worktree's own index, as a commit of all that it
    stages would."""
    given_again(
        b, "domain/repository/commit_checks.py", "def _with_index(host, index):\n    return host\n"
    )


def one_at_a_time(b: Bench) -> None:
    """A deliverable waits on the pruner while another's Round waits on its generator, so that one
    deliverable is made at a time."""
    given_again(
        b,
        "domain/rounds/course.py",
        "_given_next_in = next_in\n\n\n"
        "def next_in(run, deliverable):\n"
        "    from tree import form\n"
        "    for node in form.read(run.tree)['deliverables']:\n"
        "        if node['path'] == deliverable['path']:\n"
        "            continue\n"
        "        if any(each.generator is None for each in so_far(run, node['path'])):\n"
        "            return Next('pruner', None, False)\n"
        "    return _given_next_in(run, deliverable)\n",
    )


def blocker_stops_all(b: Bench) -> None:
    """A deliverable waits on the user's answer while any deliverable of the run keeps an open
    decision, so that one blocker stops every deliverable's work."""
    given_again(
        b,
        "domain/rounds/course.py",
        "_given_next_in = next_in\n\n\n"
        "def next_in(run, deliverable):\n"
        "    from tree import form\n"
        "    nodes = form.read(run.tree)['deliverables']\n"
        "    conditions = [c for n in nodes for c in n.get('necessary_conditions', [])]\n"
        "    if any(d['decided'] is None for c in conditions for d in c['decisions']):\n"
        "        return Next('answer', None, False)\n"
        "    return _given_next_in(run, deliverable)\n",
    )


def no_run_found(b: Bench) -> None:
    """No run is found among the runs' branches of the repository."""
    given_again(
        b,
        "domain/repository/worktree.py",
        "def newest(repository, host, origins=True):\n    return None\n",
    )


def tree_writes_pass(b: Bench) -> None:
    """The hook lets each write to a run's design tree pass, whoever writes it."""
    given_again(b, "domain/hook/command.py", "def _tree_written(called):\n    return None\n")


def bash_tree_writes_pass(b: Bench) -> None:
    """The hook lets each Bash command that writes a run's design tree pass, whoever runs it."""
    given_again(
        b, "domain/hook/command.py", "def _bash_written(called, plugin_root):\n    return None\n"
    )


def touched_by_the_first_change(b: Bench) -> None:
    """tree.py touched lists only the nodes that the first change since the last commit touches,
    as if each fact of a unit were weighed alone."""
    given_again(
        b,
        "domain/tree/command.py",
        "def _touched(run, given, cwd, plugin_root, host):\n"
        "    before, after = _committed(run, host), form.read(run.tree)\n"
        "    made = touched.changed(before, after)[:1]\n"
        "    found = []\n"
        "    for each in made:\n"
        "        found += touched.touched(before, after, _held(after, each))\n"
        "    return 0, _lines(list(dict.fromkeys(n for n in found if n not in made))), ''\n\n\n"
        "_SUBCOMMANDS['touched'] = (_touched, 1, 2)\n",
    )


def done_in_one_line(b: Bench) -> None:
    """A deliverable signed off is done in one line, its name, path, kind, and status, without
    its conditions and their decisions."""
    given_again(
        b,
        "domain/tree/signoff.py",
        "def _done(node):\n"
        "    kept = ('name', 'path', 'more_paths', 'kind')\n"
        "    done = {key: node[key] for key in kept if key in node}\n"
        "    done['status'] = 'done'\n"
        "    return done\n",
    )


def findings_to_the_generator(b: Bench) -> None:
    """The generator's Cut holds the last evaluator's findings beside its deliverable's
    decisions."""
    given_again(
        b,
        "domain/tree/cut.py",
        "_given_generator = generator\n\n\n"
        "def generator(tree, run, round_, practice, last):\n"
        "    from rounds import files\n"
        "    given = _given_generator(tree, run, round_, practice, last)\n"
        "    rounds = files.of(run, round_.deliverable)\n"
        "    judged = [files.result(each, 'evaluator') for each in rounds]\n"
        "    given['findings'] = [each for each in judged if each is not None][-1:]\n"
        "    return given\n",
    )


BREAKS: dict[str, Callable[[Bench], None]] = {
    "test_a_tree_change_out_of_form_is_refused_at_its_commit": checks_unasked,
    "test_a_deliverable_whose_point_waits_on_the_user_gets_no_cut": open_decisions_unread,
    "test_a_signoff_of_the_plan_makes_its_deliverables_generator_due": signoff_unrecorded,
    "test_a_send_back_past_the_contents_limit_is_remade_in_rounds_of_its_own": put_up_unmarked,
    "test_the_people_start_from_the_branch_without_rns_folder": trial_of_the_worktree,
    "test_an_evaluators_answers_leaving_a_condition_unanswered_are_refused": result_unchecked,
    "test_the_pull_request_stays_a_draft_after_the_last_signoff": opened_ready,
    "test_the_evaluator_waits_on_its_generators_result": judged_before_made,
    "test_no_evaluator_is_due_after_a_refactor_round": refactoring_judged,
    "test_a_deliverable_short_after_two_content_rounds_gets_no_third": no_limit,
    "test_the_evaluators_cut_holds_only_what_the_people_have": cut_of_the_whole_node,
    "test_a_generators_result_unwritten_is_refused": any_end_passes,
    "test_the_generators_checks_judge_its_files_alone_beside_another_staged": checks_in_place,
    "test_two_deliverables_resting_on_none_are_due_together": one_at_a_time,
    "test_a_blocker_kept_for_the_user_leaves_the_other_deliverables_work_going_on": (
        blocker_stops_all
    ),
    "test_a_new_conversation_picks_up_the_run_from_its_files": no_run_found,
    "test_the_orchestrators_write_to_the_design_tree_is_denied_pointing_to_a_new_pruner": (
        tree_writes_pass
    ),
    "test_a_done_deliverable_keeps_its_decisions_and_is_read_again_with_one_resting_on_it": (
        done_in_one_line
    ),
    "test_a_makers_write_to_the_design_tree_is_denied_while_the_scripts_write_it": (
        tree_writes_pass
    ),
    "test_the_generators_cut_holds_the_pruners_remedy_and_no_evaluators_finding": (
        findings_to_the_generator
    ),
    "test_the_orchestrators_write_to_the_design_tree_by_bash_is_denied_while_rns_scripts_run": (
        bash_tree_writes_pass
    ),
    "test_a_judged_rounds_result_is_weighed_whole_by_one_pruner_with_each_node_it_touches": (
        touched_by_the_first_change
    ),
}


@pytest.fixture
def broken(b: Bench, request: pytest.FixtureRequest) -> None:
    """Takes out the part that holds the case's principle item where TRACE_BROKEN is 1."""
    if os.environ.get("TRACE_BROKEN") == "1":
        BREAKS[request.node.originalname](b)
