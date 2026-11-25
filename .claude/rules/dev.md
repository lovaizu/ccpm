---
paths:
  - "plugins/**"
  - "dev/**"
  - ".claude-plugin/**"
---

# Plugin development in ccpm

**Build each plugin by [the plugin guide](../../dev/plugin-development-guide.md).**

- Rationale: the guide holds what every plugin of ccpm shares, so each is built the same way.

**Until the user says yes, send nothing to a translator, a web API, or any service other than
Claude Code and the repository's git and GitHub. Fetching a public page to read it needs no ask.**

- Rationale: text sent out may hold what the user never meant to share, such as their email
  address. Claude Code and GitHub already hold the work, as the user runs the work through them.
