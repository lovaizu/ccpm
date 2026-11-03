# code

## Goal

The maintainer, a person or an AI who takes the code over, changes what it does and knows that whoever runs it still gets each behavior its specification asks and, where something from outside is wrong, learns how to put it right.

## Parts

- **manifest**: What the maintainer needs to set the code up on a fresh machine and run its tests: all the code needs to run, with the versions it runs on, and how to run the tests.
- **module-opening**: For each module, what this module alone decides, said briefly where the maintainer meets it first on opening the module.
- **interface**: Each name a module offers to others, with all a caller needs to call it without reading its body: the types it takes and gives, what it gives, what it expects of what it takes and each way it refuses.
- **body**: The code under each interface that gives the behavior.
- **tests**: Tests that hold the specification's cases, one test for each case, so the maintainer can tell which test checks which case and which code: each named for the behavior it holds, and each showing the situation, what is done and what must be so.

## Benefits

- **Q1** (manifest, tests): Setting the code up on a fresh machine from what the code gives for its setup alone, and running the tests again and in any order, does the maintainer see them pass each time?
- **Q2** (module-opening): With one behavior to change, can the maintainer tell which module to open from what each module says it alone decides, without reading their bodies?
- **Q3** (interface): Calling a name another module offers, can the maintainer write a call that works from its interface alone, without reading its body?
- **Q4** (interface, body): For each behavior the code has, can the maintainer name the case of the specification that needs it?
- **Q5** (body): When something the code takes from outside is wrong, can whoever ran it put it right from what the code tells them alone, with nothing left half done?
- **Q6** (tests): For each case the specification names, its edges and refusals included, can the maintainer point to the one test that holds it, and tell the case from the test's name?
- **Q7** (interface, tests): When the maintainer changes a body and its callers still get what its interface says, do the tests still pass?
- **Q8** (body, tests): When the maintainer breaks the behavior a test holds, does that test fail?
- **Q9** (the whole): Given the code and its specification alone, can the maintainer make a change the specification asks and know from the tests that every other behavior still holds?

## Practices

### Q1: Setting the code up on a fresh machine from what the code gives for its setup alone, and running the tests again and in any order, does the maintainer see them pass each time?

**Thinking**: What the code gives for its setup names all the code needs, and each test sets up and clears all it uses, so a test's result rests on the code alone.

**Steps**

1. Set the code up on a clean machine or container, from what the code gives for its setup alone.
2. Add to what the setup reads each thing the setup or the tests found missing, such as a runtime or a library, with the versions the code runs on.
3. Run the tests several times, and in a shuffled order.

**Grounds**

