---
name: checklist
version: 0.2.0
---

# Checklist

A checklist is used by whoever makes a deliverable of one kind and whoever judges it. Answering its
items, the maker makes, in a way of their own, a deliverable that serves the purpose of whoever uses
the kind, nothing missing and nothing more; the judge tells whether a deliverable serves it.

A checklist rests on that purpose: who uses a deliverable of the kind and what they achieve with
it. From the purpose come the template, what every deliverable of the kind holds, in a form any
language or tool can take, and the items, the key points a deliverable must meet, each answered by
what its user has and does with it, with why it matters to them. With this idea and each why, the
maker meets the items their own way; how a deliverable is made is the plan's tasks, as a checklist
is answered on the deliverable, which holds no steps. Each point is asked in the one checklist
whose deliverable's user it serves: `usability.md` for the user of every kind, a kind's own
checklist for that kind's user, and a new checklist for a kind with none.

This file is the checklist for checklists, and is written in the shape it asks for. Each item of
`usability.md` applies to a checklist, with what a good deliverable of the kind gives its user as
its subject.

## Format

### F-1: Shape

Scope: whole

Does the checklist follow this template?

```markdown
---
name: <kind-of-deliverable, or what it judges across kinds>
version: <x.y.z>
---

# <Kind of deliverable, or what it judges across kinds>

<The purpose in one or two sentences: who uses it, and what they can then do>

<The idea the items rest on>

<How `usability.md` applies to the kind>

## Format

### F-1: Shape

<The template the deliverable follows>

## Benefit

### B-1: <Item name>

Scope: <its part, each part or whole>

<Question answered yes or no>

<Only what the question needs to be answered, such as a list or a template; most need nothing>

Why: <what goes wrong without it>
```

Each item, Format's included, says where in the deliverable it is answered: `its part`, at the part
or parts that give it; `each part`, in every part of the deliverable on its own, a part being a
section under a top heading of a document, with the title and opening as one, or a file of code;
`whole`, of the deliverable at once, for what lies between its parts, such as one name for each
thing.

A checklist for one kind is named by the kind; one that judges every kind, such as `usability.md`,
is named by what it judges. One that adds no part to its kinds' templates has no Format section.

Why: every checklist in the same shape keeps their quality even, lets a tool read any of them, and
gives the maker the purpose, then the idea, then the shape, before the items, so each item is met
inside what those already set. An item asking of every part, answered where one part gives it,
passes a part that does not, and one asking what lies between the parts cannot be answered part by
part.

### F-2: Version

Scope: its part

Is the `version` in the front matter semver?

Why: a judgment names the text it was made by in a form people and tools read the same way.

### F-3: Item IDs

Scope: whole

Is each item's ID its section's first letter and a number counted up within the section, such as
`B-2`?

Across checklists, an ID is named with the checklist's `name`, such as `release-notes B-2`.

Why: a judgment names each item by its ID, and the name tells whose item it is when several
checklists are judged at once.

### F-4: An ID never used again

Scope: whole

Compared with the version last released, is every ID that a removed or moved item had left unused,
with a moved item taking a new number in its new section?

The version last released is the one in the last release of the plugin that holds the checklist,
under whatever name it had then. A checklist in no release yet has no such ID, and passes.

Why: an ID named earlier always means the same item.

### F-5: Version raised once for each release

Scope: its part

Is the `version` raised once for each release from the version last released, and not with each
change on a branch?

A checklist in no release yet is `0.1.0`.

Why: a judgment names the text it was made by, and no draft between releases takes a number.

## Benefit

### B-1: User and purpose

Scope: its part

Can whoever makes or judges a deliverable of the kind learn, from the opening, in one or two
sentences, who uses it and what they can then do?

Why: every item is judged against the user and the purpose; without them, no item can be answered.

### B-3: The idea the items rest on

Scope: its part

From the opening, can whoever makes a deliverable of the kind tell the idea its items rest on: how a
deliverable of the kind serves its user's purpose, the ground each item is drawn from?

Why: a maker who knows only the items meets each by its letter, and fits to a guess a case no item
names; one who knows the idea and each why meets the items their own way, toward the purpose.

### B-4: How `usability.md` applies

Scope: its part

Can whoever makes or judges a deliverable of the kind tell from the opening how each item of
`usability.md` applies to the kind?

