# ccpm

Claude Code plugin marketplace for lovaizu projects.

## Plugins

- **[rn](./rn/README.md)** — *Right Now.* Give a goal, roughly; it works out what you really want, carries the work through, and calls you back only for decisions that are yours.
- **[writ](./writ/README.md)** — Documents that read as if a person wrote them for their reader, handed on without rereading.
- **[turn](./turn/README.md)** — With turn, Claude Code can make any work, such as a document, a prompt or code, that passes your checklist: another AI reads it as the one it is for, and what does not pass yet is made again.

## Install

Add the marketplace once, then install any plugin from it:

```console
> /plugin marketplace add lovaizu/ccpm
> /plugin install rn@ccpm
```

## Building the plugins

Each plugin's design, tests and trials are in [`dev/`](./dev/README.md), outside the folder that is installed.
