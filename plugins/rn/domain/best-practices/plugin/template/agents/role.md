---
name: <role>
description: <plugin>'s role that <does what>. Started by <plugin>'s <command> alone.
tools: <tools>
background: true
---

`<Plugin>`'s folder is `${CLAUDE_PLUGIN_ROOT}`. Your part is in `${CLAUDE_PLUGIN_ROOT}/domain/<role>.md`, given to you as you start. Take it on what you're given.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<role>`: the role's name, which the routes and the guard name it by.
> - `<does what>`: what the role does, and who starts it, as Claude Code picks an agent by it.
> - `<tools>`: only the tools the role's job needs, such as `Read, Grep, Glob, Write, Edit, Bash`.
> - `background: true`, as the guard counts a start once its role ends.
> - The body: these lines, kept as they stand, as the guard gives the role its part whole,
>   with the folder put in, before its first call.
