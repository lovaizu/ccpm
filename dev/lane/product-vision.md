# Lane product vision

## Roles

- **user**: one who builds a Claude Code plugin whose roles work in steps, either a person or an AI.

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

Lane instead of writing the steps and the order in prompts, with a hook of one's own for what must
hold:

- **The step says it again, for O1**: a role that Lane stops from breaking a step gets that
  step's own sentence, so it goes back to the step, where a hook that only refuses leaves it to
  seek another way.
- **The result from a run, not from a reply, for O1**: a role gives its result by running a
  script, so Lane never reads a reply such as "No more entries" as `more`.
- **The order as routes, for O1**: the user names which role comes next after which result, and
  Lane gives and holds each next move, so no code keeps the order, and a run goes on after Claude
  Code compacts its conversation.
- **Checks laid, not written, for O1**: the user reads their steps and routes as they read once
  laid, approves them, and gets the checks laid into the plugin with none to write or test.
