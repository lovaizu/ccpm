"""Decides tree.py's command line: its subcommands, what each takes and prints, and the exit code
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
from template.check import TEMPLATE
from template.check import figures as figures_of

from tree import checks, cut, form, signoff, touched

# Whom a deliverable waits on, as a refused cut says it, by what it waits on and the stage.
_WHO = {
    ("generator", None): "its generator",
    ("evaluator", None): "its evaluator",
    ("fixer", None): "its fixer",
    ("answer", None): "the user's answer to its open decision",
    ("pruner", None): "the pruner, to keep each finding left as an open decision",
    ("pruner", course.FIX): "the pruner, to weigh the decision its fixer named",
    ("sign-off", None): "the user's sign-off",
}

USAGE = """\
usage: tree.py touched <run> [<pointer>]
       tree.py check <run>
       tree.py commit <run> <ground>
       tree.py cut <run> <role> <deliverable>
       tree.py fix <run> <deliverable> <source>   (the problem's words on stdin)
       tree.py signoff <run>
"""


def main(
    argv: Sequence[str], cwd: str, plugin_root: str, host: Host, stdin: Callable[[], str] = str
) -> Answer:
    """The exit code, stdout, and stderr of `tree.py` with the arguments, from the folder `cwd`,
    with rn's folder at `plugin_root`, git reached through `host`, and what it's given on stdin
    read by `stdin`, which only `fix` reads.

    - `touched <run> <pointer>`: 0 printing each node that `tree.touched.touched` gives for the
      tree in the work branch's last commit and the tree as it stands, its pointer a line.
    - `touched <run>`: the same for each node that `tree.touched.changed` gives between the tree in
      the work branch's last commit and the tree as it stands, each node once, the changed nodes
      left out.
    - `check <run>`: 0 printing nothing where `tree.checks.faults` finds no fault in the design
      tree as it stands, else 1 printing each fault on a line of its own; it changes nothing, so
      that the pruner checks its write before it ends.
    - `commit <run> <ground>`: where `tree.checks.faults` finds none, commits the design tree as
      `push.commit` does with `<ground>` as the message, and gives 0 printing the hash; else 1
      with the first fault, git left as it was; 0 printing the last commit's hash, committing
      nothing, where the tree has no change since it. Either way it marks with that hash, as
      `rounds.files.weigh` does, each deliverable's last Fix that waits on the pruner to weigh
      the decision its fixer named, as the commit follows that pruner's weighing. It pushes
      nothing and asks gh nothing, as the final check pushes the work and the user marks the pull
      request ready.
    - `cut <run> <role> <deliverable>`, `<role>` `generator`, `evaluator`, or `fixer`: writes the
      role's Cut in the Round that `rounds.course.next_in` gives the deliverable, made anew where
      the generator starts a new Round, or, for the fixer, in its last Fix, and gives 0 printing
      the Cut's path from `cwd`; 1 where the deliverable waits on another role, the user, or the
      pruner, saying which, and where the tree's goal is open, saying that a new pruner writes it,
      each writing nothing.
    - `fix <run> <deliverable> <source>`, `<source>` one of `rounds.files.SOURCES`, with the
      problem's words on stdin, as they were printed or said: writes the deliverable's next Fix
      as `rounds.files.new_fix` does, with the problem that `rounds.files.problem` gives, and
      gives 0 printing the Fix's folder, absolute; 1 writing nothing where the source or the
      words are Wrong, or where the deliverable waits on other than the sign-off, saying on what:
      where its Rounds aren't over yet, or a Fix of it waits unfinished, on its fixer or on the
      pruner that weighs the decision its fixer named.
    - `signoff <run>`: writes the tree that `tree.signoff.signed_off` gives for the deliverable
      that `tree.signoff.waiting` names, and gives 0 printing its path; 1 where none waits. It
      commits and pushes nothing, as `commit` does once the tree is reviewed.

    `<run>` is the run's folder, as `place.of_folder` takes it. 1 with `tree.py: <what's wrong>`
    where the input is Wrong or something is Missing, saying how to mend it; 2 with what stopped it
    where it CantRun, such as a commit check of the repository refusing the design tree's commit,
    with what git said; 2 with the usage where the arguments are other than these.
    """
    if not argv or argv[0] not in _SUBCOMMANDS:
        return 2, "", USAGE
    subcommand, least, most = _SUBCOMMANDS[argv[0]]
    if not least <= len(argv) - 1 <= most:
        return 2, "", USAGE
    given = list(argv[2:]) + ([stdin()] if argv[0] in _READS_STDIN else [])
    return answered(
        "tree.py", lambda: subcommand(of_folder(cwd, argv[1]), given, cwd, plugin_root, host)
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


def _check(run: RunPlace, given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    found = _faults(run, plugin_root)
    return (1 if found else 0), _lines(found), ""


def _commit(run: RunPlace, given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    found = _faults(run, plugin_root)
    if found:
        return 1, "", f"tree.py: {found[0]}\n"
    path = os.path.relpath(run.tree, run.worktree)
    if host(["git", "status", "--porcelain", "--", path], run.worktree).out.strip():
        made = push.commit(run, [path], given[0], host)
    else:
        made = host(["git", "rev-parse", "HEAD"], run.worktree).out.strip()
    _weigh(run, made)
    return 0, f"{made}\n", ""


def _cut(run: RunPlace, given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    role, path = given
    tree = form.read(run.tree)
    form.goal(tree)
    node = form.deliverable(tree, path)
    next_ = course.next_in(run, node)
    if next_.waits_on != role:
        return 1, "", f"tree.py: {path} waits on {_who(next_)}, not on its {role}\n"
    if role == "fixer":
        fix = course.mended(run, path)[-1].fix
        return _written(fix.cut, cut.fixer(tree, run, fix), cwd)
    done = course.so_far(run, path)
    if role == "generator" and not next_.resumes:
        round_ = files.new(run, path, str(next_.stage))
    else:
        round_ = done[-1].round
    kinds = practice.kinds(plugin_root, run.worktree)
    if role == "generator":
        written = cut.generator(tree, run, round_, kinds, _last([each.generator for each in done]))
    else:
        folder = kinds[node["kind"]]
        written = cut.evaluator(tree, run, round_, practice.Found(folder, practice.read(folder)))
    return _written(round_.cut(role), written, cwd)


def _fix(run: RunPlace, given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    path, source, words = given
    problem = files.problem(source, words)
    node = form.deliverable(form.read(run.tree), path)
    next_ = course.next_in(run, node)
    if next_.waits_on != "sign-off":
        return 1, "", f"tree.py: {path} waits on {_who(next_)}, {_unfinished(next_)}\n"
    return 0, f"{files.new_fix(run, path, problem).folder}\n", ""


def _written(path: str, written: cut.Cut, cwd: str) -> Answer:
    """Writes the Cut at its path, and gives 0 printing the path from `cwd`."""
    with open(path, "w", encoding="utf-8") as file:
        file.write(json.dumps(written, indent=1) + "\n")
    return 0, f"{os.path.relpath(path, cwd)}\n", ""


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
        return 1, "", "tree.py: no deliverable waits for the user's sign-off\n"
    form.write(run.tree, signoff.signed_off(tree, waiting))
    return 0, f"{os.path.relpath(run.tree, cwd)}\n", ""


def _weigh(run: RunPlace, made: str) -> None:
    """Marks as weighed by the commit each deliverable's last Fix that waits on the pruner to weigh
    the decision its fixer named, as the commit follows the pruner's weighing."""
    for node in form.read(run.tree)["deliverables"]:
        if course.next_in(run, node) == course.Next("pruner", course.FIX, False):
            files.weigh(course.mended(run, node["path"])[-1].fix, made)


def _faults(run: RunPlace, plugin_root: str) -> list[str]:
    """Each fault that `tree.checks.faults` finds in the run's design tree as it stands, by the
    best practice of each kind that `practice.kinds` finds, and the figures of its template where
    its folder holds one."""
    kinds = practice.kinds(plugin_root, run.worktree)
    practices = {kind: practice.read(folder) for kind, folder in kinds.items()}
    figures = {
        kind: figures_of(_text(os.path.join(folder, TEMPLATE)))
        for kind, folder in kinds.items()
        if os.path.isfile(os.path.join(folder, TEMPLATE))
    }
    return checks.faults(form.read(run.tree), practices, run.worktree, figures)


def _text(path: str) -> str:
    """The file's text."""
    with open(path, encoding="utf-8") as file:
        return file.read()


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
    """Each one given, such as a node's pointer or a fault, on a line of its own."""
    return "".join(f"{each}\n" for each in given)


_Subcommand = Callable[[RunPlace, list[str], str, str, Host], Answer]
# Each subcommand, with its least and most count of arguments after its name, the run's among them.
_SUBCOMMANDS: dict[str, tuple[_Subcommand, int, int]] = {
    "touched": (_touched, 1, 2),
    "check": (_check, 1, 1),
    "commit": (_commit, 2, 2),
    "cut": (_cut, 3, 3),
    "fix": (_fix, 3, 3),
    "signoff": (_signoff, 1, 1),
}
# The subcommands that take what they're given on stdin, after their arguments.
_READS_STDIN = ("fix",)
