# Lane's test gaps

This page is for whoever makes Lane's architecture and its cases. It names each place where Lane's
cases, in `dev/lane/tests/`, can't follow [the architecture](../architecture.md) or its skeleton in
`plugins/lane/`. Every integration case also waits for the double of Claude Code, as
[the skeleton's gaps](../skeleton-gaps.md) say.

- S2: no record shows a Grep or a Glob that reaches a file never to read, so no case holds them.
  Each case waits for its record, made by `dev/tests/recorder/`.
- S10 and Route: `log`'s rules route after `/log:up`, the command that called the run. At
  `/log:up` typed after /compact, [Claude Code's states](../claude-code-states.md) would make the
  writer due again, as `claude-code-states.md:96-97` say "A Route that goes after the command makes
  its starts due in place of those before." S10 draws the reviewer due, as `architecture.md:147-148`
  say "the run record holds the run, not ended" and "reads where the run stands." The cases follow
  S10: `routes.due` leaves the starts as they stand at the command that called the run, given
  again. Neither document says which holds.
