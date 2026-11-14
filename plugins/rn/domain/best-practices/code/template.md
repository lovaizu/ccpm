# Code

## Manifest

`<manifest>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<manifest>`: what the maintainer needs to set the code up on a fresh machine and run its tests:
>   everything the code needs to run, with the versions it runs on, and how to run the tests.

## Module opening

`<module-opening>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<module-opening>`: for each module, one sentence on what this module alone decides, at the
>   place the maintainer meets first when they open the module.

## Interface

`<interface>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<interface>`: each name a module offers to others, with everything a caller needs to call it
>   without reading its body: the types it takes and gives, what it gives, what comes back when
>   there's nothing to give, what it expects of what it takes, what else it changes, and each way it
>   refuses a call.

## Body

`<body>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<body>`: the code under each interface that gives the behavior.

## Tests

`<tests>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<tests>`: tests of the specification's cases, one test for each case, so the maintainer can
>   tell which test checks which case and which code. Each test has a name that says the behavior it
>   checks, names the case one level up that it supports, and shows the situation, the action, and
>   what must be so.
