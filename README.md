# ccpm

Claude Code plugin marketplace for lovaizu projects.

## Plugins

- **[rn](./rn/README.md)** — *Right Now.* Give a goal, roughly; it works out what you really want, carries the work through, and calls you back only for decisions that are yours.
- **[writ](./writ/README.md)** — Documents that read as if a person wrote them for their reader, handed on without rereading.
- **[turn](./turn/README.md)** — Have Claude Code make any work, such as a document, a prompt or code, and get it back already read by another AI as the person it is for, made again where that reader could not find what it needed.

## Install

Add the marketplace once, then install any plugin from it:

```console
> /plugin marketplace add lovaizu/ccpm
> /plugin install rn@ccpm
```

## Building the plugins

Each plugin's design, tests and trials are in [`dev/`](./dev/README.md), outside the folder that is installed.
