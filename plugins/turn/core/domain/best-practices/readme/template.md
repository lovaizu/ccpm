# `<Product>`

`<Product>` is `<kind>` that `<what it does>`.

`<status>`.

`<Product>` is for you when `<your situation>`. With it, you `<gain>`.

`<message>`

![The usual way and the product](images/template-idea.svg)

`<excerpt>`

**Non-goals**

- `<Product>` does not `<expectation>`.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<kind>`: the kind of thing the product is, such as a command-line tool.
> - `<what it does>`: what the product does, in words the reader already uses.
> - `<status>`: where the product is not yet fit for use, such as a release still in development;
>   optional.
> - `<your situation>`: the work the reader wants done.
> - `<gain>`: what the reader can then do.
> - `<message>`: why the product solves the reader's problem where what they would do without it
>   does not, in a few plain sentences.
> - The figure: the deliverable's own at images/idea.svg, the product named in its alt text: the
>   usual way above the product, each as who does what to whom, for what the message says that a
>   picture shows better; optional.
> - `<excerpt>`: where the message names a difference in the work itself, a short excerpt of what
>   each way makes, from real runs; optional.
> - `<expectation>`: each thing a reader might expect of the product that it does not do; optional.

## Requirements

- `<requirement>`: `<check>` shows it.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<requirement>`: each thing that must be in place before installing.
> - `<check>`: a command whose output tells the reader they have it.

## Installation

```console
<command>
```

`<sign>`.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<command>`: each command that installs the product.
> - `<sign>`: what tells the reader that the installation worked.

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
>   were, in the form the reader meets them; one pair for each exchange up to the result.
> - `<language>`: the language of the text, such as console, python or json. A screen goes in place
>   of its code block, as an image taken from the run and kept in images/.

## How it works

![How the product works](images/template-how-it-works.svg)

- `<point>`.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - The figure: the deliverable's own at images/how-it-works.svg, the product named in its alt text:
>   the user, the product's parts and what they pass, each by its name, with what each does to
>   another.
> - `<point>`: each point a gain or a condition needs that the figure cannot show, in one sentence;
>   optional. A convenience, such as going on with a run that stopped, is no point here.

## Documentation

- [`<title>`](<path>): `<what it gives>`.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<title>`, `<path>`: each document a reader goes to next, by a path relative to the README, and
>   the place they get help, such as an issue tracker, by its URL; optional.
> - `<what it gives>`: for whom the document or the place is and what it gives them.

## License

[`<license>`](<path>)

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<license>`: the name of the license.
> - `<path>`: the license's full text.
