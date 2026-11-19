# Lane's test gaps

This page is for whoever makes Lane's architecture and its cases. It names each place where Lane's
cases, in `dev/lane/tests/`, can't follow [the architecture](../architecture.md) or its skeleton in
`plugins/lane/`. Every integration case also waits for the double of Claude Code, as
[the skeleton's gaps](../skeleton-gaps.md) say.

- S2: no record shows a Grep or a Glob that reaches a file never to read, so no case holds them.
  Each case waits for its record, made by `dev/tests/recorder/`.
- S9 and Route: two runs of one plugin, such as a run of `log:up` and the run of `log:tag` started
  beside it, read the same `lane/rules.json`, so the routes of both go after `/log:retry`.
  `place.place` gives the command's `typed` move on "the run whose plugin's rules route after the
  command", and neither the architecture nor
  [Claude Code's states](../claude-code-states.md#what-the-guard-answers-in-each-single-behavior)
  say which of the two that is, so no case types such a command while two runs stand.
- S9 and Run: a command with no steps of its own typed once its run ended is a `typed` move of the
  ended run, as the rules still route after it, while the architecture's Run lasts "from its call
  until its routes start no more". `routes.due` gives the starts of the latest typed command, so the command would
  start the ended run's routes again. No part says whether it does, so no case types it then.
- S9 and Run: a command with no steps of its own typed where no run of the conversation has its
  plugin's folder, such as `/log:retry` as the first command of a new conversation, has no rules
  that Lane can read at its UserPromptExpansion, so `place.skill_call` gives it as a skill's call,
  and `guard.skill_called` adds a run of a skill whose rules give no steps. No part says what that
  run holds to, so no case types it then.
