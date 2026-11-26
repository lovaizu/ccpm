"""Decides tree's command line: its subcommands, what each takes and prints, and the exit code
by which whoever ran it reads its result."""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from typing import Any, Callable

import practice
from fault import Answer, Wrong, answered
from repository import push
from repository.host import Host
from repository.place import RunPlace, of_folder
from rounds import course, files

from tree import cut, due, form, pruned, signoff, touched

# Whom a deliverable waits on, as a refused Fix says it, by what it waits on and the stage.
_WHO = {
    ("generator", None): "its generator",
    ("evaluator", None): "its evaluator",
    ("fixer", None): "its fixer",
    ("answer", None): "the user's answer to its open decision",
    ("pruner", None): "the pruner, to keep each finding left as an open decision",
    ("pruner", course.POINT): "the pruner, to weigh the point its generator gave",
    ("pruner", course.JUDGED): "the pruner, to weigh its evaluator's findings",
    ("pruner", course.FIX): "the pruner, to weigh the decision its fixer named",
    ("sign-off", None): "the user's sign-off",
}
# What `next` takes after the run, to start again each role at work.
RESTART = "--restart"

USAGE = """\
usage: tree touched <run> [<pointer>]
       tree next <run> [--restart]
       tree commit <run>
       tree fix <run> <deliverable> <source>   (the problem's words on stdin)
       tree signoff <run>
"""


def main(
    argv: Sequence[str], cwd: str, plugin_root: str, host: Host, stdin: Callable[[], str] = str
) -> Answer:
    """The exit code, stdout, and stderr of `tree` with the arguments, from the folder `cwd`,
    with rn's folder at `plugin_root`, git reached through `host`, and what it's given on stdin
    read by `stdin`, which only `fix` reads.

    - `touched <run> <pointer>`: 0 printing each node that `tree.touched.touched` gives for the
      tree in the work branch's last commit and the tree as it stands, its pointer a line.
    - `touched <run>`: the same for each node that `tree.touched.changed` gives between the tree in
      the work branch's last commit and the tree as it stands, each node once, the changed nodes
      left out.
    - `next <run>`: 0 printing each thing that `tree.due.due` gives due now, a line each, its words
      apart by a tab: `hearing`; `sign-off\\tplan`; `pruner\\t<deliverable>\\t<result>`, the result
      to weigh by its absolute path; `answer\\t<deliverable>\\t<condition>\\t<about>`;
      `start\\t<role>\\t<deliverable>\\t<cut>`, having written the role's Cut where
      `rounds.course.next_in` places it: for the generator in a new Round, or in the last one, its
      weighed point taken out by `rounds.files.reopen`; for the evaluator in the last Round; for
      the fixer in the last Fix; the Cut's path from `cwd`; `running\\t<role>\\t<deliverable>`;
      `put-up\\t<deliverable>`; `sign-off\\t<deliverable>`; and `final-check`; nothing where none
      is due.
    - `next <run> --restart`: the same, but each role at work comes as `start`, after the others,
      its Cut written anew in its Round or Fix, as a pick-up in a new conversation starts again
      each role that a pause stopped.
    - `commit <run>`: reads the pruner's result, `<run>/pruner.json`, as `tree.pruned.read` holds
      it; signs off the plan where `tree.signoff.waiting` names it, open with each condition good,
      the goal is settled, and the result asks nothing, as `tree.signoff.signed_off` writes it;
      commits the tree with the removal of each of its `stray`, as `push.commit` does, with the
      message that `tree.pruned.ground` gives; removes `pruner.json`, which no commit holds; and
      gives 0 printing the hash, then each line that `tree.pruned.told` gives. Where the tree has no
      change since the last commit and the result names no stray, it commits nothing and prints the
      last commit's hash. Either way it then marks with that hash, as `rounds.files.weigh` does, the
      Round or Fix of each of the result's `units` whose point, findings, or fixer's decision waits
      on the pruner, and no other. 1, changing nothing, where the result is missing or Wrong; where
      a unit is none that `tree next` prints on a pruner line for the tree as last committed; or
      where `push.commit` refuses a stray as Wrong. It pushes nothing and asks gh nothing, as the
      final check pushes the work and the user marks the pull request ready.
    - `fix <run> <deliverable> <source>`, `<source>` one of `rounds.files.SOURCES`, with the
      problem's words on stdin, as they were printed or said: writes the deliverable's next Fix
      as `rounds.files.new_fix` does, with the problem that `rounds.files.problem` gives, and
      gives 0 printing the Fix's folder, absolute; 1 writing nothing where the source or the
      words are Wrong, or where the deliverable waits on other than the sign-off, saying on what:
      where its Rounds aren't over yet, or a Fix of it waits unfinished, on its fixer or on the
      pruner that weighs the decision its fixer named.
    - `signoff <run>`: writes the tree that `tree.signoff.signed_off` gives for the deliverable
      that `tree.signoff.waiting` names, commits it as `push.commit` does, as `rn: <its name>,
      signed off`, so that the next pruner's change since the last commit is its own alone, and
      gives 0 printing the tree's path; 1 where none waits. It pushes nothing.

    `<run>` is the run's folder, as `place.of_folder` takes it. 1 with `tree: <what's wrong>`
    where the input is Wrong or something is Missing, saying how to mend it; 2 with what stopped it
    where it CantRun, such as a commit check of the repository refusing the design tree's commit,
    with what git said; 2 with the usage where the arguments are other than these, `next` given
    other than `--restart` after the run among them.
    """
    if not argv or argv[0] not in _SUBCOMMANDS:
        return 2, "", USAGE
    subcommand, least, most = _SUBCOMMANDS[argv[0]]
    if not least <= len(argv) - 1 <= most:
        return 2, "", USAGE
    if argv[0] == "next" and argv[2:] not in ([], [RESTART]):
        return 2, "", USAGE
    given = list(argv[2:]) + ([stdin()] if argv[0] in _READS_STDIN else [])
    return answered(
        "tree", lambda: subcommand(of_folder(cwd, argv[1]), given, cwd, plugin_root, host)
    )


