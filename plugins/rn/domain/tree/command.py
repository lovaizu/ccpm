"""Decides tree.py's command line: what each of its commands takes, which modules it joins, and
what it prints with the exit code by which a role or the orchestrator reads its result."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TextIO


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
      `rounds.each`, the latest last.
    - `push`: 0, with the pull request's URL, from `branch.push` and `github.keep_draft`.
    - `put-up plan`, `put-up deliverable <path>`, or `put-up lesson` with its words on standard
      input: 0, with the sign-off waiting, from `sign_offs.put_up`.
    - `approve` or `send-back`: 0, with the sign-off decided, from `sign_offs.decide`; for a lesson
      approved, with its issue's URL from `github.open_lesson`; for the pull request handed over and
      sent back, once `github.hand_over` marks it a draft again.
    - `comments`: 0, with each comment since the last sign-off sent back, from `github.comments`.
    - `pause`, with `{"stood": [{"record", "step"}]}` on standard input: 0, once each Place is
      written and `branch.commit`, its message naming each record and step, and `branch.push` take
      it.
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
    raise NotImplementedError("tree.command.main")
