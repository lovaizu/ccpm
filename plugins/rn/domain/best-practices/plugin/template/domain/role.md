# `<role>`

You `<do what>`. You're done when `<what holds at the end>`.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<role>`: the role's name, as its entry gives it.
> - `<do what>`, `<what holds at the end>`: what the role has to do, and what a machine
>   can see once it's done, such as a check that gives 0, so the role knows when to end.
> - The part holds no steps of the work. The practices of the best practice below are its steps.
>   The steps adapter of the plugin's proposal, in `.lane/`, gives them to the guard, which holds
>   the role to them one by one. Steps copied here would drift from them.
> - A plugin with no roles, such as Lane, leaves out this file and the role's two schemas,
>   `domain/role-in.schema.json` and `domain/role-out.schema.json`.

## What you're given

You start with one JSON line of your run values, `<value>`, in the form of
`${CLAUDE_PLUGIN_ROOT}/domain/<role>-in.schema.json`. A name in braces, such as `{<value>}`, stands
for your run value of that name: put the value in its place in a command.

The main conversation may resume you with a message whose first line is `The person's answer, word for word:`. The rest
holds the person's answer to your last point.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<value>`: each run value, such as the path of the file the role writes. The guard limits the
>   role's calls to these values.
> - The second paragraph: only for a role that ends with a point for the person.

## The best practice you use

`<best practice>`: `<intents>`.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT: `<best practice>`, `<intents>`: the path of the best practice the role
> works by, such as `${CLAUDE_PLUGIN_ROOT}/domain/best-practices/<kind>/best-practice.json`, and the
> intents whose practices it carries out, such as Q1 to Q4. The best practice is of the kind meta,
> and passes before the plugin starts. The role takes each of those practices as a step of its
> work.

## What you give

End by giving one of `<results>` with its command, which `${CLAUDE_PLUGIN_ROOT}/domain/<role>-out.schema.json`
gives. `<when each>`.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT: `<results>`, `<when each>`: each fixed word the role ends with, such as
> `asks` for a point to the person and `done`, and when it gives each. The routes choose what
> comes next by this word.
