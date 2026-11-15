# Skeleton

## Module opening

`<module-opening>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<module-opening>`: for each module, one sentence on the one decision that this module alone
>   hides, at the place the developer meets first when they open the module, such as its docstring.

## Interface

`<interface>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<interface>`: for each arrow of Sequences that reaches the module, one name with the types it
>   takes and gives, and beside it what it takes, what it gives, what else it changes, and each way
>   it refuses, with a body that fails when called.

## Prompt

`<prompt>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<prompt>`: for each part that holds a prompt, its file with a description of when to use the
>   prompt and what it gives, and the form of what it takes and gives, such as a JSON Schema, with
>   no steps. Optional: only where a part holds a prompt.

## Gaps

`<gaps>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<gaps>`: a list, one gap a line, each naming the element of the architecture it bears on and
>   what the developers can't build because of it, such as `S3: the guard hands the record no kind
>   of data, so no interface carries it`. It goes to whoever makes the architecture, and holds only
>   the gaps that the architecture doesn't yet mend.
