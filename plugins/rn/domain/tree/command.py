"""Decides tree.py's command line: what each of its commands takes, which modules it joins, and
what it prints with the exit code by which a role or the orchestrator reads its result."""

from __future__ import annotations

import datetime
import json
import os
from collections.abc import Callable, Sequence
from typing import Any, TextIO

from fault import CantRun, Missing, Wrong
from repository import git

from tree import (
    branch,
    design,
    github,
    more,
    place,
    records,
    results,
    rounds,
    runs,
    sign_offs,
    touched,
    turn,
)
from tree.design import Change, DesignTree
from tree.runs import Run
from tree.sign_offs import Kind, State

USAGE = """\
usage: tree.py start <goal>
       tree.py write <record> <ground>   (the change on standard input)
       tree.py commit <record> <step>
       tree.py round <deliverable>
       tree.py push
       tree.py put-up plan | put-up deliverable <path>
       tree.py put-up lesson   (its words on standard input)
       tree.py pause   (where each role stood on standard input)
       tree.py approve | send-back | comments | runs
"""


def main(argv: Sequence[str], stdin: TextIO, cwd: str, plugin_root: str) -> tuple[int, str, str]:
    """Runs one command of tree.py.

    Takes: the command line after `tree.py`; standard input, which write, put-up lesson, and pause
    read; the folder it runs in; and rn's folder.
    Gives, as the exit code, standard output, and standard error, each output JSON:
    - `start <goal>`: 0, with `{"worktree", "folder", "record"}`, the orchestrator's record among
      them, from `runs.start` and `records.orchestrator_record`.
    - `write <record> <ground>`, with `{"nodes": {<path>: <node>}, "more": [{"deliverable",
      "condition", "good_when"}]}` on standard input, and `<ground>` why the change decides as it
      does: 0, with `{"changed", "touched", "doing"}`, once `design.apply`, `more.keepable` against
      `rounds.at_cut`, `turn.mark_doing`, `design.write`, `rounds.keep_more`, and `branch.commit`
      take it, the commit's message `<ground>` word for word; 1, naming the more's necessary
      condition, where `more.keepable` refuses it; 1, where `<ground>` is empty, as a decision
      committed with no ground is one no one can trace.
    - `commit <record> <step>`: 0, once `place.write` keeps the start's Place and `branch.commit`
      commits its work, the message naming the record and the step.
    - `round <deliverable>`: 0, with `[{"number", "made", "answers"}]`, each round from
      `rounds.each`, the latest last, its Made, or null before the generator wrote it, and each
      evaluator's Answers, by group, in the forms that the generator and the evaluator wrote them.
    - `push`: 0, with the pull request's URL, from `branch.push` and `github.keep_draft`.
    - `put-up plan`, `put-up deliverable <path>`, or `put-up lesson` with its words on standard
      input: 0, with the sign-off waiting, from `sign_offs.put_up`.
    - `approve` or `send-back`: 0, with the sign-off decided, from `sign_offs.decide`; for a lesson
      approved, with its issue's URL from `github.open_lesson`; for the pull request handed over and
      sent back, once `github.hand_over` marks it a draft again.
    - `comments`: 0, with `[{"author", "at", "path", "line", "body"}]`, each of the user's
      comments on the pull request, of its conversation and on its lines, since the last sign-off
      sent back was put up, from `github.comments`; 1, where no sign-off was sent back.
    - `pause`, with `{"stood": [{"record", "step"}]}` on standard input, each step a whole number
      from 1: 0, with `[{"record", "step"}]` as given, once `place.write` keeps each start's Place,
      `branch.commit` commits the work, its message naming each record and step, and `branch.push`
      pushes it.
    - `runs`: 0, with `[{"name", "worktree", "record"}]` from `runs.left`.
    - `ready`: 0, with the pull request's URL, once `github.hand_over` marks it ready and
      `sign_offs.put_up` puts up the pull request handed over.
    - 1, with what's wrong, where an input is out of form, as fault.Wrong says; 1, with what's
      missing, where git or gh can't do it, as fault.Missing says, `pause` saying it committed but
      didn't push; 2, with why, where it can't run, or with the usage.
    Changes: what each module it joins changes.
    Refuses: as Gives says, by its exit code.
    Carries: each arrow to tree.py from a role or the orchestrator: S1 `O->>T: makes the run's
    worktree`, `K->>T: writes them, and commits them with each decision's ground as the message`,
    `G->>T` and `E->>T: commits its work`, `O->>T: gets the round`, `K->>T: writes the decision,
    commits it with its ground as the message, and keeps the more`; S2 `K->>T: writes it, and
    commits it with its ground as the message`; S3
    `O->>T: pushes the work`, `puts it up`, `approves the sign-off waiting`, `sends the sign-off
    waiting back`, `gets the user's comments`; S4 `O->>T: commits and pushes each role's work`; S5
    `O->>T: lists the runs left`; S6 and S7 `O->>T: puts it up`, `marks the pull request ready`,
    `sends the pull request handed over back`, and `approves the pull request handed over`.
    """
    found = _COMMANDS.get(argv[0] if argv else "")
    if found is None or len(argv) - 1 not in found[1]:
        return 2, "", USAGE
    try:
        given = found[0](list(argv[1:]), stdin, cwd, plugin_root)
    except (Wrong, Missing) as e:
        return 1, "", f"tree.py {argv[0]}: {e}\n"
    except CantRun as e:
        return 2, "", f"tree.py {argv[0]}: {e}\n"
    return 0, json.dumps(given) + "\n", ""


