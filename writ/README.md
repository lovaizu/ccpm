# writ

With writ, Claude Code writes documents, such as a README, a design document or a prompt, that
their reader understands in one reading, so you can hand them on without reading them over. It is
for anyone who has Claude Code write documents, not code, for someone else to read.

## Example

You have a small command-line tool that tidies CSV files, with notes on it in `docs/notes.md`, and
you want its README. In Claude Code you call `/writ:up`. writ keeps a checklist for each kind of
document; each item of it is one thing a good document of that kind gives its reader, and writ
asks, writes and reports by those items. Below, what you type follows `>`, and what writ says
follows `●`.

```console
> /writ:up Write the README of this tool

● I'll write it to the checklists for every document and for READMEs.
  Who reads it? I take it as developers who find the tool on GitHub and have messy CSV files.
  Is that right?

> Yes.

● What does the tool give them that tidying the file in a spreadsheet does not? Your notes do not say.

> It tidies a whole folder in one command, and keeps the originals.

● I'll write it to README.md, from docs/notes.md. Is that right?

> Yes.

● Writing README.md now. Another AI will read it as such a developer, and it will be checked
  against the checklists. I'll report once every item is met.

● Which license is the tool under? Your notes do not say.

> MIT

● README.md is written, and every item of the two checklists is met. You can hand it on as it is.

  Every document
    ✅ B-1 What it covers: lines 1-4
    ✅ B-2 The picture as meant: lines 1-30
    (every item gets a line the same way)
  README
    ✅ B-1 What they gain: line 3
    ✅ B-3 Why this one: lines 5-8
    (every item gets a line the same way)
```

A question only you can answer, such as the license, comes while the writing goes on. To check an
item, open README.md at its lines. Besides the document, writ leaves a `.turn/` folder in your
repository, with each draft and its reading; open it if you want, or leave it out of your commits.

### A document you already have

Name it: `/writ:up docs/typing-guide.md`. writ asks only what the document and your repository do
not tell. What the document says is the material, and writ makes it again to the checklists, so its
wording, its order, and parts its reader does not need may change. Commit it first: writ writes over
it, and git keeps what it was and shows what changed.

### A kind writ has no checklist for

```console
> /writ:up Write the release notes for 1.4

● I have no checklist for release notes. Which do you want?
  1. Write them to the checklist for every document alone.
  2. First make a checklist for release notes with you, then write them to it.

> 2
```

Choose 1 for a one-off, and 2 for a kind you will write again. With 2, writ asks what release notes
are for in your team, makes the checklist against writ's
[checklist for checklists](references/essentials/essentials.md), puts it at
`.writ/checklists/release-notes.md`, and writes the release notes to it. Next time, writ finds it
there; commit it, and your team writes to the same checklist.

## Why writ

Asking Claude alone also gets you a document. What writ adds:

- Claude alone fills what it does not know with guesses. writ asks you, one question at a time,
  only what an item of the checklists needs and your request and repository do not tell, and puts
  what it can work out to you to confirm.
- Claude reading its own work reads as the writer, and misses where a newcomer trips, as people do
  with their own writing. Before you get the document, another AI that does not know your
  conversation reads it as its reader, and what it could not take from it is written again.
- You judge the document from the report, item by item, with the lines that meet each, instead of
  reading it all over.
- For a kind of document writ has no checklist for, it makes one with you, and uses it from then on.

## Requirements

- Claude Code: writ runs inside it.
- A git repository, Python 3.9 or later as `python3`, and jq. writ has another plugin,
  [turn](../turn/README.md), do the writing, the reading and the checking, and turn needs them. Its
  [Requirements](../turn/README.md#requirements) say why.

## Installation

In Claude Code, add the marketplace once, then install writ:

```console
> /plugin marketplace add lovaizu/ccpm
> /plugin install writ@ccpm
```

This also installs turn, from the same marketplace, so you install nothing more for it.

Then call `/writ:up` as in the [Example](#example), for a document of your own.

## Documentation

- The checklists writ keeps: [every document](references/essentials/doc.md),
  [README](references/essentials/readme.md), [design document](references/essentials/design.md),
  [prompt](references/essentials/prompt.md), and
  [checklists](references/essentials/essentials.md)
- [Changelog](CHANGELOG.md)

## License

[MIT License](../LICENSE)
