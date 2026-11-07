# `code`

## Goal

The maintainer, a person or an AI who takes the code over, changes what the code does as its specification asks, and knows that every other behavior still holds.

## Inputs

- [architecture](../architecture/best-practice.md)

## Parts

- **manifest**: What the maintainer needs to set the code up on a fresh machine and run its tests: everything the code runs on, with the versions, and the command that runs the tests.
- **dependency-rule**: Which module may depend on which, the core on nothing outside it, stated where a machine checks it on each change, such as a tool's settings or a test that reads the imports.
- **module**: Each module, which hides one decision of the code from the rest, and says at its top which one.
  - **interface**: Each name the module offers others, with what a caller needs to call it without reading its body: what it takes and gives, what it expects of what it takes, and each way it refuses.
  - **body**: The code under the interface that gives the behavior, its names, functions, and comments written for a maintainer who reads it once.
- **edge**: Each place where something from outside comes in, such as an argument, a file, a setting, or another program's reply, which reads it into the form the core uses or refuses it with a message that says what to put right.
- **tests**: The tests of the specification's cases, each named for the one behavior it checks, with its Given, When, and Then in view, calling the code through its interface.

## Intents

| ID | About | Question |
| --- | --- | --- |
| Q1 | module, interface | With one behavior to change, does the maintainer find the one module that holds it from what each module says it hides, without reading any body, and does the change stay inside that module, so that a change for one reason never reaches code that changes for another? |
| Q2 | dependency-rule | Testing or changing the core, does the maintainer need nothing outside it, with a port only where a real outside dependency or axis of change is, so that the core runs whole in a test and a change of technology never reaches its rules? |
| Q3 | module, body | Where the code solves a problem that a design pattern names, such as rules of one kind that are each checked alone and named in the result, does the maintainer meet that pattern by its name and in the language's lightest form, and where no such problem is, plain code with no pattern, so that they grasp a piece's intent from its name without tracing its body? |
| Q4 | body | With one rule or decision of the specification to change, does the maintainer find it written in one place, and code that looks alike but means different things kept apart, so that a change is made once and whole and never reaches a rule it didn't mean to touch? |
| Q5 | interface, body | For each behavior, option, and layer the code has, can the maintainer name the case of the specification that needs it now, so that they carry and test nothing that no one asked for? |
| Q6 | edge | When something from outside is wrong, does whoever runs the code learn from its message what was wrong, where, and what the code accepts, before the code has changed anything, so that they put it right themselves and the core never acts on a value it can't trust? |
| Q7 | tests | Drawing the test list from the specification before the code, and adding each case the work shows it missed, does the maintainer's list, as it stands at the end, take a case for each class of input the specification treats alike, each boundary between classes, each combination of conditions with its result, and each state and move between states, so that the list shows when it's enough and doesn't follow the code already written? |
| Q8 | tests, body | Writing the code, does the maintainer find each behavior made by one test from the list, seen failing, then passing, and the structure improved in a step of its own, so that each test has shown that it catches the behavior's absence and each step is small enough to undo? |
| Q9 | tests | Reading a failing test, does the maintainer see from its name which one behavior broke, and in its body the state before, the act, and the expected result with every value the result rests on, so that they find the fault without reading the test's helpers or the code's body? |
| Q10 | tests, interface | When the maintainer changes a body and its callers still get what its interface says, do the tests still pass, as they call the code through its public interface and check what it gives back or leaves, not the calls it makes inside, so that a refactoring that keeps every caller's result never breaks a test? |
| Q11 | manifest, tests | Setting the code up on a fresh machine from only what it gives for its setup, and running the tests again and in any order, does the maintainer see the same result each time, so that a failing test points at the code and never at the machine, the clock, or the order? |
| Q12 | body, tests | Reading any function once from the top, with only the names it uses, can the maintainer say in one sentence what it does, and do its names say what they hold, its kind of work look done as elsewhere, and its odd lines say why, so that they read the code once and change it without undoing what it's there for? |
| Q13 | tests | When coverage, mutation testing, or a property-based test finds a gap in the tests, does the maintainer trace it to the case the test list missed and add that case, so that the tools confirm the tests drawn from the specification and never become a target that tests are written for? |
| Q14 | the whole | With only the code and its specification, can a maintainer new to the code make a change the specification asks for, and know from the tests that every other behavior still holds? |

