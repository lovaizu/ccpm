# Checklist

A checklist says how a deliverable of one kind, such as research findings, a proposal, a design
document, code or tests, is judged after it has been used: the judge answers its questions from what
happened. Whoever makes a deliverable of the kind reads it first, to know how the deliverable will
be judged. This file is the checklist for checklists, and is written in the shape it asks for.

## Benefit

### B-1: No misses

When the deliverable fell short for its user, did an item catch it?

- Achieved: every way the deliverable fell short for its user made some item Not achieved.
- Not achieved: the deliverable fell short for its user in a way that left every item Achieved.

### B-2: No false alarms

When the deliverable served its user, did it pass every item?

- Achieved: a deliverable that served its user was Achieved on every item.
- Not achieved: a deliverable that served its user was Not achieved on some item.

## Usability

### U-1: Purpose first

Where no item settled a case, could the judge decide it by the purpose the checklist opens with?

- Achieved: the judge decided each case no item settled by the purpose at the top.
- Not achieved: the judge had to guess a case no item settled, or the purpose at the top did not
  settle it.

### U-2: One answer per item

Did exactly one of each item's two lines hold?

- Achieved: for every item, exactly one of its two lines held.
- Not achieved: for some item, both lines held, or neither did.

### U-3: One thing per item

When an item was Not achieved, did it point to one thing to change?

- Achieved: from each item that was Not achieved, the maker knew the one thing to change.
- Not achieved: an item asked about more than one thing, and the maker had to work out which fell
  short.

### U-4: No repeats

Did each item's answer tell something that no other item's did?

- Achieved: no two items, in this checklist or in [doc.md](doc.md), the checklist for every
  document, always came out the same.
- Not achieved: two items always came out the same, because they ask the same thing.

### U-5: Empty sections explained

Did each section with no item say why?

- Achieved: every section with no item held `None: <why the kind needs none>`, with a reason the
  judge could check.
- Not achieved: a section was empty, or its `None:` gave no reason.

### U-6: Each item in its section

Did each item sit in the section these questions put it in?

Ask of each item, in this order, and stop at the first yes:

1. Does it ask for a set shape that a person or a tool relies on to read the deliverable? Format.
2. Without it, does the user lose what they get from the deliverable? Benefit.
3. Otherwise: Usability.

- Achieved: each item sat in the section these questions put it in.
- Not achieved: an item sat in a section these questions do not put it in.

## Format

### F-1: Same shape

Could a tool read every part of the checklist as a part of this template?

```markdown
# <Kind of deliverable>

<Purpose: what the deliverable lets its user decide or do>

## Benefit

### B-1: <Item name>

<Question the judge answers from what happened when the deliverable was used>

<Only what the question needs to be answered exactly, such as a template; most need nothing>

- Achieved: <what happened when the deliverable served its user here>
- Not achieved: <what happened when it did not>

## Usability

## Format
```

- Achieved: a tool read every part of the checklist as a part of the template.
- Not achieved: the tool met a part it could not read as one of them.

### F-2: Stable IDs

Did every ID named earlier, such as in a judgment kept from an earlier use, still mean the same
item?

- Achieved: every ID named earlier still meant the same item. An ID is the section's first letter
  and a number counted up within the section, such as `U-2`; across checklists it goes with the
  file, such as `release-notes.md U-2`. A removed item left its number unused, and an item moved to
  another section took a new number there.
- Not achieved: an ID named earlier now meant another item, or none.
