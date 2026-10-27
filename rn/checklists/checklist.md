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
each is answered by doing with the deliverable what its user does and showing what that gives them;
the ways a deliverable meets that thing are the signs under the item, not items of their own, and a
deliverable is sent back on an item only for a gap that keeps its user from what the item asks.
What a tool the project runs can judge, such as its formatter, its linter or its type checker, is
left to the tool and asked by no item. It is made from this file and `usability.md`, what any
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

<`Judged on: the built product`, where only the built product answers the question>

<Question answered yes or no, asking what the user gets>

Tried by: <what whoever answers does with the deliverable, as its user does, and how far, such as a
command run or every example followed; left out where reading the part as its user does is all>

Signs: <the ways a deliverable gives it, each a thing its user can then do; left out where the
question needs none>

Why: <what goes wrong for the user without it>
```

Each item says where in the deliverable it is answered: `its part`, at the part or parts that give
it; `each part`, in every part of the deliverable on its own, a part being a section under a top
heading of a document, with the title and opening as one, or a file of code; `whole`, of the
deliverable at once, for what lies between its parts, such as one name for each thing. The items
answered at one part stand in the order of the template's parts, and those answered at each part
or over the whole after them. A kind that adds no part to a document's shape has no Format section.
An item whose question only the built product answers, such as whether a README's commands run as
written, says so in the line `Judged on: the built product`; a work made before the product is
built is judged without such items, and on every item once it is built.

An item is answered yes, no, or could not check with why, never yes for what was not tried: its
maker and its reader each do what its `Tried by` line says, as far as it says, and give the command
run and what it printed, or the lines, as its evidence; an item whose `Tried by` cannot be done, as
when its command does not run, is answered could not check. A no names the gap and how it keeps
the user from what the item asks.

Why: every checklist in the same shape lets a tool read any of them and gives the maker the purpose,
then the idea, then the shape, before the items, so each item is met inside what those already set;
an item met where its part comes is met as the deliverable is written; and an item only the built
product answers, judged on a work made before it, such as a README written to design it, sends the
work back for what is not there yet. Maker and reader who do the same, as far, see the same, so a
gap one of them finds is not a difference in what each chose to try; signs of what the user can do
keep the reader on whether the deliverable serves, where signs of what falls short set it hunting,
and it finds something in every deliverable whether or not its user would meet it; and a check that
passes what it could not try passes what it was there to stop.

### F-2: Version

Scope: its part

Is the `version` a whole number, `1` until the plugin that holds the checklist is first released,
and raised by one for each release after?

Why: a judgment names the text it was made by, and no draft between releases takes a number.

### F-3: Made from the current inputs

Scope: its part

Does `made_from` name the version of this file and of `usability.md` that stand now? This file
names `usability.md` alone, as it is made from itself, and `usability.md`, what every checklist is
made from, names none.

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

Signs: each point of `usability.md` the kind's user needs is asked by an item or a sign.

Why: a thing with no item lets a deliverable that misses that part of the purpose pass.

### B-3: Only what the purpose needs

Scope: whole

Does each item ask a thing the purpose needs that no other item asks?

Signs: each item is a thing of its own, not one way of meeting another, such as an example or a
file layout; each point is asked in one item; each point of `usability.md` asked is one the kind
needs; each item asks what its user gets, not a step of how the deliverable is made; each part of
the template is one every deliverable of the kind needs; no item asks what a tool the project runs
judges, such as its formatter, its linter or its type checker.

Why: what is asked is answered on every deliverable, so an item beyond the purpose is added to
every deliverable of the kind, and each answer costs the maker and the judge a reading.

### B-4: What the user gets, with the lines that give it

Scope: whole

Is each item answered yes by doing with the deliverable what its user does and showing what that
gives them, the lines or what a command printed, by one who has only what that user has?

Signs: each item is met by what its user then can do, not by something written in whether they
need it or not; each is named and asked by what is there, which a line gives, not by what is absent
or kept out; each asks what its user gets, not whether the deliverable matches what was decided,
how the work was done, or how the product behaves where its user cannot run it.

Why: an item about what is there passes a deliverable its user cannot use; one about what is absent
has no line to answer it with; one the user cannot answer is answered by whoever holds what the
user does not.

### B-5: Same answer from anyone

Scope: whole

Does each item get the same yes or no whoever answers it?

Signs: each item checks one thing; each word whose bar could depend on who answers, such as clear,
enough or appropriate, has a sign under it saying what is looked at; each count names its unit;
what is done to answer it, and how far, is said in its `Tried by` line or is the reading of its
part, not left to whoever answers.

Why: when the answer depends on who judges, the maker cannot tell what passes, and judgments of the
same deliverable differ.
