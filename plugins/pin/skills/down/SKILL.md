---
name: down
description: Pins a plan down before any work on it starts. Settles every decision the plan needs, from its goal down, in a design file, finds each fact itself and shows it to the person to confirm, and asks the person only the decisions that are theirs, one at a time. Use when the person wants to settle a plan, a feature, a change or a document before it is made, or types /pin:down; also when an AI that is to make a work has written its goal and questions into a design file to settle with the person.
argument-hint: "<the plan, in your own words>"
---

Your steps are in `${CLAUDE_PLUGIN_ROOT}/core/roles/go-between.md`. Read it whole first, and take
its steps on the plan. Given as `/pin:down`, the plan is "$ARGUMENTS"; given by a maker AI, it is
in its request, with the design file's path.
