# writ

With writ, Claude Code writes a document, such as a README, a design document or a prompt, that its
reader understands in one reading. writ keeps a checklist of what a good document of each kind
gives its reader, and with the document you get, for each item of it, whether the document meets
it. You can hand the document on from that report, without reading it over.

writ is for anyone who has Claude Code write documents for someone else to read. It writes
documents only, not code.

What writ gives that asking Claude alone does not:

- It asks you only what the checklist needs and your request and repository do not tell.
- Before you get the document, another AI that does not know your conversation reads it as its
  reader. Claude reading its own work reads as the writer, and misses where a newcomer trips.
- For a kind of document it has no checklist for, it can make one with you, and uses it from then
  on.

## Example

You have a small command-line tool that tidies CSV files, with notes on it in `docs/notes.md`, and
you want its README. In Claude Code you call `/writ:up`. Below, what you type follows `>`, and what
writ says follows `●`. Each question writ asks comes from an item of the checklists, and what it can
work out from your request and repository it puts to you to confirm. Its report lists, under each
checklist it used, named with its version, each item by its ID and title, with the lines of the
document that show it.

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

  Every document (version 0.1.0)
    ✅ B-1 What it covers: lines 1-4
    ✅ B-2 The picture as meant: lines 1-30
    (every item gets a line the same way)
  README (version 0.2.0)
    ✅ B-1 What they gain: line 3
    ✅ B-3 Why this one: lines 5-8
    (every item gets a line the same way)
```

To check an item, open README.md at its lines.

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
[checklist for checklists](references/essentials/essentials.md), and puts it at
`.writ/checklists/release-notes.md`. Next time, writ finds it there; commit it, and your team writes
to the same checklist.

## Requirements

- Claude Code: writ runs inside it.
- [turn](../turn/README.md), another plugin: writ has it do the writing, the reading and the
  checking. Installing writ installs it. It needs a git repository, Python 3.9 or later as
  `python3`, and jq; its [Requirements](../turn/README.md#requirements) say why each is needed.

## Installation

In Claude Code, add the marketplace once, then install writ:

```console
> /plugin marketplace add lovaizu/ccpm
> /plugin install writ@ccpm
```

Then call `/writ:up` as in the [Example](#example), for a document of your own.

## Documentation

- The checklists writ keeps: [every document](references/essentials/doc.md),
  [README](references/essentials/readme.md), [design document](references/essentials/design.md),
  [prompt](references/essentials/prompt.md), and [checklist](references/essentials/essentials.md)
- [Changelog](CHANGELOG.md)

## License

[MIT License](../LICENSE)
