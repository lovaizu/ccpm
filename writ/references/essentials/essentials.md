# Checklist

A checklist is written for one kind of deliverable, such as research findings, a proposal, a design
document, code or tests. Two people use it: the maker, to know what a deliverable of the kind needs
to serve its user, and the judge, to decide from what happened when the deliverable was used whether
it did. This file is the checklist for checklists, and is written in the shape it asks for.

## Benefit

### B-1: Everything the deliverable needs

The checklist lets the maker know everything the deliverable needs to serve its user.

- Achieved: each way the deliverable fell short for its user was one that an item asks about.
- Not achieved: the deliverable fell short for its user in a way that no item asks about.

### B-2: Good told from bad

The checklist lets the judge tell a deliverable that served its user from one that did not.

- Achieved: a deliverable that served its user was Achieved on every item, and one that did not was
  Not achieved on at least one.
- Not achieved: a deliverable that did not serve its user was Achieved on every item, or one that did
  was Not achieved on one.

## Usability

### U-1: Purpose first

The checklist lets the maker and the judge decide a case that no item settles.

- Achieved: where no item settled a case, the maker or the judge decided it by the purpose the
  checklist opens with.
- Not achieved: where no item settled a case, they guessed, or decided against the purpose.

### U-2: One answer per item

The checklist lets the judge settle every item from what happened when the deliverable was used.

- Achieved: for every item, exactly one of its two lines held.
- Not achieved: for some item, both lines held, or neither did.

### U-3: One thing per item

The checklist lets the maker know what to change from an item that is Not achieved.

- Achieved: from the item alone, the maker knew the one thing that fell short.
- Not achieved: the item asked about more than one thing, and the maker had to work out which fell
  short.

### U-4: No repeats

The checklist lets the maker and the judge spend their attention only on items that settle
something.

- Achieved: each item's answer told something that no other item's did, in this checklist or in
  [doc.md](doc.md), the checklist for every document.
- Not achieved: two items always came out the same, because they ask the same thing.

### U-5: Empty sections explained

The checklist lets the judge tell a section thought through from a section forgotten.

- Achieved: every section with no item held `None: <why the kind needs none>`, with a reason the
  judge could check.
- Not achieved: a section was empty, or its `None:` gave no reason.

### U-6: Each item in its section

The checklist lets the maker and the judge find an item where its section says it belongs.

Ask of each item, in this order, and stop at the first yes:

1. Does it ask for a set shape that a person or a tool relies on to read the deliverable? Format.
2. Without it, does the user lose what they get from the deliverable? Benefit.
3. Otherwise: Usability.

- Achieved: each item sat in the section these questions put it in.
- Not achieved: an item sat in a section these questions do not put it in.

## Format

### F-1: Same shape

The checklist lets a tool read it as it reads every other checklist.

```markdown
# <Kind of deliverable>

<Purpose: what the deliverable lets its user decide or do>

## Benefit

### B-1: <Item name>

<What the deliverable lets its user do>

<Only what the item needs to be judged exactly, such as a template; most items need nothing>

- Achieved: <what happened when the deliverable served its user here>
- Not achieved: <what happened when it did not>

## Usability

## Format
```

- Achieved: a tool read every part of the checklist as one of the parts above.
- Not achieved: the tool met a part it could not read as one of them.

### F-2: Stable IDs

The checklist lets anything that names an item by its ID, such as a judgment kept from an earlier
use, keep pointing at the same item.

- Achieved: every ID named earlier still meant the same item. An ID is the section's first letter
  and a number counted up within the section, such as `U-2`; across checklists it goes with the
  file, such as `release-notes.md U-2`. A removed item left its number unused, and an item moved to
  another section took a new number there.
- Not achieved: an ID named earlier now meant another item, or none.
