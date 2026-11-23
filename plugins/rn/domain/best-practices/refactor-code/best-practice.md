# `refactor-code`

## Goal tree

- Maintainers, people or AI agents who come to the code at any time, understand each part in one reading and change it in one place, as each refactoring leaves the code simple: passing its tests, saying each decision once, holding the fewest elements, and revealing its intent.
  - **C1** Each behavior and each decision of the architecture holds as before, as the tests show.
    - **N1** Do the tests that passed before the refactoring pass after it, each expecting what it expected before? (the whole)
    - **N2** Does the code still carry out each decision of the architecture: each component's job, the concept model, and each sequence? (the whole)
  - **C2** The maintainer finds the one place where a change belongs.
    - **N3** Does the code write each rule or design decision once, in the module whose job it is? (the whole)
    - **N4** Does the code do each kind of thing one way throughout, with a reason beside each difference? (the whole)
  - **C3** The code holds only the elements that its behaviors need.
    - **N5** Does each module, class, function, parameter, and kind of data serve a behavior that a test or the architecture asks for, with none that only works around another or passes a call on? (the whole)
  - **C4** The maintainer understands each part in one reading.
    - **N6** Does each name say what it holds or does, without its definition? (the whole)
    - **N7** Does each thing have one name, the architecture's word for it, and does each name refer to one thing? (the whole)
    - **N8** Can the maintainer say in one sentence what each function does after one reading from the top? (the whole)
    - **N9** Where code looks wrong or roundabout, does it say why right there? (the whole)

## Inputs

- [architecture](../architecture/best-practice.md), taking `Components`, `Concept model`, `Sequences`, `Test strategy`

## Practices

### N1

Do the tests that passed before the refactoring pass after it, each expecting what it expected before?

A refactoring changes how the code does its work and never what it does, so the maintainer trusts it only where the tests that pinned each behavior before still pass, expecting the same results. Practitioners do this by Martin Fowler's [refactoring](https://refactoring.com): a series of small steps, each of which keeps every behavior, with the tests run after each one, so that a step that broke something is still the only one to undo.

1. *While deciding.* Open the inputs of your cut, and note from the architecture each decision that the code carries out, such as a component's job or the data that one part hands another, and the command that runs the tests, since the refactoring keeps the first and runs the second.
2. *While deciding.* Where the architecture gives no command, take the one that the code's manifest gives, such as pyproject.toml or a Makefile, else the runner that the test files import, such as `python -m pytest` for files that import pytest.
3. *While deciding.* Run the command. If a test fails, change nothing, and end with `point`, naming the test and its failure, since a test that already fails can't tell you whether a step broke something.
4. *While making.* Take each change as the smallest step after which the tests can run again, such as renaming one name, moving one function, or changing the form of one kind of data, and where a step needs a second step before the tests can run, take the second first.
5. *While making.* Before each step, search the tests for each function or class that the step reaches, such as by `grep -rn parse_date tests/`, and where a behavior it reaches, such as a branch or a refusal, has no test, write one that pins what the code does now: assert a value you know is wrong, run it, and put into the assertion the value that the failure shows.
6. *While making.* Where a step renames or moves a name that a test calls, change only the test's call, and leave each expected result as it was, since a changed expectation hides a changed behavior.
7. *While making.* After each step, run the tests, and where one fails, undo the step, such as by `git restore` on the files it changed, and take a smaller one.
8. *While making.* Where a behavior looks wrong, because its name, its comment, or what its callers do with it says otherwise, leave the behavior and its test as they are, and name it in the `point` you end with, with the test that pins it, since a caller may rest on it and only the person can decide to change it.

### N2

Does the code still carry out each decision of the architecture: each component's job, the concept model, and each sequence?

The developers read the architecture to know where a part belongs and what it hands to which, so code that a refactoring moved away from it sends each of them to the wrong place. A change of a component, of the concept model, or of a sequence is a change of the architecture, which its own best practice decides before any code follows, as a refactoring changes the code's structure within the design.

