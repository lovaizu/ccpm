# Lane's test gaps

This page is for whoever makes Lane's architecture and its cases. It names each place where Lane's
cases, in `dev/lane/tests/`, can't follow [the architecture](../architecture.md) or its skeleton in
`plugins/lane/`.

- S11: no record shows the main conversation's events after a Stop that a hook stops, as each
  record's Stop holds `stop_hook_active` false, so the cases of a turn's end that Lane stops, and of
  a subagent's end that reaches the main conversation before its next Stop, play that Stop by the
  record of a first Stop, `claude-code-2.1.322-send-message.jsonl`'s `the main conversation stops`.
- S4: a command that writes by a redirect, such as `grep word > file`, a part after a lone `&`, and
  a command inside `$(...)` aren't held to the step's commands, as Lane splits a command only at
  `;`, `|`, `&&`, and a newline outside quotes. A diff of the files can't take that place, as it
  doesn't say which role wrote a file while subagents write at the same time. No case covers them
  until a run shows an AI writing so.
