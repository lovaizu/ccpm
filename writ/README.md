# writ

Have Claude Code write a README, a design document or a prompt through writ, and you get:

- A document its reader understands in one reading, and acts on once they finish.
- A document you can pass on as it is, without reading it over yourself.
- A final report you can judge the document from alone, without reading the whole document again.

## Why it comes back ready to pass on

Whoever wrote a document cannot read it again as someone who does not know the discussion, so reading it over, by you or by the AI that wrote it, does not show where its reader will trip.

Before writ returns a document, a separate AI that has seen nothing but the document, who reads it, and what they read it for, uses it in that reader's place. For a README it reads as a newcomer deciding whether to use the product; for a prompt it gives the prompt to an AI and runs it. It reports only what it took in and set out to do. writ lays that beside what the document should let its reader do, finds why the document came out away from it, and rewrites from that cause, not only at the spot where the reader tripped, so the same trip does not come back elsewhere.

What the document should let its reader do is settled with you before writing: who reads it, and what they must be able to do once they have read it. writ never makes this up. What only you can decide, such as a team rule no source states, comes back to you as a question instead of being covered with sentences that read either way.

## From your request to the finished document

1. You start writ with `/writ:up`, followed by what you want written or the document to fix.
2. writ settles with you who reads the document and what they must be able to do with it.
3. writ writes it, has it used in the reader's place, and rewrites it from what it learns, until it meets what it should be, a rewrite brings it no closer, or something only you can decide comes up.
4. You get the document and the final report. The report gives each point the document was measured on a Good, if the reader got what they should, or a More, with what they missed, and each with where in the document it rests. It names whatever still falls short, and asks you what only you can decide. Once you answer, writ goes on from there.

While a document is being tried, it is used in a copy of your repository inside a temporary folder that is deleted afterward, so your other work is left untouched.

## The kinds of document writ makes

Each kind has its own file of questions. writ writes a document to them, and the AI reading in the reader's place answers them from what it did, so a Good or a More says what happened to the reader, not whether the document looks right.

- [Every document](references/essentials/doc.md): the reader understands it in one reading and knows what to decide and do. These questions apply to every kind below as well.
- [README](references/essentials/readme.md): a newcomer takes in what they gain, decides whether to use the product, and starts using it.
- [Design document](references/essentials/design.md): those who build and maintain the product can tell which feature brings each of the README's benefits to the user, and whether a change fits the design.
- [Prompt](references/essentials/prompt.md): the AI that receives it acts toward its purpose even in situations the writer did not foresee. It is checked by running it, not by reading it.

Any other document, such as a setup guide or a migration plan, is written to the questions for every document alone.

## Adding a kind of document

When a kind of document needs questions of its own, such as release notes your developers read to decide whether to upgrade, ask for them with the same command:

```console
> /writ:up questions for release notes
```

writ makes the question file the way it makes a document, measured by [the file for question files](references/essentials/essentials.md): each question is worked back from what that kind's reader must get, can be answered only by using a real document of that kind as its reader would, and the file is tried on such a document before you get it.

The file is kept in your repository at `.writ/essentials/<kind>.md`, not inside writ, because installing or updating writ replaces its folder. From then on, writ uses it for documents of that kind as it uses its own.

## What you need

- [Claude Code](https://code.claude.com)
- Python 3.9 or later

    writ checks with it what passes between its steps.

- jq

    writ reads with it only the part it needs of what each step returns.

- A git repository

    The document is tried in a copy of the repository as it would be freshly cloned.

If one of these is missing, writ stops and tells you what to install, instead of skipping a check.

## Install

writ is in the plugin marketplace `lovaizu/ccpm`. In Claude Code, add the marketplace, then install writ:

```console
> /plugin marketplace add lovaizu/ccpm
> /plugin install writ@ccpm
```

writ hands each document to turn, a plugin from the same marketplace that carries one piece of work through making it, having it used and remaking it. turn is installed with writ.

## Your first document

In your repository, start writ with what you want written:

```console
> /writ:up a README for this repository, for developers deciding whether to use it
```

To fix a document you already have, name it instead:

```console
> /writ:up docs/setup.md
```

From there it goes as in [From your request to the finished document](#from-your-request-to-the-finished-document).

## License

MIT. The full text is in [LICENSE](../LICENSE) at the root of the repository.
