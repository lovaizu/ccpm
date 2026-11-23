---
name: stack
description: Stacks the tasks of a queue file to run to their ends apart from this session, past the usage limit, and shows when they start and how to check them, or each fault of the queue and how to mend it. Use when the user, or an AI that hands out tasks, asks overnight to run a queue of tasks, or when a plugin's AI hands its own task to overnight as a queue of one.
argument-hint: "<the queue file's path>"
---

Takes: the path of a queue file, in the form of `${CLAUDE_PLUGIN_ROOT}/domain/stacker/queue.schema.json`:

$ARGUMENTS

Gives: what `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/queue.py stack <the queue file>` prints, as it stands, by `stacker.command.main` in `${CLAUDE_PLUGIN_ROOT}/domain/stacker/command.py`.

Steps: not yet written.
