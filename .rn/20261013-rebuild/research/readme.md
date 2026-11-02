# README: best practice from sources

Each entry gives a source, its URL, a quote copied from the page, and one line on what the quote
says about the README's reader, a part of the README, or a way of making it. Every page was opened
and read on 2026-11-02. Quotes from PDF text keep the words, but ligatures such as "ﬁ" are written
as plain letters.

## The reader and their moment

### GitHub Docs, the first thing a visitor sees

- Source: GitHub, "About the repository README file", GitHub Docs, n.d.
- URL: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes
- Quote: "A README is often the first item a visitor will see when visiting your repository."
- Says: the reader meets the README first, as a visitor who does not know the project yet.

### Prana et al., the first impression

- Source: Gede Artha Azriadi Prana, Christoph Treude, Ferdian Thung, Thushari Atapattu, David Lo,
  "Categorizing the Content of GitHub README Files", arXiv:1802.06997v2, 2018.
- URL: https://arxiv.org/abs/1802.06997
- Quote: "The README.md file for a repository on GitHub is often the first project document that a
  developer will see when they encounter a new project. This first impression is crucial, as Fogel
  [21] states: “The very first thing a visitor learns about a project is what its home page looks
  like. [...] This is the first piece of information your project puts out, and the impression it
  creates will carry over to the rest of the project by association.”"
- Says: what the reader takes from the README colours how they see the rest of the project.

### Art of README, the first and maybe only look

- Source: hackergrrl (noffle), "Art of README", GitHub repository README, read through the Internet
  Archive copy of 2023-12-31.
- URL: https://web.archive.org/web/20231231175007/https://github.com/hackergrrl/art-of-readme
- Quote: "A README is a module consumer's first -- and maybe only -- look into your creation. The
  consumer wants a module to fulfill their need, so you must explain exactly what need your module
  fills, and how effectively it does so."
- Says: the reader comes with a need, and the README must say which need the product fills.

### Google documentation guide, first-time users

- Source: Google, "READMEs", Google style guides, docguide/READMEs.md, n.d.
- URL: https://github.com/google/styleguide/blob/gh-pages/docguide/READMEs.md
- Quote: "README files provide critical information for people browsing your code, especially
  first-time users."
- Says: the README is written for the person who arrives without knowing the code.

### Make a README, where the newcomer starts

- Source: Danny Guo, "Make a README", makeareadme.com, n.d.
- URL: https://www.makeareadme.com/
- Quote: "In the top level directory of the project. This is where someone who is new to your project
  will start out."
- Says: the README sits where a newcomer starts, so it serves the newcomer.

### Write the Docs, two audiences

- Source: Write the Docs, "How to write software documentation", writethedocs.org, n.d.
- URL: https://www.writethedocs.org/guide/writing/beginners-guide-to-docs/
- Quote: "Users - want to use your code and don’t care how it works." and "Developers - want to
  contribute to your code."
- Says: users and contributors need different things, so the writer first names which one they
  write for.

### Open Source Guides, readers are not you

- Source: GitHub, "Starting an Open Source Project", Open Source Guides, opensource.guide, n.d.
- URL: https://opensource.guide/starting-a-project/
- Quote: "Better documentation means more users, less support requests, and more contributors. (…)
  Remember that your readers aren’t you."
- Says: the writer must not assume the reader knows what the writer knows.

## Deciding whether the product is for them

### Open Source Guides, the four questions

- Source: GitHub, "Starting an Open Source Project", Open Source Guides, opensource.guide, n.d.
- URL: https://opensource.guide/starting-a-project/
- Quote: "READMEs do more than explain how to use your project. They also explain why your project
  matters, and what your users can do with it." and the list items "What does this project do?",
  "Why is this project useful?", "How do I get started?" and "Where can I get more help, if I need
  it?"
- Says: the README answers what it does and why it is useful before how to start.

### GitHub Docs, what a README usually holds