def _start(args: list[str], stdin: TextIO, cwd: str, plugin_root: str) -> Any:
    root = git.worktrees(cwd)[0][0]
    run = runs.start(root, args[0], datetime.date.today().strftime("%Y%m%d"))
    folder = os.path.relpath(run.folder, run.worktree)
    return {"worktree": run.worktree, "folder": folder, "record": records.orchestrator_record(run)}


def _write(args: list[str], stdin: TextIO, cwd: str, plugin_root: str) -> Any:
    record, ground = args
    if not ground.strip():
        raise Wrong("<ground> is empty; give why the change decides as it does, its commit message")
    nodes, kept = _change(stdin.read())
    run = _run(cwd)
    records.role_of(record)
    before = _tree_or_empty(run)
    after = design.apply(before, Change(nodes))
    marked_tree, marked = turn.mark_doing(after, sign_offs.read(run))
    for each in kept:
        more.keepable(rounds.at_cut(run, each.deliverable), marked_tree, each)
    paths = [design.write(run, marked_tree), *(rounds.keep_more(run, kept) if kept else ())]
    branch.commit(run, paths, ground)
    changed = design.changed(before, marked_tree)
    return {
        "changed": list(changed),
        "touched": list(touched.touched(marked_tree, changed)),
        "doing": list(marked),
    }


def _commit(args: list[str], stdin: TextIO, cwd: str, plugin_root: str) -> Any:
    record, step = args
    if not step.isdigit() or int(step) < 1:
        raise Wrong(f"<step> must be a step's number from 1, not {step!r}")
    _kept(_run(cwd), [(record, int(step))], f"{record}: step {step} ended")
    return {"record": record, "step": int(step)}


def _pause(args: list[str], stdin: TextIO, cwd: str, plugin_root: str) -> Any:
    stood = _stood(stdin.read())
    run = _run(cwd)
    _kept(run, stood, "paused: " + "; ".join(f"{r} at step {s}" for r, s in stood))
    try:
        branch.push(run)
    except Missing as e:
        raise Missing(f"the work is committed but not pushed, as {e}") from None
    return [{"record": r, "step": s} for r, s in stood]


def _kept(run: Run, stood: list[tuple[str, int]], message: str) -> None:
    """Keeps the Place of each start at the step it stands at, with the files of the work, and
    commits the work with the message; refuses, before it writes, a record that names no start of
    the run."""
    paths = [rounds.place_path(run, record) for record, _ in stood]
    work = git.changed(run.worktree)
    for path, (record, step) in zip(paths, stood):
        place.write(path, place.Place(record, step, work))
    branch.commit(run, ["."], message)


def _round(args: list[str], stdin: TextIO, cwd: str, plugin_root: str) -> Any:
    run = _run(cwd)
    design.read(run)
    return [
        {
            "number": each.number,
            "made": _made_as_written(each.made) if each.made else None,
            "answers": [_answers_as_written(a) for a in each.answers],
        }
        for each in rounds.each(run, args[0])
    ]


def _made_as_written(made: results.Made) -> Any:
    """A Made in the form of generator-out.schema.json's `made`, as the generator wrote it."""
    return {
        "decisions": [{"path": p, "where": w} for p, w in made.decisions.items()],
        "more": [{"condition": c, "where": w} for c, w in made.more.items()],
        "settled": [
            {"point": s.point, "decided": s.decided, "ground": s.ground} for s in made.settled
        ],
    }


def _answers_as_written(answers: results.Answers) -> Any:
    """An evaluator's Answers in the form of evaluator-out.schema.json's `answers`."""
    return {
        "good": [{"question": q, "lines": list(lines)} for q, lines in answers.good.items()],
        "more": [{"question": q, "good_when": g} for q, g in answers.more.items()],
    }


def _push(args: list[str], stdin: TextIO, cwd: str, plugin_root: str) -> Any:
    run = _run(cwd)
    branch.push(run)
    return github.keep_draft(run).url


def _put_up(args: list[str], stdin: TextIO, cwd: str, plugin_root: str) -> Any:
    kinds = {
        "plan": (Kind.PLAN, 0),
        "deliverable": (Kind.DELIVERABLE, 1),
        "lesson": (Kind.LESSON, 0),
    }
    if args[0] not in kinds or len(args) - 1 != kinds[args[0]][1]:
        raise Wrong("put-up takes `plan`, `deliverable <path>`, or `lesson`")
    kind = kinds[args[0]][0]
    what = args[1] if kind is Kind.DELIVERABLE else stdin.read() if kind is Kind.LESSON else ""
    return sign_offs.as_json(sign_offs.put_up(_run(cwd), kind, what))


