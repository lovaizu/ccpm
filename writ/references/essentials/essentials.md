# Viewpoint files

A viewpoint file is written for one kind of work, such as research findings, a proposal, a design
document, code or tests, and serves two people:

- To whoever makes a work of the kind, it shows what the work needs to achieve its purpose.
- To whoever judges the work from what came of using it, it is the measure of whether the work
  achieved its purpose.

This file is for writing such a viewpoint file.

## The form

```markdown
# <Kind>

<What a work of the kind lets its receiver decide or do, with the receiver named in general>

## Benefit

### B-1: <Point name>

<What the work lets its receiver do>

- Achieved: <what, in what came of using the work, shows it achieved>
- Not achieved: <what shows it not>

## Usability

## Format
```

- The opening holds the purpose and nothing else. Every point is worked back from it, and where a
  point's words do not reach, the maker and the judge decide by it. A kind can have more than one
  receiver: code is run by its users and changed by those who keep it.
- Every file has the same three sides, so the points are always looked for, talked over and judged
  from all three:
  - Benefit: what the receiver gets from the work, the work as it should be. That it is right, and
    that whoever changes it later can, belong here.
  - Usability: what supports the benefit, such as speed, ease of use and the receiver's effort.
  - Format: the form the receiver or a tool relies on, such as what the work takes in and hands on,
    or the style it shares with the receiver's other works.
- A side with no point holds `None: <why a work of the kind needs none here>`. Left empty, a side
  thought through and a side forgotten look the same.
- A point's sentence is what the maker aims at; its two lines are what the judge decides by, as one
  of the two.

## IDs

- A point's ID is its side's letter and a number counted up within the side: `B-2`. Across files, a
  point is named with its file: `release-notes.md B-2`.
- An ID is never used again. A point taken out leaves its number unused; a point moved to another
  side has changed its meaning, and takes a new number there. So a record that names an ID always
  means the same point.

## Writing the points

- Work each point back from the purpose: for each side, ask what the receiver must get from the
  work to do what it is for, and make each such thing a point.
- Give each point one thing. A point that holds two hides the one that falls short behind the one
  that holds.
- Keep a point only if a work that fails its receiver on that side fails it. Picture the usual ways
  a work of the kind fails: what it says is wrong, it says too little, it is written for someone
  else, or it comes in a form its receiver or tool cannot take. A point about a part being there
  passes them all.
- Write the two lines in terms of what the receiver did, said or got in using the work, so that any
  use of any work of the kind shows which one holds.
- Leave out what [doc.md](doc.md) already holds for every document.

## Checking the file

Use a real work of the kind as its receiver would, and judge each point from what came of it. Where
a point cannot be judged from that, or a work known to fall short passes it, write the point again
from the purpose, not to fit that one use.

## Example

```markdown
# Release notes

Release notes let someone who uses the product decide whether to upgrade to a version, and, once
upgraded, go on working without being caught out by what changed.

## Benefit

### B-1: What the upgrade asks

The notes let the reader tell what they must do differently once they upgrade.

- Achieved: what the reader said they must do is what the version asked of them when they upgraded
  and went on working, "nothing" included.
- Not achieved: the reader learned what it asked of them only when something stopped them.

### B-2: What the upgrade gives

The notes let the reader weigh the upgrade by their own work.

- Achieved: the reader named what the version changes in their own work, and decided on that.
- Not achieved: the reader repeated the product's terms, or could not tell this version from any
  other.

## Usability

### U-1: What matters found first

The notes let the reader find what concerns them without reading every entry.

- Achieved: the reader reached the entries that changed their own work before deciding.
- Not achieved: the reader decided before reaching an entry that changed their work, or read every
  entry to find it.

## Format

None: the notes are read by people, and no tool takes them in.
```
