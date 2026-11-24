# Prompt

## Description

`<description>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<description>`: what the host reads to choose the prompt for a request: a name that says what
>   the prompt does, and a description of what it does and the requests to use it for.

## Tools

`<tools>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<tools>`: the tools the AI may use. The prompt lists them where the host reads them, when the
>   host allows such a list. The host refuses any tool not on it.

## Goal

`<goal>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<goal>`: what the AI reads first in the body: what it's to achieve, for whom, how it knows it
>   has finished, what lies outside its task, and what the user decides and the AI judges, as N7
>   says.

## Context

`<context>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<context>`: what the AI needs and can't find or know on its own: the situation, its inputs and
>   where they lie, and the rules of this place.

## Steps

`<steps>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<steps>`: the steps, in the order the AI takes them. Each step names the result that holds when
>   it ends, what it's for, and the question the AI thinks through there. A step with one right
>   result names the script that does it and how to run it. A rule stands only where that intent
>   can't hold it, with its reason, as N6 says.
> - Where some runs take steps that others don't, one step names each kind of run and gives each
>   its own steps, as N5 says.

## Output

`<output>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<output>`: what the AI hands back, in what form, and to whom, with the intent from which the AI
>   writes each message and each claim, which N14 gives for messages and N15 for claims.

