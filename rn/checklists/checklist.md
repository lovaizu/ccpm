---
name: checklist
version: 0.2.0
---

# Checklist

A checklist is used by whoever makes a deliverable of one kind and whoever judges it. Answering its
items as they make it, the maker makes a deliverable that serves the kind's purpose, nothing missing
and nothing more; answering its items, the judge can tell whether a deliverable serves that purpose.

This file is the checklist
for checklists, and is written in the shape it asks for. Each item of `readability.md` applies to a
checklist, with what a good deliverable of the kind gives its user as its subject.

## Format

### F-1: Shape

Does the checklist follow this template?

```markdown
---
name: <kind-of-deliverable>
version: <x.y.z>
---

# <Kind of deliverable>

<The purpose in one or two sentences: who uses it, and what they can then do>

<Where the kind is a document, how `readability.md` applies to it>

## Format

### F-1: Shape

<The template the deliverable follows>

## Benefit

### B-1: <Item name>

<Question answered yes or no>

<Only what the question needs to be answered, such as a list or a template; most need nothing>

Why: <what goes wrong without it>

## Usability

None: <why the kind needs no item here>
```

Every checklist has the three sections, in this order: the shape the maker takes before writing,
then what the user gets, then what makes it easy to use.

Why: every checklist in the same shape keeps their quality even, lets a tool read any of them, and
gives the maker the shape first, so each item after it is met inside a shape already taken.

### F-2: A section thought through

Does each section with no item hold `None:` and its reason?

Why: a section thought through is told from a section forgotten.

### F-3: Version

Is the `version` in the front matter semver?

Why: a judgment names the text it was made by in a form people and tools read the same way.

### F-4: Item IDs

Is each item's ID its section's first letter and a number counted up within the section, such as
`U-2`?

Across checklists, an ID is named with the checklist's `name`, such as `release-notes U-2`.

Why: a judgment names each item by its ID, and the name tells whose item it is when several
checklists are judged at once.

### F-5: An ID never used again

Compared with the version last released, is every ID that a removed or moved item had left unused,
with a moved item taking a new number in its new section?

The version last released is the one in the last release of the plugin that holds the checklist,
under whatever name it had then. A checklist in no release yet has no such ID, and passes.

Why: an ID named earlier always means the same item.

### F-6: Version raised once for each release

Is the `version` raised once for each release from the version last released, and not with each
change on a branch?

A checklist in no release yet is `0.1.0`.

Why: a judgment names the text it was made by, and no draft between releases takes a number.

## Benefit

### B-1: User and purpose

Can whoever makes or judges a deliverable of the kind learn, from the opening, in one or two
sentences, who uses it and what they can then do?

Why: every item is judged against the user and the purpose; without them, no item can be answered.

### B-7: How `readability.md` applies

Where the kind is a document, can whoever makes or judges it tell from the opening how each item of
`readability.md` applies to the kind?

Look for: what the kind's subject is, for the items that ask about the reader's picture of it; and,
for each item of `readability.md` that the kind's shape settles otherwise, such as an opening its
template has no place for, how it is answered for the kind. An item not named is answered as
`readability.md` asks it.

Why: `readability.md` is answered beside the kind's checklist; an item of it that the kind's shape
cannot meet, or that is answered on a subject wider than the kind's, fails a deliverable that serves
its reader, and the maker cannot tell what passes.

### B-2: Every part of the purpose checked

For each thing the opening says the user decides or does, can whoever judges learn from some item,
in whichever section it sits, whether the user can?

Why: items drawn from the purpose, one for each thing it names, are enough when every thing has
one; a thing with no item lets a deliverable that misses that part of the purpose pass.

### B-3: What the user gets

Does a yes to each Benefit and Usability item tell whoever judges that the user gets something from
the deliverable, rather than that something is in it?

Look for: an item met by writing something in, such as an opening that tells what the deliverable
covers, whether its user needs it or not; and an item that asks of every deliverable of the kind a
part only some need, such as a figure of who does what where nothing acts in turn.

Why: an item about what is there passes a deliverable its user cannot use, and fails a good one that
does without that part; and since the maker meets every item, what such an item asks for is added
to every deliverable of the kind, needed or not.

### B-4: One thing per item

Can whoever judges tell, from each item answered no, the one thing that falls short?

An item that checks two things does not.

Why: when an item checks two things, the one that falls short hides behind the one that holds.

### B-5: Answered yes or no

Can whoever judges answer each item yes or no?

Why: an answer that is neither leaves the deliverable neither passed nor failed, so no one can tell
whether it serves its purpose.

### B-6: Same answer from anyone

Can the maker know what passes, because each item gets the same answer whoever answers it?

A question that holds a word whose bar depends on who answers, such as concrete, clear, enough or
appropriate, does not; nor does one that counts in a unit it does not say, such as one change or
one idea. Such a word is replaced by what is looked at to answer yes, and such a count by what
counts as one.

Why: when the answer depends on who judges, the maker cannot tell what passes, and judgments of the
same deliverable differ.

### B-8: Each item named by what it gives

Can whoever makes the deliverable tell from each item's name alone what the user gets when the item
is met?

Look for: a name that says what is absent or kept out, such as "Nothing of the specification" or
"No case a principle settles"; it fails.

Why: an item is named alone in a judgment and in the maker's mind; a name of what is kept out is
read as a rule, and the maker writes to avoid it rather than to give the user something.

## Usability

### U-4: Each item in its section

Can whoever uses the checklist find each item in the section these questions put it in?

Ask of each item, in this order, and stop at the first yes:

1. Does it ask for a shape that a person or a tool tells without reading what the deliverable
   says, such as a heading, a name, a marking or a number's form? Format.
2. Without it, does the user lose what they get from the deliverable? Benefit.
3. Otherwise: Usability.

Why: with every item where the questions put it, anyone finds it where they look, and each section
holds what its name says.

### U-5: Items in the order the maker meets them

Can the maker take the items in the order they write, because within each section the items stand
in the order the maker meets them writing the deliverable from the top, and those that hold over
the whole, such as one name for each thing, stand last?

Why: a maker who writes from the top meets each item where its part comes, instead of holding every
item in mind at once; and an item that holds over the whole is checked once the whole is there.
