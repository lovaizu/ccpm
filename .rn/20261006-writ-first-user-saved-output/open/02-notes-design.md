Design point to fix, from the More in 01-report-design-a1.md, waiting for writ.

- A1, writ/docs/verification.md "How a run goes": the trial starts `writ:first-user` as a subagent
  from a `claude -p` session with the Agent tool, as pith does, not as the main session
  (`claude -p --agent`), so its own record is `<session>/subagents/agent-<id>.jsonl` and the hook
  input carries its `agent_id`, as in use.
  - Why: started with `--agent`, the first user's record is the session's main record and no
    `agent_id` is given, a form writ never runs it in, so a pass there would not show A1 in use.
