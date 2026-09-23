# Push and review (ccpm)

How changes reach the user: pushed continuously, reviewed on the pull request — never held back in a
local branch, never gated in the console.

## Push on every change

- **Commit and push as soon as a change is made — do not ask first.** One task is one commit; the
  moment it is committed, push it. Never sit on local commits, and never ask "may I push?".
  - Rationale: the pushed branch is the shared truth. Work the user cannot see cannot be reviewed,
    built on, or recovered — pushing is what makes it real.

## Review happens on the PR

- **Conduct user review and approval on the pull request, not in the console.** Where a workflow
  defines a console review gate (e.g. the `rn` task user-review step), the gate still stands — it just
  moves to the PR: push the change, then point the user there.
  - Rationale: the PR renders diffs, long documents, and figures properly and keeps an addressable
    history; the console is too cramped to review a real artifact, and approving prose there means
    approving something the user never read in its rendered form.