def _touched(run: RunPlace, given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    before, after = _committed(run, host), form.read(run.tree)
    if given:
        return 0, _lines(touched.touched(before, after, given[0])), ""
    made = touched.changed(before, after)
    found: list[str] = []
    for each in made:
        found += touched.touched(before, after, _held(after, each))
    return 0, _lines(list(dict.fromkeys(node for node in found if node not in made))), ""


def _next(run: RunPlace, given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    tree = form.read(run.tree)
    found = due.due(run, tree)
    if given:
        working = [due.Due("start", each.words) for each in found if each.kind == "running"]
        found = [each for each in found if each.kind != "running"] + working
    lines = []
    for each in found:
        if each.kind == "start":
            role, path = each.words
            written = _started(run, tree, role, path, plugin_root)
            lines.append(["start", role, path, os.path.relpath(written, cwd)])
        elif each.kind == "sign-off-plan":
            lines.append(["sign-off", "plan"])
        else:
            lines.append([each.kind, *each.words])
    return 0, _lines(["\t".join(each) for each in lines]), ""


def _started(run: RunPlace, tree: form.Tree, role: str, path: str, plugin_root: str) -> str:
    """Writes the Cut of the role due for the deliverable where `rounds.course.next_in` places
    it, and gives the Cut's path."""
    if role == "fixer":
        fix = course.mended(run, path)[-1].fix
        return _written(fix.cut, cut.fixer(tree, run, fix))
    node = form.deliverable(tree, path)
    next_ = course.next_in(run, node)
    done = course.so_far(run, path)
    if role == "generator" and not next_.resumes:
        round_ = files.new(run, path, str(next_.stage))
    else:
        round_ = done[-1].round
    if role == "generator" and next_.resumes and done[-1].generator is not None:
        files.reopen(round_)
    kinds = practice.kinds(plugin_root, run.worktree)
    if role == "generator":
        written = cut.generator(tree, run, round_, kinds, _last([each.generator for each in done]))
    else:
        folder = kinds[node["kind"]]
        written = cut.evaluator(tree, run, round_, practice.Found(folder, practice.read(folder)))
    return _written(round_.cut(role), written)


def _commit(run: RunPlace, given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    weighing = pruned.read(run.pruner)
    weighable = _weighable(run, _committed(run, host))
    for each in weighing["units"]:
        if os.path.normpath(each) not in weighable:
            raise Wrong(
                f"{each}: is no unit that tree next prints on a pruner line now; name in units"
                " only each path that such a line gave, and none for the hearing or the user's"
                " words"
            )
    tree = form.read(run.tree)
    plan = signoff.waiting(tree, {})
    signs = plan is not None and tree["goal"]["decided"] is not None and not weighing["ask"]
    if plan is not None and signs:
        form.write(run.tree, signoff.signed_off(tree, plan))
    path = os.path.relpath(run.tree, run.worktree)
    changed = host(["git", "status", "--porcelain", "--", path], run.worktree).out.strip()
    if changed or weighing["stray"]:
        message = pruned.ground(weighing, run.name, signs)
        try:
            made = push.commit(run, [path], message, host, weighing["stray"])
        except Wrong:
            form.write(run.tree, tree)
            raise
    else:
        made = host(["git", "rev-parse", "HEAD"], run.worktree).out.strip()
    _weigh(weighable, weighing["units"], made)
    os.remove(run.pruner)
    return 0, _lines([made, *pruned.told(weighing)]), ""


def _fix(run: RunPlace, given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    path, source, words = given
    problem = files.problem(source, words)
    node = form.deliverable(form.read(run.tree), path)
    next_ = course.next_in(run, node)
    if next_.waits_on != "sign-off":
        return 1, "", f"tree: {path} waits on {_who(next_)}, {_unfinished(next_)}\n"
    return 0, f"{files.new_fix(run, path, problem).folder}\n", ""


def _written(path: str, written: cut.Cut) -> str:
    """Writes the Cut at its path, and gives the path."""
    with open(path, "w", encoding="utf-8") as file:
        file.write(json.dumps(written, indent=1) + "\n")
    return path


def _who(next_: course.Next) -> str:
    """Whom the deliverable waits on, in words."""
    return _WHO.get((next_.waits_on, next_.stage), _WHO[(next_.waits_on, None)])


def _unfinished(next_: course.Next) -> str:
    """Why a deliverable that doesn't wait on the sign-off takes no Fix, and what to do, in
    words."""
    if next_.waits_on == "fixer" or next_.stage == course.FIX:
        return "as a Fix of it is unfinished; end that Fix before another"
    return (
        "as its Rounds aren't over yet; a Fix mends a deliverable whose Rounds are over, and its"
        " Rounds mend it till then"
    )


def _signoff(run: RunPlace, given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    tree = form.read(run.tree)
    nexts = {
        node["path"]: course.next_in(run, node)
        for node in tree["deliverables"]
        if node["status"] != "done" and node["kind"] != "design-tree"
    }
    waiting = signoff.waiting(tree, nexts)
    if waiting is None:
        return 1, "", "tree: no deliverable waits for the user's sign-off\n"
    form.write(run.tree, signoff.signed_off(tree, waiting))
    name = form.deliverable(tree, waiting)["name"]
    push.commit(run, [os.path.relpath(run.tree, run.worktree)], f"rn: {name}, signed off", host)
    return 0, f"{os.path.relpath(run.tree, cwd)}\n", ""


def _weighable(run: RunPlace, committed: form.Tree) -> dict[str, files.Round | files.Fix | None]:
    """Each unit that `tree next` prints on a pruner line for the tree as last committed, as it
    stood when the pruner was handed its unit, by its absolute path, with the Round or Fix to mark
    weighed; None for the last Round's findings past the limit, weighed already; none where no
    commit holds the tree yet."""
    found: dict[str, files.Round | files.Fix | None] = {}
    if not committed:
        return found
    for each in due.due(run, committed):
        if each.kind != "pruner":
            continue
        path, unit = each.words
        if os.path.basename(unit) == f"{files.FIXER}.json":
            found[unit] = course.mended(run, path)[-1].fix
        else:
            last = course.so_far(run, path)[-1]
            found[unit] = last.round if last.unweighed else None
    return found


def _weigh(
    weighable: dict[str, files.Round | files.Fix | None], units: list[str], made: str
) -> None:
    """Marks as weighed by the commit the Round or Fix of each unit that the pruner weighed, as
    the commit follows its weighing, and no other, as another deliverable's unit may end while
    it weighs."""
    for each in units:
        folder = weighable[os.path.normpath(each)]
        if folder is not None:
            files.weigh(folder, made)


def _committed(run: RunPlace, host: Host) -> Any:
    """The design tree in the work branch's last commit, or {} where none holds it yet."""
    path = os.path.relpath(run.tree, run.worktree)
    shown = host(["git", "show", f"HEAD:{path}"], run.worktree)
    return json.loads(shown.out) if shown.code == 0 else {}


def _held(tree: Any, pointer: str) -> str:
    """The pointer, or, for a node the tree no longer holds, its nearest one that it holds."""
    while pointer.count("/") > 1:
        try:
            form.at(tree, pointer)
            return pointer
        except Wrong:
            pointer = pointer.rsplit("/", 1)[0]
    return pointer


def _last(results: list[Any]) -> Any:
    """The latest of a role's results in the Rounds, None where it wrote none, or None."""
    written = [each for each in results if each is not None]
    return written[-1] if written else None


def _lines(given: list[str]) -> str:
    """Each one given, such as a node's pointer, on a line of its own."""
    return "".join(f"{each}\n" for each in given)


_Subcommand = Callable[[RunPlace, list[str], str, str, Host], Answer]
# Each subcommand, with its least and most count of arguments after its name, the run's among them.
_SUBCOMMANDS: dict[str, tuple[_Subcommand, int, int]] = {
    "touched": (_touched, 1, 2),
    "next": (_next, 1, 2),
    "commit": (_commit, 1, 1),
    "fix": (_fix, 3, 3),
    "signoff": (_signoff, 1, 1),
}
# The subcommands that take what they're given on stdin, after their arguments.
_READS_STDIN = ("fix",)
