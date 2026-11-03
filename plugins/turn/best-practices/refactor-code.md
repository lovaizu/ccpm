# refactor-code

## Standard

### Goal

The maintainer, a person or an AI who comes to change the code at any time after it is written, changes it quickly without breaking another behavior: they understand each part on one reading and find the one place the change belongs.

### Checklist

- **Q1** (the whole): Reading any name in the code, can the maintainer say what it holds or does without going to where it is defined?
- **Q2** (the whole): Each time the maintainer meets a name, can they tell rightly whether it names a thing they have already met, and which one?
- **Q3** (the whole): Reading any function once from the top, with nothing from outside it but the names it uses, can the maintainer say in one sentence what it does?
- **Q4** (the whole): Where code looks wrong or roundabout, can the maintainer learn right there why it is so, before they change it?
- **Q5** (the whole): Moving from one module to another, does the maintainer find each kind of thing done the same way, so that each difference they meet is one the code needs?
- **Q6** (the whole): With one rule or one design decision to change, can the maintainer find the one place that holds it and make the whole change there?
- **Q7** (the whole): Whatever line the maintainer reads, code or comment, would they lose something they need if it were gone?
- **Q8** (the whole): After the code's structure is changed, does each caller, a person, a script or other code, get every behavior it got before?

## Practice

### Q8: After the code's structure is changed, does each caller, a person, a script or other code, get every behavior it got before?

**Thinking**: The structure is changed in small steps that each keep every behavior, checked by the tests from before, and no behavior is changed among them.

**Steps**

1. Run the tests before any change, and begin only when every one passes.
2. Where a behavior the change will touch has no test, write a test of what the code does now, and see it pass.
3. After each small change of structure, such as a rename or a function moved, run the tests; where one fails, undo the change and make a smaller one.
4. Leave each test's expected result as it was, and change a test's call only where a name it uses was renamed.
5. Where a behavior looks wrong, keep it and its test, and return it as a point about what the code does rather than change it here.

**Grounds**

