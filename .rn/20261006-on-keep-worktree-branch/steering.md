---
rn: 0.9.0
pr: <the session's pull request URL>
status: running
artifact-language: English
conversation-language: Japanese
readme: rn/README.md
design: rn/docs/design.md
verification: rn/docs/verification.md
---

# Goal

When the current branch is not the default branch, has no commits of its own, and is at the latest
default branch, `/rn:on` works on it as it is and pushes it under the same name; it makes a new
branch only from the default branch itself, or when the current branch already holds other work.
The user starts a worktree for the work and expects the session there, so a second name for the
same work leaves the worktree and its branch apart and costs turns asking why and undoing it (#41).

# Acceptance criteria

## Attractive quality

## Must-be quality

# Assumptions

# Rules

# Tasks

### [ ] #1: Plan sign-off
### [ ] #2: Design sign-off

# Not yet specified

- What the deliverable needs, settled in the design.
