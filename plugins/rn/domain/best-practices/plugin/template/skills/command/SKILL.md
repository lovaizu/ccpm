---
name: <command>
description: <What a run gives the person>. Use when the person types /<plugin>:<command>, or asks <plugin> to <do what>.
argument-hint: "<the request, in the person's words>"
---

You're `<plugin>`'s orchestrator in this conversation, for the request "$ARGUMENTS". `<Plugin>`'s folder is `${CLAUDE_PLUGIN_ROOT}`. Your part is in `${CLAUDE_PLUGIN_ROOT}/domain/orchestrator.md`: read it whole first, and then carry it out for the request.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<command>`: the skill's name, as the person types it after `/<plugin>:`.
> - `<What a run gives the person>`, `<do what>`: what the person gets, and the words they would ask
>   for it in. Claude Code picks a skill by them.
> - `disable-model-invocation: true`: add it to the frontmatter when the skill approves something
>   that's the caller's to decide, such as a merge. Then only the caller can start the skill.
> - The body: it points to the orchestrator's part, `domain/orchestrator.md`, written in the form of `domain/role.md`.
>   The main conversation reads the part whole. A part that a skill names comes back whole after
>   `/compact`.
