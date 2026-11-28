# `ccpm`

Claude Code plugin marketplace for lovaizu projects.

## Plugins

- **[rn](./plugins/rn/README.md)**: rn makes what you ask for, such as a document, code, or a
  plugin, so that the people it's for can use it for what they're after, and asks you only the
  points that are yours.
- **[overnight](./plugins/overnight/README.md)**: overnight runs a piece of work in Claude Code while
  you're away, and resumes it by itself after the usage limit or an error stops it.

## Install

Add the marketplace once, then install a plugin from it.

```console
claude plugin marketplace add lovaizu/ccpm
claude plugin install rn@ccpm
```

## Building the plugins

Each plugin's architecture and tests are in [`dev/`](./dev/README.md), outside the folder that
Claude Code installs.
