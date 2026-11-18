# Lane's test gaps

Each place where Lane's test cases, in this folder, can't follow
[the architecture](../architecture.md) and the skeleton in `plugins/lane/`, for whoever makes the
architecture.

- S5 and claude-code-states.md, a role's Read, Grep, or Glob: no record in `dev/tests/recorded/`
  holds a Grep's or a Glob's events, so the double of Claude Code sends neither, and no
  integration case shows a Lane of reads_none stopping a Grep or a Glob. Only the unit cases of
  reads_none show it, by Calls of their own.
- S4, `CC->>G: the PostToolUse, with its agent_id`: the sequence draws no branch where the Agent
  call that the guard let through fails or is denied after its PreToolUse, and Lane hooks no
  PostToolUseFailure, so its Start stays untied and counts as running: the main conversation's end
  goes with the start still due, and the same start again is stopped. The cases
  `untied-as-its-call-failed` of `unit/test_guard_states.py` show it, marked xfail.
- S5 and claude-code-states.md, a subagent resumed by SendMessage while it runs: the resume is
  tied at its PreToolUse, and the SubagentStop of the pass before it names no call, so the guard
  checks that end against the resume's Start. Where a Route opened the resume, the end of the pass
  that gave its Result is stopped, as no Result came since the resume. No record holds a resume
  that a Route opens, queued to a subagent that runs, so no case shows it.
