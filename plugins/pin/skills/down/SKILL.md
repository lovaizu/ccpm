---
name: down
description: Pins a plan down before any work on it starts. Settles every point the plan needs, from its goal down, in a design tree, finds each fact itself and shows it to the person to confirm, and asks the person only the decisions that are theirs, one at a time. Use when the person wants to settle a plan, a feature, a change or a document before it is made, or types /pin:down; also when an AI that is to make a work for the person has written its goal, its questions and what it settled into a design tree, to settle the rest with the person.
argument-hint: "<the plan, in your own words>"
---

Pin's folder is `${CLAUDE_PLUGIN_ROOT}`. Your steps are in `${CLAUDE_PLUGIN_ROOT}/core/roles/orchestrator.md`. Read it whole first, and take
its steps on the plan. Typed as `/pin:down`, the plan is "$ARGUMENTS". Called by an AI, it is
the AI's request, with the design tree's path where the AI wrote one.
