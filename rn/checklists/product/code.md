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

Tried by: the code's tests run on the oldest version of the runtime the development rules name,
with only the libraries and tools they name installed.

Signs: the code runs, and its tests pass, on the oldest version of the runtime the development rules
name, with only what they name installed.

Why: what the code uses beyond the development rules is missing on some user's machine, and the code
fails there for a reason the user was never told.

### B-2: A stop cleared by what it says

Scope: whole

When the code stops, can whoever runs it go on by doing what the stop says?

Tried by: each stop the code has, run with an input that makes it, the action it names taken with
only what whoever runs the code has, and the run made again.

Signs:
- each thing taken in from outside, such as a file, an argument or what another program hands it,
  is checked where it comes in, before it is used, against what the requirements say it must not
  be;
- each stop names the input or the condition that was wrong;
- each stop names an action, such as a value to give instead or how to install a missing tool;
- whoever is stopped can take that action with what they have, without a read another check stops,
  and once it is taken the same check lets the run go on.

Why: a wrong input used fails far from where it came in, or does harm, such as writing outside the
folder it was meant for; a stop that says only that something failed leaves the user to read the
code; and a stop its own action does not clear leaves the run stuck, going round or ended.

### B-3: What each part does, told where it is written

Scope: each part

Can the maintainer tell what each module, function and test does, and what each name in it stands
for, from its opening, its signature and its names, without reading its body or its callers?

Signs:
- each name of a module, function, variable or test says its thing, all of it and nothing else;
- each opening, signature and comment tells all of what it tells, such as when a function stops,
  and only what the code does;
- each word used in a sense of the code's own, and each name taken from another product, is
  explained by an opening or a comment;
- the reason behind each decision, and what each regular expression or algorithm does, is said;
- each comment tells the code, not how the work went or where it stands, such as the task a line
  was added for;
- errors are handled as the code around them handles them, where the development rules settle no
  choice.

Why: a part not told by its own lines sends the maintainer into its body and its callers at every
use; a name or a comment that says something else is believed; a comment about the work turns wrong
as the code changes; and a difference from the code around it is read as meaning something.

### B-4: Only what a behavior asked now needs

Scope: each part

Does each function, parameter, branch, option and comment give the maintainer something a behavior
the requirements ask now needs?

Signs:
- each part is as general as its callers use it, each parameter one its callers give different
  values;
- each case serves a behavior the requirements name now;
- each comment says what the line under it does not already say.

Why: each part is read, tested and kept true by every maintainer on every change, and when a
guessed need comes, it seldom has the shape that was guessed.

### B-5: One change in one place

Scope: whole

Can the maintainer change one thing the code takes on in one place, with no other place left that
still holds the old one?

Tried by: the whole read, then the code's tests run once and `git status` read for each file the
run made.

Signs:
- each function and module takes on one thing;
- each piece of knowledge, such as a rule, a value or a way of reading an input, is written in one
  place across the repository, and every other place that needs it takes it from there;
- each thing has one name across the code and its tests, so a search for the name finds every place
  of it, and each name stands for one thing;
- each file that running the code or its tests makes, such as Python's `__pycache__/`, is kept out
  of the repository by its ignore file.

Why: a part that takes on two things is changed for one and breaks the other; knowledge written
twice is fixed in one place and left wrong in the other; a place a search for the name misses
is left as it was; and a file a run makes is a copy of the code, committed with it and stale after
the next change.

### B-6: Every behavior held by a test

Scope: whole

When a behavior the requirements ask is broken in the code, does some test fail?

Tried by: the tests read beside the requirements; the unit tests run with the lines and branches
they run counted, without the property tests; the property tests run; and mutation testing run on
the code the work made or changed, each with the settings kept in the repository.

Signs:
- each equivalence partition of an input or an output, the values a function treats alike, the
  invalid ones among them, gives some test a value;
- each boundary of a partition whose values stand in order, such as numbers or lengths, and the
  value on either side of it, is taken by some test;
- each feasible rule of a decision table, a combination of the conditions' values that can happen,
  is taken by some test;
- each transition between states, an invalid one included, an event given in a state that does not
  take it, is taken by some test;
- each behavior over inputs of a kind, such as any text, path or list, has a property test making
  many inputs of the kind on each run and checking what every one must give, such as a parse giving
  back what was written, with each input that once failed kept as an example;
- every statement and branch is run by the unit tests, counted without the property tests, whose
  inputs change from run to run;
- each small change a fault could make, such as a comparison, an operator or a value replaced,
  fails some test, so no mutant survives but one kept out as the last sign says;
- each test's expected value is written from the requirements, not taken from the code it checks;
- each line, branch, input or mutant left out of the coverage, the property tests or the mutation
  testing, a survivor of mutation testing among them, is the maker's choice, named beside it or in
  the check's settings with why, such as an environment the tests cannot make, or a line no
  behavior changes with, and settled by the maker, not put to the user.

Why: tests passing give trust only in the behaviors they would fail on; a gap looks the same as a
test that works and lets a fault pass, faults gather at boundaries, such as `<` written for `<=`,
and a check left out with no decision written beside it cannot be told from one left out to make
the run pass, so the next maintainer keeps the gap.

### B-7: A failure taken as one fault

Scope: whole

When a check fails after a change, can the maintainer take it as a fault of that change, in the one
behavior the failing test names?

Tried by: every check the development rules name run once, with the settings kept in the
repository.

Signs:
- each test fails on a fault of one behavior, the one its name says;
- each test gives the same result on every run, reading no clock, network or machine it runs on,
  leaving no files or state behind for the next, and needing no other to run first;
- every check the development rules name, such as the tests, the formatter, the linter or the type
  checker, run with the settings kept in the repository, passes on the code.

Why: a test that holds several behaviors leaves the maintainer to read its code to learn which
broke; a test that fails on some runs and not on others teaches them to rerun it rather than read
it, and then a real failure is rerun too; and a check already failing hides the failure a change
brings.

### B-8: Every check run on every change

Scope: whole

Can the maintainer run the whole test run in seconds, so that the checks run on every change and
mutation testing, which runs the tests once for each mutant, ends in minutes?

Tried by: the whole test run run once, and the time it took read.

Signs: the whole test run ends in seconds; a set-up made by running other programs, such as a
repository made by git commands, is made once and copied for each test that needs it.

Why: a test run that takes minutes is run less often, and mutation testing multiplies its time by
the number of mutants, so the maintainer waits on every change, or stops running the checks.

### B-9: The same behavior beside another run

Scope: whole

Does whoever runs the code get the behavior the requirements ask while another run of it goes on at
the same time?

Signs: each file, port, folder or other place a run writes or holds is one that no other run at
the same time, such as a second session or a second test worker, writes or holds too.

Why: runs that share a place they write overwrite each other's work, and the fault shows only when
they happen to meet, so a test seldom finds it.

### B-10: What a machine can see, shown on every change

Scope: whole

Does the command that checks the work run a formatter, a linter and a type checker, so that the
maintainer is shown on every change what they find?

Tried by: the command that checks the work, as the development rules name it, run once, and what it
printed read for each of the three.

Signs: the development rules name a formatter, a linter and a type checker, each set up with its
settings kept in the repository; the command that checks the work runs all three and fails on what
they find.

Why: a tool finds the same thing every time and at once, where a maintainer reading for it finds
some of it and spends a change on each, and what no tool is set to show is left to be found on some
changes only.
