# `<name>`

## Role

`<role>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<name>`: the role's name, such as `Generator`.
> - `<role>`: what the AI reads first: who it is and the one job it's accountable for, in one
>   sentence, where its job ends and another role's begins, and why the role exists, as N3 says,
>   with what the user decides and the AI judges, as N7 says. The entry that starts
>   the prompt, such as `agents/<role>.md`, holds its name, description, and tools, in the form
>   Claude Code fixes.

## Steps

`<steps>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<steps>`: the steps, in the order the AI takes them. Each step gives its purpose and intent:
>   the result that holds when it ends, what it's for, and the question the AI thinks through
>   there. Beside them, a step holds only the plugin's own rules, each with its reason, such as the
>   script that does a step with one right result, and the facts the AI can't find on its own, such
>   as where its inputs lie, as N4, N6, and N9 say.
> - Where some runs take steps that others don't, one step names each kind of run and gives each
>   its own steps, as N5 says.

## Output

`<output>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<output>`: what the AI hands back, in what form, and to whom, with the intent from which the AI
>   writes each message and each claim, which N14 gives for messages and N15 for claims.
