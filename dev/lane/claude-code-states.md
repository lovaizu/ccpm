# Claude Code's states that Lane's guard meets

This document lists each state of Claude Code in which Lane's guard places a hook event on its Run,
its Start, and its role, by the rule of the guard in [the architecture](architecture.md#components):
a Run by `session_id`, the main conversation by an event with no `agent_id`, and a Start and its role
by the `agent_id` that the PostToolUse of its Agent call ties to it. Each state names the events
that Claude Code sends, what the guard places them by, and the records in
[`dev/tests/recorded/`](../tests/recorded/) that show them, as `<file>:<lines>`. The events change
with each version of Claude Code, so the compatibility test of the architecture's Test strategy
checks them on each new version, and this list changes with the records.

## The states that the main use and rn bring about

| State | Events, in order | What the guard places them by | Records |
|---|---|---|---|
| The main conversation's calls in a Run | PreToolUse, then PostToolUse or PostToolUseFailure, and Stop at the end of a turn, each with no `agent_id` and no `agent_type`. | The Run of the event's `session_id`, and the main conversation by the missing `agent_id`. | `claude-code-2.1.322.jsonl:19-20` |
| A subagent started in the background | The main conversation's PreToolUse of Agent, then SubagentStart and the PostToolUse of Agent in either order, the PostToolUse naming the subagent as `tool_response.agentId`; the subagent's calls and SubagentStop, each with its `agent_id` and `agent_type`; and its end reaching the main conversation as a UserPromptSubmit of a `<task-notification>`, with a new `prompt_id`. | The Start that the guard let through at the PreToolUse, tied to the `agentId` at the PostToolUse of the same `tool_use_id`, as Lane hooks no SubagentStart, and each later event by its `agent_id`. | `claude-code-2.1.322.jsonl:10-18`, and SubagentStart after the PostToolUse in `claude-code-2.1.325-skill-command-while-subagent.jsonl:6-8` |
| A background subagent that runs on through a later prompt | The subagent's calls and SubagentStop after the main conversation's Stop and after a later prompt, each with the `prompt_id` of that later prompt. | The subagent's `agent_id`, never the `prompt_id`. | `claude-code-2.1.325-skill-command-while-subagent.jsonl:12-21` |
| Several subagents at once, two of one role among them | One assistant message's two Agent calls, each with its PreToolUse, SubagentStart, and PostToolUse before the next call's PreToolUse; two `agent_id`s of the same `agent_type`; their ends in either order. | Each Start tied at the PostToolUse of its own Agent call, so two Starts of one role never wait to be tied at once. | `claude-code-2.1.325-two-subagents.jsonl:5-25`, `:30-50`, and `:55-75` |
| A subagent resumed by SendMessage | After its end: the main conversation's PreToolUse of SendMessage with `to`, its PostToolUse with `resumedAgentId`, SubagentStart of the same `agent_id`, and a later end. To a subagent that runs: the PostToolUse says the message is queued, and the subagent's SubagentStop comes, then SubagentStart of the same `agent_id`, with no `<task-notification>` between. | The subagent's `agent_id`, which keeps its Start; a resume that a Route lists counts as a Start of that subagent at its PreToolUse. | `claude-code-2.1.322-send-message.jsonl:11-16`, and a queued message in `claude-code-2.1.322-subagent-of-subagent.jsonl:5-8` |
| `/compact` | PreCompact, a SubagentStop of the summary with an `agent_id` that no start named and an empty `agent_type`, SessionStart with `source` `compact`, and PostCompact, each with the same `session_id`; a subagent that runs goes on, with the compaction's `prompt_id`. | The same `session_id`, so the Run goes on; the summary's end lies outside the Run, as no Start ties its `agent_id`. | `claude-code-2.1.322-compact.jsonl:5-8`, and with a subagent running `claude-code-2.1.325-compact-while-subagent.jsonl:10-17` |
| A Run picked up in a new conversation | SessionEnd, then SessionStart with a new `session_id` and `transcript_path`. | The new `session_id`, which has no Run, so the guard picks the Run up from the kept results, as S7 draws. | `claude-code-2.1.323-worktree.jsonl:14-15` |
| EnterWorktree | From the PostToolUse of EnterWorktree on, each event's `cwd` and `transcript_path` lie in the worktree, the `session_id` stays, and each hook's `CLAUDE_PROJECT_DIR` stays the root. | The `session_id`, never the `transcript_path`, so the Run goes on in the worktree. | `claude-code-2.1.323-worktree.jsonl:5-12` and `:21-30` |
| A skill typed by a person | UserPromptSubmit, then UserPromptExpansion with `command_name` and `command_args`. | The `command_name`, which starts a Run that a person called. | `claude-code-2.1.322.jsonl:8-9` |
| A skill called by the Skill tool | PreToolUse and PostToolUse of Skill with `tool_input.skill` and `args`, and no UserPromptExpansion; a skill that sets `disable-model-invocation: true` is refused before any hook. | `tool_input.skill`, which starts a Run that an AI called. | `claude-code-2.1.322-skill.jsonl:3-4`, `claude-code-2.1.323-skill-command.jsonl:16` |

## Rare states

In each, Lane does what its line says, and never holds a call to the rules of another Run.

- Two conversations in one repository: each `session_id` has its own Run, and neither Run's lanes
  hold the other conversation's calls.
- A subagent started by a subagent: the guard stops the start, as only the main conversation starts
  the roles. `claude-code-2.1.322-subagent-of-subagent.jsonl:2-4` shows the events.
- A subagent's SendMessage to another subagent: the guard lets it through as talk that moves no Run,
  and the subagent it reaches stays on its own Start.
- A subagent in the foreground: no role's subagent runs there, as `lay.py print` refuses a role
  whose file doesn't set `background: true`; any other's events carry an `agent_id` that no Start
  ties, and lie outside the Run. `claude-code-2.1.323-worktree.jsonl:23-28` shows the events.
- A subagent stopped by TaskStop: no SubagentStop comes, and its `<task-notification>` says
  `killed`, so its Start runs no more with no Result, as S5 draws.
  `claude-code-2.1.323-task-stop.jsonl:9-15` shows the events.
- `/clear`, and a conversation resumed by `--resume`: the guard places each event by the
  `session_id` that it carries, so a new one starts no Run until the plugin's skill is called, and
  the same one goes on with its Run.
