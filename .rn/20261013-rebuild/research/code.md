# Best practice sources: code

Code here is built to a specification, with its comments and docstrings. A maintainer, a person or
an AI, takes it over to change what a product does. These sources say what that maintainer needs
from the code.

Each quote was copied from the page as it was opened on 2026-11-02. Quotes from PDF files come
from their extracted text. In those, ligatures such as "fi" and words broken across lines are
written as plain words.

## Set the code up and run its tests from what it declares

- **Adam Wiggins, "The Twelve-Factor App", II. Dependencies, 12factor.net, last updated 2017.**
  https://12factor.net/dependencies
  > A twelve-factor app never relies on implicit existence of system-wide packages. It declares all dependencies, completely and exactly, via a dependency declaration manifest.

  The manifest names everything the code needs, so the maintainer depends on nothing they were
  not told about.

- **Adam Wiggins, "The Twelve-Factor App", II. Dependencies, 12factor.net, last updated 2017.**
  https://12factor.net/dependencies
  > One benefit of explicit dependency declaration is that it simplifies setup for developers new to the app.

  The maintainer who is new to the code is the one the manifest serves.

- **pip developers, "Repeatable Installs", pip documentation v26.2.2, 2026.**
  https://pip.pypa.io/en/stable/topics/repeatable-installs/
  > Pinning package versions of your dependencies in the requirements file protects you from bugs or incompatibilities in newly released versions

  A manifest that gives exact versions keeps a new release of a library from breaking the code on
  the next machine.

## Find the module a change belongs in

- **D. L. Parnas, "On the Criteria To Be Used in Decomposing Systems into Modules", Communications
  of the ACM 15(12), 1972.** https://www.win.tue.nl/~wstomv/edu/2ip30/references/criteria_for_modularization.pdf
  > We propose instead that one begins with a list of difficult design decisions or design decisions which are likely to change. Each module is then designed to hide such a decision from the others.

  Each module owns one decision, so a change to that decision is made in that module alone.

- **D. L. Parnas, same paper, 1972.**
  https://www.win.tue.nl/~wstomv/edu/2ip30/references/criteria_for_modularization.pdf
  > product flexibility-it should be possible to make drastic changes to one module without a need to change others; (3) comprehensibility-it should be possible to study the system one module at a time.

  The maintainer gets two things from good modules: a change stays in one module, and they can
  read one module at a time.

- **D. L. Parnas, same paper, 1972.**
  https://www.win.tue.nl/~wstomv/edu/2ip30/references/criteria_for_modularization.pdf
  > Every module in the second decomposition is characterized by its knowledge of a design decision which it hides from all others. Its interface or definition was chosen to reveal as little as possible about its inner workings.

  A module's opening can say in a sentence which decision it holds, because it holds one.

- **Google, "Google Python Style Guide", 3.8.2 Modules, google.github.io/styleguide, current.**
  https://google.github.io/styleguide/pyguide.html
  > Files should start with a docstring describing the contents and usage of the module.

  The module's opening comment is where the maintainer looks first.

- **Tom Manshreck, "Documentation", ch. 10 of Winters, Manshreck and Wright, Software Engineering
  at Google, O'Reilly, 2020.** https://abseil.io/resources/swe-book/html/ch10.html
  > Any API that cannot be succinctly described in the first paragraph or two is usually the sign of an API that is not well thought out. Consider breaking the API into separate components in those cases.

  If a module's opening cannot be short, the module holds more than one thing.

- **Tom Manshreck, same chapter, 2020.** https://abseil.io/resources/swe-book/html/ch10.html
  > The key win for stumblers is clearly identifying the purpose of an API, often at the top of a file header.

  A maintainer who does not yet know where to look learns it from the top of each file.

## Call code they did not write from its interface alone

- **Google, "Google Python Style Guide", 3.8.3 Functions and Methods, current.**
  https://google.github.io/styleguide/pyguide.html
  > A docstring should give enough information to write a call to the function without reading the function’s code.

  This is the test of an interface comment: the maintainer writes a working call from it.

