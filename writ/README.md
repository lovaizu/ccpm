# writ

With writ, Claude Code writes a document that its reader understands in one reading and acts on: a
new one, or one you already have, made again. writ keeps checklists: one for every document, and one
for each kind, such as READMEs. Each item of a checklist says what a good document gives its reader.
With the document you get one report: for each item, whether the document meets it, and the lines of
the document that show it. You can hand the document on from that report, without reading it over.

writ is for anyone who has Claude Code write READMEs, design documents, prompts or other documents
for someone else to read. It takes documents only, not code.

What writ gives that asking Claude to write the document does not:

- It knows what a good document of each kind is, from that kind's checklist, and asks you, one
  question at a time, only what the checklist's items need and your request and repository do not
  tell.
- Another AI, who does not know your conversation, reads the document as its reader before you get
  it, and what that reader does not get from it is written again. Claude reading its own work reads
  as the writer, and can miss where a newcomer trips, as people do with their own writing.
- For a kind it has no checklist for, it can make one with you first, and uses it from then on.

writ has [turn](../turn/README.md), another plugin, do the writing, the reading and the checking.

## Example

You have a small command-line tool that tidies CSV files, with notes on it in `docs/notes.md`, and
you want its README. In Claude Code you call `/writ:up`. In the consoles below, what you type
follows `>`, and what writ says follows `●`:

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
```

Each question comes from an item of a checklist: the README checklist asks whether a newcomer can
tell why to choose this tool, so writ asks what it gives that other ways do not. What writ can work
out from your request and repository, it puts to you as a proposal, and you only say whether it is
right.

writ then hands the work to turn. turn works in rounds; in a round it does three steps: 1 write the
document, 2 have the other AI read it as the developer, 3 check from that reading which items are
met. After `To make:`, turn says what the document must let its reader do. A ❓ is a question only
you can answer; answer it when it shows, and writing goes on with your answer. A ⚠️ is something the
reader did not yet get, which starts a second round; ✅ means nothing is missing:

```console
Plan: 1 write → 2 read → 3 check   (once more if something is missing; two rounds at most)

Round 1
  1 write   To make: developers who find the tool on GitHub can tell what it saves them
            and tidy their own folder with it.
            ❓ Which license is the tool under? Your notes do not say.

> MIT

  2 read    Read as a developer who finds the tool on GitHub.
  3 check   ⚠️ Not yet: the developer can tell which Python version the tool needs.
Round 2
  1 write   To make: the same, now naming the Python version.
  2 read    Read again, as the same developer.
  3 check   ✅ Nothing missing.
done
```

Then writ reports. Under each checklist it used, named with its version so you can tell later which
checklist the document was checked by, the report lists each of that checklist's items by its ID
and title, marked ✅ when met, with the lines of README.md that show it:

```console
● README.md is written, and every item of the two checklists is met. You can hand it on as it is.

  Every document (version 0.1.0)
    ✅ B-1 What it covers: lines 1-4
    ✅ B-2 The picture as meant: lines 1-30
    (every item gets a line the same way)
  README (version 0.1.0)
    ✅ B-1 What they gain: line 3
    ✅ B-3 Why this one: lines 5-8
    (every item gets a line the same way)
```

To check an item, open README.md at its lines; you need not read the whole document.

### When an item is still not met

When an item is still not met after the second round, the report marks it ⚠️ with what the document
would need to meet it, and writ asks you what to do. Answer in the conversation, in your own words,
in one of three ways. Say what you want, such as "The readers are data analysts, not developers",
and writ has turn make the document again from your words. Say "Run it again", and turn makes it
again from the document as it is. Or say "Take it as it is", and writ stops there.

### Fixing a document you already have

To have a document you already have made again, name it: `/writ:up docs/typing-guide.md`. writ
reads it, asks only what the document and your repository do not tell, and makes it again from what
is there. Commit it first: writ writes over it, and git keeps what it was.

### A kind writ has no checklist for

```console
> /writ:up Write the release notes for 1.4

● I have no checklist for release notes. Which do you want?
  1. Write them to the checklist for every document alone.
  2. First make a checklist for release notes with you, then write them to it.

> 2
```

Choose 1 for a one-off. Choose 2 for a kind you will write again: writ asks what release notes are
for in your team, one question at a time, and has turn make the checklist against writ's
[checklist for checklists](references/essentials/essentials.md). It puts it at
`.writ/checklists/release-notes.md` in your repository, then writes the release notes to it. Next
time, writ finds it there. Commit it, and your team writes to the same checklist.

## Requirements

- Claude Code: writ runs inside it.
- turn: writ hands it every piece of writing and checking. Installing writ installs it.
- What turn needs: a git repository, Python 3.9 or later as `python3`, and jq. turn's
  [Requirements](../turn/README.md#requirements) say why each is needed.

## Installation

In Claude Code, add the marketplace once, then install writ:

```console
> /plugin marketplace add lovaizu/ccpm
> /plugin install writ@ccpm
```

Then call `/writ:up` as in the [Example](#example), with a document of your own.

## Documentation

- The checklists writ keeps: [every document](references/essentials/doc.md),
  [README](references/essentials/readme.md), [design document](references/essentials/design.md),
  [prompt](references/essentials/prompt.md), and [checklist](references/essentials/essentials.md)
- [Changelog](CHANGELOG.md)

## License

[MIT License](../LICENSE)