- [The Twelve-Factor App](https://12factor.net/dependencies), Wiggins, II. Dependencies, 12factor.net, 2017: "A twelve-factor app never relies on implicit existence of system-wide packages. It declares all dependencies, completely and exactly, via a dependency declaration manifest."
- [The Twelve-Factor App](https://12factor.net/dependencies), Wiggins, II. Dependencies, 12factor.net, 2017: "One benefit of explicit dependency declaration is that it simplifies setup for developers new to the app."
- [Repeatable Installs](https://pip.pypa.io/en/stable/topics/repeatable-installs/), pip developers, pip documentation, 2026: "Pinning package versions of your dependencies in the requirements file protects you from bugs or incompatibilities in newly released versions"
- [Testing Overview](https://abseil.io/resources/swe-book/html/ch11.html), Bender, Software Engineering at Google, ch. 11, abseil.io, 2020: "All tests should strive to be hermetic: a test should contain all of the information necessary to set up, execute, and tear down its environment. Tests should assume as little as possible about the outside environment, such as the order in which the tests are run."
- [Testing Overview](https://abseil.io/resources/swe-book/html/ch11.html), Bender, Software Engineering at Google, ch. 11, abseil.io, 2020: "It doesn’t take needing to investigate many flakes before a team loses trust in the test suite. After that happens, engineers will stop reacting to test failures, eliminating any value the test suite provided."
- [Test Desiderata](https://testdesiderata.com/), No author named, testdesiderata.com, no date: "Isolated — tests should return the same results regardless of the order in which they are run."

### Q2: With one behavior to change, can the maintainer tell which module to open from what each module says it alone decides, without reading their bodies?

**Thinking**: Each module alone decides one thing the specification leaves to the code, and says that thing briefly where the maintainer meets it first, such as at its top.

**Steps**

1. Where that cannot be said briefly, split the module.
2. Take a behavior the specification might change, read only what the modules say they decide, and check that it points to one module; where it does not, rewrite it or move the decision.

**Grounds**

- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html), Google, google.github.io/styleguide, no date: "Files should start with a docstring describing the contents and usage of the module."
- [Documentation](https://abseil.io/resources/swe-book/html/ch10.html), Manshreck, Software Engineering at Google, ch. 10, abseil.io, 2020: "The key win for stumblers is clearly identifying the purpose of an API, often at the top of a file header."
- [Documentation](https://abseil.io/resources/swe-book/html/ch10.html), Manshreck, Software Engineering at Google, ch. 10, abseil.io, 2020: "Any API that cannot be succinctly described in the first paragraph or two is usually the sign of an API that is not well thought out. Consider breaking the API into separate components in those cases."

### Q3: Calling a name another module offers, can the maintainer write a call that works from its interface alone, without reading its body?

**Thinking**: The interface tells a caller all they need to call it, so the body can stay unread and can change behind it.

**Steps**

1. Choose the names other modules may use, and mark every other name as internal.
2. Say for each name the types it takes and gives, such as in its signature where the language allows.
3. Write beside it, such as in a doc comment, what it gives, what comes back when there is nothing to give, what it expects of what it takes, what else it changes, and each way it refuses a right call.
4. Leave out of that what the types already say.
5. Have someone who has not read the body write a call from the interface alone, and run it; where it fails or they had to guess, add what was missing.

**Grounds**

- [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/), van Rossum, Warsaw and Coghlan, peps.python.org, 2001: "All undocumented interfaces should be assumed to be internal."
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html), Google, google.github.io/styleguide, no date: "Type annotations improve the readability and maintainability of your code. The type checker will convert many runtime errors to build-time errors"
- [PEP 257 – Docstring Conventions](https://peps.python.org/pep-0257/), Goodger and van Rossum, peps.python.org, 2001: "The docstring for a function or method should summarize its behavior and document its arguments, return value(s), side effects, exceptions raised, and restrictions on when it can be called (all if applicable)."
- [PEP 257 – Docstring Conventions](https://peps.python.org/pep-0257/), Goodger and van Rossum, peps.python.org, 2001: "However, the nature of the return value cannot be determined by introspection, so it should be mentioned."
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html), Google, google.github.io/styleguide, no date: "For example, a function that mutates one of its arguments as a side effect should note that in its docstring."
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html), Google, google.github.io/styleguide, no date: "List all exceptions that are relevant to the interface followed by a description."
- [PEP 257 – Docstring Conventions](https://peps.python.org/pep-0257/), Goodger and van Rossum, peps.python.org, 2001: "The one-line docstring should NOT be a “signature” reiterating the function/method parameters (which can be obtained by introspection)."
- [Hyrum's Law](https://www.hyrumslaw.com/), Wright, hyrumslaw.com, no date: "With a sufficient number of users of an API, it does not matter what you promise in the contract: all observable behaviors of your system will be depended on by somebody."
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html), Google, google.github.io/styleguide, no date: "A docstring should give enough information to write a call to the function without reading the function’s code."
- [A Philosophy of Software Design vs Clean Code](https://github.com/johnousterhout/aposd-vs-clean-code), Ousterhout, in Ousterhout and Martin, github.com/johnousterhout/aposd-vs-clean-code, 2024–2025: "It should be possible to use a method without reading its code. The way we achieve this is by writing a header comment that describes the method's interface (all the information someone needs in order to invoke the method)."

### Q4: For each behavior the code has, can the maintainer name the case of the specification that needs it?

**Thinking**: The code gives the behaviors the specification asks, in the form the cases ask for now, and no more, so the maintainer carries nothing no one needs.

**Steps**

1. For each option, mode and case the code handles, name the case of the specification that asks for it.

**Grounds**

- [What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html), Google, google.github.io/eng-practices, no date: "A particular type of complexity is over-engineering, where developers have made the code more generic than it needs to be, or added functionality that isn’t presently needed by the system."
- [What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html), Google, google.github.io/eng-practices, no date: "Encourage developers to solve the problem they know needs to be solved now, not the problem that the developer speculates might need to be solved in the future."
- [Yagni](https://martinfowler.com/bliki/Yagni.html), Fowler, martinfowler.com, 2015: "The code for the presumptive feature adds some complexity to the software, this complexity makes it harder to modify and debug that software, thus increasing the cost of other features."

### Q5: When something the code takes from outside is wrong, can whoever ran it put it right from what the code tells them alone, with nothing left half done?

**Thinking**: What comes from outside, such as arguments, files, settings and the replies of other programs, is checked where it comes in, before anything is done, and a refusal tells whoever ran the code which program refused, what was wrong, where, and what is accepted.

**Steps**

1. At that place, read it into the form the inside uses, checking its type and format and whether its value makes sense for what is to be done.
2. Refuse a value that cannot be read rather than guess it, and catch only the error you mean to handle.
3. Write each check so it runs however the code is run, not as one that can be turned off, such as an assert.
4. Give the code each wrong input the specification names, and read the message as the one who ran it: check that they can put it right from that alone.

**Grounds**

- [Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html), OWASP, cheatsheetseries.owasp.org, no date: "Use a maintained parser for the expected format, handle parsing failures, and validate the resulting values before business processing or storage."
- [Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html), OWASP, cheatsheetseries.owasp.org, no date: "Validate both syntax (the expected type and format) and semantics (whether the value makes sense for the operation)."
- [Parse, don't validate](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/), King, lexi-lambda.github.io, 2019: "Get your data into the most precise representation you need as quickly as you can. Ideally, this should happen at the boundary of your system, before any of the data is acted upon."
- [Parse, don't validate](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/), King, lexi-lambda.github.io, 2019: "Late-discovered errors in an input stream will result in some portion of invalid input having been processed, with the consequence that program state is difficult to accurately predict."
- [10 Usability Heuristics for User Interface Design](https://www.nngroup.com/articles/ten-usability-heuristics/), Nielsen, nngroup.com, 1994, updated 2024: "Error messages should be expressed in plain language (no error codes), precisely indicate the problem, and constructively suggest a solution."
- [GNU Coding Standards](https://www.gnu.org/prep/standards/html_node/Errors.html), GNU Project, 4.4 Formatting Error Messages, gnu.org, no date: "Error messages from other noninteractive programs should look like this: program:sourcefile:lineno: message"
- [PEP 20 – The Zen of Python](https://peps.python.org/pep-0020/), Peters, peps.python.org, 2004: "Errors should never pass silently."
- [PEP 20 – The Zen of Python](https://peps.python.org/pep-0020/), Peters, peps.python.org, 2004: "In the face of ambiguity, refuse the temptation to guess."
- [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/), van Rossum, Warsaw and Coghlan, peps.python.org, 2001: "Additionally, for all try/except clauses, limit the try clause to the absolute minimum amount of code necessary. Again, this avoids masking bugs"
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html), Google, google.github.io/styleguide, no date: "Do not use assert statements in place of conditionals or validating preconditions."

### Q6: For each case the specification names, its edges and refusals included, can the maintainer point to the one test that holds it, and tell the case from the test's name?

**Thinking**: The tests come from the specification's cases, one behavior each, before the code, so each test says which case it holds.

**Steps**

1. List every case the specification names: the usual one, each edge and each refusal.
2. Name each test for the behavior it holds; where the name needs "and", split the test.
3. Write each test so its reader sees the situation, what is done and what must be so, such as in three parts: Given, When and Then.
4. Write each expected value from the specification, not from what the code gives.
5. Run each test before its code is written, and see it fail.
6. Set the list of cases against the tests, and check that each case points to one test.

**Grounds**

- [Canon TDD](https://tidyfirst.substack.com/p/canon-tdd), Beck, tidyfirst.substack.com, 2023: "The initial step in TDD, given a system & a desired change in behavior, is to list all the expected variants in the new behavior."
- [Unit Testing](https://abseil.io/resources/swe-book/html/ch12.html), Kuefler, Software Engineering at Google, ch. 12, abseil.io, 2020: "There’s a better way: rather than writing a test for each method, write a test for each behavior."
- [Unit Testing](https://abseil.io/resources/swe-book/html/ch12.html), Kuefler, Software Engineering at Google, ch. 12, abseil.io, 2020: "A behavior is any guarantee that a system makes about how it will respond to a series of inputs while in a particular state."
- [Unit Testing](https://abseil.io/resources/swe-book/html/ch12.html), Kuefler, Software Engineering at Google, ch. 12, abseil.io, 2020: "The test name is very important: it will often be the first or only token visible in failure reports, so it’s your best opportunity to communicate the problem when the test breaks."
- [Unit Testing](https://abseil.io/resources/swe-book/html/ch12.html), Kuefler, Software Engineering at Google, ch. 12, abseil.io, 2020: "if you need to use the word "and" in a test name, there’s a good chance that you’re actually testing multiple behaviors and should be writing multiple tests!"
- [Unit Testing](https://abseil.io/resources/swe-book/html/ch12.html), Kuefler, Software Engineering at Google, ch. 12, abseil.io, 2020: "Behaviors can often be expressed using the words "given," "when," and "then""
- [Given When Then](https://martinfowler.com/bliki/GivenWhenThen.html), Fowler, martinfowler.com, 2013: "The given part describes the state of the world before you begin the behavior you're specifying in this scenario."
- [Canon TDD](https://tidyfirst.substack.com/p/canon-tdd), Beck, tidyfirst.substack.com, 2023: "Mistake: copying actual, computed values & pasting them into the expected values of the test. That defeats double checking, which creates much of the validation value of TDD."

### Q7: When the maintainer changes a body and its callers still get what its interface says, do the tests still pass?

**Thinking**: The tests call the code as its callers do, so they fail only where a caller would break.

**Steps**

1. Use the real parts where they run fast and wholly inside the test, and a stand-in only for what is slow or outside it.
2. Change a body without changing what its interface says, and run the tests; rewrite through the interface each test that fails.

**Grounds**

- [Unit Testing](https://abseil.io/resources/swe-book/html/ch12.html), Kuefler, Software Engineering at Google, ch. 12, abseil.io, 2020: "By far the most important way to ensure this is to write tests that invoke the system being tested in the same way its users would; that is, make calls against its public API rather than its implementation details."
- [Test Doubles](https://abseil.io/resources/swe-book/html/ch13.html), Trenk and Bly, Software Engineering at Google, ch. 13, abseil.io, 2020: "We prefer realistic tests because they give more confidence that the system under test is working properly."
- [Unit Testing](https://abseil.io/resources/swe-book/html/ch12.html), Kuefler, Software Engineering at Google, ch. 12, abseil.io, 2020: "When an engineer refactors the internals of a system without modifying its interface, whether for performance, clarity, or any other reason, the system’s tests shouldn’t need to change."
- [Unit Testing](https://abseil.io/resources/swe-book/html/ch12.html), Kuefler, Software Engineering at Google, ch. 12, abseil.io, 2020: "Tests that need to be changed during a refactoring indicate that either the change is affecting the system’s behavior and isn’t a pure refactoring, or that the tests were not written at an appropriate level of abstraction."
- [Testing on the Toilet: Test Behavior, Not Implementation](https://testing.googleblog.com/2013/08/testing-on-toilet-test-behavior-not.html), Trenk, Google Testing Blog, 2013: "Tests that are independent of implementation details are easier to maintain since they don't need to be changed each time you make a change to the implementation."
- [Test Desiderata](https://testdesiderata.com/), testdesiderata.com, no date: "Structure-insensitive — tests should not change their result if the structure of the code changes."

### Q8: When the maintainer breaks the behavior a test holds, does that test fail?

**Thinking**: A test is worth the faults it catches, so each one checks the result its case asks, and a broken behavior fails it.

**Steps**

1. Find each line or branch no test runs, such as by counting them while the tests run, and add a test for each.
2. Change the code in small ways, such as by a mutation testing tool, and for each change that the tests still pass, add or mend the test of the behavior it breaks.
3. Run the code over many inputs the specification allows, such as by property tests, and keep each input it fails on as a fixed test.

**Grounds**

- [What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html), Google, google.github.io/eng-practices, no date: "Will the tests actually fail when the code is broken?"
- [Canon TDD](https://tidyfirst.substack.com/p/canon-tdd), Beck, tidyfirst.substack.com, 2023: "Mistake: write tests without assertions just to get code coverage."
- [Testing Overview](https://abseil.io/resources/swe-book/html/ch11.html), Bender, Software Engineering at Google, ch. 11, abseil.io, 2020: "That’s because code coverage only measures that a line was invoked, not what happened as a result."
- [Code Coverage Best Practices](https://testing.googleblog.com/2020/08/code-coverage-best-practices.html), Arguelles, Ivanković and Bender, Google Testing Blog, 2020: "In fact a lot of the value of code coverage data is to highlight not what’s covered, but what’s not covered."
- [Code Coverage Best Practices](https://testing.googleblog.com/2020/08/code-coverage-best-practices.html), Arguelles, Ivanković and Bender, Google Testing Blog, 2020: "A better technique to assess whether you’re adequately exercising the lines your tests cover, and adequately asserting on failures, is mutation testing."
- [Cosmic Ray: mutation testing for Python](https://cosmic-ray.readthedocs.io/en/latest/), Sixty North AS, cosmic-ray.readthedocs.io, no date: "It makes small changes to your production source code, running your test suite for each change. If a test suite passes on mutated code, then you have a mismatch between your tests and your functionality."
- [Hypothesis](https://hypothesis.readthedocs.io/en/latest/), Hypothesis developers, hypothesis.readthedocs.io, no date: "With Hypothesis, you write tests which should pass for all inputs in whatever range you describe, and let Hypothesis randomly choose which of those inputs to check - including edge cases you might not have thought about."
- [Replaying failed tests](https://hypothesis.readthedocs.io/en/latest/tutorial/replaying-failures.html), Hypothesis developers, hypothesis.readthedocs.io, no date: "@example adds an explicit input which Hypothesis will run every time, in addition to the randomly generated test cases."

### Q9: Given the code and its specification alone, can the maintainer make a change the specification asks and know from the tests that every other behavior still holds?

**Thinking**: Only a change made by someone new to the code shows whether the code lets them change it and trust the result.

**Steps**

1. Have someone who has not seen the code, a person or an AI, set it up and make one change the specification asks, with only the code and its specification.
2. Note each body they read to find the place or to write a call, and each time they could not tell whether another behavior broke.
3. Have them run the changed code with a wrong input, and note where its message did not tell them how to put it right.
4. Trace each note to the part whose question it fails, and mend it there.

**Grounds**

- [What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html), Google, google.github.io/eng-practices, no date: "The “users” are usually both end-users (when they are affected by the change) and developers (who will have to “use” this code in the future)."
- [Testing Overview](https://abseil.io/resources/swe-book/html/ch11.html), Bender, Software Engineering at Google, ch. 11, abseil.io, 2020: "automated testing can quickly catch mistakes, and this makes it possible to change software with confidence."
- [Self Testing Code](https://martinfowler.com/bliki/SelfTestingCode.html), Fowler, martinfowler.com, 2014: "You have self-testing code when you can run a series of automated tests against the code base and be confident that, should the tests pass, your code is free of any substantial defects."
