---
rn: 0.9.0
pr: 
status: running
artifact-language: English
conversation-language: Japanese
readme: rn/README.md
design: rn/docs/design.md
verification: rn/docs/verification.md
---

# Goal

Fix #43 and #44: rn's checks know which session runs rn and which agents it started, so its
conductor can answer other sessions and no other session is taken for the conductor; and the
conductor waits for every agent it starts before it goes on, however Claude Code runs the agent, the
same way in every conversation.

# Acceptance criteria

## Attractive quality

## Must-be quality

# Assumptions

# Rules

- Follow `.claude/rules/plugin.md` and `.claude/rules/final-check.md`.

# Tasks

### [ ] #1: Plan sign-off
### [ ] #2: Design sign-off

# Not yet specified
