---
name: down
description: Pins a plan down before any work on it starts. Finds every decision the plan needs, from its goal down, keeps them in a design tree file, finds each fact itself and shows it to the person to confirm, and asks the person only the decisions that are theirs, one at a time, until nothing is left assumed. Use when the person wants to settle a plan, a feature, a change or a document before it is made, or types /pin:down; also when a role is given a goal and questions to pin down as a design tree.
argument-hint: "<the plan, in your own words>"
---

`pinner.md` below is `${CLAUDE_PLUGIN_ROOT}/core/roles/pinner.md`.
The check below is `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check.py <design tree>`, run as written,
with the design tree's path in place of `<design tree>`.

Read `${CLAUDE_PLUGIN_ROOT}/core/roles/pinner.md` whole first, and take its steps on the plan.
Given as `/pin:down`, the plan is "$ARGUMENTS"; given by the one who started you, it is in what
they gave you.