- Source: GitHub, "About the repository README file", GitHub Docs, n.d.
- URL: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes
- Quote: "What the project does", "Why the project is useful", "How users can get started with the
  project", "Where users can get help with your project", "Who maintains and contributes to the
  project"
- Says: GitHub lists five things a README tells, in this order.

### Write the Docs, why people do not use code

- Source: Write the Docs, "How to write software documentation", writethedocs.org, n.d.
- URL: https://www.writethedocs.org/guide/writing/beginners-guide-to-docs/
- Quote: "They don’t know why your project exists or how it meets their needs." and "Regardless,
  clearly state what your project does and why."
- Says: a reader who cannot see why the product exists does not use it.

### Make a README, the description and alternatives

- Source: Danny Guo, "Make a README", makeareadme.com, n.d.
- URL: https://www.makeareadme.com/
- Quote: "Let people know what your project can do specifically. Provide context and add a link to
  any reference visitors might be unfamiliar with. A list of Features or a Background subsection can
  also be added here. If there are alternatives to your project, this is a good place to list
  differentiating factors."
- Says: the description tells what the product does and how it differs from other ways.

### Prana et al., purpose is often missing

- Source: Prana et al., "Categorizing the Content of GitHub README Files", arXiv:1802.06997v2, 2018.
- URL: https://arxiv.org/abs/1802.06997
- Quote: "We find that information discussing the ‘What’ and ‘How’ of a repository is very common,
  while many README files lack information regarding the purpose and status of a repository."
- Says: in 393 sampled repositories, READMEs often skip why the project exists and what state it is
  in.

### Prana et al., the 'Why' category

- Source: Prana et al., "Categorizing the Content of GitHub README Files", arXiv:1802.06997v2, 2018.
- URL: https://arxiv.org/abs/1802.06997
- Quote: "Conversely, category two (‘Why’) is rare in README files. For instance, some repositories
  compare their work to other repositories based on factors such as simplicity, flexibility, and
  performance. Others list advantages of their project in the introduction."
- Says: a 'Why' part holds the advantages and the comparison with other projects.

### Prana et al., what readers expect

- Source: Prana et al., "Categorizing the Content of GitHub README Files", arXiv:1802.06997v2, 2018.
- URL: https://arxiv.org/abs/1802.06997
- Quote: "Usage instructions (e.g., “How to use the features or components of the repository”) and
  license information (e.g., “With my job it’s most important to know the licensing information”)
  were identified as most important by three participants each."
- Says: twenty professionals named usage and licence most often as the one thing a README must hold.

### Art of README, name and one-liner

- Source: hackergrrl (noffle), "Art of README", Internet Archive copy of 2023-12-31.
- URL: https://web.archive.org/web/20231231175007/https://github.com/hackergrrl/art-of-readme
- Quote: "Name -- self-explanatory names are best." and "One-liner -- having a one-liner that
  describes the module is useful for getting an idea of what the module does in slightly greater
  detail."
- Says: the reader judges from the name and one line whether to read on.

### Standard Readme, the short description

- Source: Richard Litt, "Standard Readme" specification, spec.md, GitHub, n.d.
- URL: https://github.com/RichardLitt/standard-readme/blob/main/spec.md
- Quote: "Must be less than 120 characters." and "Must be on its own line."
- Says: the short description is one short line under the title.

### Google documentation guide, status

- Source: Google, "READMEs", Google style guides, n.d.
- URL: https://github.com/google/styleguide/blob/gh-pages/docguide/READMEs.md
- Quote: "Status of whether this package or library is deprecated, or not for general release, etc."
- Says: the reader needs to know before use whether the product is meant for them to use now.

### Make a README, project status

- Source: Danny Guo, "Make a README", makeareadme.com, n.d.
- URL: https://www.makeareadme.com/
- Quote: "If you have run out of energy or time for your project, put a note at the top of the README
  saying that development has slowed down or stopped completely."
- Says: a limit on the product's future goes at the top, where the reader decides.

## Reading in the order they decide

