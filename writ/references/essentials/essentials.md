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

## <Point name>

<What the work lets its receiver do>

- Achieved: <what, in what came of using the work, shows it achieved>
- Not achieved: <what shows it not>
```

- The opening holds the purpose and nothing else. Every point is worked back from it, and where a
  point's words do not reach, the maker and the judge decide by it. A kind can have more than one
  receiver: code is run by its users and changed by those who keep it.
- Each point has a heading, so it is named, not found by its place in the file.
- Its sentence is what the maker aims at; its two lines are what the judge decides by, as one of
  the two.

## Writing the points

- Work each point back from the purpose: ask what the receiver must get from the work to do what it
  is for, and make each such thing a point. Look for them from each of these sides; a side
  that brings up nothing needs no point:
  - The purpose itself: the receiver can do what the work is for.
  - Correctness: what the work says or does is right, so the receiver can rely on it.
  - What supports it: speed, ease of use, the receiver's effort.
  - Those who change it later: whoever keeps or takes over the work can change it.
  - What it takes in and hands on: the form the next reader, person or tool, relies on.
- Leave style to a checker. It holds as well for a work that misses its purpose, so it is no point.
- Give each point one thing. A point that holds two hides the one that falls short behind the one
  that holds.
- Keep a point only if a work that misses its purpose fails it. Picture the usual ways a work of the
  kind fails: what it says is wrong, it says too little, or it is written for someone else. A point
  about a part being there, or how the work looks, passes all three.
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

## What the upgrade asks

The notes let the reader tell what they must do differently once they upgrade.

- Achieved: what the reader said they must do is what the version asked of them when they upgraded
  and went on working, "nothing" included.
- Not achieved: the reader learned what it asked of them only when something stopped them.

## What the upgrade gives

The notes let the reader weigh the upgrade by their own work.

- Achieved: the reader named what the version changes in their own work, and decided on that.
- Not achieved: the reader repeated the product's terms, or could not tell this version from any
  other.
```
