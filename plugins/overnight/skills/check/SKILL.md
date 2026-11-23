---
name: check
description: Shows where the tasks of a stacked queue stand, which finished, with each reply and the folder each wrote in, and why each other was given up, or overnight's version where no stacked queue is named. Use when the user, or an AI that handed out tasks, asks overnight how a queue's tasks ended, or to take their results in.
argument-hint: "[the queue file's path]"
---

Takes: the path of a queue file that `/overnight:stack` stacked, or nothing:

$ARGUMENTS

Gives: what `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/queue.py check [<the queue file>]` prints, as it stands, by `checker.command.main` in `${CLAUDE_PLUGIN_ROOT}/domain/checker/command.py`.

Steps: not yet written.