Look for: what the kind's subject is, for the items that ask about the reader's picture of it; and,
for each item of `usability.md` that the kind's shape settles otherwise, such as an opening its
template has no place for, how it is answered for the kind. An item not named is answered as
`usability.md` asks it.

Why: `usability.md` is answered beside the kind's checklist; an item of it that the kind's shape
cannot meet, or that is answered on a subject wider than the kind's, fails a deliverable that serves
its reader, and the maker cannot tell what passes.

### B-5: A template drawn from the purpose

Scope: its part

Can whoever makes a deliverable of the kind fill the template with what every deliverable of the
kind holds, each part called for by the purpose and the idea?

Look for: a part only some deliverables need; a part the purpose and the idea do not call for; a
form of one language or tool.

Why: a part only some need is added to every deliverable, and a part the purpose does not call for
is filled with nothing it asks.

### B-2: Every part of the purpose checked

Scope: whole

For each thing the opening says the user decides or does, can whoever judges learn from some item
whether the user can?

Why: items drawn from the purpose, one for each thing it names, are enough when every thing has
one; a thing with no item lets a deliverable that misses that part of the purpose pass.

### B-6: What the user gets

Scope: whole

Does a yes to each item tell whoever judges that the user gets something from the deliverable,
rather than that something is in it?

Look for: an item met by writing something in, such as an opening that tells what the deliverable
covers, whether its user needs it or not; and an item that asks of every deliverable of the kind a
part only some need, such as a figure of who does what where nothing acts in turn.

Why: an item about what is there passes a deliverable its user cannot use, and fails a good one that
does without that part; and since the maker meets every item, what such an item asks for is added
to every deliverable of the kind, needed or not.

### B-7: Each item met the maker's own way

Scope: whole

Does the checklist leave how a deliverable of the kind is made to the maker, holding no steps of the
work?

Why: a checklist is answered on the deliverable, which holds no steps; steps put in a checklist are
followed without the purpose, and how a deliverable is made is the plan's tasks.

### B-8: One thing per item

Scope: whole

Can whoever judges tell, from each item answered no, the one thing that falls short?

An item that checks two things does not.

Why: when an item checks two things, the one that falls short hides behind the one that holds.

### B-9: Answered yes or no

Scope: whole

Can whoever judges answer each item yes or no?

Why: an answer that is neither leaves the deliverable neither passed nor failed, so no one can tell
whether it serves its purpose.

### B-10: Same answer from anyone

Scope: whole

Can the maker know what passes, because each item gets the same answer whoever answers it?

A question that holds a word whose bar depends on who answers, such as concrete, clear, enough or
appropriate, does not; nor does one that counts in a unit it does not say, such as one change or
one idea. Such a word is replaced by what is looked at to answer yes, and such a count by what
counts as one.

Why: when the answer depends on who judges, the maker cannot tell what passes, and judgments of the
same deliverable differ.

### B-11: Each item named by what it gives

Scope: whole

Can whoever makes the deliverable tell from each item's name alone what the user gets when the item
is met?

Look for: a name that says what is absent or kept out, such as "Nothing of the specification" or
"No case a principle settles"; it fails.

Why: an item is named alone in a judgment and in the maker's mind; a name of what is kept out is
read as a rule, and the maker writes to avoid it rather than to give the user something.

### B-12: Each item answered by what the user has and does

Scope: whole

Can each item be answered by one who has only what the deliverable's user has, such as the whole
repository for whoever maintains code, and does what they do with it, such as running its tests?

Look for: an item that asks whether the deliverable matches what was decided, how the work was done,
such as a test seen failing before its code, or how the product behaves where the user cannot run
it.

Why: an item given to one who cannot answer it is left without an answer, or answered by one who
holds what the user does not, so a deliverable the user cannot use passes.

### B-13: Each point asked in one place

Scope: whole

Does each item ask what no item of the checklists answered beside it, such as `usability.md`,
asks?

Why: a point asked in two places is fixed in one and left in the other, and the two drift until
they ask different things.

### B-14: Items in the order of the template

Scope: whole

Do the items answered at one part stand in the order of the template's parts, and those answered at
each part or over the whole, such as one name for each thing, stand after them?

Why: whoever makes or judges the deliverable meets each item where its part comes, instead of
holding every item in mind at once; and an item that holds over the whole is checked once the
whole is there.
