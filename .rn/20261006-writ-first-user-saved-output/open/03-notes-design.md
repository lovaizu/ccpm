Design points to fix, from 02-report-proposal.md, waiting for writ.

- A1, writ/docs/design.md:82: every path under `.claude/projects` named anywhere in the call is
  taken, in a Bash command too, whatever the word around it, such as `F=<path>` or a quoted path,
  and the call is let through only when each one is the first user's own saved output.
  - Why: the call stopped in #36 was `F=<saved path>; wc -l $F; grep -n FAILED $F; ...; cd <repo> &&
    git status --short`; read as single words, the path behind `F=` is missed, and a path left
    unread either stops the first user's own read or lets another file through.
- A1, writ/docs/design.md:82, the last sentence: what the rule rests on is now three runs of the A1
  scene with `writ:first-user` itself as a subagent on Claude Code 2.1.291, in each of which its own
  record quoted the saved path in the `<persisted-output>` wrapper before the read.
  - Why: the sentence still names one trial with a general-purpose subagent, which shows less than
    is now known.
