# Test implementation

## Report

`<report>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<report>`: the code that makes the report from the records, how to run it, and the decision
>   the report serves, such as `whether KR1.1 came closer`.

## Records

`<records>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<records>`: where each run keeps its records, and each record with what it holds, one line
>   each, such as `hooks.jsonl: each hook event with its time`.

## Checks of a run

`<checks>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<checks>`: one test for each thing a run as meant does, named by it, in the test code.

## Checks and judges

`<judges>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<judges>`: each judge's prompt with its one point, and the messages the developer marked
>   with their marks, beside the tests of the checks.

## Stages

`<stages>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<stages>`: one line for each stage that held, in order: its size, and the path of the records
>   that showed it held.
