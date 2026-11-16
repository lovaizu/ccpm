# Lane's skeleton gaps

Each place where Lane's skeleton, in `plugins/lane/`, can't follow
[the architecture](architecture.md), for whoever makes the architecture.

- A role's Read in [Claude Code's states](claude-code-states.md), for the Read that S6 adds with the
  lines it read. A Read whose `tool_input` names no `limit` reads only as many lines as Claude
  Code's Read reads by default, so whether a Read read a file whole doesn't follow from `offset` and
  `limit`. The lines read come only from the Read's PostToolUse, whose fields no record shows yet.
  `place.ReadPosted` carries the first and the last line read, and where `place` takes them from is
  left open.
