# ccpm

Claude Code plugin marketplace for lovaizu projects.

## Plugins

- **[rn](./plugins/rn/README.md)** — Carries work that takes days from your rough words to a pull request ready to merge; you decide what you really want, how it is built and whether the result is it, and nothing else.
- **[lane](./plugins/lane/README.md)** — lane lets an AI notice when it drifts from the steps your plugin gives it, and tells it the right way, so it finds its way back at full speed with no one watching each move.
- **[turn](./plugins/turn/README.md)** — With turn, each step of your plugin has AI make its work, such as a document or code, until it passes the step's checklists: an AI that did not make it reads it first as the one it is for, and what does not pass yet is made again.

## Install

Add the marketplace once, then install any plugin from it:

```console
> /plugin marketplace add lovaizu/ccpm
> /plugin install rn@ccpm
```

## Building the plugins

Each plugin's architecture, tests and trials are in [`dev/`](./dev/README.md), outside the folder that is installed.