- [Definition Of Refactoring](https://martinfowler.com/bliki/DefinitionOfRefactoring.html), Fowler, martinfowler.com/bliki, 2004: "Refactoring (noun): a change made to the internal structure of software to make it easier to understand and cheaper to modify without changing its observable behavior."
- [Opportunistic Refactoring](https://martinfowler.com/bliki/OpportunisticRefactoring.html), Fowler, martinfowler.com/bliki, 2011: "This continuous attention to the code is important - but do remember that you should only refactor when your tests are green."
- [Characterization Testing](https://michaelfeathers.silvrback.com/characterization-testing), Feathers, michaelfeathers.silvrback.com, 2016: "The purpose of characterization testing is to document your system’s actual behavior, not check for the behavior you wish your system had."
- [Refactoring](https://refactoring.com/), Fowler, refactoring.com, no date: "Its heart is a series of small behavior preserving transformations. Each transformation (called a “refactoring”) does little, but a sequence of these transformations can produce a significant restructuring."
- [Refactoring](https://refactoring.com/), Fowler, refactoring.com, no date: "The system is kept fully working after each refactoring, reducing the chances that a system can get seriously broken during the restructuring."
- [Testing Overview](https://abseil.io/resources/swe-book/html/ch11.html), Bender, Software Engineering at Google, ch. 11, abseil.io, 2020: "Changes that refactor code while preserving existing behavior should (ideally) require no changes to existing tests."
- [Characterization Testing](https://michaelfeathers.silvrback.com/characterization-testing), Feathers, michaelfeathers.silvrback.com, 2016: "However, if you haven’t determined that the behavior you've uncovered is a bug, it’s often a good idea to leave the test in place."
- [Canon TDD](https://tidyfirst.substack.com/p/canon-tdd), Beck, Software Design: Tidy First?, tidyfirst.substack.com, 2023: "Mistake: mixing refactoring into making the test pass. Again with the “wearing two hats” problem. Make it run, then make it right."
- [Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html), Google, google.github.io/eng-practices, no date: "It’s usually best to do refactorings in a separate CL from feature changes or bug fixes."

### Q7: Whatever line the maintainer reads, code or comment, would they lose something they need if it were gone?

**Thinking**: Each line earns its place by what the maintainer would lose without it, and what gives nothing is taken out and left to version control.

**Steps**

1. Fold each function or layer that only passes a call on into its caller, and drop each parameter that every caller gives the same value, using that value inside.
2. Keep a comment that says what the code cannot say plainly, such as what a regular expression matches.

**Grounds**

- [Beck Design Rules](https://martinfowler.com/bliki/BeckDesignRules.html), Fowler, martinfowler.com/bliki, 2015: "The last rule tells us that anything that doesn't serve the three prior rules should be removed."
- [Writing system software: code comments.](https://antirez.com/news/124), Sanfilippo (antirez), antirez.com, 2018: "But source code is not for making backups."
- [What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html), Google, google.github.io/eng-practices, no date: "A particular type of complexity is over-engineering, where developers have made the code more generic than it needs to be, or added functionality that isn’t presently needed by the system."
- [A Philosophy of Software Design vs Clean Code](https://github.com/johnousterhout/aposd-vs-clean-code), Ousterhout, github.com/johnousterhout/aposd-vs-clean-code, 2025: "I call these interfaces "shallow": they don't help much in terms of reducing what the programmer needs to know."
- [Quality Analysis of Source Code Comments](https://www.cqse.eu/fileadmin/content/news/publications/2013-quality-analysis-of-source-code-comments.pdf), Steidl, Hummel and Juergens, ICPC 2013: "If source code understanding was not harder with the comment being deleted, the comment would not be helpful."
- [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/), van Rossum, Warsaw and Coghlan, peps.python.org, 2001: "Inline comments are unnecessary and in fact distracting if they state the obvious."
- [What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html), Google, google.github.io/eng-practices, no date: "There are some exceptions (regular expressions and complex algorithms often benefit greatly from comments that explain what they’re doing, for example) but mostly comments are for information that the code itself can’t possibly contain, like the reasoning behind a decision."

### Q1: Reading any name in the code, can the maintainer say what it holds or does without going to where it is defined?

**Thinking**: A name says in whole words what it holds or does, so the maintainer reads each line without going to a definition.

**Steps**

1. For each name, write in a few words what it holds or does, without looking at its definition; then look, and flag the name where the two differ.
2. Make a name say more the farther from its definition it is read.

**Grounds**

- [What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html), Google, google.github.io/eng-practices, no date: "A good name is long enough to fully communicate what the item is or does, without being so long that it becomes hard to read."
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html), Google, google.github.io/styleguide, no date: "Avoid abbreviation. In particular, do not use abbreviations that are ambiguous or unfamiliar to readers outside your project, and do not abbreviate by deleting letters within a word."
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html), Google, google.github.io/styleguide, no date: "Generally speaking, descriptiveness should be proportional to the name’s scope of visibility."

### Q2: Each time the maintainer meets a name, can they tell rightly whether it names a thing they have already met, and which one?

**Thinking**: Each thing has one name, the word its users and documents already use for it, and each name names one thing.

**Steps**

1. List the things the code handles, and for each the names the code gives it.

**Grounds**

- [UbiquitousLanguage](https://martinfowler.com/bliki/UbiquitousLanguage.html), Fowler, martinfowler.com/bliki, 2006: "Ubiquitous Language is the term Eric Evans uses in Domain Driven Design for the practice of building up a common, rigorous language between developers and users."
- [Concise and Consistent Naming](https://wwwbroy.in.tum.de/publ/papers/deissenboeck_pizka_identifier_naming.pdf), Deißenböck and Pizka, IWPC 2005: "A typical example for a synonym is the usage of the different identifier names accountNumber and number for the concept of an account number."
- [Concise and Consistent Naming](https://wwwbroy.in.tum.de/publ/papers/deissenboeck_pizka_identifier_naming.pdf), Deißenböck and Pizka, IWPC 2005: "In computer programs, homonyms pose an obstacle for program comprehension since the developer has to take all elements of the set Cn into account when spotting an identifier named n."

### Q6: With one rule or one design decision to change, can the maintainer find the one place that holds it and make the whole change there?

**Thinking**: Each rule or design decision is written once, in the module whose job it is, and things unrelated in meaning are not tied together in the code, however alike they look.

**Steps**

1. For each rule or decision the code holds, such as a limit, a format or a path, list every place that writes it.
2. Where a shared function takes flags so that each caller gets its own path, split it into one function for each rule.
3. Where code reaches into another module's insides, have it use what that module offers its callers.
4. Where a rule truly cannot be kept in one place, say at each place where the others are, such as in a comment beside it.
5. Pick one rule, imagine it changed, and count the places that would change; mend the code until it is one.

**Grounds**

- [Orthogonality and the DRY Principle](https://www.artima.com/articles/orthogonality-and-the-dry-principle), Venners, a conversation with Hunt and Thomas, artima.com, 2003 (Thomas): "DRY says that every piece of system knowledge should have one authoritative, unambiguous representation."
- [Orthogonality and the DRY Principle](https://www.artima.com/articles/orthogonality-and-the-dry-principle), Venners, artima.com, 2003 (Thomas): "The obvious answer is, if you have more than one way to express the same thing, at some point the two or three different representations will most likely fall out of step with each other."
- [Orthogonality and the DRY Principle](https://www.artima.com/articles/orthogonality-and-the-dry-principle), Venners, artima.com, 2003 (Thomas): "Most people take DRY to mean you shouldn't duplicate code. That's not its intention."
- [Canon TDD](https://tidyfirst.substack.com/p/canon-tdd), Beck, Software Design: Tidy First?, tidyfirst.substack.com, 2023: "Mistake: abstracting too soon. Duplication is a hint, not a command."
- [The Wrong Abstraction](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction), Metz, sandimetz.com, 2016: "If you find yourself passing parameters and adding conditional paths through shared code, the abstraction is incorrect."
- [Orthogonality and the DRY Principle](https://www.artima.com/articles/orthogonality-and-the-dry-principle), Venners, artima.com, 2003 (Hunt): "The basic idea of orthogonality is that things that are not related conceptually should not be related in the system."
- [A Philosophy of Software Design vs Clean Code](https://github.com/johnousterhout/aposd-vs-clean-code), Ousterhout, github.com/johnousterhout/aposd-vs-clean-code, 2025: "The worst case is when there is a crucial piece of information hidden in some far-away piece of code that the developer has never heard of."
- [Writing system software: code comments.](https://antirez.com/news/124), Sanfilippo (antirez), antirez.com, 2018: "it is not possible to centralize a given concept or interface in one piece, so there are places in the code that tells you to remember to do things in some other place of the code."
- [Orthogonality and the DRY Principle](https://www.artima.com/articles/orthogonality-and-the-dry-principle), Venners, artima.com, 2003 (Hunt): "One piece of knowledge in the domain changes, one piece of the system changes."

### Q3: Reading any function once from the top, with nothing from outside it but the names it uses, can the maintainer say in one sentence what it does?

**Thinking**: A function does one thing at one level and takes what it uses as its inputs, so its reader holds only what it says, and a long one reads as calls to steps named for what they do.

**Steps**

1. Read each function, test functions included, once from the top, and write in one sentence what it does.
2. Flag a function whose sentence needs an "and", or for which the reader had to read another body.
3. Join back two functions that cannot be understood apart.
4. Write a clever construct in its plain form.

**Grounds**

- [What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html), Google, google.github.io/eng-practices, no date: "“Too complex” usually means “can’t be understood quickly by code readers.” It can also mean “developers are likely to introduce bugs when they try to call or modify this code.”"
- [PEP 20 – The Zen of Python](https://peps.python.org/pep-0020/), Peters, peps.python.org, 2004: "If the implementation is hard to explain, it's a bad idea."
- [Beck Design Rules](https://martinfowler.com/bliki/BeckDesignRules.html), Fowler, martinfowler.com/bliki, 2015: "Kent's form of expressing this rule implies that the key to enabling understanding is to express your intention in the code, so that your readers can understand what your purpose was when writing it."
- [Code Smell](https://martinfowler.com/bliki/CodeSmell.html), Fowler, martinfowler.com/bliki, 2006: "The second is that smells don't always indicate a problem. Some long methods are just fine."
- [A Philosophy of Software Design vs Clean Code](https://github.com/johnousterhout/aposd-vs-clean-code), Ousterhout, github.com/johnousterhout/aposd-vs-clean-code, 2025: "Two methods are entangled (or "conjoined" in APOSD terminology) if, in order to understand how one of them works internally, you also need to read the code of the other."
- [A Philosophy of Software Design vs Clean Code](https://github.com/johnousterhout/aposd-vs-clean-code), Ousterhout, github.com/johnousterhout/aposd-vs-clean-code, 2025: "How much information must a developer have in their head in order to carry out a task?"
- [Style Guides and Rules](https://abseil.io/resources/swe-book/html/ch08.html), Schwartz, Software Engineering at Google, ch. 8, abseil.io, 2020: "Even if a construct is well understood by a project’s engineers, future project members and maintainers are not guaranteed to have the same understanding."

### Q5: Moving from one module to another, does the maintainer find each kind of thing done the same way, so that each difference they meet is one the code needs?

**Thinking**: Each kind of thing is done one way across the code, the way the code already has, the nearest code first, unless a better one replaces it everywhere, so a difference means a real difference.

**Steps**

1. List the kinds of thing the code does in many places, such as reporting an error, checking an input, reading a file, or laying out a module or a test.
2. For each kind, gather each way the code does it.
3. Where a place needs another way, say why beside it, such as in a comment.

**Grounds**

- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html), Google, google.github.io/styleguide, no date: "If code you add to a file looks drastically different from the existing code around it, it throws readers out of their rhythm when they go to read it."
- [Style Guides and Rules](https://abseil.io/resources/swe-book/html/ch08.html), Schwartz, Software Engineering at Google, ch. 8, abseil.io, 2020: "Consistency is what enables any engineer to jump into an unfamiliar part of the codebase and get to work fairly quickly."
- [What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html), Google, google.github.io/eng-practices, no date: "If no other rule applies, the author should maintain consistency with the existing code."
- [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/), van Rossum, Warsaw and Coghlan, peps.python.org, 2001: "Consistency within a project is more important. Consistency within one module or function is the most important."
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html), Google, google.github.io/styleguide, no date: "Consistency should not generally be used as a justification to do things in an old style without considering the benefits of the new style"

### Q4: Where code looks wrong or roundabout, can the maintainer learn right there why it is so, before they change it?

**Thinking**: What the code cannot say, the reason it is so, such as a limit outside the code or a way tried and dropped, is given where the maintainer meets it.

**Steps**

1. Read each line as a maintainer who knows the language but not the purpose, and flag code that looks wrong, roundabout or more than it needs.
2. For each, first make the code say it plainly, where it can.
3. Check each comment against the code beside it, and correct or remove one that no longer holds.

**Grounds**

- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html), Google, google.github.io/styleguide, no date: "On the other hand, never describe the code. Assume the person reading the code knows Python (though not what you’re trying to do) better than you do."
- [What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html), Google, google.github.io/eng-practices, no date: "If the code isn’t clear enough to explain itself, then the code should be made simpler."
- [Writing system software: code comments.](https://antirez.com/news/124), Sanfilippo (antirez), antirez.com, 2018: "Why comments explain the reason why the code is doing something, even if what the code is doing is crystal clear."
- [A Philosophy of Software Design vs Clean Code](https://github.com/johnousterhout/aposd-vs-clean-code), Ousterhout, github.com/johnousterhout/aposd-vs-clean-code, 2025: "The second general reason for comments is for important information that is not obvious from the code."
- [Documentation](https://abseil.io/resources/swe-book/html/ch10.html), Manshreck, Software Engineering at Google, ch. 10, abseil.io, 2020: "Implementation comments, on the other hand, can assume a lot more domain knowledge of the reader, though be careful in assuming too much: people leave projects, and sometimes it’s safer to be methodical about exactly why you wrote this code the way you did."
- [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/), van Rossum, Warsaw and Coghlan, peps.python.org, 2001: "Comments that contradict the code are worse than no comments. Always make a priority of keeping the comments up-to-date when the code changes!"