def _decided(approved: bool) -> Callable[[list[str], TextIO, str, str], Any]:
    def decide(args: list[str], stdin: TextIO, cwd: str, plugin_root: str) -> Any:
        run = _run(cwd)
        given = sign_offs.decide(run, approved)
        shown: dict[str, Any] = sign_offs.as_json(given)
        if approved and given.kind is Kind.LESSON:
            shown["issue"] = github.open_lesson(plugin_root, given.what)
        # Runs only for the pull request handed over, as in the case xfail until hand_over is built,
        # test_gm_on_the_pull_request_handed_over_marks_it_a_draft_again.
        if not approved and given.kind is Kind.PULL_REQUEST:  # pragma: no cover
            github.hand_over(run, False)
        return shown

    return decide


def _comments(args: list[str], stdin: TextIO, cwd: str, plugin_root: str) -> Any:
    run = _run(cwd)
    sent = [s for s in sign_offs.read(run).each if s.state is State.SENT_BACK]
    # Runs only where the orchestrator asks the comments before /rn:gm sent a sign-off back, which
    # no case does; taken back to the cases' designer.
    if not sent:  # pragma: no cover
        raise Wrong("no sign-off was sent back; run comments after send-back, as /rn:gm loads")
    return [
        {"author": c.author, "at": c.at, "path": c.path, "line": c.line, "body": c.body}
        for c in github.comments(run, sent[-1].at)
    ]


def _runs(args: list[str], stdin: TextIO, cwd: str, plugin_root: str) -> Any:
    return [
        {"name": r.name, "worktree": r.worktree, "record": records.orchestrator_record(r)}
        for r in runs.left(cwd)
    ]


def _stood(text: str) -> list[tuple[str, int]]:
    """Where each start stood, as tree.py pause reads it on standard input: each record and step."""
    form = 'the pause on standard input must be {"stood": [{"record": <path>, "step": <from 1>}]}'
    # Each refusal below runs only on a pause out of form, which no case gives; taken back to the
    # cases' designer.
    try:
        given = json.loads(text)
    except ValueError as e:  # pragma: no cover
        raise Wrong(f"{form}; it isn't JSON: {e}") from None
    try:
        stood = [(each["record"], each["step"]) for each in given["stood"]]
    except (KeyError, TypeError):  # pragma: no cover
        raise Wrong(f"{form}, not {json.dumps(given)}") from None
    wrong = [
        json.dumps({"record": r, "step": s})
        for r, s in stood
        if not (isinstance(r, str) and type(s) is int and s >= 1)
    ]
    if wrong:  # pragma: no cover
        raise Wrong(f"{form}, not {', '.join(wrong)}")
    return stood


def _change(text: str) -> tuple[dict[str, Any], list[more.More]]:
    """The change that tree.py write reads on standard input: its nodes, and each More to keep."""
    try:
        given = json.loads(text)
    except ValueError as e:
        raise Wrong(f"the change on standard input isn't JSON: {e}") from None
    if not (isinstance(given, dict) and set(given) == {"nodes", "more"}):
        raise Wrong('the change must be {"nodes": {<path>: <node>}, "more": [<more>]}')
    if not isinstance(given["nodes"], dict) or not isinstance(given["more"], list):
        raise Wrong('the change\'s "nodes" must be an object, and its "more" a list')
    try:
        kept = [more.More(m["deliverable"], m["condition"], m["good_when"]) for m in given["more"]]
    except (KeyError, TypeError):
        raise Wrong('each more must be {"deliverable", "condition", "good_when"}') from None
    return given["nodes"], kept


def _run(cwd: str) -> Run:
    run = runs.of_folder(cwd)
    if run is None:
        raise Wrong(f"{cwd} lies in no run's worktree; run it in the worktree that start gave")
    return run


def _tree_or_empty(run: Run) -> DesignTree:
    """The run's design tree, or an empty one before the first change writes it."""
    if os.path.exists(os.path.join(run.folder, "design-tree.json")):
        return design.read(run)
    return DesignTree({})


# Each command, with what runs it and how many arguments it takes after its name.
_COMMANDS: dict[str, tuple[Callable[[list[str], TextIO, str, str], Any], tuple[int, ...]]] = {
    "start": (_start, (1,)),
    "write": (_write, (2,)),
    "commit": (_commit, (2,)),
    "round": (_round, (1,)),
    "push": (_push, (0,)),
    "put-up": (_put_up, (1, 2)),
    "approve": (_decided(True), (0,)),
    "send-back": (_decided(False), (0,)),
    "comments": (_comments, (0,)),
    "pause": (_pause, (0,)),
    "runs": (_runs, (0,)),
}
