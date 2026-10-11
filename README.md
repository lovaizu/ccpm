# ccpm

Claude Code plugin marketplace for lovaizu projects.

## Plugins

- **[rn](./rn/README.md)** — *Right Now.* Give a goal, roughly; it works out what you really want, carries the work through, and calls you back only for decisions that are yours.
- **[writ](./writ/README.md)** — Documents that read as if a person wrote them for their reader, handed on without rereading.
- **[turn](./turn/README.md)** — For plugin authors: hand one task to turn, and get back a deliverable someone has already used in the receiver's place, with what tripped them up fixed.

## Install

Add the marketplace once, then install any plugin from it:

```console
> /plugin marketplace add lovaizu/ccpm
> /plugin install rn@ccpm
```

## Building the plugins

Each plugin's design, tests and trials are in [`dev/`](./dev/README.md), outside the folder that is installed.