- **Google, same guide, 3.8.3 Functions and Methods.**
  https://google.github.io/styleguide/pyguide.html
  > For example, a function that mutates one of its arguments as a side effect should note that in its docstring.

  What the caller must know, such as a side effect, belongs in the interface.

- **Google, same guide, 3.8.3, Raises.** https://google.github.io/styleguide/pyguide.html
  > List all exceptions that are relevant to the interface followed by a description.

  Each way a function refuses is part of what the caller needs.

- **Google, same guide, 3.8.3, Raises.** https://google.github.io/styleguide/pyguide.html
  > You should not document exceptions that get raised if the API specified in the docstring is violated (because this would paradoxically make behavior under violation of the API part of the API).

  The interface lists the refusals a caller can meet when they call it rightly, not what a misuse
  happens to do.

- **David Goodger and Guido van Rossum, "PEP 257 – Docstring Conventions", peps.python.org, 2001.**
  https://peps.python.org/pep-0257/
  > The docstring for a function or method should summarize its behavior and document its arguments, return value(s), side effects, exceptions raised, and restrictions on when it can be called (all if applicable).

  This is the list of what an interface comment holds.

- **David Goodger and Guido van Rossum, same PEP, 2001.** https://peps.python.org/pep-0257/
  > The one-line docstring should NOT be a “signature” reiterating the function/method parameters (which can be obtained by introspection).

  The comment says what the signature cannot say.

- **David Goodger and Guido van Rossum, same PEP, 2001.** https://peps.python.org/pep-0257/
  > However, the nature of the return value cannot be determined by introspection, so it should be mentioned.

  What comes back is the part of the interface the maintainer most often cannot guess.

