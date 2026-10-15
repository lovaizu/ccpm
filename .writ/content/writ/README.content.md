# What writ's README says

## readme

### B-1: What they gain
- writ is a plugin with which Claude Code makes work for someone else, such as a README, a design
  document, a prompt, or code and its tests, that its reader understands in one reading, so you can
  hand it on without reading it over.

### B-2: Who it is for
- Anyone who has Claude Code make such work.

### B-3: Why this one
- Asking Claude alone also gets you a document. What writ adds:
- Claude alone fills what it does not know with guesses. writ asks you, one question at a time, only
  what the checklists need and your request and repository do not tell, each with a recommended
  answer, and puts what it can work out to you to confirm.
- Claude reading its own work reads as the writer, and misses where a newcomer trips. Before you get
  the document, another AI that does not know your conversation reads it as its reader, and what it
  could not take from it is written again.
- You judge the document from the report: first what writ decided for you, each with its ground,
  then each item of the checklists with the lines that give it, instead of reading it all over.

### B-4: Using it on their own work
- The situation: you have a small command-line tool that tidies CSV files, with notes on it in
  `docs/notes.md`, and you want its README.
- writ keeps a checklist for each kind of document: a list of items, each one thing a good document
  of that kind gives its reader.
- What you type in Claude Code: `/writ:up Write the README of this tool`.
- What writ says and asks, in this example, with what you type after `>` and what writ says after
  `●`:
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
- writ asks what it needs before it writes, so once it says it is writing, you can leave it at work;
  a question only you can answer that shows up only in the writing comes at the end, with the
  report.
- To check an item, open README.md at the lines the report gives for it.

### B-5: Started from the README alone
- Installing: in Claude Code, add the marketplace once with `/plugin marketplace add lovaizu/ccpm`,
  then install writ with `/plugin install writ@ccpm`. This also installs turn.
- Then call `/writ:up` as in the example, for a document of your own.

### B-7: Terms of use
- MIT License (`../LICENSE`).

### B-9: Why each requirement is needed
- Claude Code: writ runs inside it.
- A git repository, Python 3.9 or later as `python3`, and jq: writ has another plugin, turn
  (`../turn/README.md`), do the writing, the reading and the checking, and turn needs them.

### F-1: Under Documentation
- Beyond the first document (`beyond-the-first-document.md`): a document you already have, and a
  kind writ has no checklist for.
- The checklists writ keeps: every document (`checklists/doc.md`), README (`checklists/readme.md`),
  design document (`checklists/design.md`), prompt (`checklists/prompt.md`), code and its tests
  (`checklists/code.md`), and checklists (`checklists/checklist.md`).
- The changelog (`CHANGELOG.md`): what changed in each version.

## readme: Usability

### U-1: Nothing to learn of the product's inside
- The only part named is turn, the plugin writ installs with and has do the writing, reading and
  checking; the reader sees it installed.

## doc

### B-12: Every term known
- A checklist: a list of items, each one thing a good document of that kind gives its reader.
- The report: what writ decided for you, each with its ground, then each item with the lines that
  give it.

### B-13: One name for each thing
- "The document" names what writ makes; "the reader" names the person the document is for, in the
  example "the developer"; "another AI" names the one that reads the document in the reader's place.
