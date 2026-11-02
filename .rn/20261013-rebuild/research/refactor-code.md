# Best practice sources: refactor-code

Refactor-code is how a code base is written so that a maintainer, a person or an AI, changes it
with confidence. The maintainer comes to the code at any time after it is written. These sources
say what that maintainer needs from how the code is written.

Each quote was copied from the page as it was opened on 2026-11-02. Quotes from PDF files come
from their extracted text. In those, ligatures such as "fi" and words broken across lines are
written as plain words.

## Why the maintainer needs code that is easy to understand

- **Xin Xia, Lingfeng Bao, David Lo, Zhenchang Xing, Ahmed E. Hassan and Shanping Li, "Measuring
  Program Comprehension: A Large-Scale Field Study with Professionals", IEEE Transactions on
  Software Engineering 44(10), 2018.** https://xin-xia.github.io/publication/TSE17.pdf
  > Previous studies show that program comprehension takes up as much as half of a developer’s time.

  The study itself measured 78 professional developers over 3,148 hours, and its abstract gives
  about 58 percent of their time spent on comprehension. (The sign before "58" did not survive the
  PDF's text, so it is not quoted here.)

- **Martin Fowler, "Is High Quality Software Worth the Cost?", martinfowler.com, 2019.**
  https://martinfowler.com/articles/is-quality-worth-cost.html
  > Programmers spend most of their time modifying code. Even in a new system, almost all programming is done in the context of an existing code base.

  The maintainer's work is mostly understanding code that is already there.

- **Martin Fowler, same article, 2019.** https://martinfowler.com/articles/is-quality-worth-cost.html
  > Logic can get tangled, the data can be hard to follow, the names used to refer to things may have made sense to Tony six months ago, but are as mysterious to me as his reasons for leaving the company.

  The maintainer meets code whose writer is gone.

- **John Ousterhout and Robert Martin, "A Philosophy of Software Design vs Clean Code",
  github.com/johnousterhout/aposd-vs-clean-code, 2024–2025 (Ousterhout's words).**
  https://github.com/johnousterhout/aposd-vs-clean-code
  > For me, the fundamental goal of software design is to make it easy to understand and modify the system.

  The goal of how code is written is the maintainer's understanding and change.

- **John Ousterhout, same discussion.** https://github.com/johnousterhout/aposd-vs-clean-code
  > How much information must a developer have in their head in order to carry out a task?

  The measure of how hard code is to change is what the maintainer must hold in mind.

- **John Ousterhout, same discussion.** https://github.com/johnousterhout/aposd-vs-clean-code
  > The worst case is when there is a crucial piece of information hidden in some far-away piece of code that the developer has never heard of.

  What the maintainer needs should be where they look.

- **Guido van Rossum, Barry Warsaw and Alyssa Coghlan, "PEP 8 – Style Guide for Python Code",
  peps.python.org, 2001.** https://peps.python.org/pep-0008/
  > One of Guido’s key insights is that code is read much more often than it is written.

  Code is written for its reader.

- **Shaindel Schwartz, "Style Guides and Rules", ch. 8 of Winters, Manshreck and Wright, Software
  Engineering at Google, O'Reilly, 2020.** https://abseil.io/resources/swe-book/html/ch08.html
  > We’d rather the code be tedious to type than difficult to read.

  When the writer's ease and the reader's ease conflict, the reader wins.

- **Martin Fowler, "Refactoring", refactoring.com, current.** https://refactoring.com/
  > Often enhancements are applied on top of each other in a manner that makes it increasingly harder to make changes. Over time new work slows to a crawl.

  Code that is not kept clear gets slower to change with each change.

- **Miryung Kim, Thomas Zimmermann and Nachiappan Nagappan, "A Field Study of Refactoring
  Challenges and Benefits", FSE 2012.**
  https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/kim-fse-2012.pdf
  > The quantitative analysis of Windows 7 version history finds that the binary modules refactored by this team experienced significant reduction in the number of inter-module dependencies and post-release defects, indicating a visible benefit of refactoring.

  A field study at Microsoft found fewer defects after refactoring.

## Read a name and know what it holds

- **Google, "What to look for in a code review", Naming, google.github.io/eng-practices,
  current.** https://google.github.io/eng-practices/review/reviewer/looking-for.html
  > A good name is long enough to fully communicate what the item is or does, without being so long that it becomes hard to read.

  A name says what it holds or does.

- **Google, "Google Python Style Guide", 3.16 Naming, google.github.io/styleguide, current.**
  https://google.github.io/styleguide/pyguide.html
  > Avoid abbreviation. In particular, do not use abbreviations that are ambiguous or unfamiliar to readers outside your project, and do not abbreviate by deleting letters within a word.

  A reader from outside the project can read the name.

- **Google, same guide, 3.16.1 Names to Avoid.** https://google.github.io/styleguide/pyguide.html
  > Generally speaking, descriptiveness should be proportional to the name’s scope of visibility.

  A name read far from where it is set says more.

- **Johannes Hofmeister, Janet Siegmund and Daniel V. Holt, "Shorter Identifier Names Take Longer to
  Comprehend", SANER 2017.** https://www.se.cs.uni-saarland.de/publications/docs/HoSeHo17.pdf
  > We found that words lead to, on average, 19% faster comprehension speed compared to letters and abbreviations, but we did not find a significant difference in speed between letters and abbreviations.

  In an experiment with 72 professional developers, names made of words let them find defects
  faster.

## Tell whether two names mean the same thing

- **Florian Deißenböck and Markus Pizka, "Concise and Consistent Naming", IWPC 2005.**
  https://wwwbroy.in.tum.de/publ/papers/deissenboeck_pizka_identifier_naming.pdf
  > In computer programs, homonyms pose an obstacle for program comprehension since the developer has to take all elements of the set Cn into account when spotting an identifier named n.

  One name used for two things makes the maintainer weigh both at each use.

- **Florian Deißenböck and Markus Pizka, same paper.**
  https://wwwbroy.in.tum.de/publ/papers/deissenboeck_pizka_identifier_naming.pdf
  > A typical example for a synonym is the usage of the different identifier names accountNumber and number for the concept of an account number.

  Two names for one thing make the maintainer learn both and wonder whether they differ.

- **Martin Fowler, "UbiquitousLanguage", martinfowler.com/bliki, 2006.**
  https://martinfowler.com/bliki/UbiquitousLanguage.html
  > Ubiquitous Language is the term Eric Evans uses in Domain Driven Design for the practice of building up a common, rigorous language between developers and users.

  The one name kept for a thing is the word its users already use.

## Understand a function on one reading

- **Google, "What to look for in a code review", Complexity.**
  https://google.github.io/eng-practices/review/reviewer/looking-for.html
  > “Too complex” usually means “can’t be understood quickly by code readers.” It can also mean “developers are likely to introduce bugs when they try to call or modify this code.”

  Complexity is judged by the reader's time and the next change's faults.

- **John Ousterhout, "A Philosophy of Software Design vs Clean Code".**
  https://github.com/johnousterhout/aposd-vs-clean-code
  > Two methods are entangled (or "conjoined" in APOSD terminology) if, in order to understand how one of them works internally, you also need to read the code of the other.

  A function split so that its reader flips between two bodies is harder to read, not easier.

- **John Ousterhout, same discussion.** https://github.com/johnousterhout/aposd-vs-clean-code
  > I call these interfaces "shallow": they don't help much in terms of reducing what the programmer needs to know.

  A function that hides little behind its name costs a name and gives nothing.

- **Martin Fowler, "Beck Design Rules", martinfowler.com/bliki, 2015.**
  https://martinfowler.com/bliki/BeckDesignRules.html
  > Kent's form of expressing this rule implies that the key to enabling understanding is to express your intention in the code, so that your readers can understand what your purpose was when writing it.

  Code shows what it is for, so the reader can say what it does.

- **Tim Peters, "PEP 20 – The Zen of Python", peps.python.org, 2004.**
  https://peps.python.org/pep-0020/
  > If the implementation is hard to explain, it's a bad idea.

  A function the maintainer cannot sum up is a sign to rewrite it.

- **Shaindel Schwartz, "Style Guides and Rules", ch. 8, 2020.**
  https://abseil.io/resources/swe-book/html/ch08.html
  > Even if a construct is well understood by a project’s engineers, future project members and maintainers are not guaranteed to have the same understanding.

  Clever constructs cost the next maintainer.

## Learn why the code is so before changing it

- **Google, "What to look for in a code review", Comments.**
  https://google.github.io/eng-practices/review/reviewer/looking-for.html
  > If the code isn’t clear enough to explain itself, then the code should be made simpler.

  What a comment would say about what the code does, the code says itself.

- **Google, same page.** https://google.github.io/eng-practices/review/reviewer/looking-for.html
  > mostly comments are for information that the code itself can’t possibly contain, like the reasoning behind a decision.

  A comment holds the reason.

- **Google, same page, the sentence the quote above ends.**
  https://google.github.io/eng-practices/review/reviewer/looking-for.html
  > There are some exceptions (regular expressions and complex algorithms often benefit greatly from comments that explain what they’re doing, for example) but mostly comments are for information that the code itself can’t possibly contain, like the reasoning behind a decision.

  A comment may say what code cannot say plainly, such as what a regular expression matches.

- **Google, "Google Python Style Guide", 3.8.5 Block and Inline Comments.**
  https://google.github.io/styleguide/pyguide.html
  > On the other hand, never describe the code. Assume the person reading the code knows Python (though not what you’re trying to do) better than you do.

  The reader knows the language and lacks the intent.

- **Salvatore Sanfilippo (antirez), "Writing system software: code comments.", antirez.com,
  2018.** https://antirez.com/news/124
  > Why comments explain the reason why the code is doing something, even if what the code is doing is crystal clear.

  Code can be clear and still need its reason.

- **John Ousterhout, "A Philosophy of Software Design vs Clean Code".**
  https://github.com/johnousterhout/aposd-vs-clean-code
  > The second general reason for comments is for important information that is not obvious from the code.

  Where the code looks wrong or roundabout, a comment says why it is right.

- **Tom Manshreck, "Documentation", ch. 10 of Software Engineering at Google, 2020.**
  https://abseil.io/resources/swe-book/html/ch10.html
  > Implementation comments, on the other hand, can assume a lot more domain knowledge of the reader, though be careful in assuming too much: people leave projects, and sometimes it’s safer to be methodical about exactly why you wrote this code the way you did.

  The reason is written down because the writer may not be there to ask.

- **Guido van Rossum, Barry Warsaw and Alyssa Coghlan, "PEP 8", Comments, 2001.**
  https://peps.python.org/pep-0008/
  > Comments that contradict the code are worse than no comments. Always make a priority of keeping the comments up-to-date when the code changes!

  A comment that no longer holds misleads the maintainer.

## Find the same kind of thing done the same way

- **Google, "Google Python Style Guide", 4 Parting Words.**
  https://google.github.io/styleguide/pyguide.html
  > If code you add to a file looks drastically different from the existing code around it, it throws readers out of their rhythm when they go to read it.

  Sameness lets the reader attend to what differs.

- **Google, same guide, 4 Parting Words.** https://google.github.io/styleguide/pyguide.html
  > Consistency should not generally be used as a justification to do things in an old style without considering the benefits of the new style

  Consistency does not keep a worse way in place.

- **Guido van Rossum, Barry Warsaw and Alyssa Coghlan, "PEP 8", A Foolish Consistency, 2001.**
  https://peps.python.org/pep-0008/
  > Consistency within a project is more important. Consistency within one module or function is the most important.

  The nearer the code, the more it should match.

- **Shaindel Schwartz, "Style Guides and Rules", ch. 8, 2020.**
  https://abseil.io/resources/swe-book/html/ch08.html
  > Consistency is what enables any engineer to jump into an unfamiliar part of the codebase and get to work fairly quickly.

  A maintainer moving between modules works at once where things are done alike.

- **Google, "What to look for in a code review", Consistency.**
  https://google.github.io/eng-practices/review/reviewer/looking-for.html
  > If no other rule applies, the author should maintain consistency with the existing code.

  When no rule decides, the existing code decides.

## Change one rule in one place

- **Bill Venners with Andy Hunt and Dave Thomas, "Orthogonality and the DRY Principle", artima.com,
  2003 (Thomas's words).** https://www.artima.com/articles/orthogonality-and-the-dry-principle
  > DRY says that every piece of system knowledge should have one authoritative, unambiguous representation.

  Each rule the code knows is written once.

- **Dave Thomas, same interview.** https://www.artima.com/articles/orthogonality-and-the-dry-principle
  > The obvious answer is, if you have more than one way to express the same thing, at some point the two or three different representations will most likely fall out of step with each other.

  Two copies of a rule drift apart when one is changed.

- **Dave Thomas, same interview.** https://www.artima.com/articles/orthogonality-and-the-dry-principle
  > Most people take DRY to mean you shouldn't duplicate code. That's not its intention.

  The one place is for each piece of knowledge, not for each repeated line.

- **Andy Hunt, same interview.** https://www.artima.com/articles/orthogonality-and-the-dry-principle
  > One piece of knowledge in the domain changes, one piece of the system changes.

  The maintainer's change to one rule touches one place.

- **Andy Hunt, same interview.** https://www.artima.com/articles/orthogonality-and-the-dry-principle
  > The basic idea of orthogonality is that things that are not related conceptually should not be related in the system.

  Code that reaches into another module's insides ties together what is unrelated.

- **Martin Fowler, "Beck Design Rules", 2015.** https://martinfowler.com/bliki/BeckDesignRules.html
  > Kent expressed it as saying everything should be said “Once and only Once.”

  Beck's rule of simple design says the same.

- **D. L. Parnas, "On the Criteria To Be Used in Decomposing Systems into Modules", 1972.**
  https://www.win.tue.nl/~wstomv/edu/2ip30/references/criteria_for_modularization.pdf
  > A data structure, its internal linkings, accessing procedures and modifying procedures are part of a single module. They are not shared by many modules as is conventionally done.

  What knows one thing is kept together.

- **Sandi Metz, "The Wrong Abstraction", sandimetz.com, 2016.**
  https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction
  > duplication is far cheaper than the wrong abstraction

  Lines that look alike but hold different rules are not merged.

- **Sandi Metz, same post.** https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction
  > If you find yourself passing parameters and adding conditional paths through shared code, the abstraction is incorrect.

  A shared function full of flags for its callers holds more than one rule.

- **Kent Beck, "Canon TDD", Software Design: Tidy First? (substack), 2023.**
  https://tidyfirst.substack.com/p/canon-tdd
  > Mistake: abstracting too soon. Duplication is a hint, not a command.

  Repetition is a reason to look, not a rule to merge.

- **Salvatore Sanfilippo (antirez), "Writing system software: code comments.", 2018.**
  https://antirez.com/news/124
  > it is not possible to centralize a given concept or interface in one piece, so there are places in the code that tells you to remember to do things in some other place of the code.

  Where a rule truly cannot be in one place, a comment points to the other place.

## Lose nothing if a line were removed

- **Martin Fowler, "Beck Design Rules", 2015.** https://martinfowler.com/bliki/BeckDesignRules.html
  > The last rule tells us that anything that doesn't serve the three prior rules should be removed.

  A line that does no work is taken out.

- **Martin Fowler, same post.** https://martinfowler.com/bliki/BeckDesignRules.html
  > Ironically the extra complexity of all of these elements usually made the system harder to modify and thus less flexible in practice.

  Parts added for changes that may come make the changes that do come harder.

- **Google, "What to look for in a code review", Complexity.**
  https://google.github.io/eng-practices/review/reviewer/looking-for.html
  > A particular type of complexity is over-engineering, where developers have made the code more generic than it needs to be, or added functionality that isn’t presently needed by the system.

  Code more general than its use is a cost to its reader.

- **Daniela Steidl, Benjamin Hummel and Elmar Juergens, "Quality Analysis of Source Code
  Comments", ICPC 2013.**
  https://www.cqse.eu/fileadmin/content/news/publications/2013-quality-analysis-of-source-code-comments.pdf
  > If source code understanding was not harder with the comment being deleted, the comment would not be helpful.

  A comment is tested by asking what its removal would lose.

- **Daniela Steidl, Benjamin Hummel and Elmar Juergens, same paper.**
  https://www.cqse.eu/fileadmin/content/news/publications/2013-quality-analysis-of-source-code-comments.pdf
  > Member comments in particular should provide more information than just repeating the method name.

  A comment that repeats the name gives the reader nothing.

- **Guido van Rossum, Barry Warsaw and Alyssa Coghlan, "PEP 8", Inline Comments, 2001.**
  https://peps.python.org/pep-0008/
  > Inline comments are unnecessary and in fact distracting if they state the obvious.

  A comment that says what the line plainly does takes attention and gives none.

- **Salvatore Sanfilippo (antirez), "Writing system software: code comments.", 2018.**
  https://antirez.com/news/124
  > A trivial comment is a guide comment where the cognitive load of reading the comment is the same or higher than just reading the associated code.

  The same test, put as reading cost.

- **Salvatore Sanfilippo (antirez), same post.** https://antirez.com/news/124
  > But source code is not for making backups.

  Old code kept in comments belongs in version control.

## Better the code without changing what it does

- **Martin Fowler, "Definition Of Refactoring", martinfowler.com/bliki, 2004.**
  https://martinfowler.com/bliki/DefinitionOfRefactoring.html
  > Refactoring (noun): a change made to the internal structure of software to make it easier to understand and cheaper to modify without changing its observable behavior.

  The definition from Fowler's Refactoring, as he restates it.

- **Martin Fowler, "Refactoring", refactoring.com.** https://refactoring.com/
  > Its heart is a series of small behavior preserving transformations. Each transformation (called a “refactoring”) does little, but a sequence of these transformations can produce a significant restructuring.

  Large improvements are made of small steps.

- **Martin Fowler, same page.** https://refactoring.com/
  > The system is kept fully working after each refactoring, reducing the chances that a system can get seriously broken during the restructuring.

  After each step, every behavior still holds.

- **Martin Fowler, "Opportunistic Refactoring", martinfowler.com/bliki, 2011.**
  https://martinfowler.com/bliki/OpportunisticRefactoring.html
  > This continuous attention to the code is important - but do remember that you should only refactor when your tests are green.

  Refactoring starts from passing tests.

- **Erik Kuefler, "Unit Testing", ch. 12 of Software Engineering at Google, O'Reilly, 2020.**
  https://abseil.io/resources/swe-book/html/ch12.html
  > When an engineer refactors the internals of a system without modifying its interface, whether for performance, clarity, or any other reason, the system’s tests shouldn’t need to change.

  The tests from before the change, left as they were, are the check of a refactoring.

- **Erik Kuefler, same chapter.** https://abseil.io/resources/swe-book/html/ch12.html
  > Tests that need to be changed during a refactoring indicate that either the change is affecting the system’s behavior and isn’t a pure refactoring, or that the tests were not written at an appropriate level of abstraction.

  A test that must change shows a behavior change or a test bound to how the code works inside.

- **Andrew Trenk, "Testing on the Toilet: Test Behavior, Not Implementation", Google Testing Blog,
  2013.** https://testing.googleblog.com/2013/08/testing-on-toilet-test-behavior-not.html
  > Tests that are independent of implementation details are easier to maintain since they don't need to be changed each time you make a change to the implementation.

  Tests through the interface survive a refactoring.

- **"Test Desiderata", testdesiderata.com, no author or date on the page; it links Kent Beck's original papers on medium.com.**
  https://testdesiderata.com/
  > Structure-insensitive — tests should not change their result if the structure of the code changes.

  The property a test needs for a refactoring to be checked by it.

- **Adam Bender, "Testing Overview", ch. 11 of Software Engineering at Google, 2020.**
  https://abseil.io/resources/swe-book/html/ch11.html
  > Changes that refactor code while preserving existing behavior should (ideally) require no changes to existing tests.

  The same rule, from Google's testing overview.

- **Miryung Kim, Thomas Zimmermann and Nachiappan Nagappan, "A Field Study of Refactoring
  Challenges and Benefits", FSE 2012.**
  https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/kim-fse-2012.pdf
  > 77% of the participants consider that refactoring comes with a risk of introducing subtle bugs and functionality regression

  Most developers surveyed at Microsoft saw regression as the main risk.

- **Miryung Kim and others, same paper.**
  https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/kim-fse-2012.pdf
  > “The primary risk is regression, mostly from misunderstanding subtle corner cases in the original code and not accounting for them in the refactored code.”

  The faults come from corner cases the maintainer did not know the code handled.

- **Miryung Kim and others, same paper.**
  https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/kim-fse-2012.pdf
  > Many participants also mentioned that, when a regression test suite is inadequate, there is no safety net for checking the correctness of refactoring.

  Without tests, the maintainer cannot tell a refactoring from a break.

- **Michael Feathers, "Characterization Testing", michaelfeathers.silvrback.com, 2016.**
  https://michaelfeathers.silvrback.com/characterization-testing
  > The purpose of characterization testing is to document your system’s actual behavior, not check for the behavior you wish your system had.

  Where code has no tests, the maintainer first writes tests of what it does now.

- **Michael Feathers, same post.** https://michaelfeathers.silvrback.com/characterization-testing
  > However, if you haven’t determined that the behavior you've uncovered is a bug, it’s often a good idea to leave the test in place.

  A surprising behavior is kept until someone decides it is wrong.

- **Kent Beck, "Structure & Behavior", Software Design: Tidy First? (substack), 2021.**
  https://tidyfirst.substack.com/p/structure-and-behavior
  > One of TF?’s observations is that changes to the structure of the system are fundamentally different from changes to the behavior of the system.

  A change to structure and a change to behavior are made and checked apart.

- **Kent Beck, same post.** https://tidyfirst.substack.com/p/structure-and-behavior
  > Treat reversible and irreversible decisions differently. Reversible decisions don’t need the same level of scrutiny, so pass them on through.

  A structure change is cheap to undo, so its review can be light where the tests hold.

- **Kent Beck, "Canon TDD", 2023.** https://tidyfirst.substack.com/p/canon-tdd
  > Mistake: mixing refactoring into making the test pass. Again with the “wearing two hats” problem. Make it run, then make it right.

  Changing behavior and bettering structure are done one at a time.

- **Google, "Small CLs", Separate Out Refactorings, google.github.io/eng-practices, current.**
  https://google.github.io/eng-practices/review/developer/small-cls.html
  > It’s usually best to do refactorings in a separate CL from feature changes or bug fixes.

  A refactoring goes in a change of its own, so its reviewer sees no behavior change in it.

- **Martin Fowler, "An example of preparatory refactoring", martinfowler.com, 2015.**
  https://martinfowler.com/articles/preparatory-refactoring-example.html
  > So first I refactor the code into the structure that makes it easy to add the feature, or as Kent Beck pithily put it “make the change easy, then make the easy change”.

  A refactoring often comes just before the change it serves.

- **Martin Fowler, "Code Smell", martinfowler.com/bliki, 2006.**
  https://martinfowler.com/bliki/CodeSmell.html
  > A code smell is a surface indication that usually corresponds to a deeper problem in the system.

  A smell tells the maintainer where to look.

- **Martin Fowler, same post.** https://martinfowler.com/bliki/CodeSmell.html
  > The second is that smells don't always indicate a problem. Some long methods are just fine.

  A smell is a reason to look, not a verdict.

## Not found

- Martin Fowler, Refactoring (2nd edition, 2018), the book itself, with its catalog of smells and
  "Two Hats". I did not open it. Fowler's refactoring.com and bliki pages stand in for it.
- Martin Fowler, "Workflows of Refactoring" (2014),
  https://martinfowler.com/articles/workflowsOfRefactoring/. The page opened, but its slides are
  drawn by script, and the text I could read held only their titles.
- Kent Beck, Tidy First? (O'Reilly, 2023), the book. Its O'Reilly chapter pages returned 403. Beck's
  post "Reversible Structure Changes" on his substack is for paying readers only. His free post
  "Structure & Behavior" stands in for both.
- Michael Feathers, Working Effectively with Legacy Code (2004), the book, with its definition of
  legacy code as code without tests. I did not open it. His characterization-testing post stands
  in for it.
- John Ousterhout, A Philosophy of Software Design, the book. Its author's second-edition extract
  (https://web.stanford.edu/~ouster/cgi-bin/aposd2ndEdExtract.pdf) opened but has no text a tool
  could read. His discussion with Robert Martin stands in for it.
- Wen, Nagy, Bavota and Lanza, "A Large-Scale Empirical Study on Code-Comment Inconsistencies",
  ICPC 2019. Both PDF links at usi.ch returned 403.
- A study that measures whether consistent style across modules speeds up a maintainer. I did not
  find one; the entries on consistency above are guidelines, not studies.
