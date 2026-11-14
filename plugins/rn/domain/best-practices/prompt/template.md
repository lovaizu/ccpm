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
>   has finished, and what lies outside its task.

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
>   it ends. It gives either the rules the step needs, each with its reason, or the script that does
>   the step and how to run it.

## Output

`<output>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<output>`: what the AI hands back, in what form, and to whom.

