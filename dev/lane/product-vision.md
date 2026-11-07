# Lane Product Vision

## Roles

- **user**: one who builds a Claude Code plugin whose roles work in steps, a person or an AI.

## OKRs

- O1: The user has the plugin they build run as they designed it, on every run: each role keeping
  the steps they wrote, and the roles started in the order they set.
  - KR1.1: Of the runs of the user's plugin, the share that goes wrong: a role breaks a step and
    goes on, or is stopped and does it another way; a move the steps allow is stopped, the user's
    own work outside the run among them; a role starts that the order does not name, or one it
    names is stopped; the run stops while the order names a move; or the user writes a check or
    code of their own, or leaves a step unheld, as Lane cannot hold it. Lower is better.
  - KR1.2: The time from the user's first step or order for a plugin to its first run that keeps
    them. Shorter is better.

KR1.1 comes first: a change that improves KR1.2 is kept only if KR1.1 does not get worse. Key
results have no targets, as a measure made a target stops being a good measure (Goodhart's
law). They show whether a change brought its objective closer.

## Concept

Lane instead of writing the steps and the order in prompts, with a hook of one's own for what must
hold:

- **The step says it again**: a role stopped from breaking a step is shown that step's own
  sentence, so it goes back to the step, where a hook that only refuses leaves it to seek another
  way (O1).
- **The result from a run, not from a reply**: a role gives its result by running a script, so a
  reply such as "No more entries" is never read as `more` (O1).
- **The order as routes**: the user names which role comes next after which result, and each next
  move is told and held, so no code keeps the order, and a run goes on after its conversation is
  compacted (O1).
- **Checks laid, not written**: the user sees their steps and routes as they will read, approves
  them, and gets the checks laid into the plugin, writing and testing none (O1).
