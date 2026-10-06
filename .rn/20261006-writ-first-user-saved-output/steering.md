---
rn: 0.9.0
pr: 
status: running
artifact-language: English
conversation-language: Japanese
readme: writ/README.md
design: writ/docs/design.md
verification: writ/docs/verification.md
---

# Goal

Issue #36: writ's first-user history check stops a first user reading its own saved command output.
When a `writ:first-user` runs a Bash command whose output is too large, Claude Code saves it under
`~/.claude/projects/<project>/<session>/tool-results/`, and the check, which blocks any path under
`/.claude/projects`, stops the first user from reading it, so it spends a step finding another way.

# Acceptance criteria

## Attractive quality

## Must-be quality

# Assumptions

# Rules

# Tasks

### [ ] #1: Plan sign-off
### [ ] #2: Design sign-off

# Not yet specified
