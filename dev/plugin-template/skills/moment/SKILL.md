---
name: <moment>
description: <What the command does to the run>. Use when the person types /<plugin>:<moment>.
argument-hint: "[<what the person adds, in their own words>]"
disable-model-invocation: true
---

The person typed /<plugin>:<moment> <to do what, such as approve what the run put up>. As `<plugin>`'s orchestrator, carry out the steps below, with your part in `${CLAUDE_PLUGIN_ROOT}/domain/orchestrator.md`, which you read whole first unless you've read it in this conversation. Their words follow word for word, empty where they typed the command alone:

$ARGUMENTS

## Steps

1. <Each step that this moment alone takes, such as recording the approval by a command of the plugin's own.>
2. Go on by your part's step <n>, <such as starting the role that the guard gives next>.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<moment>`: the skill's name, as the person types it after `/<plugin>:`, such as one that
>   approves, sends back, or pauses the run.
> - `<What the command does to the run>`: what the command does, so that the person and Claude Code
>   don't take it for another of the plugin's commands.
> - `disable-model-invocation: true`: keep it where the command decides what's the caller's, such
>   as an approval or a pause, so that only the caller can start the skill.
> - `$ARGUMENTS`: keep it where the person may add words, as the orchestrator carries them word for
>   word. Otherwise remove it, the sentence that leads to it, and `argument-hint`.
> - The steps: only those of this moment, as Claude Code loads this file when the person types the
>   command. A step that every moment takes stays in the orchestrator's part. End with the step of
>   the part that the run goes on by.
