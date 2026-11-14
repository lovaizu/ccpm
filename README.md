# `ccpm`

Claude Code plugin marketplace for lovaizu projects.

## Plugins

- **[Rn](./plugins/rn/README.md)**—rn makes what you ask for, such as a document, code, or a plugin, so that the people it's for can use it for what they're after. It asks you one point at a time, only what's yours, and leaves one draft pull request for you to merge.
- **[Lane](./plugins/lane/README.md)**—Lane lets an AI notice when it drifts from the steps your plugin gives it. Lane shows it the right way, so it finds its way back at full speed with no one watching each move.

## Install

Add the marketplace once, then install any plugin from it:

```console
> /plugin marketplace add lovaizu/ccpm
> /plugin install rn@ccpm
```

## Building the plugins

Each plugin's architecture and tests are in [`dev/`](./dev/README.md), outside the folder that Claude Code installs.
