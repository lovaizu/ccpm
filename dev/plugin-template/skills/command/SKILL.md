---
name: <command>
description: <What a run gives the person>. Use when the person types /<plugin>:<command>, or asks <plugin> to <do what>.
argument-hint: "<the request, in the person's words>"
---

You're `<plugin>`'s orchestrator in this conversation, for the request "$ARGUMENTS". `<Plugin>`'s folder is `${CLAUDE_PLUGIN_ROOT}`. Your part is in `${CLAUDE_PLUGIN_ROOT}/domain/orchestrator.md`: read it whole first. It holds the steps that every moment of the run shares, and the steps below are those of the run's start.

## Steps

1. <Start the run, such as by making its folder, `.<plugin>/<yyyymmdd>-<name>/`, with your record in it, as the run keeps its work there.>
2. Draft the goal from the request: what the person is after, and for whom. Plan the work it
   needs, by `<the best practice of the plan>`. Put the goal and the plan to the person where
   they're theirs to decide, as the roles would make again any work toward a goal they didn't mean.
3. Carry out your part's steps for the request.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<command>`: the skill's name, as the person types it after `/<plugin>:`.
> - `<What a run gives the person>`, `<do what>`: what the person gets, and the words they would ask
>   for it in. Claude Code picks a skill by them.
> - The body: it points to the orchestrator's part, `domain/orchestrator.md`, which starts from the template's part of that name.
>   The main conversation reads the part whole. A part that a skill names comes back whole after
>   `/compact`.
> - The steps: only those of the run's start, as Claude Code loads this file when the person types
>   the command. A step that every moment takes goes in the orchestrator's part. A command that the
>   person types later in the run starts from `skills/moment/SKILL.md`.
