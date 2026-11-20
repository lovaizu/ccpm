---
name: <command>
description: <What a run gives the person>. Use when the person types /<plugin>:<command>, or asks <plugin> to <do what>.
argument-hint: "<the request, in the person's words>"
---

You're `<plugin>`'s orchestrator in this conversation. `<Plugin>`'s folder is `${CLAUDE_PLUGIN_ROOT}`. Your part is in `${CLAUDE_PLUGIN_ROOT}/domain/orchestrator.md`: read it whole first, unless you've read it in this conversation, then carry out its steps of a new request, with the person's words below, word for word:

$ARGUMENTS

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<command>`: the skill's name, as the person types it after `/<plugin>:`.
> - `<What a run gives the person>`, `<do what>`: what the person gets, and the words they would ask
>   for it in. Claude Code picks a skill by them.
> - The body: an entry alone, which points to the orchestrator's part, `domain/orchestrator.md`, and
>   names the event whose steps it carries out, as the part holds the steps of each event and those
>   that every event shares. A part that a skill names comes back whole after `/compact`.
