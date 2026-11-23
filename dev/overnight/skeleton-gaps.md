# Skeleton

## Module opening

Each module in `plugins/overnight/domain/` states the one decision it hides in the first sentence
of its docstring.

## Interface

Each interface lies in its module, with its types in its signature and its contract in its
docstring. Its body raises `NotImplementedError` with its name.

## Prompt

`/overnight:stack` and `/overnight:check` lie in `plugins/overnight/skills/`, each with what it
takes and gives, and no steps.

## Gaps

- S1: the arrow by which the stacker starts the runner names only the queue's tasks (Task). The
  runner also needs the queue's start hour (Queue) and each carried-on task's session (Run). So
  `runner.handoff.Handoff` carries both, which the arrow doesn't show.
- Directory structure: `<queue>/` holds only `runs.json` and each `<task>.md`. The runner's lock on
  the queue needs a file, which has no place there. So `record.place.Place.lock` puts it in
  `<queue>/`, which Directory structure doesn't show.
