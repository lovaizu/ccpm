---
name: checklist
version: 1
made_from:
  usability: 1
---

# Checklist

A checklist is used by whoever makes a deliverable of one kind and whoever judges it. Answering its
items, the maker makes, in a way of their own, a deliverable that serves the purpose of whoever uses
the kind, nothing missing and nothing more; the judge tells, from it alone, whether a deliverable
serves it.

A checklist is drawn from that purpose: who uses a deliverable of the kind and what they achieve
with it. Its few items each ask one thing the purpose needs, as what the user gets, so
each is answered with the lines that give it; the ways a deliverable meets that thing are the signs
under the item, not items of their own. It is made from this file and `usability.md`, what any
reader needs: each point of `usability.md` the kind's user needs is put in the kind's own terms, as
an item or a sign under one, and a point the kind does not need is left out. The deliverable is
judged by its own checklist alone.

## Format

### F-1: Shape

Scope: whole

Does the checklist follow this template?

```markdown
---
name: <kind-of-deliverable>
version: <n>
made_from:
  checklist: <version of this file it was made from>
  usability: <version of usability.md it was made from>
---

# <Kind of deliverable>

<The purpose in one or two sentences: who uses it, and what they can then do>

<The idea the items rest on>

## Format

### F-1: Shape

Scope: whole

<The template the deliverable follows>

## Benefit

### B-1: <What the user gets>

Scope: <its part, each part or whole>

<Question answered yes or no, asking what the user gets>

Look for: <the signs a deliverable falls short of it; left out where the question needs none>

Why: <what goes wrong for the user without it>
```

Each item says where in the deliverable it is answered: `its part`, at the part or parts that give
it; `each part`, in every part of the deliverable on its own, a part being a section under a top
heading of a document, with the title and opening as one, or a file of code; `whole`, of the
deliverable at once, for what lies between its parts, such as one name for each thing. The items
answered at one part stand in the order of the template's parts, and those answered at each part
or over the whole after them. A kind that adds no part to a document's shape has no Format section.

Why: every checklist in the same shape lets a tool read any of them and gives the maker the purpose,
then the idea, then the shape, before the items, so each item is met inside what those already set;
an item met where its part comes is met as the deliverable is written.

### F-2: Version

Scope: its part

Is the `version` a whole number, `1` until the plugin that holds the checklist is first released,
and raised by one for each release after?

Why: a judgment names the text it was made by, and no draft between releases takes a number.

### F-3: Made from the current inputs

Scope: its part

Does `made_from` name the version of this file and of `usability.md` that stand now? This file
names `usability.md` alone, as it is made from itself.

Why: a checklist made from an earlier version of its inputs asks what they no longer ask, and the
version shows which checklists to make again when an input changes.

### F-4: Item IDs

Scope: whole

Is each item's ID its section's first letter and a number counted up within the section, such as
`B-2`, with no ID that a released version gave another item?

Why: a judgment names each item by its ID, and an ID named earlier always means the same item.

## Benefit

### B-1: User and purpose

Scope: its part

Can whoever makes or judges a deliverable of the kind learn, from the opening, who uses it, what
they then achieve, and the idea by which a deliverable of the kind serves that?

Why: every item is judged against the user and the purpose; a maker who knows only the items meets
each by its letter, and fits a guess to a case no item names.

### B-2: Each thing the purpose needs, asked

Scope: whole

For each thing the opening says the user achieves or does, does some item ask whether the user can?

Look for: a point of `usability.md` the kind's user needs that no item or sign asks.

Why: a thing with no item lets a deliverable that misses that part of the purpose pass.

### B-3: Only what the purpose needs

Scope: whole

Does each item ask a thing the purpose needs that no other item asks?

Look for: an item that is one way of meeting another item, such as an example or a file layout; a
point asked in two items; a point of `usability.md` the kind does not need; steps of the work,
which are the plan's tasks; a part of the template only some deliverables need.

Why: what is asked is answered on every deliverable, so an item beyond the purpose is added to
every deliverable of the kind, and each answer costs the maker and the judge a reading.

### B-4: What the user gets, with the lines that give it

Scope: whole

Is each item answered yes by pointing to the lines of the deliverable that give its user something,
by one who has only what that user has and does what they do with it?

Look for: an item met by writing something in, whether its user needs it or not; an item named or
asked by what is absent or kept out, which no line gives; an item asking whether the deliverable
matches what was decided, how the work was done, or how the product behaves where the user cannot
run it.

Why: an item about what is there passes a deliverable its user cannot use; one about what is absent
has no line to answer it with; one the user cannot answer is answered by whoever holds what the
user does not.

### B-5: Same answer from anyone

Scope: whole

Does each item get the same yes or no whoever answers it?

Look for: an item that checks two things; a word whose bar depends on who answers, such as clear,
enough or appropriate, with no sign under it saying what is looked at; a count in a unit it does
not say.

Why: when the answer depends on who judges, the maker cannot tell what passes, and judgments of the
same deliverable differ.