### Art of README, cognitive funneling

- Source: hackergrrl (noffle), "Art of README", Internet Archive copy of 2023-12-31.
- URL: https://web.archive.org/web/20231231175007/https://github.com/hackergrrl/art-of-readme
- Quote: "The ordering presented here is lovingly referred to as "cognitive funneling," and can be
  imagined as a funnel held upright, where the widest end contains the broadest more pertinent
  details, and moving deeper down into the funnel presents more specific details that are pertinent
  for only a reader who is interested enough in your work to have reached that deeply in the
  document."
- Says: the README goes from what every reader needs to what only a convinced reader needs.

### Art of README, a predictable format

- Source: hackergrrl (noffle), "Art of README", Internet Archive copy of 2023-12-31.
- URL: https://web.archive.org/web/20231231175007/https://github.com/hackergrrl/art-of-readme
- Quote: "Thus, it follows that in a README it is desirable to have:" followed by the list items "a
  predictable format" and "certain key elements present"
- Says: a reader who scans many READMEs finds each thing faster where they expect it.

### Standard Readme, quoting perlmodstyle

- Source: Richard Litt, "Standard Readme" specification, quoting Kirrily "Skud" Robert, perlmodstyle.
- URL: https://github.com/RichardLitt/standard-readme/blob/main/spec.md
- Quote: "Ideally, someone who's slightly familiar with your module should be able to refresh their
  memory without hitting "page down". As your reader continues through the document, they should
  receive a progressively greater amount of knowledge."
- Says: the first screen serves the returning reader, and detail grows down the page.

### Standard Readme, fixed order

- Source: Richard Litt, "Standard Readme" specification, n.d.
- URL: https://github.com/RichardLitt/standard-readme/blob/main/spec.md
- Quote: "Sections must appear in order given below. Optional sections may be omitted."
- Says: the specification fixes the order of sections, from title to licence.

### Prana et al., labels help readers find things

- Source: Prana et al., "Categorizing the Content of GitHub README Files", arXiv:1802.06997v2, 2018.
- URL: https://arxiv.org/abs/1802.06997
- Quote: "The majority of participants perceived the automated labeling of sections based on our
  classifier to ease information discovery."
- Says: readers find information faster when each section's kind is plain.

## Checking they can start, and installing

### Make a README, installation steps

- Source: Danny Guo, "Make a README", makeareadme.com, n.d.
- URL: https://www.makeareadme.com/
- Quote: "However, consider the possibility that whoever is reading your README is a novice and would
  like more guidance. Listing specific steps helps remove ambiguity and gets people to using your
  project as quickly as possible. If it only runs in a specific context like a particular programming
  language version or operating system or has dependencies that have to be installed manually, also
  add a Requirements subsection."
- Says: the reader gets exact steps, and a list of what must be in place first.

### Standard Readme, install

- Source: Richard Litt, "Standard Readme" specification, n.d.
- URL: https://github.com/RichardLitt/standard-readme/blob/main/spec.md
- Quote: "Code block illustrating how to install." and "`Dependencies`. Required if there are unusual
  dependencies or dependencies that must be manually installed."
- Says: the install part is a code block, with a dependency list where the reader must add things.

### Prana et al., what readers expect to find

- Source: Prana et al., "Categorizing the Content of GitHub README Files", arXiv:1802.06997v2, 2018.
- URL: https://arxiv.org/abs/1802.06997
- Quote: "participants mentioned usage instructions (five participants), installation instructions
  (three participants), prerequisites (three participants), repository license (two participants),
  purpose of the repository and target audience (two participants), known bugs and trouble-shooting
  tips (two participants)"
- Says: readers expect usage, installation and prerequisites first.

### Art of README, installation

- Source: hackergrrl (noffle), "Art of README", Internet Archive copy of 2023-12-31.
- URL: https://web.archive.org/web/20231231175007/https://github.com/hackergrrl/art-of-readme
- Quote: "Installation -- if I've read this far down, then I'm sold on trying out the module. If there
  are nonstandard installation notes, here's where they'd go, but even if it's just a regular npm
  install, I'd like to see that mentioned, too."
