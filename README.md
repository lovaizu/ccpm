# `ccpm`

Claude Code plugin marketplace for lovaizu projects.

## Plugins

- **[rn](./plugins/rn/README.md)**: rn makes what you ask for, such as a document, code, or a
  plugin, so that the people it's for can use it for what they're after, and asks you only the
  points that are yours.
- **[Lane](./plugins/lane/README.md)**: Lane lets an AI notice when it drifts from the steps your
  plugin gives it, and shows it the right way, so it finds its way back at full speed with no one
  watching each move.

## Install

Add the marketplace once, then install a plugin from it. Installing rn installs Lane with it.

```console
claude plugin marketplace add lovaizu/ccpm
claude plugin install rn@ccpm
```

## Building the plugins

Each plugin's architecture and tests are in [`dev/`](./dev/README.md), outside the folder that
Claude Code installs.
