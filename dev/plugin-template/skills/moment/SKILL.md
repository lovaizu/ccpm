---
name: <moment>
description: <What the command does to the run>. Use when the person types /<plugin>:<moment>.
argument-hint: "[<what the person adds, in their own words>]"
disable-model-invocation: true
---

You're `<plugin>`'s orchestrator in this conversation. `<Plugin>`'s folder is `${CLAUDE_PLUGIN_ROOT}`. Your part is in `${CLAUDE_PLUGIN_ROOT}/domain/orchestrator.md`: read it whole with the Read tool first, unless you've read it in this conversation, then carry out its steps of <the event, such as a sign-off>, with the person's words below, word for word, empty where they typed the command alone:

$ARGUMENTS

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<moment>`: the skill's name, as the person types it after `/<plugin>:`, such as one that
>   approves, sends back, or pauses the run.
> - `<What the command does to the run>`: what the command does, so that the person and Claude Code
>   don't take it for another of the plugin's commands.
> - `disable-model-invocation: true`: keep it where the command decides what's the caller's, such
>   as an approval or a pause, so that only the caller can start the skill.
> - `$ARGUMENTS`: keep it where the person may add words, as the orchestrator carries them word for
>   word. Otherwise remove it, the words that lead to it, and `argument-hint`.
> - The body: an entry alone, which names the event whose steps the orchestrator's part holds.
