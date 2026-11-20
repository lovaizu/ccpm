---
name: <role>
description: <plugin>'s role that <does what>. Started by <plugin>'s <command> alone.
tools: <tools>
background: true
---

`<Plugin>`'s folder is `${CLAUDE_PLUGIN_ROOT}`. Your part is in `${CLAUDE_PLUGIN_ROOT}/domain/<role>.md`: read it whole with the Read tool first, then carry it out with what you're given.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<role>`: the role's name. `lane/rules.json` and the order refer to the role by it.
> - `<does what>`: what the role does, and who starts it. Claude Code picks an agent by this text.
> - `<tools>`: only the tools the role's job needs, such as `Read, Grep, Glob, Write, Edit, Bash`.
> - `background: true`: keep it, because Lane follows only a subagent started in the background.
> - The body: keep these lines as they stand. Lane holds the role to reading its part whole by the
>   rule of the files its first step reads whole.
