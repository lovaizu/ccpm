# Test cases

## E2E cases

`<e2e-cases>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<e2e-cases>`: one test for each key result, named by what the users get, with the key result
>   it supports, such as `KR1.1`, and its Given, When, and Then stated in the test, or no test
>   where the product holds a prompt, as the user's E2E run tries it whole.

## Integration cases

`<integration-cases>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<integration-cases>`: one test for each path, rule, decision, and handoff, named by what it
>   shows, with the element of the design it supports, such as `S3` or the rule's name, and its
>   Given, When, and Then stated in the test, or `None.` where the agreed testing names no
>   integration testing.

## Unit cases

`<unit-cases>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<unit-cases>`: one test for each variation that an interface's requirements name: each class
>   of what it takes and gives, each refusal, each bound, and each transition that the product's
>   use brings about where its result depends on what came before. Each test is named by what it shows, and
>   its Given, When, and Then stated in the test, its Then the whole of what the interface gives and
>   changes.

## Properties

`<properties>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<properties>`: one test for each invariant that the requirements state, as agreed,
>   of one kind of John Hughes's, with a generator of the inputs
>   that the product's use can bring. Each test is named by what holds, with the element it rests
>   on, and its Given any, When, and Then stated in the test, or `None.` where the agreed testing
>   names no property-based testing.

## Trace

`<trace>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<trace>`: the script that checks the trace, and how to run it, such as
>   `python3 <path> check <product>`, or `None.` where the agreed testing names no traceability.

## Gaps

`<gaps>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<gaps>`: a list, one gap a line, each naming the element of the design it bears on and what
>   the cases can't show because of it, such as `S5: no part holds the order of the runs, so no
>   case can show it`. It goes to whoever decided the parts, and holds only the gaps that the
>   design doesn't yet mend.
