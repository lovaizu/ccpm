# Hook events after an Agent call's PreToolUse that fails or is denied

The question this answers is for `dev/lane/architecture.md` N13, S4: an Agent call that fails or is
denied after its PreToolUse, and the Start that the guard made for it.

Each record was made on Claude Code 2.1.327, by the recorder's `rec` plugin logging every hook
event, with `claude -p --model haiku --dangerously-skip-permissions`. The main conversation made
one Agent call with `run_in_background` set to true.

## Which hook events, with which fields, does Claude Code send after the PreToolUse of an Agent call that then fails?

The answer depends on how the call fails.

- The subagent type doesn't exist. The events are PreToolUse, then PostToolUseFailure, then Stop.
  PostToolUseFailure gives `tool_name` `Agent`, the call's `tool_use_id`, and `error`:
  `Agent type 'rec:nosuch' not found. Available agents: ...`. It also gives `is_interrupt` false
  and `duration_ms`, and no `agent_id`. No SubagentStart or SubagentStop comes. Source:
  `dev/tests/recorded/claude-code-2.1.327-agent-unknown-type.jsonl:5-7`.
- A permission rule denies the call, here `deny: ["Agent(rec:sleeper)"]` given by `--settings`: the
  same events. PreToolUse runs first, then PostToolUseFailure with the call's `tool_use_id` and
  `error`: `Agent type 'rec:sleeper' has been denied by permission rule 'Agent(rec:sleeper)' from
  flagSettings.`, then Stop. No PermissionDenied event, SubagentStart, or SubagentStop comes.
  Source: `dev/tests/recorded/claude-code-2.1.327-agent-denied-by-rule.jsonl:5-7`.
- A PreToolUse hook of another plugin denies the call, with `permissionDecision` `deny`, while the
  `rec` plugin's PreToolUse hook lets it through. The events are PreToolUse, then Stop. No
  PostToolUse, PostToolUseFailure, PermissionDenied, SubagentStart, or SubagentStop comes. The tool
  result that the model gets is `PreToolUse:Agent hook error: denier denies each Agent call`, with
  `is_error` true and the call's `tool_use_id`. Source:
  `dev/tests/recorded/claude-code-2.1.327-agent-denied-by-hook.jsonl:5-6`. The tool result is in
  that run's `stream.jsonl`, which the record doesn't keep.

## Does any event name the call's tool_use_id?

The answer depends on how the call fails.

- The call fails, or a permission rule denies it: yes. PostToolUseFailure names the same
  `tool_use_id` as the call's PreToolUse. Sources: line 5 and line 6 of the first two records.
- Another plugin's PreToolUse hook denies the call: no. No hook event after the PreToolUse names
  the call. The next event is the main conversation's Stop. Source:
  `dev/tests/recorded/claude-code-2.1.327-agent-denied-by-hook.jsonl:5-6`.

## What these records leave out

- A person denying the call at a permission prompt: `claude -p` shows no prompt, so no record
  holds it.
