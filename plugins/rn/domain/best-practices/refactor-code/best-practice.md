# `refactor-code`

## Goal

The maintainer changes the structure of existing code toward what the code best practice asks, and every caller, whether a person, a script, or other code, still gets each behavior it got before.

## Inputs

- [code](../code/best-practice.md)

## Parts

- **tests**: The tests of each behavior the change touches, passing before the first step and after each one, with a test of what the code does now where none was.
- **steps**: Each change of structure, small enough that every behavior holds after it, and kept apart from any change of behavior, such as in a commit of its own.

## Intents

| ID | About | Question |
| --- | --- | --- |
| Q1 | tests | Before the structure changes, does the maintainer have a passing test of each behavior the change will touch, one written from what the code does now where none was, so that a step that breaks a behavior shows at once? |
| Q2 | steps, tests | Changing the structure, does the maintainer take steps so small that every test passes after each, and change no behavior in any of them, so that a failing test points at the one step that broke it and undoing that step costs nothing? |
| Q3 | steps | Choosing what to change, does the maintainer move the code toward a shortfall that a question of the code best practice names, and stop where the code answers it, so that each change makes the code easier for its maintainer to change, and not only different? |
| Q4 | the whole | After the structure changes, does each caller, whether a person, a script, or other code, get every behavior it got before, and does the code answer the question it moved toward? |

## Practices

### Q1

Before the structure changes, does the maintainer have a passing test of each behavior the change will touch, one written from what the code does now where none was, so that a step that breaks a behavior shows at once?

**Name**

Characterization test, also known as golden master testing and self-testing code

**Thinking**

Begin only from tests that all pass, as a test already failing hides the one a step breaks. Where a behavior the change will touch has no test, write one of what the code does now, and see it pass, as a refactoring is only as safe as the tests that check it. Where a behavior looks wrong, keep the behavior and its test, and report it as a point about what the code does, rather than change it here, as a change of behavior made inside a refactoring passes unseen by the tests that should have caught it.

**Applies**

Every change of structure of code that has callers.

**Excludes**

Code no one calls yet, such as a draft with no tests, is still being made. Make it test first, by the code best practice's test-driven development.

**Cost**

Tests of what the code does now take time before any change, and they pin a behavior that may be wrong until someone decides it.

**Sources**

- [Feathers, characterization test, as Wikipedia's Characterization test sums it up](https://en.wikipedia.org/wiki/Characterization_test), secondary, as the maker read only a summary of it
- [Fowler, Self Testing Code](https://martinfowler.com/bliki/SelfTestingCode.html)
- [Fowler, Definition Of Refactoring](https://martinfowler.com/bliki/DefinitionOfRefactoring.html)

**Steps**

1. Run the tests before any change, and begin only when every one passes. The trace: `{tests}` run.

### Q2

Changing the structure, does the maintainer take steps so small that every test passes after each, and change no behavior in any of them, so that a failing test points at the one step that broke it and undoing that step costs nothing?

**Name**

Refactoring, also known as behavior-preserving transformation and the two hats

**Thinking**

Change the structure in steps that each keep every behavior, such as a rename, an extracted or inlined function, or a moved one, and run the tests after each. Where a test fails, undo the step and take a smaller one, rather than mend forward, as a mend on a broken step mixes two changes the tests can't tell apart. Leave each test's expected result as it was, and change a test's call only where a name it uses changed. Change no behavior in a step of structure: a change of behavior gets a step of its own, test first, by the code best practice's test-driven development. A rearrangement that leaves the code broken for days is a restructuring, not a refactoring, and loses the safety each small step gives.

**Applies**

Each change of structure.

**Excludes**

A change the specification asks for is a change of behavior, made test first by the code best practice, with a refactoring before it where the structure makes it hard.

**Cost**

Small steps take more runs of the tests than one large change, and a slow suite makes each step costly. Keep the tests fast and alone in what they touch, as the code best practice asks of its tests.

**Sources**

- [Fowler, Definition Of Refactoring](https://martinfowler.com/bliki/DefinitionOfRefactoring.html)
- [Fowler, Refactoring Malapropism](https://martinfowler.com/bliki/RefactoringMalapropism.html)
- [Beck, Canon TDD, 2023](https://newsletter.kentbeck.com/p/canon-tdd)
- [Fowler, Refactoring, as its book page sums it up](https://martinfowler.com/books/refactoring.html), secondary, as the maker read only a summary of it

### Q3

Choosing what to change, does the maintainer move the code toward a shortfall that a question of the code best practice names, and stop where the code answers it, so that each change makes the code easier for its maintainer to change, and not only different?

**Name**

Preparatory refactoring, also known as opportunistic refactoring, refactoring toward patterns, and the campsite rule

**Thinking**

A refactoring needs a direction. Name the question of the code best practice that the code falls short of, such as a module that hides two decisions, a rule written in two places, or a name that says nothing, and change the code toward its answer. Refactor right before a change of behavior that the structure makes hard: make the change easy, then make the easy change. Refactor as you go, and leave the code better than you found it, rather than in a phase planned apart, as a long planned restructuring is the exception in code that's refactored well. Stop where the code answers the question, as refactoring past the need, and abstracting before the need shows, are mistakes of their own.

**Applies**

Each refactoring, before a change of behavior or while reading code to change it.

**Excludes**

Code that answers every question of the code best practice needs no refactoring, and one made anyway changes it for nothing.

**Cost**

Naming the shortfall takes reading the code against the code best practice before any change.

**Sources**

- [Fowler, An example of preparatory refactoring](https://martinfowler.com/articles/preparatory-refactoring-example.html)
- [Fowler, Opportunistic Refactoring](https://martinfowler.com/bliki/OpportunisticRefactoring.html)
- [Fowler, Workflows of Refactoring](https://martinfowler.com/articles/workflowsOfRefactoring/)
- [Kerievsky, Refactoring to Patterns](https://www.industriallogic.com/refactoring-to-patterns/)
- [Beck, Canon TDD, 2023](https://newsletter.kentbeck.com/p/canon-tdd)

### Q4

After the structure changes, does each caller, whether a person, a script, or other code, get every behavior it got before, and does the code answer the question it moved toward?

**Name**

Behavior preservation, also known as regression testing

**Thinking**

A caller sees more than the tests may check, such as a command's options, the form of its output, its exit codes, and the files it writes. List each caller of the code that changed, and check that each still gets what it got before, by running the tests whole and the code as each caller runs it. Then read the code against the question of the code best practice it moved toward, and check that the shortfall is gone.

**Applies**

Every refactoring, once its last step is made.

**Excludes**

A caller the change can't reach, such as code behind an interface that didn't change, needs no check of its own beyond the tests.

**Cost**

Running the code as each caller runs it takes a setup for each kind of caller.

**Sources**

- [Fowler, Definition Of Refactoring](https://martinfowler.com/bliki/DefinitionOfRefactoring.html)
- [Software Engineering at Google, chapter 11, Testing Overview](https://abseil.io/resources/swe-book/html/ch11.html)
