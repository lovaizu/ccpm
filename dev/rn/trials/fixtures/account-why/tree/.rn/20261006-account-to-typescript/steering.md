---
rn: 0.9.0
pr: PR_URL
status: running
artifact-language: English
conversation-language: Japanese
readme: README.md
design: docs/design.md
verification: docs/verification.md
---

# Goal

Move src/account to TypeScript, so that users who registered with only an email address stop seeing
their name as "undefined undefined": it keeps bringing support inquiries, and the user wants them
gone.

# Acceptance criteria

## Attractive quality

## Must-be quality

# Assumptions

- Fact, reported by the user: users who registered with only an email address see their name as
  "undefined undefined", and support gets repeated inquiries about it.
- Fact, checked by running src/account/account.js: `displayName({})` returns "undefined undefined".

# Rules

# Tasks

### [ ] #1: Plan sign-off
### [ ] #2: Design sign-off

# Not yet specified
