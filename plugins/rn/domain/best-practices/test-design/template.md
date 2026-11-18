# Test cases

## E2E cases

`<e2e-cases>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<e2e-cases>`: one test for each key result, named by what the users get, with the key result
>   it supports, such as `KR1.1`, and its Given, When, and Then stated in the test.

## Integration cases

`<integration-cases>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<integration-cases>`: one test for each path, rule, decision, and handoff, named by what it
>   shows, with the element of the architecture it supports, such as `S3` or the rule's name, and its
>   Given, When, and Then stated in the test.

## Unit cases

`<unit-cases>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<unit-cases>`: one test for each class of what an interface takes or gives, and one for each
>   transition that the product's use brings about where its result depends on what came before.
>   Each test is named by its class, or by its state and event, with the integration case it
>   supports, and its Given, When, and Then stated in the test.

## Trace

`<trace>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<trace>`: the script that checks the trace, and how to run it, such as
>   `python3 <path> check <product>`.

## Gaps

`<gaps>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<gaps>`: a list, one gap a line, each naming the element of the architecture it bears on and
>   what the cases can't show because of it, such as `S5: no part holds the order of the runs, so no
>   case can show it`. It goes to whoever makes the architecture, and holds only the gaps that the
>   architecture doesn't yet mend.
