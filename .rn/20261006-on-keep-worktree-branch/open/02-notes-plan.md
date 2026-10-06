Where the plan stands at the pause.

Agreed with the user:

- Artifacts in English; conversation in Japanese.
- The session runs in the worktree `.claude/worktrees/fix-branch` on its own branch
  `worktree-fix-branch`, which `/rn:on` kept instead of making a new one (the user renamed the
  worktree from `fix-fu` first). This session is itself a case of #41.

Under way:

- The intent question `01-notes-question.md` is drafted and not yet put to the user. Its use by a
  first user was stopped before it wrote a report: have a fresh first user take it up by the Question
  section of `conductor.md`, settle that report, then ask the user.

Found while working out the plan, still open:

- rn's checks refuse to start any agent while `steering.md` lacks an ID that the verification document
  refers to. In a session that changes `rn` itself, `rn/docs/verification.md` refers to `rn`'s own
  A1–A4 and M1–M7, so they were copied into `steering.md` to go on; whether this goal changes or adds
  to them, and whether that check itself should wait until the plan is agreed, is for the plan.
- Forms of the input still to check where the product runs: a worktree branch behind the latest
  default branch (main moved since the worktree was made), and a branch with commits of its own.