- Says: even a standard install command is written out for the reader who has decided.

## Seeing it work on their own case

### Make a README, usage with output

- Source: Danny Guo, "Make a README", makeareadme.com, n.d.
- URL: https://www.makeareadme.com/
- Quote: "Use examples liberally, and show the expected output if you can. It's helpful to have inline
  the smallest example of usage that you can demonstrate, while providing links to more sophisticated
  examples if they are too long to reasonably include in the README."
- Says: the README shows the smallest example with its output, and links to longer ones.

### Art of README, usage before the API

- Source: hackergrrl (noffle), "Art of README", Internet Archive copy of 2023-12-31.
- URL: https://web.archive.org/web/20231231175007/https://github.com/hackergrrl/art-of-readme
- Quote: "Usage -- rather than starting to delve into the API docs, it'd be great to see what the
  module looks like in action. I can quickly determine whether the example JS fits the desired style
  and problem."
- Says: an example in action lets the reader judge fit before reading the details.

### Write the Docs, a small code example

- Source: Write the Docs, "How to write software documentation", writethedocs.org, n.d.
- URL: https://www.writethedocs.org/guide/writing/beginners-guide-to-docs/
- Quote: "Show a common example use case for your project."
- Says: the example is a common use, not a rare one.

### Diátaxis, tutorials: show where the learner is going

- Source: Daniele Procida, "Tutorials", Diátaxis, diataxis.fr, n.d.
- URL: https://diataxis.fr/tutorials/
- Quote: "It’s important to allow the learner to form an idea of what they will achieve right from the
  start. As well as helping to set expectations, it allows them to see themselves building towards
  the completed goal as they work."
- Says: a walkthrough opens with the result the reader will reach.

### Diátaxis, tutorials: visible results

- Source: Daniele Procida, "Tutorials", Diátaxis, n.d.
- URL: https://diataxis.fr/tutorials/
- Quote: "Every step the learner follows should produce a comprehensible result, however small."
- Says: each step of a walkthrough shows the reader something they can check.

### Diátaxis, tutorials: the narrative of the expected

- Source: Daniele Procida, "Tutorials", Diátaxis, n.d.
- URL: https://diataxis.fr/tutorials/
- Quote: "Keep up a narrative of expectations: “You will notice that …”; “After a few moments, the
  server responds with …”. Show the user actual example output, or even the exact expected output."
- Says: the walkthrough tells the reader what they should see after each step.

### Diátaxis, tutorials: minimal explanation

- Source: Daniele Procida, "Tutorials", Diátaxis, n.d.
- URL: https://diataxis.fr/tutorials/
- Quote: "A tutorial is not the place for explanation. In a tutorial, the user is focused on correctly
  following your directions and getting the expected results."
- Says: explanation in a walkthrough is cut to a line, with a link to the rest.

### Diátaxis, tutorials: one path

- Source: Daniele Procida, "Tutorials", Diátaxis, n.d.
- URL: https://diataxis.fr/tutorials/
- Quote: "Your guidance needs to remain focused on what’s required to reach the conclusion, and
  everything else can be left for another time."
- Says: a walkthrough leaves out options and alternatives.

### Diátaxis, tutorials: reliability

- Source: Daniele Procida, "Tutorials", Diátaxis, n.d.
- URL: https://diataxis.fr/tutorials/
- Quote: "A learner who follows your directions and doesn’t get the expected results will quickly lose
  confidence, in the tutorial, the tutor and themselves."
- Says: a walkthrough that fails on the reader's machine costs their trust, so it must be run and
  checked.

### Standard Readme, usage

- Source: Richard Litt, "Standard Readme" specification, n.d.
- URL: https://github.com/RichardLitt/standard-readme/blob/main/spec.md
- Quote: "Code block illustrating common usage." and "If CLI compatible, code block indicating common
  usage."