- **John Ousterhout and Robert Martin, "A Philosophy of Software Design vs Clean Code",
  github.com/johnousterhout/aposd-vs-clean-code, 2024–2025 (Ousterhout's words).**
  https://github.com/johnousterhout/aposd-vs-clean-code
  > It should be possible to use a method without reading its code. The way we achieve this is by writing a header comment that describes the method's interface (all the information someone needs in order to invoke the method).

  The author of A Philosophy of Software Design puts the interface comment at the root of
  abstraction.

- **John Ousterhout, same discussion, 2024–2025.**
  https://github.com/johnousterhout/aposd-vs-clean-code
  > The best methods are those that provide a lot of functionality but have a very simple interface: they replace a large cognitive load (reading the detailed implementation) with a much smaller cognitive load (learning the interface). I call these methods "deep".

  A good interface is much smaller than the body behind it.

- **John Ousterhout, same discussion, 2024–2025.**
  https://github.com/johnousterhout/aposd-vs-clean-code
  > In a project of any size, I think your approach would result in developers spending large amounts of time reading code to re-derive the interfaces, and probably making mistakes along the way.

  Without interface comments, the maintainer reads bodies to learn what to pass, and gets it
  wrong.

- **Salvatore Sanfilippo (antirez), "Writing system software: code comments.", antirez.com,
  2018.** https://antirez.com/news/124
  > The goal of a function comment is to prevent the reader from reading code in the first place.

  The author of Redis states the same aim from practice.

- **Guido van Rossum, Barry Warsaw and Alyssa Coghlan, "PEP 8 – Style Guide for Python Code",
  Public and Internal Interfaces, peps.python.org, 2001.** https://peps.python.org/pep-0008/
  > Documented interfaces are considered public, unless the documentation explicitly declares them to be provisional or internal interfaces exempt from the usual backwards compatibility guarantees. All undocumented interfaces should be assumed to be internal.

  The maintainer tells which names other modules may use from what is documented.

- **Hyrum Wright, "Hyrum's Law", hyrumslaw.com, date not given on the page.**
  https://www.hyrumslaw.com/
  > With a sufficient number of users of an API, it does not matter what you promise in the contract: all observable behaviors of your system will be depended on by somebody.

  Whatever the interface leaves unsaid, callers come to rely on, so the interface must say what is
  promised.

- **Guido van Rossum, Jukka Lehtosalo and Łukasz Langa, "PEP 484 – Type Hints", peps.python.org,
  2014.** https://peps.python.org/pep-0484/
  > This PEP aims to provide a standard syntax for type annotations, opening up Python code to easier static analysis and refactoring

  Types in the signature let tools check calls the maintainer writes.

- **Google, "Google Python Style Guide", 2.21 Type Annotated Code, Pros.**
  https://google.github.io/styleguide/pyguide.html
  > Type annotations improve the readability and maintainability of your code. The type checker will convert many runtime errors to build-time errors

  A wrong call is caught before it runs.

## Read a body and know why it is so

- **Google, "What to look for in a code review", Comments, google.github.io/eng-practices,
  current.** https://google.github.io/eng-practices/review/reviewer/looking-for.html
  > Usually comments are useful when they explain why some code exists, and should not be explaining what some code is doing.

  A comment in a body gives the reason the code cannot show.

- **Google, same page, Comments.**
  https://google.github.io/eng-practices/review/reviewer/looking-for.html
  > Note that comments are different from documentation of classes, modules, or functions, which should instead express the purpose of a piece of code, how it should be used, and how it behaves when used.

  The interface comment and the comment in the body serve different readers and say different
  things.

- **Google, "Google Python Style Guide", 3.8.5 Block and Inline Comments.**
  https://google.github.io/styleguide/pyguide.html
  > If you’re going to have to explain it at the next code review, you should comment it now.

  A test for where a body needs a comment.

## Get only what the specification asks

- **Google, "What to look for in a code review", Complexity.**
  https://google.github.io/eng-practices/review/reviewer/looking-for.html
  > Encourage developers to solve the problem they know needs to be solved now, not the problem that the developer speculates might need to be solved in the future.

  The code gives the behaviors asked, and no more for the maintainer to carry.

- **Google, same page, Functionality.**
  https://google.github.io/eng-practices/review/reviewer/looking-for.html
  > The “users” are usually both end-users (when they are affected by the change) and developers (who will have to “use” this code in the future).

  The developer who takes the code over is one of its users.

## Learn from what the code says when something from outside is wrong

- **Tim Peters, "PEP 20 – The Zen of Python", peps.python.org, 2004.**
  https://peps.python.org/pep-0020/
  > Errors should never pass silently.

  A wrong input stops the code with a message; it does not give a wrong result quietly.

- **Tim Peters, same PEP, 2004.** https://peps.python.org/pep-0020/
  > In the face of ambiguity, refuse the temptation to guess.

  The code refuses an input it cannot read rather than guessing what was meant.

- **Jakob Nielsen, "10 Usability Heuristics for User Interface Design", #9, nngroup.com, 1994,
  last reviewed 2024.** https://www.nngroup.com/articles/ten-usability-heuristics/
  > Error messages should be expressed in plain language (no error codes), precisely indicate the problem, and constructively suggest a solution.

  Whoever runs the code puts it right from the message alone.

- **GNU Project, "GNU Coding Standards", 4.4 Formatting Error Messages, gnu.org, current.**
  https://www.gnu.org/prep/standards/html_node/Errors.html
  > Error messages from other noninteractive programs should look like this:

  A message names the program and, where there is one, the file and line, so the reader finds the
  place.

- **OWASP, "Input Validation Cheat Sheet", cheatsheetseries.owasp.org, current.**
  https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html
  > Use a maintained parser for the expected format, handle parsing failures, and validate the resulting values before business processing or storage.

  The code checks what comes in before it acts on it.

- **OWASP, same page.**
  https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html
  > Validate both syntax (the expected type and format) and semantics (whether the value makes sense for the operation).

  A value of the right type can still be wrong for the operation, and the check covers both.

- **Alexis King, "Parse, don't validate", lexi-lambda.github.io, 2019.**
  https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/
  > Get your data into the most precise representation you need as quickly as you can. Ideally, this should happen at the boundary of your system, before any of the data is acted upon.

  Checks sit where the input comes in, and the parts inside trust what they are given.

- **Alexis King, same post, quoting "The Seven Turrets of Babel" (2016).**
  https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/
  > Late-discovered errors in an input stream will result in some portion of invalid input having been processed, with the consequence that program state is difficult to accurately predict.

  A check spread through the code leaves work half done when it fails.

- **Google, "Google Python Style Guide", 2.4 Exceptions.**
  https://google.github.io/styleguide/pyguide.html
  > Do not use assert statements in place of conditionals or validating preconditions.

  A check that must hold in use is real code, not an assert that can be switched off.

- **Guido van Rossum, Barry Warsaw and Alyssa Coghlan, "PEP 8", Programming Recommendations,
  2001.** https://peps.python.org/pep-0008/
  > Additionally, for all try/except clauses, limit the try clause to the absolute minimum amount of code necessary. Again, this avoids masking bugs

  Catching too much hides the fault the maintainer needs to see.

## See from the tests which behavior each one holds

- **Erik Kuefler, "Unit Testing", ch. 12 of Software Engineering at Google, O'Reilly, 2020.**
  https://abseil.io/resources/swe-book/html/ch12.html
  > There’s a better way: rather than writing a test for each method, write a test for each behavior.

  Tests follow the cases of the specification, not the functions of the code.

- **Erik Kuefler, same chapter, 2020.** https://abseil.io/resources/swe-book/html/ch12.html
  > A behavior is any guarantee that a system makes about how it will respond to a series of inputs while in a particular state.

  A behavior the specification asks is one such guarantee.

- **Erik Kuefler, same chapter, 2020.** https://abseil.io/resources/swe-book/html/ch12.html
  > Behaviors can often be expressed using the words "given," "when," and "then"

  Given, When and Then is how a behavior from the specification is written as a test.

- **Erik Kuefler, same chapter, 2020.** https://abseil.io/resources/swe-book/html/ch12.html
  > The test name is very important: it will often be the first or only token visible in failure reports, so it’s your best opportunity to communicate the problem when the test breaks.

  The maintainer learns which behavior broke from the test's name.

- **Erik Kuefler, same chapter, 2020.** https://abseil.io/resources/swe-book/html/ch12.html
  > if you need to use the word "and" in a test name, there’s a good chance that you’re actually testing multiple behaviors and should be writing multiple tests!

  One test holds one behavior.

- **Martin Fowler, "Given When Then", martinfowler.com/bliki, 2013.**
  https://martinfowler.com/bliki/GivenWhenThen.html
  > The given part describes the state of the world before you begin the behavior you're specifying in this scenario. You can think of it as the pre-conditions to the test.

  The three parts keep apart the starting state, what is done, and what must follow.

- **Erik Kuefler, same chapter, 2020.** https://abseil.io/resources/swe-book/html/ch12.html
  > Clear tests are trivially correct upon inspection; that is, it is obvious that a test is doing the correct thing just from glancing at it.

  The maintainer trusts a test they can check by reading it.

- **Erik Kuefler, same chapter, 2020.** https://abseil.io/resources/swe-book/html/ch12.html
  > A little bit of duplication is OK in tests so long as that duplication makes the test simpler and clearer.

  A test shows its values in place, even when another test shows them too.

- **Kent Beck, "Canon TDD", Software Design: Tidy First? (substack), 2023.**
  https://tidyfirst.substack.com/p/canon-tdd
  > The initial step in TDD, given a system & a desired change in behavior, is to list all the expected variants in the new behavior.

  The tests come from a list of every case of the behavior, before code is written.

- **Kent Beck, same post, 2023.** https://tidyfirst.substack.com/p/canon-tdd
  > Mistake: copying actual, computed values & pasting them into the expected values of the test. That defeats double checking, which creates much of the validation value of TDD.

  A test's expected value is written from the specification, not taken from the code.

- **Kent Beck, same post, 2023.** https://tidyfirst.substack.com/p/canon-tdd
  > Mistake: write tests without assertions just to get code coverage.

  A test that runs code but checks nothing holds no behavior.

- **"Test Desiderata", testdesiderata.com, no author or date on the page; it links Kent Beck's original papers on medium.com.**
  https://testdesiderata.com/
  > Readable — tests should be comprehensible for reader, invoking the motivation for writing this particular test.

  The reader of a test learns why it is there.

- **Kent Beck, same page.** https://testdesiderata.com/
  > Specific — if a test fails, the cause of the failure should be obvious.

  A failure points the maintainer to its cause.

## After a change, trust what the tests say

- **Adam Bender, "Testing Overview", ch. 11 of Software Engineering at Google, O'Reilly, 2020.**
  https://abseil.io/resources/swe-book/html/ch11.html
  > automated testing can quickly catch mistakes, and this makes it possible to change software with confidence.

  Tests are what lets the maintainer change code they did not write.

- **Adam Bender, same chapter, 2020.** https://abseil.io/resources/swe-book/html/ch11.html
  > All tests should strive to be hermetic: a test should contain all of the information necessary to set up, execute, and tear down its environment. Tests should assume as little as possible about the outside environment, such as the order in which the tests are run.

  A test's result rests on the code alone.

- **Adam Bender, same chapter, 2020.** https://abseil.io/resources/swe-book/html/ch11.html
  > It doesn’t take needing to investigate many flakes before a team loses trust in the test suite. After that happens, engineers will stop reacting to test failures, eliminating any value the test suite provided.

  A test that fails at random teaches the maintainer to ignore real failures.

- **"Test Desiderata", testdesiderata.com.** https://testdesiderata.com/
  > Isolated — tests should return the same results regardless of the order in which they are run.

  The same point from the Test Desiderata list.

- **Erik Kuefler, "Unit Testing", ch. 12, 2020.** https://abseil.io/resources/swe-book/html/ch12.html
  > By far the most important way to ensure this is to write tests that invoke the system being tested in the same way its users would; that is, make calls against its public API rather than its implementation details.

  A test through the interface fails only when a caller would be broken.

- **Andrew Trenk and Dillon Bly, "Test Doubles", ch. 13 of Software Engineering at Google, O'Reilly,
  2020.** https://abseil.io/resources/swe-book/html/ch13.html
  > We prefer realistic tests because they give more confidence that the system under test is working properly.

  A test that uses the real parts where it can tells the maintainer more.

- **Martin Fowler, "Self Testing Code", martinfowler.com/bliki, 2014.**
  https://martinfowler.com/bliki/SelfTestingCode.html
  > You have self-testing code when you can run a series of automated tests against the code base and be confident that, should the tests pass, your code is free of any substantial defects.

  One command tells the maintainer whether the code still works.

- **Google, "What to look for in a code review", Tests.**
  https://google.github.io/eng-practices/review/reviewer/looking-for.html
  > Will the tests actually fail when the code is broken?

  A test is worth only the faults it catches.

- **Adam Bender, "Testing Overview", ch. 11, 2020.** https://abseil.io/resources/swe-book/html/ch11.html
  > That’s because code coverage only measures that a line was invoked, not what happened as a result.

  Full coverage shows every line ran, not that every behavior is checked.

- **Carlos Arguelles, Marko Ivanković and Adam Bender, "Code Coverage Best Practices", Google
  Testing Blog, 2020.** https://testing.googleblog.com/2020/08/code-coverage-best-practices.html
  > In fact a lot of the value of code coverage data is to highlight not what’s covered, but what’s not covered.

  Coverage finds the lines no test runs.

- **Carlos Arguelles, Marko Ivanković and Adam Bender, same post, 2020.**
  https://testing.googleblog.com/2020/08/code-coverage-best-practices.html
  > A better technique to assess whether you’re adequately exercising the lines your tests cover, and adequately asserting on failures, is mutation testing.

  Mutation testing checks what coverage cannot.

- **Sixty North AS, "Cosmic Ray: mutation testing for Python", cosmic-ray.readthedocs.io, 2019.**
  https://cosmic-ray.readthedocs.io/en/latest/
  > It makes small changes to your production source code, running your test suite for each change. If a test suite passes on mutated code, then you have a mismatch between your tests and your functionality.

  A surviving mutant shows a behavior no test holds.

- **Goran Petrović, Marko Ivanković, Gordon Fraser and René Just, "Practical Mutation Testing at
  Scale: A view from Google", arXiv:2102.11378 (IEEE TSE), 2021.** https://arxiv.org/pdf/2102.11378
  > However, code coverage alone might be misleading, in particular when program statements are covered but the expected program outcome is not asserted upon

  The same gap, seen across Google's code.

- **Goran Petrović and others, same paper, 2021.** https://arxiv.org/pdf/2102.11378
  > An unproductive mutant is either trivially equivalent to the original program or it is detectable, but adding a test for it would not improve the test suite

  Some mutants cannot be told apart by any input, and a test for them adds nothing.

- **Hypothesis developers, "Hypothesis" documentation, hypothesis.readthedocs.io, current.**
  https://hypothesis.readthedocs.io/en/latest/
  > With Hypothesis, you write tests which should pass for all inputs in whatever range you describe, and let Hypothesis randomly choose which of those inputs to check - including edge cases you might not have thought about.

  A property test finds the inputs the maintainer did not think of.

- **David R. MacIver, "What is Property Based Testing?", hypothesis.works, 2016.**
  https://hypothesis.works/articles/what-is-property-based-testing/
  > Property based testing is the construction of tests such that, when these tests are fuzzed, failures in the test reveal problems with the system under test that could not have been revealed by direct fuzzing of that system.

  The author of Hypothesis defines what a property test is for.

- **Hypothesis developers, "Replaying failed tests", Hypothesis documentation, current.**
  https://hypothesis.readthedocs.io/en/latest/tutorial/replaying-failures.html
  > @example adds an explicit input which Hypothesis will run every time, in addition to the randomly generated test cases.

  An input a property test failed on is kept as a fixed case, so every run checks it again.

- **Scott Wlaschin, "Choosing properties for property-based testing", fsharpforfunandprofit.com,
  2014.** https://fsharpforfunandprofit.com/posts/property-based-testing-2/
  > In my experience, many properties can be discovered by using one of the seven approaches listed below.

  Properties come from known patterns, such as an inverse ("There and back again") or an
  invariant ("Some things never change").

## Not found

- John Ousterhout, A Philosophy of Software Design, the book itself. I did not open it. Its
  author's extract of the second edition
  (https://web.stanford.edu/~ouster/cgi-bin/aposd2ndEdExtract.pdf) opened, but it has no text a
  tool could read, and no page renderer was installed. Ousterhout's words above come from his
  discussion with Robert Martin instead.
- Kent Beck, Test-Driven Development: By Example, the book. I did not open it. Beck's own "Canon
  TDD" post stands in for it.
- Wen, Nagy, Bavota and Lanza, "A Large-Scale Empirical Study on Code-Comment Inconsistencies",
  ICPC 2019. Both PDF links at usi.ch returned 403, and I found no other copy.
- An empirical study of error-message quality in programs run from a command line. I did not
  find one I could open; the Nielsen heuristic and the GNU standard above are guidelines, not
  studies.
- D. L. Parnas, "On the Criteria To Be Used in Decomposing Systems into Modules", 1972. Opened
  again on 2026-11-02 to check the quotes above, the PDF holds scanned page images and no text a
  tool could read, so its quotes could not be confirmed and code.json does not use them.
