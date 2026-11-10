# `refactor-code`

## Goal

Maintainers, people or AI agents who come to the code at any time, change it quickly without breaking another behavior.

## Critical success factors

| ID | Factor |
| --- | --- |
| C1 | Every caller gets the same behavior after a change of structure. |
| C2 | The maintainer understands each part in one reading. |
| C3 | The maintainer finds the one place where a change belongs. |

## Necessary conditions

| ID | Factor | Condition | Sections |
| --- | --- | --- | --- |
| N1 | C1 | After a change of structure, does each caller, whether a person, a script, or other code, get every behavior it got before? | the whole |
| N2 | C2 | Does each line, whether code or a comment, give the maintainer something they need? | the whole |
| N3 | C2 | Does each name say what it holds or does, without its definition? | the whole |
| N4 | C2 | Does each thing have one name, and does each name refer to one thing? | the whole |
| N5 | C2 | Can the maintainer say in one sentence what each function does after one reading from the top? | the whole |
| N6 | C2 | Where code looks wrong or roundabout, does it say why right there? | the whole |
| N7 | C3 | Does the code write each rule or design decision once, in the module that has that job? | the whole |
| N8 | C3 | Does the code do each kind of thing the same way throughout, with a reason beside each difference? | the whole |

## Practices

### N1

After a change of structure, does each caller, whether a person, a script, or other code, get every behavior it got before?

A change of structure is safe only if no caller can tell it happened. Martin Fowler's [refactoring](https://refactoring.com) changes the structure in small steps, each of which keeps every behavior, checked by the tests from before the change.

1. *While making.* Run the tests before any change, and begin only when every one passes. The trace: `{tests}` run.
2. *While making.* Decide each step by asking whether the tests can tell you it kept every behavior.
3. *While making.* Where a behavior that the change reaches has no test, write a test of what the code does now, and see it pass.
4. *While making.* If a step is too big to check, make a smaller one.
5. *While making.* After each small change of structure, such as a rename or a moved function, run the tests. Where a test fails, undo the change, and make a smaller one.
6. *While making.* Leave each test's expected result as it was, and change a test's call only where the change renamed a name it uses.
7. *While making.* Keep a behavior that looks wrong, along with its test.
8. *While making.* Report a behavior that looks wrong as a point about what the code does, instead of changing it here.

### N2

Does each line, whether code or a comment, give the maintainer something they need?

Every line costs the maintainer reading time. The method is the removal of the smells Lazy Element, Speculative Generality, Middle Man, and Comments in Martin Fowler's Refactoring, second edition.

1. *While making.* For each line, ask what the maintainer would lose without it. Remove what gives them nothing, since version control keeps it.
2. *While making.* Fold into its caller each function or layer that only passes a call on.
3. *While making.* Drop each parameter to which every caller gives the same value.
4. *While making.* Keep a comment that says what the code can't say plainly, such as what a regular expression matches.

### N3

Does each name say what it holds or does, without its definition?

A name that says what it holds lets the maintainer read each line without going to a definition. The method is the intention-revealing names of Robert C. Martin's Clean Code, with longer names for wider scopes.

1. *While making.* For each name, write in a few words what it holds or does without looking at its definition.
2. *While making.* Compare those words with the definition, and rename the name where the two differ.
3. *While making.* Make a name say more the farther from its definition the maintainer reads it.

### N4

Does each thing have one name, and does each name refer to one thing?

A maintainer who meets two names takes them for two things, and one name used for two things merges them. The method is the ubiquitous language of Eric Evans's Domain-Driven Design: the code names each thing with the word its users use.

1. *While making.* List the things the code handles, and the names the code gives each.
2. *While making.* For each thing, keep the word its users already use, such as the one in its documents.
3. *While making.* If two names refer to one thing, keep one.
4. *While making.* If one name refers to two things, give one of them another name.

### N5

Can the maintainer say in one sentence what each function does after one reading from the top?

A function that does one thing at one level, and takes what it uses as inputs, asks its reader to hold only what it says. The method is the Composed Method of Kent Beck's Smalltalk Best Practice Patterns: each method does one identifiable task, with all its operations at one level of abstraction.

1. *While making.* Read each function, test functions included, once from the top, and write in one sentence what it does.
2. *While making.* If the sentence needs `and`, or you had to read another body, split the function, or make it take what it reached for as an input.
3. *While making.* Write a long function as calls to steps, each named for what it does.
4. *While making.* Join back two functions that the reader can't understand apart.
5. *While making.* Write a clever construct in its plain form.
6. *While making.* Read each changed function once from the top as a maintainer new to it, and check that you can say in one sentence what it does.

### N6

Where code looks wrong or roundabout, does it say why right there?

A maintainer who doesn't know why odd code is so may undo what it's there for. The method is the Comments smell of Martin Fowler's Refactoring: first change the code until it says the point itself, and comment only where it can't.

1. *While making.* Read each line as a maintainer who knows the language but not the purpose, and mark code that looks wrong, roundabout, or more than it needs.
2. *While making.* For each mark, make the code say it plainly where it can.
3. *While making.* Where the code can't say it, state the reason right there, such as a limit outside the code or a way tried and dropped.
4. *While making.* Check each comment against the code beside it, and correct or remove one that no longer holds.

### N7

Does the code write each rule or design decision once, in the module that has that job?

A rule written in several places changes in some of them and not the others. The method is the principle Don't Repeat Yourself of Andy Hunt and Dave Thomas's The Pragmatic Programmer: each piece of knowledge has one authoritative place in the system.

1. *While making.* For each rule or design decision the code holds, such as a limit, a format, or a path, list every place that writes it.
2. *While making.* Keep one of those places, in the module that has that job.
3. *While making.* Leave apart things that only look alike but differ in meaning.
4. *While making.* Where a shared function takes flags so that each caller gets its own path, split it into one function for each rule.
5. *While making.* Where code reaches into another module's insides, have it use what that module offers its callers.
6. *While making.* Where the code truly can't keep a rule in one place, say at each place where the others are, such as in a comment beside it.
7. *While making.* Pick one rule, imagine that it changed, and count the places that would change. Change the code until that count is one.

### N8

Does the code do each kind of thing the same way throughout, with a reason beside each difference?

When the code does each kind of thing one way, a difference means a real difference. The method is the consistency rule of [Python's style guide](https://peps.python.org/pep-0008/#a-foolish-consistency-is-the-hobgoblin-of-little-minds): consistency within a module matters most, then consistency within the project.

1. *While making.* List the kinds of thing the code does in many places, such as reporting an error, checking an input, reading a file, or laying out a module or a test.
2. *While making.* For each kind, gather each way the code does it.
3. *While making.* Keep the way that the code already uses most.
4. *While making.* Where the code uses two ways alike, keep the way of the code nearest to the place.
5. *While making.* Choose a better way only where it replaces the others everywhere.
6. *While making.* Where a place needs another way, say why beside it, such as in a comment.