- Says: usage is shown as a code block the reader can copy.

## Understanding how it works, to explain it to others

### Diátaxis, explanation

- Source: Daniele Procida, "Explanation", Diátaxis, n.d.
- URL: https://diataxis.fr/explanation/
- Quote: "Provide background and context in your explanation: explain why things are so - design
  decisions, historical reasons, technical constraints - draw implications, mention specific
  examples."
- Says: an explanation of how the product works tells why it is so.

### Diátaxis, explanation joins things together

- Source: Daniele Procida, "Start here - Diátaxis in five minutes", Diátaxis, n.d.
- URL: https://diataxis.fr/start-here/
- Quote: "Explanatory guides provide context and background. They serve the need to understand and put
  things in a bigger picture. Explanation joins things together, and helps answer the question why?"
- Says: the reader who must explain the product to someone else needs the bigger picture.

### Art of README, quoting Ken Williams

- Source: hackergrrl (noffle), "Art of README", quoting Ken Williams, Internet Archive copy of
  2023-12-31.
- URL: https://web.archive.org/web/20231231175007/https://github.com/hackergrrl/art-of-readme
- Quote: "Your documentation is complete when someone can use your module without ever having to look
  at its code."
- Says: the reader should never need the source code to use the product.

### Make a README, visuals

- Source: Danny Guo, "Make a README", makeareadme.com, n.d.
- URL: https://www.makeareadme.com/
- Quote: "Depending on what you are making, it can be a good idea to include screenshots or even a
  video (you'll frequently see GIFs rather than actual videos)."
- Says: a picture shows the reader what the product looks like.

### Venigalla and Chimalakonda, lists, images and links

- Source: Akhila Sri Manasa Venigalla, Sridhar Chimalakonda, "An Empirical Study On Correlation
  between Readme Content and Project Popularity", arXiv:2206.10772, 2022.
- URL: https://arxiv.org/abs/2206.10772
- Quote: "We perform the study on 1950 readme files of public GitHub projects, spanning across ten
  programming languages, and observe that readme files in majority of the popular projects are well
  organised using lists and images, and comprise links to external sources."
- Says: popular projects' READMEs use lists, images and links.

## Finding where to read next, so the README stays short

### Art of README, brevity

- Source: hackergrrl (noffle), "Art of README", Internet Archive copy of 2023-12-31.
- URL: https://web.archive.org/web/20231231175007/https://github.com/hackergrrl/art-of-readme
- Quote: "The ideal README is as short as it can be without being any shorter. Detailed documentation
  is good -- make separate pages for it! -- but keep your README succinct."
- Says: detail goes to other pages, and the README links to them.

### GitHub Docs, wikis for longer documentation

- Source: GitHub, "About the repository README file", GitHub Docs, n.d.
- URL: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes
- Quote: "A README should only contain information necessary for developers to get started using and
  contributing to your project. Longer documentation is best suited for wikis."
- Says: the README holds only what is needed to start.

### GitHub Docs, relative links

- Source: GitHub, "About the repository README file", GitHub Docs, n.d.
- URL: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes
- Quote: "Relative links are easier for users who clone your repository. Absolute links may not work
  in clones of your repository - we recommend using relative links to refer to other files within
  your repository."
- Says: links to other files in the repository are relative, so they work in a clone.

### Make a README, too long or too short

- Source: Danny Guo, "Make a README", makeareadme.com, n.d.
- URL: https://www.makeareadme.com/
- Quote: "Also keep in mind that while a README can be too long and detailed, too long is better than
  too short. If you think your README is too long, consider utilizing another form of documentation
  rather than cutting out information."
- Says: a long README is moved into other documents, not cut.

### Google documentation guide, link at a minimum

- Source: Google, "READMEs", Google style guides, n.d.
- URL: https://github.com/google/styleguide/blob/gh-pages/docguide/READMEs.md
- Quote: "At a minimum, your `README.md` file should contain a link to your user- and/or team-facing
  documentation."
- Says: the one thing every README holds is a link to the fuller documentation.

### Prana et al., references

- Source: Prana et al., "Categorizing the Content of GitHub README Files", arXiv:1802.06997v2, 2018.
- URL: https://arxiv.org/abs/1802.06997
- Quote: "The second most frequent category is ‘References’. This category includes links to further
  details such as API documentation, getting support, and translations."
- Says: links onward are the second most common kind of README section.

### Make a README, support

- Source: Danny Guo, "Make a README", makeareadme.com, n.d.
- URL: https://www.makeareadme.com/
- Quote: "Tell people where they can go to for help. It can be any combination of an issue tracker, a
  chat room, an email address, etc."
- Says: a reader who gets stuck learns where to ask.

### Make a README, contributing

- Source: Danny Guo, "Make a README", makeareadme.com, n.d.
- URL: https://www.makeareadme.com/
- Quote: "For people who want to make changes to your project, it's helpful to have some documentation
  on how to get started. Perhaps there is a script that they should run or some environment variables
  that they need to set. Make these steps explicit."
- Says: the contributor is a second reader, with their own steps.

### Open Source Guides, link to CONTRIBUTING

- Source: GitHub, "Starting an Open Source Project", Open Source Guides, n.d.
- URL: https://opensource.guide/starting-a-project/
- Quote: "Link to your CONTRIBUTING file from your README, so more people see it."
- Says: the README points contributors to the file written for them.

### Venigalla and Chimalakonda, contribution guidelines and references

- Source: Venigalla and Chimalakonda, "An Empirical Study On Correlation between Readme Content and
  Project Popularity", arXiv:2206.10772, 2022.
- URL: https://arxiv.org/abs/2206.10772
- Quote: "Also, repositories with readme files containing contribution guidelines and references were
  observed to be associated with higher popularity."
- Says: READMEs with contribution guidelines and references go with more popular projects.

## Knowing the terms of use

### Art of README, licence placement

- Source: hackergrrl (noffle), "Art of README", Internet Archive copy of 2023-12-31.
- URL: https://web.archive.org/web/20231231175007/https://github.com/hackergrrl/art-of-readme
- Quote: "License -- most modules put this at the very bottom, but this might actually be better to
  have higher up; you're likely to exclude a module VERY quickly if it has a license incompatible with
  your work."
- Says: the reader may rule the product out by its licence alone.

### Make a README, licence

- Source: Danny Guo, "Make a README", makeareadme.com, n.d.
- URL: https://www.makeareadme.com/
- Quote: "For open source projects, say how it is licensed."
- Says: the README names the licence.

### Open Source Guides, a licence is required

- Source: GitHub, "Starting an Open Source Project", Open Source Guides, n.d.
- URL: https://opensource.guide/starting-a-project/
- Quote: "An open source license guarantees that others can use, copy, modify, and contribute back to
  your project without repercussions."
- Says: the licence is what lets the reader use the product.

## Ways of making a README

### Tom Preston-Werner, write the README first

- Source: Tom Preston-Werner, "Readme Driven Development", tom.preston-werner.com, 2010.
- URL: https://tom.preston-werner.com/2010/08/23/readme-driven-development.html
- Quote: "Write your Readme first." and "Until you’ve written about your software, you have no idea
  what you’ll be coding."
- Says: writing the README before the code settles what the product is.

### Tom Preston-Werner, a single introductory file

- Source: Tom Preston-Werner, "Readme Driven Development", 2010.
- URL: https://tom.preston-werner.com/2010/08/23/readme-driven-development.html
- Quote: "By restricting your design documentation to a single file that is intended to be read as an
  introduction to your software, RDD keeps you safe from DDD-turned-waterfall syndrome by punishing
  you for lengthy or overprecise specification."
- Says: one introductory file keeps the design short and readable.

### Tom Preston-Werner, the team reads it before the code exists

- Source: Tom Preston-Werner, "Readme Driven Development", 2010.
- URL: https://tom.preston-werner.com/2010/08/23/readme-driven-development.html
- Quote: "If everyone else on the team has access to this information before you’ve completed the
  project, then they can confidently start work on other projects that will interface with your code."
- Says: an early README lets others build against the product before it is done.

### Diátaxis, four kinds of documentation

- Source: Daniele Procida, "Start here - Diátaxis in five minutes", Diátaxis, n.d.
- URL: https://diataxis.fr/start-here/
- Quote: "The core idea of Diátaxis is that there are fundamentally four identifiable kinds of
  documentation, that respond to four different needs. The four kinds are: tutorials, how-to guides,
  reference and explanation. Each has a different purpose, and needs to be written in a different
  way."
- Says: each part of a README serves one of these needs, and is written for that need.

### Diátaxis, crossing the boundaries

- Source: Daniele Procida, "Start here - Diátaxis in five minutes", Diátaxis, n.d.
- URL: https://diataxis.fr/start-here/
- Quote: "Crossing or blurring the boundaries described in the map is at the heart of a vast number of
  problems in documentation."
- Says: a part that mixes two kinds, such as steps full of explanation, serves neither need.

### Diátaxis, the compass

- Source: Daniele Procida, "Start here - Diátaxis in five minutes", Diátaxis, n.d.
- URL: https://diataxis.fr/start-here/
- Quote: "When creating documentation, it helps clarify your own intentions, and helps make sure you’re
  actually doing what you think you’re doing."
- Says: the writer asks of each passage whether it informs action or understanding, for study or for
  work.

### Diátaxis, the workflow

- Source: Daniele Procida, "Start here - Diátaxis in five minutes", Diátaxis, n.d.
- URL: https://diataxis.fr/start-here/
- Quote: "Ask: is there any way in which it could be improved?" and "Decide on one thing you could do
  to it right now, however small, that would improve it."
- Says: the writer improves the document one small change at a time.

### Diátaxis, how-to guides from the user's view

- Source: Daniele Procida, "How-to guides", Diátaxis, n.d.
- URL: https://diataxis.fr/how-to-guides/
- Quote: "How-to guides must be written from the perspective of the user, not of the machinery."
- Says: steps are framed by what the user wants done, not by what the tool can do.

### Standard Readme, checks a README must pass

- Source: Richard Litt, "Standard Readme" specification, n.d.
- URL: https://github.com/RichardLitt/standard-readme/blob/main/spec.md
- Quote: "Must not contain broken links." and "If there are code examples, they should be linted in
  the same way as the code is linted in the rest of the project."
- Says: links and code examples in a README are checked like code.

### Write the Docs, avoid FAQs as documentation

- Source: Write the Docs, "How to write software documentation", writethedocs.org, n.d.
- URL: https://www.writethedocs.org/guide/writing/beginners-guide-to-docs/
- Quote: "Importantly, beware of overusing Frequently Asked Questions (FAQs) as documentation."
- Says: an FAQ grows stale and scattered, so it does not stand in for the README's parts.

## Not found

- Art of README on GitHub: `github.com/hackergrrl/art-of-readme` and its raw README returned 404, and
  the Medium copy by noffle returned 403. The entries above cite the Internet Archive copy of
  2023-12-31 instead.
- Prana et al. in its journal form: only the arXiv version (v2, 2018) was opened, so no journal page
  or page numbers are cited.
- A source on "non-goals" in a README: no README guide I opened names a non-goals part. Google's
  design-doc practice names one, and it is in the architecture file.
- A source on a README reader who explains or recommends the product to a colleague or a manager: no
  guide or study I opened addresses that reader directly.
- A source on a figure of a product's parts in a README: no README guide I opened asks for one beyond
  screenshots or video.
- Diátaxis on a README as such: the pages I opened (home, start here, tutorials, how-to guides,
  explanation) do not discuss a README; the entries apply its four kinds to the README's parts.
