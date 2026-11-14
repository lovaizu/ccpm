# Lane product vision

## Roles

- user\
  One who builds a Claude Code plugin whose roles work in steps, either a person or an AI.

## Objectives and key results

- O1: the user has the plugin they build run as they designed it, on every run: each role keeping
  the steps they wrote, and the roles started in the order they set.
  - KR1.1: of the runs of the user's plugin, the share that goes wrong in one of these ways. Lower
    is better.
    - A role breaks a step and goes on, or a check stops it and it does the step another way.
    - A check stops a move the steps allow, the user's own work outside the run among them.
    - A role starts that the order doesn't name, or a check stops one it names.
    - The run stops while the order names a move.
    - The user writes a check or code of their own, or leaves a step unheld, as Lane can't hold
      it.
  - KR1.2: the time from the user's first step or order for a plugin to its first run that keeps
    them. Shorter is better.

KR1.1 comes first: keep a change that improves KR1.2 only if KR1.1 doesn't get worse. Key
results have no targets, as a measure made a target stops being a good measure, by Goodhart's
law. They show whether a change brought its objective closer.

## Concept

Lane holds each role of the user's plugin to the steps and the order the user wrote, on every run,
by checks it lays from them.

- The step said again, for O1\
  A role that Lane stops gets the step's own sentence, and goes back to the step.
- The result from a run, not from a reply, for O1\
  A role gives its result by running a script, so Lane never misreads a reply as a result.
- The order as routes, for O1\
  The user names which move comes after each result, and Lane gives and holds each next move.
- Checks laid, not written, for O1\
  The user approves their steps and routes as laid, and writes and tests no check.
- A run picked up where it stopped, for O1\
  After a pause, a new conversation goes on from the results that the plugin kept.
