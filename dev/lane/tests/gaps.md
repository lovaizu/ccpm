# Lane's test gaps

This page is for whoever makes Lane's architecture and its cases. It names each place where Lane's
cases, in `dev/lane/tests/`, can't follow [the architecture](../architecture.md) or its skeleton in
`plugins/lane/`. Every integration case also waits for the double of Claude Code, as
[the skeleton's gaps](../skeleton-gaps.md) say.

- S2: no record shows a Grep or a Glob that reaches a file never to read, so no case holds them.
  Each case waits for its record, made by `dev/tests/recorder/`.
- S9 and the guard: `guard.start_made` stops each start of the plugin's subagents that isn't due,
  and each start by a subagent, and `place.place` gives a SendMessage as a `start`, while
  [Claude Code's states](../claude-code-states.md) let through, as talk that moves no Run, a resume
  that no order makes due and a subagent's message to another subagent. No interface gives that
  talk, so `test_a_resume_that_the_order_doesnt_make_due_goes_through_as_talk` and
  `test_a_subagents_message_to_another_subagent_goes_through_as_talk` follow the states, which no
  part holds.
- S10: [Claude Code's states](../claude-code-states.md) still have the guard pick a Run up in a new
  conversation from the kept results, and count a resume that a Route lists as a Start, while the
  architecture now gives a new conversation's starts due, and each resume due, from the plugin's
  order alone. The cases of S10 follow the architecture.
