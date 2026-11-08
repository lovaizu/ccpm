# `<Product>`

`<Product>` is `<kind>` that `<what it gives>`.

`<status>`.

`<Product>` is for you when `<your situation>`. With it, you `<gain>`.

**Non-goals**

- `<Product>` doesn't `<expectation>`.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<kind>`: the kind of thing the product is, such as a command-line tool.
> - `<what it gives>`: the one thing the product gives the reader, in words the reader already uses,
>   so that the sentence says in short what the product is.
> - `<status>`: where the product isn't yet fit for use, such as a release still in development, so
>   that the reader doesn't rest their work on it unaware. Leave it out where the product is ready
>   for use.
> - `<your situation>`: the work the reader wants done, so that a reader can tell whether they're
>   in it.
> - `<gain>`: the end the reader reaches with the product.
> - `<expectation>`: each thing a reader might expect of the product that it doesn't do, so that a
>   reader who needs it turns away before installing. Leave out Non-goals where there's none.

## Requirements

- `<requirement>`: `<check>` shows it.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<requirement>`: each thing that must be in place before installing.
> - `<check>`: a command whose output shows the reader they have it.

## Installation

```console
<command>
```

`<sign>`.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<command>`: each command that installs the product.
> - `<sign>`: what shows the reader that the installation worked.

## Walkthrough

At the end, you have `<result>`.

`<situation>`. You type:

```<language>
<input>
```

`<Product>` shows:

```<language>
<output>
```

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<result>`: what the reader has once the run ends.
> - `<situation>`: what the run starts from, in one sentence.
> - `<input>`, `<output>`: what the user gave and what the product showed in a real run, as they
>   were, in the form the reader meets them. One pair goes for each exchange up to the result.
> - `<language>`: the language of the text, such as console, python, or json. A screen goes in place
>   of its code block, as an image taken from the run and kept in images/.

## How it works

![The usual way and the product](images/template-problem.svg)

1. **`<problem>`.** `<how it goes away>`.

![How the product works](images/template-how-it-works.svg)

**`<doubt>`** `<how it does it>`.

[`<title>`](<path>)

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - The first figure: the deliverable's own, at images/problem.svg, with the product named in its
>   alt text. It lets the reader see at a glance that the problem goes away. The skeleton here is one such form: the
>   way the reader would do the work without the product on top, and the product below it, with the
>   problem left in the one and gone in the other.
> - `<problem>`, `<how it goes away>`: each problem the reader feels in the work, in their words,
>   and what the product does that makes it go away, in a sentence or two, so that the reader
>   pictures their own problem gone. A numbered list, each item's number the one the figure marks
>   it with, so the reader finds it on the figure.
> - The second figure: one for each doubt, followed by its paragraph. Each is the deliverable's own,
>   at images/how-<name>.svg, with the product named in its alt text. It shows at a glance how the
>   product does the doubted thing. The skeleton here is one such form: the user, the product's
>   parts and what they pass, with the lines that do it marked. One figure for several doubts shows
>   none of them at a glance.
> - `<doubt>`, `<how it does it>`: each point where a newcomer would ask whether the product can
>   really do that, and how the product does it, in a sentence or two, so that the reader believes
>   it before they try it. The doubt as the reader would ask it, in bold, opens the paragraph that
>   comes just after its figure, so it needs no letter or number.
> - `<title>`, `<path>`: the page that explains it further, where it needs a long sequence of
>   figures. Leave it out where the paragraph is enough.

## Documentation

- [`<title>`](<path>): `<what it gives>`.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<title>`, `<path>`: each document a reader goes to next, by a path relative to the README, and
>   the place they get help, such as an issue tracker, by its URL. Leave out Documentation where
>   there's none.
> - `<what it gives>`: for whom the document or the place is and what it gives them.

## License

[`<license>`](<path>)

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<license>`: the name of the license.
> - `<path>`: the license's full text.
