# Claude Code's states that Lane's guard meets

This document lists each state of Claude Code in which Lane's guard places a hook event on its Run,
its Start, and its role, by the rule of the guard in [the architecture](architecture.md#components):
the Runs of a conversation by `session_id`, the main conversation by an event with no `agent_id`, a
Start and its role by the `agent_id` that the PostToolUse of its Agent call ties to it, and the Run
of a skill by the skill that a command, a Start, or a result names. Each state names the events
that Claude Code sends, what the guard places them by, and the records in
[`dev/tests/recorded/`](../tests/recorded/) that show them, as `<file>:<lines>`. The events change
with each version of Claude Code, so the compatibility test of the architecture's Test strategy
checks them on each new version, and this list changes with the records.

## Where the guard finds the plugin it serves

Found on Claude Code 2.1.328, with two plugins loaded by `--plugin-dir`: one whose hook wrote each
input it got, and one with a skill `hi`.

- A hook gets only the skill's name, such as `"tool_input":{"skill":"b:hi"}` on the Skill call or
  `"prompt":"/b:hi"` on UserPromptSubmit, and its own plugin's folder in `CLAUDE_PLUGIN_ROOT`. No
  field names the folder of the plugin whose skill runs.
- Once the skill expands, by the Skill tool or by a typed command, the transcript at
  `transcript_path` holds a user message whose text opens
  `Base directory for this skill: <the plugin's folder>/skills/hi`. The guard reads the plugin's
  folder there.
- The transcript holds that message only from the conversation's next event after the skill's
  call: a hook that read the transcript at each event found it at the next PreToolUse and at the
  Stop, but not at UserPromptExpansion of `/b:hi` nor at the PreToolUse or PostToolUse of the
  Skill call. So the guard adds the Run at the skill's call, and reads its plugin's folder and
  rules at the next event of the main conversation.
- Claude Code puts each loaded plugin's `bin/` on the path of the Bash tool, so a plugin's step
  names a command of Lane's by its name alone.

## The states that the main use and rn bring about

| State | Events, in order | What the guard places them by | Records |
|---|---|---|---|
| The main conversation's calls in a Run | PreToolUse, then PostToolUse or PostToolUseFailure, and Stop at the end of a turn, each with no `agent_id` and no `agent_type`. | The Run of the event's `session_id`, and the main conversation by the missing `agent_id`. | `claude-code-2.1.322.jsonl:19-20` |
| A subagent started in the background | The main conversation's PreToolUse of Agent, then SubagentStart and the PostToolUse of Agent in either order, the PostToolUse naming the subagent as `tool_response.agentId`; the subagent's calls and SubagentStop, each with its `agent_id` and `agent_type`; and its end reaching the main conversation as a UserPromptSubmit of a `<task-notification>`, with a new `prompt_id`. | The Start that the guard let through at the PreToolUse, tied to the `agentId` at the PostToolUse of the same `tool_use_id`, as Lane hooks no SubagentStart, and each later event by its `agent_id`. | `claude-code-2.1.322.jsonl:10-18`, and SubagentStart after the PostToolUse in `claude-code-2.1.325-skill-command-while-subagent.jsonl:6-8` |
| A background subagent that runs on through a later prompt | The subagent's calls and SubagentStop after the main conversation's Stop and after a later prompt, each with the `prompt_id` of that later prompt. | The subagent's `agent_id`, never the `prompt_id`. | `claude-code-2.1.325-skill-command-while-subagent.jsonl:12-21` |
| Several subagents at once, two of one role among them | One assistant message's two Agent calls, each with its PreToolUse, SubagentStart, and PostToolUse before the next call's PreToolUse; two `agent_id`s of the same `agent_type`; their ends in either order. | Each Start tied at the PostToolUse of its own Agent call, so two Starts of one role never wait to be tied at once. | `claude-code-2.1.325-two-subagents.jsonl:5-25`, `:30-50`, and `:55-75` |
| A subagent resumed by SendMessage | After its end: the main conversation's PreToolUse of SendMessage with `to`, its PostToolUse with `resumedAgentId`, SubagentStart of the same `agent_id`, and a later end. To a subagent that runs: the PostToolUse says the message is queued, and the subagent's SubagentStop comes, then SubagentStart of the same `agent_id`, with no `<task-notification>` between. | The subagent's `agent_id`, which keeps its Start; a resume that a Route lists counts as a Start of that subagent at its PreToolUse. | `claude-code-2.1.322-send-message.jsonl:11-16`, and a queued message in `claude-code-2.1.322-subagent-of-subagent.jsonl:5-8` |
| An Agent call that fails after its PreToolUse | PostToolUseFailure with the call's `tool_use_id`, its `error`, and no `agent_id`, then Stop, with no SubagentStart, where it names no subagent type that exists or a permission rule denies it; Stop alone where another plugin's PreToolUse hook denies it. | The Start of the call's `tool_use_id`, dropped at the PostToolUseFailure, or, untied, at the Stop. | `claude-code-2.1.327-agent-unknown-type.jsonl:5-7`, `claude-code-2.1.327-agent-denied-by-rule.jsonl:5-7`, `claude-code-2.1.327-agent-denied-by-hook.jsonl:5-6` |
| `/compact` | PreCompact, a SubagentStop of the summary with an `agent_id` that no start named and an empty `agent_type`, SessionStart with `source` `compact`, and PostCompact, each with the same `session_id`; a subagent that runs goes on, with the compaction's `prompt_id`. | The same `session_id`, so the Run goes on; the summary's end lies outside the Run, as no Start ties its `agent_id`. | `claude-code-2.1.322-compact.jsonl:5-8`, and with a subagent running `claude-code-2.1.325-compact-while-subagent.jsonl:10-17` |
| A Run picked up in a new conversation | SessionEnd, then SessionStart with a new `session_id` and `transcript_path`. | The new `session_id`, which has no Run, so the guard picks the Run up from the kept results, as S2 draws. | `claude-code-2.1.323-worktree.jsonl:14-15` |
| EnterWorktree | From the PostToolUse of EnterWorktree on, each event's `cwd` and `transcript_path` lie in the worktree, the `session_id` stays, and each hook's `CLAUDE_PROJECT_DIR` stays the root. | The `session_id`, never the `transcript_path`, so the Run goes on in the worktree. | `claude-code-2.1.323-worktree.jsonl:5-12` and `:21-30` |
| A skill typed by a person | UserPromptSubmit, then UserPromptExpansion with `command_name` and `command_args`. | The `command_name`, which starts a Run that a person called. | `claude-code-2.1.322.jsonl:8-9` |
| A skill called by the Skill tool | PreToolUse and PostToolUse of Skill with `tool_input.skill` and `args`, and no UserPromptExpansion; a skill that sets `disable-model-invocation: true` is refused before any hook. | `tool_input.skill`, which starts a Run that an AI called, or, where it names another plugin's skill that a move of a Run names, sets that Run aside. | `claude-code-2.1.322-skill.jsonl:3-4`, `claude-code-2.1.323-skill-command.jsonl:16` |
| A command of another skill typed while a subagent runs | The main conversation's Stop, then UserPromptSubmit and UserPromptExpansion of the other skill's `command_name`, with a new `prompt_id`, while the subagent runs on; its later calls and SubagentStop carry that `prompt_id`. | The `command_name`, which starts that skill's Run beside the first, and each event of the subagent by its `agent_id`, which keeps it on its Start's Run. | `claude-code-2.1.325-skill-command-while-subagent.jsonl:12-21` |
| A reporter run by Bash | PreToolUse and PostToolUse of Bash, with the subagent's `agent_id` where a subagent runs it; the command's environment holds `CLAUDE_CODE_SESSION_ID` and no ID of the subagent. | The `agent_id` of the PostToolUse, by which the guard adds the Result or the Mark for the subagent that ran the reporter. | `claude-code-2.1.322.jsonl:14-16`, and the environment in `claude-code-2.1.322-bash-environment.jsonl:1-2` |
| A role's Read, Grep, or Glob | PreToolUse, then PostToolUse, each with the role's `agent_id` where a subagent calls it; a Read's `tool_input` names `file_path`, and may name `offset` and `limit`; its PostToolUse's `tool_response.file` gives `startLine`, `numLines`, and `totalLines`, the lines it read, counting the empty line after a last newline, and a Read with no `limit` reads a file of 2500 lines whole; a Grep's and a Glob's name `path` and `pattern`. | The `agent_id`, and the `tool_input`, by which a rule of the files never to read stops the call at its PreToolUse, and the guard adds a Read of a path that a rule of the files to read whole names, with the lines from `startLine` to `startLine` plus `numLines` less one, at its PostToolUse. | A Read whole and in part in `claude-code-2.1.325-read.jsonl:5-8`; Grep and Glob aren't recorded yet |

## Rare states

In each, Lane does what its line says, and never holds a call to the rules of another Run.

- Two conversations in one repository: each `session_id` has its own Run, and neither Run's rules
  hold the other conversation's calls.
- A subagent started by a subagent: the guard stops the start, as only the main conversation starts
  the roles. `claude-code-2.1.322-subagent-of-subagent.jsonl:2-4` shows the events.
- A subagent's SendMessage to another subagent: the guard lets it through as talk that moves no Run,
  and the subagent it reaches stays on its own Start.
- A subagent in the foreground: the PostToolUse of its Agent call, which names it, comes only
  after its calls and its SubagentStop, so no Start ties it while it works. A plugin's role sets
  `background: true`, as the definition of rules and adapters says, since Lane can't hold a role
  started there; any other subagent's events carry an `agent_id` that no Start ties, and lie
  outside the Run.
  `claude-code-2.1.323-worktree.jsonl:23-28` shows the events.
- A subagent stopped by TaskStop: no SubagentStop comes, and its `<task-notification>` says
  `killed`, so its Start runs no more with no Result, and the guard gives its start due again.
  `claude-code-2.1.323-task-stop.jsonl:9-15` shows the events.
- `/clear`, and a conversation resumed by `--resume`: the guard places each event by the
  `session_id` that it carries, so a new one starts no Run until the plugin's skill is called, and
  the same one goes on with its Run.

## What the guard answers in each single behavior

The architecture's S1 and S2 draw the guard's answers on the walkthrough's path. The guard answers
the main conversation at the event that the main conversation meets: a start or a call at its
PreToolUse, a subagent's end at the UserPromptSubmit of its `<task-notification>`, and an end of
the turn at its Stop. In each state
below, the guard answers as this list says, and each answer has an integration case that names the
guard.

- An Agent call that fails after its PreToolUse: the guard drops the call's Start at its
  PostToolUseFailure, or, where no event came, each Start still untied at the main conversation's
  Stop, so the start is due again and the Stop stops with the starts due.
- A resume by SendMessage that a Route makes due: the guard lets it through as a Start of that
  subagent. A resume that no Route makes due, such as one to answer a question, goes through as
  talk that moves no Run, and the subagent's Start runs again.
- A resume queued to a subagent that still runs: the guard holds the resume's Start back until that
  subagent's SubagentStop, which it checks as the end of the pass that ran, its Result first, then
  its Steps, and then ties the resume's Start to the subagent.
- A subagent stopped by TaskStop: the guard ends its Start with no Result, and gives its start due
  again.
- A command of another skill of the plugin typed while a subagent runs: the guard starts that
  skill's Run beside the first. Each Run holds to its own Routes, and the main conversation's calls
  to each Run's Rules. The main conversation's Stop stops while a start of either Run is due.
- The plugin's command typed again once its Run ended: the guard adds a new Run, as the ended Run's
  Routes start no more.
