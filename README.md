# ccpm

Claude Code plugin marketplace for lovaizu projects.

## Plugins

- **[Rn](./plugins/rn/README.md)** — Rn carries work that takes days from your rough words to a pull request ready to merge. You decide what you really want, how it is built and whether the result is it, and nothing else.
- **[Lane](./plugins/lane/README.md)** — Lane lets an AI notice when it drifts from the steps your plugin gives it. Lane tells it the right way, so it finds its way back at full speed with no one watching each move.
- **[Pin](./plugins/pin/README.md)** — Pin settles every fact and decision your plan needs before an AI starts to make it. It finds each fact itself and asks you only the decisions that are yours, one at a time.
- **[Turn](./plugins/turn/README.md)** — Turn makes a work you ask for, such as a README or a module of code, ready to use as it comes. It asks you only the decisions that are yours, and an AI that did not make the work judges it in its user's place.

## Install

Add the marketplace once, then install any plugin from it:

```console
> /plugin marketplace add lovaizu/ccpm
> /plugin install rn@ccpm
```

## Building the plugins

Each plugin's architecture, tests and trials are in [`dev/`](./dev/README.md), outside the folder that is installed.
