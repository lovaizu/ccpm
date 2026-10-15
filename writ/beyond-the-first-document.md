# Beyond the first document

What writ does past the first document the [README](README.md) shows: making a document you already
have again, and writing a kind of document writ has no checklist for.

## A document you already have

Name it: `/writ:up docs/typing-guide.md`. writ makes it again to the checklists, so its wording, its
order, and parts its reader does not need may change. Commit it first: writ writes over it, and git
keeps what it was.

## A kind writ has no checklist for

For a kind writ has no checklist for, such as release notes, writ asks which you want:

```console
> /writ:up Write the release notes for 1.4

● I have no checklist for release notes. Which do you want?
  1. Write them to the checklist for every document alone.
  2. First make a checklist for release notes with you, then write them to it.
```

Choose the first for a one-off, and the second for a kind you will write again. With the second,
writ makes the checklist with you against its [checklist for checklists](checklists/checklist.md),
puts it at `.writ/checklists/release-notes.md`, and finds it there next time; commit it, and your
team writes to the same checklist.
