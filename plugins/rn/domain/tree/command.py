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
from repository.place import RunPlace, of_folder, of_session
from rounds import course, files

from tree import checks, cut, form, signoff, touched

# Whom a deliverable waits on, as a refused cut says it.
_WHO = {
    "generator": "its generator",
    "evaluator": "its evaluator",
    "answer": "the user's answer to its open decision",
    "orchestrator": "the orchestrator, to keep each finding left as an open decision",
    "sign-off": "the user's sign-off",
}

# The form of the argument that names a run by its conversation's session ID.
_SESSION = "--session="

USAGE = """\
usage: tree.py touched <run> [<pointer>]
       tree.py commit <run> <ground>
       tree.py cut <run> <role> <deliverable>
       tree.py signoff <run>
"""


def main(argv: Sequence[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    """The exit code, stdout, and stderr of `tree.py` with the arguments, from the folder `cwd`,
    with rn's folder at `plugin_root`, and git reached through `host`.

    - `touched <run> <pointer>`: 0 printing each node that `tree.touched.touched` gives for the
      tree in the work branch's last commit and the tree as it stands, its pointer a line, one word
      each, as Lane takes the lines as a checklist's items.
    - `touched <run>`: the same for each node that `tree.touched.changed` gives between the tree in
      the work branch's last commit and the tree as it stands, each node once, the changed nodes
      left out.
    - `commit <run> <ground>`: where `tree.checks.faults` finds none, commits the design tree as
      `push.commit` does with `<ground>` as the message, and gives 0 printing the hash; else 1
      with the first fault, git left as it was; 0 printing the last commit's hash, committing
      nothing, where the tree has no change since it. It pushes nothing and asks gh nothing, as the
      final check pushes the work and the user marks the pull request ready.
    - `cut <run> <role> <deliverable>`, `<role>` `generator` or `evaluator`: writes the role's Cut
      in the Round that `rounds.course.next_of` gives the deliverable, made anew where the
      generator starts a new Round, and gives 0 printing the Cut's path from `cwd`; 1 where the
      deliverable waits on another role, the user, or the orchestrator, saying which.
    - `signoff <run>`: writes the tree that `tree.signoff.signed_off` gives for the deliverable
      that `tree.signoff.waiting` names, and gives 0 printing its path; 1 where none waits. It
      commits and pushes nothing, as `commit` does once the tree is reviewed.

    `<run>` is the run's folder, as `place.of_folder` takes it, or `--session=<session ID>`, the run
    that `place.of_session` gives for the conversation of the session, as Lane runs a checklist's
    command whose run the turn makes before it's named. 1 with `tree.py: <what's wrong>`
    where the input is Wrong or something is Missing, saying how to mend it; 2 with what stopped it
    where it CantRun, such as a commit check of the repository refusing the design tree's commit,
    with what git said; 2 with the usage where the arguments are other than these.
    """
    if not argv or argv[0] not in _SUBCOMMANDS:
        return 2, "", USAGE
    subcommand, least, most = _SUBCOMMANDS[argv[0]]
    if not least <= len(argv) - 1 <= most:
        return 2, "", USAGE
    return answered(
        "tree.py",
        lambda: subcommand(_run(cwd, argv[1]), list(argv[2:]), cwd, plugin_root, host),
    )


def _run(cwd: str, given: str) -> RunPlace:
    """The run that the argument names: its folder, or `--session=<session ID>`."""
    if not given.startswith(_SESSION):
        return of_folder(cwd, given)
    session = given[len(_SESSION) :]
    run = of_session(cwd, session) if session else None
    if run is None:
        raise Wrong(f"no run here holds the session {session!r}; give the run's folder")
    return run


def _touched(run: RunPlace, given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    before, after = _committed(run, host), form.read(run.tree)
    if given:
        return 0, _lines(touched.touched(before, after, given[0])), ""
    made = touched.changed(before, after)
    found: list[str] = []
    for each in made:
        found += touched.touched(before, after, _held(after, each))
    return 0, _lines(list(dict.fromkeys(node for node in found if node not in made))), ""


def _commit(run: RunPlace, given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    tree = form.read(run.tree)
    practices = {
        kind: practice.read(folder)
        for kind, folder in practice.kinds(plugin_root, run.worktree).items()
    }
    found = checks.faults(tree, practices, run.worktree)
    if found:
        return 1, "", f"tree.py: {found[0]}\n"
    path = os.path.relpath(run.tree, run.worktree)
    if host(["git", "status", "--porcelain", "--", path], run.worktree).out.strip():
        made = push.commit(run, [path], given[0], host)
    else:
        made = host(["git", "rev-parse", "HEAD"], run.worktree).out.strip()
    return 0, f"{made}\n", ""


def _cut(run: RunPlace, given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    role, path = given
    tree = form.read(run.tree)
    node = form.deliverable(tree, path)
    kinds = practice.kinds(plugin_root, run.worktree)
    done = course.so_far(run, path)
    next_ = course.next_in(run, node)
    if next_.waits_on != role:
        return 1, "", f"tree.py: {path} waits on {_WHO[next_.waits_on]}, not on its {role}\n"
    if role == "generator" and not next_.resumes:
        round_ = files.new(run, path, str(next_.stage))
    else:
        round_ = done[-1].round
    kind = node["kind"]
    if role == "generator" and round_.stage == "refactor":
        kind = str(practice.refactoring(kind))
    found = practice.Found(kinds[kind], practice.read(kinds[kind]))
    if role == "generator":
        last = (
            _last([each.generator for each in done]),
            _last([each.evaluator for each in done]),
        )
        written = cut.generator(tree, run, round_, found, last)
    else:
        written = cut.evaluator(tree, run, round_, found)
    with open(round_.cut(role), "w", encoding="utf-8") as file:
        file.write(json.dumps(written, indent=1) + "\n")
    return 0, f"{os.path.relpath(round_.cut(role), cwd)}\n", ""


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


def _lines(nodes: list[str]) -> str:
    """The nodes, a pointer a line."""
    return "".join(f"{each}\n" for each in nodes)


_Subcommand = Callable[[RunPlace, list[str], str, str, Host], Answer]
# Each subcommand, with its least and most count of arguments after its name, the run's among them.
_SUBCOMMANDS: dict[str, tuple[_Subcommand, int, int]] = {
    "touched": (_touched, 1, 2),
    "commit": (_commit, 2, 2),
    "cut": (_cut, 3, 3),
    "signoff": (_signoff, 1, 1),
}
