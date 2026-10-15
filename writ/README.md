# writ

writ is a Claude Code plugin with which Claude makes work for someone else, such as a README, a
design document, a prompt, or code and its tests, that its reader understands in one reading, so you
can hand it on without reading it over. It is for anyone who has Claude Code make such work.

## Example

You have a small command-line tool that tidies CSV files, with notes on it in `docs/notes.md`, and
you want its README.

writ keeps a checklist for every document, and one for each kind of document: a list of items, each
one thing a good document gives its reader.

In Claude Code you type `/writ:up Write the README of this tool`. What follows is what writ says
and asks in this example, with what you type after `>` and what writ says after `●`:

```console
> /writ:up Write the README of this tool

● I'll write it to the checklists for every document and for READMEs.
  Who reads it? I take it as developers who find the tool on GitHub and have messy CSV files.
  Is that right?

> Yes.

● What does the tool give them that tidying the file in a spreadsheet does not? Your notes do not
  say.

> It tidies a whole folder in one command, and keeps the originals.

● Which license is the tool under? Your notes do not say, and the repository has no license file.
  I'd suggest MIT, the usual one for a small tool.

> MIT

● Writing README.md now, from docs/notes.md. Another AI will read it as such a developer, and it
  will be checked against the checklists; what is not met yet is written again. I'll hand it back
  with the report.

● README.md is written. The report:

  Decided for you
    The README names no other tool to compare with: your notes name none, and the comparison with
    a spreadsheet covers what a developer weighs.

  Every document
    ✅ B-2 The picture as meant: lines 1-4
    (every item gets a line the same way)
  README
    ✅ B-3 Why this one: lines 5-8
    (every item gets a line the same way)
```

writ asks what it needs before it writes, so once it says it is writing, you can leave it to run. A
question only you can answer that shows up only in the writing comes at the end, with the report.
To check an item, open README.md at the lines the report gives for it.

## Why writ

Asking Claude alone also gets you a document. What writ adds:

- writ asks you what it does not know, where Claude alone guesses.

  A guess reads as smoothly as a fact, so you would have to find it in the document yourself. writ
  asks only what the checklists need and your request and repository do not tell, so each answer
  settles a point the document would otherwise get wrong.

- The document is read in its reader's place before you get it, where Claude alone reads it as its
  writer.

  Claude reading its own document knows what it meant, and misses where its reader would trip.
  Another AI that does not know your conversation has only the document, as its reader will, so what
  it could not take from it is written again before it reaches you.

- You judge the document from the report, where with Claude alone you read it all over.

  The report sets out what writ decided for you and the lines that give each item, so you look at
  the document only where you doubt it.

## Requirements

- Claude Code, which writ runs inside.
- Your project kept in a git repository, Python 3.9 or later run as `python3`, and jq, the
  command-line JSON processor, run as `jq`.

  writ has another plugin, turn ([`../turn/README.md`](../turn/README.md)), do the writing, the
  reading of the document in its reader's place, and the checking against the checklists, and turn
  needs them.

## Installation

In Claude Code, add the marketplace once, then install writ. This also installs turn.

```console
/plugin marketplace add lovaizu/ccpm
/plugin install writ@ccpm
```

Then call `/writ:up` as in the example, for a document of your own.

## Documentation

- [Beyond the first document](beyond-the-first-document.md): a document you already have, and a kind
  writ has no checklist for
- [The checklist for every document](checklists/doc.md)
- [The checklist for READMEs](checklists/readme.md)
- [The checklist for design documents](checklists/design.md)
- [The checklist for prompts](checklists/prompt.md)
- [The checklist for code and its tests](checklists/code.md)
- [The checklist for checklists](checklists/checklist.md)
- [What changed in each version](CHANGELOG.md)

## License

[MIT License](../LICENSE)
