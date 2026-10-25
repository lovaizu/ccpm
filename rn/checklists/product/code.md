---
name: code
version: 1
made_from:
  checklist: 1
  usability: 1
---

# Code

Code is used by whoever runs it and whoever maintains it, a person or an AI. Whoever runs it gets
the behavior they asked for, and from each stop how to go on; whoever maintains it reads what each
part does where it is written, changes one thing in one place, and trusts, from its tests passing,
that every behavior still holds.

Code serves them through two designs. The code is split into functions and modules by what each
takes on, one thing each; each says what it takes in and gives back, and what comes from outside is
checked where it comes in. Its tests are designed from the requirements, what the code must do, by
the technique that fits what each function takes in and decides, so they hold what the code must do
rather than what it happens to do, and each fails when the behavior it holds breaks. The development
rules are the project's own rules for its code: the runtime and its versions, the libraries and
tools allowed, and the checks every change passes. The signs on the code are drawn from Google's
"What to look for in a code review" (google/eng-practices, CC BY 3.0), and those on the tests'
design from the techniques of the ISTQB Certified Tester Foundation Level syllabus v4.0.1,
chapter 4.

## Format

### F-1: Shape

Scope: whole

Does each file of the code follow this template, in the forms its language and the development
rules set?

```text
<At the top of each module>  what the module does, and why it is there
<For each function>          what it takes in, what it gives back, and when it stops,
                             as types where the language has them, otherwise as a comment
<For each test>              name: what must happen, as one sentence
                             body: Given: <the situation>, When: <what is done>,
                             Then: <what must be so>, each in plain words, as comments
```

Why: the maintainer finds what each module and function is for, and what each test checks, in the
same place in every file, before reading any body.

## Benefit

### B-1: The same behavior on any machine

Scope: whole

Does whoever runs the code get the behavior the requirements ask, on any machine with only what the
development rules name?

Look for: an import, a tool or a feature of the language beyond what the development rules name, or
newer than the oldest version of the runtime they name.

Why: what the code uses beyond the development rules is missing on some user's machine, and the code
fails there for a reason the user was never told.

### B-2: A stop cleared by what it says

Scope: whole

When the code stops, can whoever runs it go on by doing what the stop says?

Look for:
- something taken in from outside, such as a file, an argument or what another program hands it,
  used before a check stops what the requirements say it must not be;
- a stop that does not name the input or the condition that was wrong;
- a stop that names no action, such as a value to give instead or how to install a missing tool;
- an action whoever is stopped cannot take with what they have, such as a read another check stops,
  or one after which the same check still stops.

Why: a wrong input used fails far from where it came in, or does harm, such as writing outside the
folder it was meant for; a stop that says only that something failed leaves the user to read the
code; and a stop its own action does not clear leaves the run stuck, going round or ended.

### B-3: What each part does, told where it is written

Scope: each part

Can the maintainer tell what each module, function and test does, and what each name in it stands
for, from its opening, its signature and its names, without reading its body or its callers?

Look for:
- a name of a module, function, variable or test that says less than its thing, or something else;
- an opening, a signature or a comment that leaves out part of what it tells, such as when a
  function stops, or that says what the code does not do;
- a word used in a sense of the code's own, or a name taken from another product, that no opening or
  comment explains;
- the reason behind a decision, or what a regular expression or an algorithm does, left unsaid;
- a comment telling how the work went or where it stands, such as the task a line was added for;
- an idiom, a way of handling errors or a layout unlike the code around it, where the development
  rules settle no choice.

Why: a part not told by its own lines sends the maintainer into its body and its callers at every
use; a name or a comment that says something else is believed; a comment about the work turns wrong
as the code changes; and a difference from the code around it is read as meaning something.

### B-4: Only what a behavior asked now needs

Scope: each part

Does each function, parameter, branch, option and comment give the maintainer something a behavior
the requirements ask now needs?

Look for:
- code more general than its callers use, such as a parameter every caller gives the same value;
- a case for a future the requirements do not name;
- a comment that says again what the line under it does.

Why: each part is read, tested and kept true by every maintainer on every change, and when a
guessed need comes, it seldom has the shape that was guessed.

### B-5: One change in one place

Scope: whole

Can the maintainer change one thing the code takes on in one place, with no other place left that
still holds the old one?

Look for:
- a function or module that takes on two things;
- a piece of knowledge, such as a rule, a value or a way of reading an input, written in two places
  across the repository;
- one thing under two names across the code and its tests, so a search for one name misses the
  places of the other, or one name for two things.

Why: a part that takes on two things is changed for one and breaks the other; knowledge written
twice is fixed in one place and left wrong in the other; and a place a search for the name misses
is left as it was.

### B-6: Every behavior held by a test

Scope: whole

When a behavior the requirements ask is broken in the code, does some test fail?

Look for:
- an equivalence partition of an input or an output, the values a function treats alike, the
  invalid ones among them, that no test takes a value from;
- a boundary of a partition whose values stand in order, such as numbers or lengths, or the value
  on either side of it, that no test takes;
- a feasible rule of a decision table, a combination of the conditions' values that can happen,
  that no test takes;
- a transition between states, an invalid one included, an event given in a state that does not
  take it, that no test takes;
- a behavior over inputs of a kind, such as any text, path or list, with no property test making
  many inputs of the kind on each run and checking what every one must give, such as a parse giving
  back what was written, with each input that once failed kept as an example;
- a statement or a branch that no unit test runs, counted without the property tests, whose
  inputs change from run to run;
- a small change a fault could make, such as a comparison, an operator or a value replaced, that no
  test fails on: a survivor of mutation testing;
- a test whose expected value is taken from the code it checks;
- a line, branch, input or mutant left out of the coverage, the property tests or the mutation
  testing, with nothing beside it or in the check's settings saying that the user decided it and
  why, such as an environment the tests cannot make, or a line no behavior changes with.

Why: tests passing give trust only in the behaviors they would fail on; a gap looks the same as a
test that works and lets a fault pass, faults gather at boundaries, such as `<` written for `<=`,
and a check left out with no decision written beside it cannot be told from one left out to make
the run pass, so the next maintainer keeps the gap.

### B-7: A failure taken as one fault

Scope: whole

When a check fails after a change, can the maintainer take it as a fault of that change, in the one
behavior the failing test names?

Look for:
- a test that would fail on a fault of two behaviors;
- a test that reads the clock, the network or the machine it runs on, that leaves files or state
  behind for the next, or that needs another to run first;
- a check the development rules name, such as the tests, the formatter, the linter or the type
  checker, run with the settings kept in the repository, already failing on the code.

Why: a test that holds several behaviors leaves the maintainer to read its code to learn which
broke; a test that fails on some runs and not on others teaches them to rerun it rather than read
it, and then a real failure is rerun too; and a check already failing hides the failure a change
brings.

### B-8: Every check run on every change

Scope: whole

Can the maintainer run the whole test run in seconds, so that the checks run on every change and
mutation testing, which runs the tests once for each mutant, ends in minutes?

Look for: a test that sets up by running other programs, such as a repository made by git commands
for every test, where it could be made once and copied.

Why: a test run that takes minutes is run less often, and mutation testing multiplies its time by
the number of mutants, so the maintainer waits on every change, or stops running the checks.

### B-9: The same behavior beside another run

Scope: whole

Does whoever runs the code get the behavior the requirements ask while another run of it goes on at
the same time?

Look for: a file, port, folder or other place a run writes or holds that another run at the same
time, such as a second session or a second test worker, could write or hold too.

Why: runs that share a place they write overwrite each other's work, and the fault shows only when
they happen to meet, so a test seldom finds it.