## Practices

### Q1

With one behavior to change, does the maintainer find the one module that holds it from what each module says it hides, without reading any body, and does the change stay inside that module, so that a change for one reason never reaches code that changes for another?

**Name**

Information hiding, also known as single responsibility principle, deep modules, and high cohesion and low coupling

**Thinking**

Design the module boundaries before the code. List the decisions the specification leaves to the code that are hard or likely to change, such as a data format, a rule, or how the code talks to another program, and give each module one of them to hide behind its interface. A module then has one reason to change, and a change of its decision stays inside it. Decompose by these decisions, not by the steps of the processing, as modules cut by steps all know the shared data, and one change of it reaches them all. Make each module deep: an interface much simpler than its body. Split a module by concern, not by length, as a module that holds several decisions changes for several reasons, and its maintainer reads all of them for any one change. Join pieces that can't be understood apart, as a module whose interface costs as much to learn as its body saves adds a place to look and hides nothing. Say at the top of each module, in a sentence, which decision it hides. Treat size as a sign to look into, such as a module past 1,000 lines, and not as a rule: the test is whether the module hides one decision behind a simple interface.

**Applies**

Every module, and each change that adds a decision to the code.

**Excludes**

A script of a few lines that makes one decision needs no split. The boundaries between the product's components, such as its processes or plugins, come from its architecture. This practice divides the code inside each. Pieces inside one module that no case needs, such as a port with one adapter, are Q2's and Q5's.

**Cost**

Finding the decisions likely to change takes thought before any code, and a boundary drawn wrong costs a move later, which the refactor-code best practice makes safe.

**Sources**

