# writ

With writ, Claude Code makes work for someone else, such as a README, a design document, a prompt,
or code and its tests, that its reader understands in one reading, so you can hand it on without
reading it over. It is for anyone who has Claude Code make such work.

## Example

You have a small command-line tool that tidies CSV files, with notes on it in `docs/notes.md`, and
you want its README. writ keeps a checklist for each kind of document: a list of items, each one
thing a good document of that kind gives its reader. In Claude Code you call `/writ:up`. Below, what
you type follows `>`, and what writ says follows `●`.

```console
> /writ:up Write the README of this tool

● I'll write it to the checklists for every document and for READMEs.
  Who reads it? I take it as developers who find the tool on GitHub and have messy CSV files.
  Is that right?

> Yes.

● What does the tool give them that tidying the file in a spreadsheet does not? Your notes do not say.

> It tidies a whole folder in one command, and keeps the originals.

● Writing README.md now, from docs/notes.md. Another AI will read it as such a developer, and it
  will be checked against the checklists; what is not met yet is written again, and I'll report
  once every item is met.

● README.md is written. One point is left for you: which license is the tool under? Your notes
  do not say, so the README names none yet.

> MIT

● README.md now names the MIT license, and every item of the two checklists is met. The report,
  with the lines that meet each item:

  Every document
    ✅ B-1 What it covers: lines 1-4
    (every item gets a line the same way)
  README
    ✅ B-3 Why this one: lines 5-8
    (every item gets a line the same way)
```

A question only you can answer, such as the license, comes at the end with any other such
question, so you can leave writ at work. To check an item, open README.md at the lines the report
gives for it.

### A document you already have

Name it: `/writ:up docs/typing-guide.md`. writ makes it again to the checklists, so its wording, its
order, and parts its reader does not need may change. Commit it first: writ writes over it, and git
keeps what it was.

### A kind writ has no checklist for

```console
> /writ:up Write the release notes for 1.4

● I have no checklist for release notes. Which do you want?
  1. Write them to the checklist for every document alone.
  2. First make a checklist for release notes with you, then write them to it.
```

Choose 1 for a one-off, and 2 for a kind you will write again. With 2, writ makes the checklist with
you against its [checklist for checklists](checklists/checklist.md), puts it at
`.writ/checklists/release-notes.md`, and finds it there next time; commit it, and your team writes
to the same checklist.

## Why writ

Asking Claude alone also gets you a document. What writ adds:

- Claude alone fills what it does not know with guesses. writ asks you, one question at a time,
  only what the checklists need and your request and repository do not tell, and puts what it can
  work out to you to confirm.
- Claude reading its own work reads as the writer, and misses where a newcomer trips. Before you get
  the document, another AI that does not know your conversation reads it as its reader, and what it
  could not take from it is written again.
- You judge the document from the report, item by item, at the lines it gives, instead of reading
  it all over.

## Requirements

- Claude Code.
- A git repository, Python 3.9 or later as `python3`, and jq: writ has another plugin,
  [turn](../turn/README.md), do the writing, the reading and the checking, and turn needs them.

## Installation

In Claude Code, add the marketplace once, then install writ:

```console
> /plugin marketplace add lovaizu/ccpm
> /plugin install writ@ccpm
```

This also installs turn. Then call `/writ:up` as in the [Example](#example), for a document of your
own.

## Documentation

- The checklists writ keeps: [every document](checklists/doc.md),
  [README](checklists/readme.md), [design document](checklists/design.md),
  [prompt](checklists/prompt.md), [code and its tests](checklists/code.md), and
  [checklists](checklists/checklist.md)
- [Changelog](CHANGELOG.md)

## License

[MIT License](../LICENSE)
