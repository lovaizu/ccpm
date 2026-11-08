---
name: <role>
description: <plugin>'s role that <does what>. Started by <plugin>'s <command> alone.
tools: <tools>
background: true
---

`<Plugin>`'s folder is `${CLAUDE_PLUGIN_ROOT}`. Your part is in `${CLAUDE_PLUGIN_ROOT}/domain/<role>.md`, given to you as you start. Carry it out with what you're given.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<role>`: the role's name. The routes and the guard refer to the role by it.
> - `<does what>`: what the role does, and who starts it. Claude Code picks an agent by this text.
> - `<tools>`: only the tools the role's job needs, such as `Read, Grep, Glob, Write, Edit, Bash`.
> - `background: true`: keep it, because the guard counts a start only once its role ends.
> - The body: keep these lines as they stand. Before the role's first call, the guard gives the
>   role its whole part, with the folder filled in.