- [Parnas, On the Criteria To Be Used in Decomposing Systems into Modules, CACM 1972, as Martin's The Single Responsibility Principle sums it up](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html), secondary, as the maker read only a summary of it
- [Martin, The Single Responsibility Principle, 2014](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html)
- [Stevens, Myers and Constantine, Structured design, IBM Systems Journal 1974, as Wikipedia's Cohesion sums it up](https://en.wikipedia.org/wiki/Cohesion_(computer_science)), secondary, as the maker read only a summary of it
- [Ousterhout, Modular Design, CS190 lecture notes](https://web.stanford.edu/~ouster/cgi-bin/cs190-winter18/lecture.php?topic=modularDesign)
- [Ousterhout and Martin, A Philosophy of Software Design vs Clean Code](https://github.com/johnousterhout/aposd-vs-clean-code)
- [Dijkstra, On the role of scientific thought, EWD447, 1974](https://www.cs.utexas.edu/~EWD/transcriptions/EWD04xx/EWD447.html)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

### Q2

Testing or changing the core, does the maintainer need nothing outside it, with a port only where a real outside dependency or axis of change is, so that the core runs whole in a test and a change of technology never reaches its rules?

**Name**

Dependency inversion principle, also known as ports and adapters, hexagonal architecture, and the Dependency Rule

**Thinking**

The core, the code that holds the specification's rules, depends on nothing outside it, such as the file system, another process, the network, the clock, or a framework. Where the core needs one of these, it declares what it needs as an interface it owns, a port, and an adapter at the edge implements the port for the technology. The source dependencies then point inward, and the core runs whole in a test with a fake for each port. Put a port only where a real outside dependency or a real axis of change is, such as the file system, another program, or the protocol the code is called by, and none between pieces inside the core, as a layer added only so that a test can stand in for it makes the code harder to change and tests nothing real. Give a port the language's lightest form, such as a function passed in or a structural type, before a class hierarchy. State which module may depend on which as a rule, and have a machine check it on each change: a tool that checks module dependency rules where the language has one, else a test that reads each module's imports, else the evaluator reads it. The plan picks the way for each deliverable.

**Applies**

Code whose rules touch anything outside the process, or that more than one kind of caller drives, such as a person and a test.

**Excludes**

A script whose whole job is to talk to one outside thing, such as a command that only copies files, has no core to keep apart. Test it at the level that runs it real.

**Cost**

Each port adds an interface, an adapter, and a fake that must stay true to the real thing, and the fake needs tests of its own.

**Sources**

- [Cockburn, Hexagonal architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [Martin, The Clean Architecture, 2012](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Fowler, Beck and Hansson, Is TDD Dead?, 2014](https://martinfowler.com/articles/is-tdd-dead/)
- [Import Linter, a tool that checks module dependency rules in Python](https://import-linter.readthedocs.io/en/stable/)
- [PEP 544, Protocols: Structural subtyping](https://peps.python.org/pep-0544/)

### Q3

Where the code solves a problem that a design pattern names, such as rules of one kind that are each checked alone and named in the result, does the maintainer meet that pattern by its name and in the language's lightest form, and where no such problem is, plain code with no pattern, so that they grasp a piece's intent from its name without tracing its body?

**Name**

Design patterns, also known as refactoring to patterns

**Thinking**

A pattern is a known solution to a recurring problem in a context, under a name that carries its intent to anyone who knows it. Use one where the problem matches its intent, such as Specification for rules that are each checked and named alone, Strategy for interchangeable ways of doing one thing, or Gateway for wrapping an outside resource, and name the piece after it, so that its name tells the maintainer what it's for. Take the language's lightest form: where functions are values, Strategy and Command are functions, not classes. Write the plain form first, and refactor toward a pattern when the need shows, such as at the third rule of a kind, as a pattern put in early guesses at a need, and a pattern that doesn't pull its weight is complexity with no return. Take a pattern out where it no longer serves.

**Applies**

A recurring problem whose shape a catalog of patterns names, in code that grows toward it.

**Excludes**

Code whose problem matches no pattern's intent stays plain, as a pattern forced on it hides the plain solution.

**Cost**

The maintainer must know a pattern for its name to help them, and a piece named for a pattern it isn't misleads more than no name.

**Sources**

- [Fowler, Is Design Dead?](https://martinfowler.com/articles/designDead.html)
- [Kerievsky, Refactoring to Patterns](https://www.industriallogic.com/refactoring-to-patterns/)
- [Norvig, Design Patterns in Dynamic Languages, 1996, as a search result sums it up](https://norvig.com/design-patterns/), secondary, as the maker read only a summary of it
- [Fowler, Catalog of Patterns of Enterprise Application Architecture](https://martinfowler.com/eaaCatalog/)
- [Gamma et al. 1994, as Wikipedia's Software design pattern sums it up](https://en.wikipedia.org/wiki/Software_design_pattern), secondary, as the maker read only a summary of it
- [Evans and Fowler, Specifications, as Wikipedia's Specification pattern sums it up](https://en.wikipedia.org/wiki/Specification_pattern), secondary, as the maker read only a summary of it

### Q4

With one rule or decision of the specification to change, does the maintainer find it written in one place, and code that looks alike but means different things kept apart, so that a change is made once and whole and never reaches a rule it didn't mean to touch?

**Name**

Don't repeat yourself, also known as DRY, once and only once, and single source of truth

**Thinking**

Each piece of knowledge has one place in the code that holds it, such as a limit, a format, a path, or a rule, and every other place takes it from there. DRY is about knowledge, not text: two pieces of code that look alike but would change for different reasons are duplicates by accident, and they stay apart, as one abstraction over both ties a change of one to the other. Wait for evidence before you abstract, such as a third copy of the same knowledge, as a wrong abstraction costs more than the duplication it removed. Where an abstraction turns out wrong, such as a shared function that grows a flag for each caller, inline it back into each caller and look again. Where a piece of knowledge can't live in one place, such as a value that a script and its documentation both state, say at each place where the others are. A machine finds copied code, such as a check for duplicate code. Only the reader can tell whether two copies are one piece of knowledge.

**Applies**

The code, and each rule or value it holds.

**Excludes**

In tests, a little repetition that lets each test read on its own wins, as Q9 says.

**Cost**

Waiting for the third copy leaves two copies to change together for a while, and judging what's one piece of knowledge takes a reader who knows the specification.

**Sources**

- [Hunt and Thomas, The Pragmatic Programmer, as Wikipedia's Don't repeat yourself sums it up](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself), secondary, as the maker read only a summary of it
- [Metz, The Wrong Abstraction, 2016](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction)
- [Beck, Canon TDD, 2023](https://newsletter.kentbeck.com/p/canon-tdd)
- [Fowler, Beck Design Rules](https://martinfowler.com/bliki/BeckDesignRules.html)
- [Fowler, Refactoring, as its book page sums it up](https://martinfowler.com/books/refactoring.html), secondary, as the maker read only a summary of it

### Q5

For each behavior, option, and layer the code has, can the maintainer name the case of the specification that needs it now, so that they carry and test nothing that no one asked for?

**Name**

You aren't gonna need it, also known as YAGNI

**Thinking**

The code gives the behaviors the specification asks for now, in the form its cases ask for. A capability built on a guess that it'll be needed costs its building, the delay of what was needed, the weight it adds to every later change, and its repair when the guess proves wrong. YAGNI holds only while the code stays easy to change, which its tests and its design keep it. It doesn't excuse skipping the design, and it doesn't hold against what makes the code easier to change, such as a clear boundary. A function or a layer that only passes a call on, and a parameter to which every caller gives the same value, are weight of this kind. Fold them in.

**Applies**

Each option, mode, layer, and case the code handles.

**Excludes**

A boundary that the design draws for a decision likely to change is no guess, as Q1 says, and stays.

**Cost**

A need that comes later costs a change then, which the tests and the design keep small.

**Sources**

- [Fowler, Yagni](https://martinfowler.com/bliki/Yagni.html)
- [Fowler, Is Design Dead?](https://martinfowler.com/articles/designDead.html)
- [Fowler, Beck Design Rules](https://martinfowler.com/bliki/BeckDesignRules.html)

### Q6

When something from outside is wrong, does whoever runs the code learn from its message what was wrong, where, and what the code accepts, before the code has changed anything, so that they put it right themselves and the core never acts on a value it can't trust?

**Name**

Input validation at the trust boundary, also known as parse, don't validate and fail fast

**Thinking**

Check what comes from outside where it comes in, before the code acts on it, such as arguments, files, settings, the environment, and the replies of other programs. Check its form and type, then whether its value makes sense for what the code is to do, such as an end that comes after its start. Accept what the rules allow and refuse the rest, rather than try to name every bad value. Read the input into the form the core uses, so that the core holds only values already checked and checks nothing again, as checks spread through the code find a bad input after part of the work is done, and leave the data half changed. Write each check so that it runs however the code is run, and not as an assertion a setting can turn off. Catch only the error you mean to handle. A refusal's message says which program refused, what was wrong and where, and what it accepts or how to fix it, as a message that says only that something failed leaves the person stuck and hands the fault to the maintainer.

**Applies**

Every place where data crosses into the code from something it doesn't control, its own stored files and other internal sources among them.

**Excludes**

A value that passes between modules inside the core, which the edge has already checked, needs no check again. The interface says what each module expects.

**Cost**

Each edge holds a reader and a message for each way it refuses, and a test of each.

**Sources**

- [OWASP, Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [King, Parse, don't validate, 2019](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/)
- [Google, Writing Helpful Error Messages](https://developers.google.com/tech-writing/error-messages)

### Q7

Drawing the test list from the specification before the code, and adding each case the work shows it missed, does the maintainer's list, as it stands at the end, take a case for each class of input the specification treats alike, each boundary between classes, each combination of conditions with its result, and each state and move between states, so that the list shows when it's enough and doesn't follow the code already written?

**Name**

Specification-based test design, also known as black-box test design, equivalence partitioning, boundary value analysis, decision table testing, and state transition testing

**Thinking**

Draw the test list from the specification, not from the code, as cases drawn from the code follow what it already does and pass on its maker's own assumptions. Divide each input and each result the specification names into classes it treats alike, the refused ones among them, and take one case from each. Where a class ends on an ordered scale, such as a length or a count, take the value at each edge and the nearest value across it, as faults gather at edges. Where a result turns on a combination of conditions, list each combination that can occur with its result, as such a table shows a rule missing or two that contradict. Where a behavior depends on what came before, draw the states and the moves between them, and take each move, the refused ones among them. Write each expected value from the specification, as one copied from what the code gives checks nothing. Add to the list as the work shows a case it missed. These techniques draw the cases of a unit. The architecture best practice says what each level above it tests.

**Applies**

Each unit's tests, before its code.

**Excludes**

A level above the unit draws its tests from what it checks against, such as the paths of a sequence, as the architecture best practice says.

**Cost**

The list takes time before any code, and a wide specification gives a long one. Take one case from each class, not each value.

**Sources**

- [ISTQB Certified Tester Foundation Level v4.0, chapter 4, as ASTQB sums it up](https://study.astqb.org/?p=22), secondary, as the maker read only a summary of it
- [Beck, Canon TDD, 2023](https://newsletter.kentbeck.com/p/canon-tdd)
- [Vocke, The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)

**Steps**

1. Read each input whole, the specification among them, before you list the cases. The trace: `{inputs}` read to its end.

### Q8

Writing the code, does the maintainer find each behavior made by one test from the list, seen failing, then passing, and the structure improved in a step of its own, so that each test has shown that it catches the behavior's absence and each step is small enough to undo?

**Name**

Test-driven development, also known as Canon TDD, red-green-refactor, and test-first

**Thinking**

Take one test from the list at a time. Write it, run it, and see it fail for the reason its case names, as a test that never failed hasn't shown that it can catch the behavior's absence. Write the least code that makes it pass, and run every test. Then improve the structure with every test passing, and change no behavior in that step, as a step that changes both can't tell a broken behavior from a broken refactoring. Repeat until the list is empty. Don't turn the whole list into tests at once, don't delete an assertion to get a pass, and don't abstract before the tests show the need. Writing the test is where you design the interface, how a caller calls the behavior, and refactoring is where you design the body. Keep each cycle small and steady, as the evidence ties quality to small, even cycles more than to the order of test and code alone.

**Applies**

Each behavior whose result the specification states before the code exists.

**Excludes**

Where the behavior isn't known yet, such as how an outside program answers, explore first, throw that code away, then make the behavior test first. Where the design is still open across many features, design the module boundaries first, as Q1 says, then run the cycle inside them.

**Cost**

The first tests come before any working code, and a test that fails for the wrong reason costs a look at why.

**Sources**

- [Beck, Canon TDD, 2023](https://newsletter.kentbeck.com/p/canon-tdd)
- [Fucci et al., A Dissection of the Test-Driven Development Process, IEEE TSE 2016](https://arxiv.org/abs/1611.05994)
- [Fowler, Beck and Hansson, Is TDD Dead?, 2014](https://martinfowler.com/articles/is-tdd-dead/)
- [Ousterhout and Martin, A Philosophy of Software Design vs Clean Code](https://github.com/johnousterhout/aposd-vs-clean-code)
- [Fowler, Self Testing Code](https://martinfowler.com/bliki/SelfTestingCode.html)

**Steps**

1. Run the tests, and see the new test fail, before you write the code that makes it pass. The trace: `{tests}` run.

### Q9

Reading a failing test, does the maintainer see from its name which one behavior broke, and in its body the state before, the act, and the expected result with every value the result rests on, so that they find the fault without reading the test's helpers or the code's body?

**Name**

Given-When-Then, also known as Arrange-Act-Assert, Four-Phase Test, and DAMP

**Thinking**

A test checks one behavior, and its name says that behavior, as a test named for a function breaks for any of its behaviors and names none. Lay each test out in three parts, the state before, the act, and the expected result, such as Given, When, and Then. Keep logic out of tests, such as loops, conditions, and computed expected values, as a test that would need a test of its own checks nothing anyone trusts. Prefer descriptive and meaningful phrases to removing every repetition: each test shows its own inputs and expectations, and a helper builds the object under test or asserts one fact, and hides no value the assertion rests on. Hold the test code to the same design and readability as the code, and to the limits a machine measures on it, as a test the maintainer can't read is one they delete or mend wrongly. A failure's message says what was expected, what came, and the inputs that matter.

**Applies**

Every test, at every level.

**Excludes**

A test that runs one behavior over a table of listed cases may loop over the table, where each row names its case and a failure names the row.

**Cost**

Tests come out longer than a shared, compact form, and a change to a shared setup is made in each test that writes it out.

**Sources**

- [Fowler, Given When Then](https://martinfowler.com/bliki/GivenWhenThen.html)
- [Wake, 3A: Arrange, Act, Assert, 2001](https://xp123.com/3a-arrange-act-assert/)
- [Software Engineering at Google, chapter 12, Unit Testing](https://abseil.io/resources/swe-book/html/ch12.html)
- [Google Testing Blog, Tests Too DRY? Make Them DAMP!, 2019, as its title and comments show](https://testing.googleblog.com/2019/12/testing-on-toilet-tests-too-dry-make.html), secondary, as the maker read only a summary of it
- [Beck, Test Desiderata](https://testdesiderata.com/)

### Q10

When the maintainer changes a body and its callers still get what its interface says, do the tests still pass, as they call the code through its public interface and check what it gives back or leaves, not the calls it makes inside, so that a refactoring that keeps every caller's result never breaks a test?

**Name**

Test doubles, also known as classicist testing, sociable unit tests, and testing through the public interface

**Thinking**

Call the code through its public interface, as its callers do, and check the result or the state it leaves, not the calls it makes inside, as a test of a private part or of inner calls fails on each refactoring and passes when a caller breaks. Use the real collaborator where it runs fast and wholly inside the test. Next prefer a fake, a small working stand-in true to the real thing's contract, with tests of its own. Use a stub or a mock only where neither serves. Keep mocks, which check the calls made, for dependencies outside the process that the code doesn't own and whose calls others see, such as a message sent or a mail, and use a dependency the code owns, such as its own files, for real. Never mock a collaborator inside the code, as that ties the test to how the code is built. Draw a double of something outside from its documentation or from a recorded run of the real thing, so that it gives only what the real one would.

**Applies**

Every test that has collaborators.

**Excludes**

A level whose job is to run the outside world real, such as a trial of the whole product, uses no double for it. Whether each behavior has a test is Q7's, and a test that asserts nothing is Q13's.

**Cost**

Tests that use real collaborators run more code and can fail for a fault in one, which the collaborator's own tests then name.

**Sources**

- [Fowler, Test Double, quoting Meszaros, xUnit Test Patterns](https://martinfowler.com/bliki/TestDouble.html)
- [Fowler, Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html)
- [Fowler, Unit Test](https://martinfowler.com/bliki/UnitTest.html)
- [Software Engineering at Google, chapter 13, Test Doubles](https://abseil.io/resources/swe-book/html/ch13.html)
- [Khorikov, When to Mock](https://enterprisecraftsmanship.com/posts/when-to-mock/)
- [Vocke, The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)

### Q11

Setting the code up on a fresh machine from only what it gives for its setup, and running the tests again and in any order, does the maintainer see the same result each time, so that a failing test points at the code and never at the machine, the clock, or the order?

**Name**

Hermetic tests, also known as test isolation and deterministic tests

**Thinking**

What the code gives for its setup names everything it needs to run and to run its tests, with the versions it runs on. Each test sets up and clears all it uses, shares no state with another, and reads nothing of the machine it isn't given, such as the user's settings, the time of day, the network, or a random value it doesn't seed. A real tool the tests run does only what the test asks of it, so turn off what it does on its own, such as reading the machine's settings or starting work in the background. A test whose result changes from run to run teaches the maintainer to ignore failures. Try the setup on a clean machine, and run the tests several times in a shuffled order.

**Applies**

Every test, and what the code gives for its setup.

**Excludes**

A test whose subject varies by nature, such as one that runs an AI, states how many runs of how many must pass, as the architecture best practice says.

**Cost**

Each test sets up its own world, which takes time to write and to run, and a clean machine takes setting up.

**Sources**

- [Beck, Test Desiderata](https://testdesiderata.com/)
- [Software Engineering at Google, chapter 11, Testing Overview](https://abseil.io/resources/swe-book/html/ch11.html)
- [Software Engineering at Google, chapter 12, Unit Testing](https://abseil.io/resources/swe-book/html/ch12.html)

### Q12

Reading any function once from the top, with only the names it uses, can the maintainer say in one sentence what it does, and do its names say what they hold, its kind of work look done as elsewhere, and its odd lines say why, so that they read the code once and change it without undoing what it's there for?

**Name**

Intention-revealing code, also known as the rules of simple design and readable code

**Thinking**

Write for the reader while you write, not in a pass after. A name says in whole words what it holds or does, more the farther from its definition it's read. Each thing has one name, the one its users and documents use, as two names for one thing, or one for two, sends the maintainer to the definitions. A function does one thing at one level and takes what it uses as its inputs, so that its reader holds in mind only what it says. One whose summary needs an "and" does two. Keep each function simple enough to grasp and to test, its cyclomatic complexity under McCabe's established limit of 10, or up to 15 where the team has the reasons and the testing to match, measured by a machine with the function's size on the code and its tests alike. The plan picks the tool and any other limit for each deliverable. Do each kind of thing one way throughout, such as reporting an error or reading a file, the way the code already does it unless a better way replaces it everywhere, so that a difference the maintainer meets means a real one. Where the code can't say why it's so, such as a limit outside it or a way tried and dropped, say why in a comment beside it, and say nothing the code already says. Write a clever construct in its plain form.

**Applies**

Every function, name, and comment, of the code and of its tests.

**Excludes**

A generated file, or a table of data that a tool reads, is read by that tool and not by the maintainer, and is held to the tool's form.

**Cost**

Writing for the reader slows the first draft, and a limit a machine measures sometimes splits a function its reader would rather read whole. Where that's so, say why beside it.

**Sources**

- [Fowler, Beck Design Rules](https://martinfowler.com/bliki/BeckDesignRules.html)
- [Watson and McCabe, Structured Testing: A Testing Methodology Using the Cyclomatic Complexity Metric, NIST Special Publication 500-235, 1996](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication500-235.pdf)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Ousterhout and Martin, A Philosophy of Software Design vs Clean Code](https://github.com/johnousterhout/aposd-vs-clean-code)
- [Fowler, Refactoring, as its book page sums it up](https://martinfowler.com/books/refactoring.html), secondary, as the maker read only a summary of it

### Q13

When coverage, mutation testing, or a property-based test finds a gap in the tests, does the maintainer trace it to the case the test list missed and add that case, so that the tools confirm the tests drawn from the specification and never become a target that tests are written for?

**Name**

Test adequacy criteria, also known as code coverage, mutation testing, and property-based testing

**Thinking**

These tools show where the tests fall short, and draw no tests themselves. Coverage shows a line or a branch that no test runs, and says only that a line ran, not that a test checked what it did. Mutation testing changes the code in small ways and shows each change no test notices, the strongest check of whether the tests check the behavior. A property-based test states what must hold for every input in a range, makes inputs, and shrinks a failure to its smallest form, which finds edges no one listed. For each gap, ask which class, boundary, rule, or state the test list missed, add that case to the list, and write its test by the cycle of Q8. Don't write a test only to move a number, as a test with no assertion raises coverage and checks nothing. Mark a change that alters no behavior, or a line of no interest such as logging, to be left out, and count the marks beside the survivors, so that a lower count can't come from more marks. Read a number as a sign to look into, not a target. The plan sets where each tool runs, such as on each change in CI, and any threshold for each deliverable.

**Applies**

The tests of every unit, once they pass.

**Excludes**

A tool's finding that no case of the specification explains, such as a mutant of code that no case needs, points at the code, not the tests. Take the code out, as Q5 says.

**Cost**

Mutation testing runs the tests once for each change it makes, which takes long on a large code base, and a property-based test needs a tool and properties to state.

**Sources**

- [Fowler, Test Coverage](https://martinfowler.com/bliki/TestCoverage.html)
- [Petrović and Ivanković, State of Mutation Testing at Google, ICSE-SEIP 2018](https://research.google/pubs/state-of-mutation-testing-at-google/)
- [Petrović, Ivanković, Fraser and Just, Practical Mutation Testing at Scale, 2021](https://arxiv.org/abs/2102.11378)
- [MacIver, In praise of property-based testing](https://increment.com/testing/in-praise-of-property-based-testing/)
- [Arguelles, Ivanković and Bender, Code Coverage Best Practices, Google Testing Blog 2020, as a search result sums it up](https://testing.googleblog.com/2020/08/code-coverage-best-practices.html), secondary, as the maker read only a summary of it
- [Beck, Canon TDD, 2023](https://newsletter.kentbeck.com/p/canon-tdd)
- [Cosmic Ray, a mutation testing tool for Python](https://cosmic-ray.readthedocs.io/en/latest/)
- [Hypothesis, a property-based testing tool for Python](https://hypothesis.readthedocs.io/en/latest/)

### Q14

With only the code and its specification, can a maintainer new to the code make a change the specification asks for, and know from the tests that every other behavior still holds?

**Name**

Maintainability, also known as analysability, modifiability, and testability

**Thinking**

Only a change made by someone new to the code shows whether the code lets them change it and trust the result. Have someone who hasn't seen the code, a person or an AI, set it up and make one change the specification asks for, with the code and its specification alone. Note each body they read to find the place or to write a call, each time they couldn't tell whether another behavior broke, and each message of a wrong input that didn't tell them how to put it right. Trace each note to the question whose practice falls short, and mend the code there.

**Applies**

Code handed over to its maintainer, and again after a change to its design.

**Excludes**

The trial shows whether the whole serves the maintainer. It doesn't show which question falls short, which each note traced to its question shows.

**Cost**

Each trial needs a maintainer who hasn't seen the code, and a change the specification could ask for.

**Sources**

- [ISO/IEC 25010, Maintainability, as iso25000.com sums it up](https://iso25000.com/en/iso-25000-standards/iso-25010?start=4), secondary, as the maker read only a summary of it
- [Ousterhout and Martin, A Philosophy of Software Design vs Clean Code](https://github.com/johnousterhout/aposd-vs-clean-code)