1. *While deciding.* For each change that you plan, ask whether it moves a job from one component to another, adds or removes a component or a concept of the concept model, or changes what one part hands another in a sequence, by the decisions that you noted from the architecture.
2. *While deciding.* Where it does, take the change out of the plan, and name it in the `point` you end with: the smell it mends, the places it reaches, and the decision of the architecture that it changes, since the architecture is to decide it first.

### N3

Does the code write each rule or design decision once, in the module whose job it is?

A rule written in several places changes in some of them and not the others, so a maintainer's change works in one place and breaks in another. Practitioners find these places by the code smells of Fowler's [Refactoring](https://refactoring.com/catalog/), which name the shapes that make one change reach many places, and take first where the code changes most, as Adam Tornhill's hotspot analysis does from the version history.

1. *While deciding.* Run `git log --format= --name-only` on the deliverable's files, count the commits of each file, and list the files that change most, with each file that they call or that calls them, since a smell in them slows each change to come, and one in a file that never changes slows none. Where the files have no history of their own yet, as code just made, list every file, as each is new to its maintainers.
2. *While deciding.* In the files that N3.1 lists, list each place of Duplicated Code, where two places write one rule; Shotgun Surgery, where one change of a rule reaches several modules; Divergent Change, where one module changes for unrelated reasons; Feature Envy, where a function works on another module's data more than its own; Data Clumps, where the same few values travel together through several calls; and Repeated Switches, where the same choice among kinds is written in several places.
3. *While deciding.* For each place, ask whether a change of the rule would have to change every one of its copies, and take apart those that wouldn't, such as two `30`s, of which one is a timeout in seconds and the other a page size.
4. *While deciding.* For each rule that several places write, choose the module that keeps it: the one whose job, as its opening or the architecture's component says, the rule belongs to, else the one whose code reads or writes what the rule acts on, and of several, the one that the others already import, so that no two modules come to import each other.
5. *While making.* Move each rule into the module that keeps it, by Fowler's refactorings, such as Move Function, Extract Function, Combine Functions into Class, Introduce Parameter Object for a data clump, or Replace Conditional with Polymorphism for repeated switches, and have each other place use it from there.
6. *While making.* Where the places that need a rule can't read one shared definition, such as a Python module and a shell script, write at each place where the others are, such as `# Also in deploy.sh.`

### N4

Does the code do each kind of thing one way throughout, with a reason beside each difference?

When the code does each kind of thing one way, the maintainer who learned the way once reads it everywhere, and a difference tells them of a real difference.

1. *While deciding.* List the kinds of thing that several places of the code do, such as reporting an error, checking an input, reading a file, or laying out a module or a test, and for each, every way the code does it and where.
2. *While deciding.* For each kind, take the way that the project's style settings name, such as the rules of ruff in pyproject.toml, else the way that the code uses most, and where two are alike, the way nearest the place, the order of consistency that [Python's style guide](https://peps.python.org/pep-0008/#a-foolish-consistency-is-the-hobgoblin-of-little-minds) gives.
3. *While making.* Rewrite each place to the way chosen for its kind, and where the chosen way would break a caller or a limit at a place, such as a script that must exit with a code where the library raises, keep that place's way, and say why beside it.

### N5

Does each module, class, function, parameter, and kind of data serve a behavior that a test or the architecture asks for, with none that only works around another or passes a call on?

Each element is one more thing that the maintainer holds in mind on each change, so the code is simplest with the fewest elements that pass the tests and reveal the intent, the last of Kent Beck's [rules of simple design](https://martinfowler.com/bliki/BeckDesignRules.html). An element that only works around another hides the design that the code could have, so the maintainer pays for both.

1. *While deciding.* For each module of the files that N3.1 lists, write its job in one sentence from its opening and the architecture's component, and for each element of it, ask which behavior that a test or the architecture asks for fails without it.
2. *While deciding.* List each element for which none fails, and each place of Lazy Element, a function or class that adds nothing to what it calls; Middle Man, a module whose functions only pass calls on; Speculative Generality, a parameter, branch, or hook that no caller uses; Temporary Field, data set only on some paths; Message Chains, a caller that walks through several objects to reach one; and a kind of data or a mechanism that exists only to work around another, such as two records of one fact that the code keeps in step.
3. *While deciding.* For each mechanism that only works around another, write the design without the cause, such as one record where the code keeps two in step, and plan the steps that reach it, as N2 holds each change within the architecture.
4. *While making.* Remove each element that no behavior needs, and fold each lazy element and middle man into its callers, by Fowler's Remove Dead Code, Inline Function, Inline Class, Remove Middle Man, or Hide Delegate, unless an entry point in the manifest or a document that a person follows names it, since a caller outside the repository may call it.
5. *While making.* Take the planned steps toward each design without its workaround, the tests run after each, until the mechanism that it worked around is gone.

### N6

Does each name say what it holds or does, without its definition?

A name that says what it holds or does lets the maintainer read each line where it stands, without opening a definition, which Fowler's smell Mysterious Name marks where it fails.

1. *While making.* In the files that N3.1 lists, for each name that another module uses, or that the code uses far from its definition, read it at a place that uses it, and write in a few words what it holds or does from that place alone.
2. *While making.* Open the definition and compare it with those words, and where the two differ, rename the name at every place to words that say what the definition holds or does, with as many words as a reader at its farthest use needs, such as `open_orders` in place of `data`.

### N7

Does each thing have one name, the architecture's word for it, and does each name refer to one thing?

A maintainer who meets two names takes them for two things, and one name used for two things merges them in their mind, so each change misses a place or reaches a wrong one.

1. *While deciding.* List the things that the code handles, and for each, every name that the code gives it, such as `user`, `account`, and `member` for one record, by reading its types, its parameters, and its variables.
2. *While deciding.* For each thing, keep the word that the architecture's concept model or components use for it, else the name that the code uses most, and where one name refers to two things, give the other thing the architecture's word for it, else a word that tells the two apart, such as `session_id`.
3. *While making.* Rename each name that differs from the word you kept at every place, in the code, its tests, and its messages, one name in each step.

### N8

Can the maintainer say in one sentence what each function does after one reading from the top?

A maintainer who can sum up a function after one reading can change it without reading what it calls or what calls it. Fowler's smells Long Function, Long Parameter List, and Loops mark where they can't.

1. *While making.* Read each function of the files that N3.1 lists, and each function that your steps made or changed, once from the top, and write in one sentence what it does.
2. *While making.* Where the sentence needs `and` to join two tasks that a caller could want apart, such as `reads the file and checks each row`, extract each task into a function named for it. Fowler's Extract Function and Split Phase do this.
3. *While making.* Where a line stopped you in that reading, such as a nested comprehension or a chained conditional expression, or where a function mixes lines at two levels, such as a loop over the bytes of a record beside a call to `save_order`, rewrite it in a plain form or move the lower lines into a function named for what they do.
4. *While making.* Where you had to read something outside the function to write the sentence, such as a global setting it reads, make the function take that thing as a parameter.

### N9

Where code looks wrong or roundabout, does it say why right there?

A maintainer who doesn't know why odd code is there may straighten it and undo what it's there for, while a comment that says only what the code says is one more line to read past, as Fowler's smell Comments marks.

1. *While making.* Read the files that N3.1 lists as a maintainer who knows the language but not the purpose, and mark code that looks wrong, roundabout, or more than it needs, such as a sleep before a retry or a copy of a list that nothing changes.
2. *While making.* For each mark, where a name of a few words can say the reason, extract the code into a function or a constant of that name, else find the reason in the commit that brought the line, such as by `git log -L 40,42:sync.py`, or in the inputs of your cut, and write it in a comment right there.
3. *While making.* Where none of these gives the reason, leave the code unchanged, and name the line in the `point` you end with, since a guessed reason misleads the next maintainer.
4. *While making.* Remove each comment that says only what the code under it says plainly, or that holds code taken out of use, and correct each that says what the code no longer does.
