---
paths:
  - "plugins/**"
  - "dev/**"
  - ".claude-plugin/**"
---

# Plugin development in ccpm

**Build a plugin whose roles work together to make a work, such as rn, by [the plugin
guide](plugin-development.md). Build any other plugin, such as one of a hook and a script, as
simply as Claude Code's [plugin documentation](https://code.claude.com/docs/en/plugins) lets its
kind be built, with the LICENSE, README, CHANGELOG, and unit tests that any plugin of ccpm
carries.**

- Rationale: the guide is for plugins of roles, as it says at its start, so a plugin of another
  kind built by it takes on parts that serve no one, such as an architecture of roles it lacks.

**Until the user says yes, send nothing to a translator, a web API, or any service other than
Claude Code and the repository's git and GitHub. Fetching a public page to read it needs no ask.**

- Rationale: text sent out may hold what the user never meant to share, such as their email
  address. Claude Code and GitHub already hold the work, as the user runs the work through them.
