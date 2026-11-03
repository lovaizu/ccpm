# readme

## Goal

From the README alone, someone who meets the product for the first time starts using it only when it serves their work.

## Parts

- **summary**: The product's name first, and under it one sentence that says what kind of thing the product is and what it does.
- **gain**: The paragraph after the summary: whom the product is for and what they gain with it.
- **idea**: After the gain: the idea that makes the gain possible, in a paragraph; where the idea has parts, how they fit together, and each part with what it is and what it ensures for the reader.
- **non-goals**: At the end of the opening, before anything about installing: each thing the product does not do that a reader might expect of it, set apart so the reader sees it as what the product does not do.
- **requirements**: Each thing that must be in place before installing.
- **installation**: The steps that install the product.
- **walkthrough**: One run of the use most readers come for, step by step, each step with what the product shows, up to the result.
- **how-it-works**: One figure of the user, the product's parts and the things they pass, each shown by its name only, and the action or intent of each toward another, so a reader sees at a glance how the opening's promises are kept. Under it stand only the points and what the figure cannot show.
- **links**: Where to read next: for users, the documents for fuller use; apart from them, for those who change the product, the development documents.
- **license**: The license's name, linked to its full text.

## Benefits

- **Q1** (summary): When a colleague asks what the product is, can the reader answer in one sentence that tells them what it does?
- **Q2** (gain): Reading the gain, can the reader tell what the product would let them do, and so whether it is for them?
- **Q3** (gain, idea): When a colleague asks why this product and not another way of doing the same work, can the reader name what it does differently that brings the gain?
- **Q4** (non-goals): Before installing, can the reader tell what the product does not do that they might have expected of it?
- **Q5** (gain, walkthrough): After the walkthrough, can the reader tell that the product would give them, on work of their own, the gain the opening promised?
- **Q6** (requirements, installation, walkthrough): Starting with nothing set up, can the reader get the walkthrough's result by the README's steps alone?
- **Q7** (gain, idea, how-it-works): For each gain and the idea, can the reader see in the figure of how the product works how the product keeps it?
- **Q8** (links): When the reader needs more than the README gives, such as fuller use or a change to the product, can they tell from it where to read next?
- **Q9** (license): Can the reader tell from the README the terms on which they and their team may use the product?
- **Q10** (the whole): Reading from the top, does the reader find each answer just when they come to need it, so they can stop as soon as they have what they came for?

## Practices

### Q1: When a colleague asks what the product is, can the reader answer in one sentence that tells them what it does?

**Thinking**: The sentence names the kind of thing the product is and what it does, in words the reader already uses, so they can say it again to a colleague.

**Steps**

1. Write one sentence on its own line under the title, such as "<Name> is a <kind> that <does what>.", saying what the product does with no feature names or mechanisms.
2. Ask whether a colleague who hears only the sentence could say what the product does; if not, replace each vague or praising word with what the product does.

**Grounds**

- [Art of README](https://web.archive.org/web/20231231175007/https://github.com/hackergrrl/art-of-readme), hackergrrl, github.com/hackergrrl/art-of-readme, Internet Archive copy of 2023-12-31: "One-liner -- having a one-liner that describes the module is useful for getting an idea of what the module does in slightly greater detail."
- [About the repository README file](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes), GitHub, GitHub Docs, no date: "What the project does"
- [Standard Readme](https://github.com/RichardLitt/standard-readme/blob/main/spec.md), Litt, github.com/RichardLitt/standard-readme, spec.md, no date: "Must be on its own line."
- [Make a README](https://www.makeareadme.com/), Guo, makeareadme.com, no date: "Let people know what your project can do specifically."

### Q2: Reading the gain, can the reader tell what the product would let them do, and so whether it is for them?

**Thinking**: The gain is what the reader can do with the product, taken from what the product's users want, such as the objectives in its UX, so the reader tells from it whether the product meets their need.

**Steps**

1. Name whom the product is for by the work they want done.
2. Ask whether a reader outside that group can tell from it that the product is not for them; if not, name the group and the work more closely.

**Grounds**

- [Art of README](https://web.archive.org/web/20231231175007/https://github.com/hackergrrl/art-of-readme), hackergrrl, github.com/hackergrrl/art-of-readme, Internet Archive copy of 2023-12-31: "The consumer wants a module to fulfill their need, so you must explain exactly what need your module fills, and how effectively it does so."
- [Starting an Open Source Project](https://opensource.guide/starting-a-project/), GitHub, Open Source Guides, opensource.guide, no date: "They also explain why your project matters, and what your users can do with it."
- [About the repository README file](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes), GitHub, GitHub Docs, no date: "Why the project is useful"
- [How to write software documentation](https://www.writethedocs.org/guide/writing/beginners-guide-to-docs/), Write the Docs, writethedocs.org, no date: "They don’t know why your project exists or how it meets their needs."

### Q3: When a colleague asks why this product and not another way of doing the same work, can the reader name what it does differently that brings the gain?

**Thinking**: The idea is the one thing the product does that other ways of doing the same work do not, and it is what brings the gain.

**Steps**

1. Write it as one paragraph that names the other way and says what the product does instead.
2. Ask whether the reader could say the difference to a colleague in their own words; if not, replace each word that only praises with what the product does.

**Grounds**

- [Make a README](https://www.makeareadme.com/), Guo, makeareadme.com, no date: "If there are alternatives to your project, this is a good place to list differentiating factors."
- [Make a README](https://www.makeareadme.com/), Guo, makeareadme.com, no date: "Let people know what your project can do specifically."

### Q4: Before installing, can the reader tell what the product does not do that they might have expected of it?

**Thinking**: A non-goal is something the reader could reasonably expect of the product that it does not do, so a reader who needs it learns that before they install.

**Steps**

1. Keep only what the product does not do and a reader could reasonably expect of it.

**Grounds**

- [Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/), Ubl, industrialempathy.com, 2020: "Note, that non-goals aren’t negated goals like “The system shouldn’t crash”, but rather things that could reasonably be goals, but are explicitly chosen not to be goals."

### Q5: After the walkthrough, can the reader tell that the product would give them, on work of their own, the gain the opening promised?

**Thinking**: The walkthrough is one run of the use most readers come for, on work like the reader's, with the product's real output, so the reader sees what they would get.

**Steps**

1. Say at the start what the reader will have at the end.
2. End with the result, and ask whether it shows the gain the opening promised; if not, pick another piece of work or another scenario.

**Grounds**

- [Tutorials](https://diataxis.fr/tutorials/), Procida, Diátaxis, diataxis.fr, no date: "It’s important to allow the learner to form an idea of what they will achieve right from the start."
- [How to write software documentation](https://www.writethedocs.org/guide/writing/beginners-guide-to-docs/), Write the Docs, writethedocs.org, no date: "Show a common example use case for your project."
- [Make a README](https://www.makeareadme.com/), Guo, makeareadme.com, no date: "Use examples liberally, and show the expected output if you can."
- [Tutorials](https://diataxis.fr/tutorials/), Procida, Diátaxis, diataxis.fr, no date: "Show the user actual example output, or even the exact expected output."
- [Art of README](https://web.archive.org/web/20231231175007/https://github.com/hackergrrl/art-of-readme), hackergrrl, github.com/hackergrrl/art-of-readme, Internet Archive copy of 2023-12-31: "I can quickly determine whether the example JS fits the desired style and problem."
- [Tutorials](https://diataxis.fr/tutorials/), Procida, Diátaxis, diataxis.fr, no date: "Your guidance needs to remain focused on what’s required to reach the conclusion, and everything else can be left for another time."

### Q6: Starting with nothing set up, can the reader get the walkthrough's result by the README's steps alone?

**Thinking**: The steps are written for a reader who has nothing set up, and tried that way, because the author's own setup hides the gaps.

**Steps**

1. List each thing that must be in place, by what it is and how the reader tells they have it.
2. Write each install step so the reader can do it without working out what to type, such as a command to copy, even a common one, and after it what the reader sees when it worked.
3. From a machine or sandbox where nothing the product needs is in place, follow the requirements, the install steps and the walkthrough as written, and do nothing they do not say; where a step fails, or needs something the README does not say, write it in and start again.

**Grounds**

- [Starting an Open Source Project](https://opensource.guide/starting-a-project/), GitHub, Open Source Guides, opensource.guide, no date: "Remember that your readers aren’t you."
- [Make a README](https://www.makeareadme.com/), Guo, makeareadme.com, no date: "If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection."
- [Make a README](https://www.makeareadme.com/), Guo, makeareadme.com, no date: "Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible."
- [Standard Readme](https://github.com/RichardLitt/standard-readme/blob/main/spec.md), Litt, github.com/RichardLitt/standard-readme, spec.md, no date: "Code block illustrating how to install."
- [Art of README](https://web.archive.org/web/20231231175007/https://github.com/hackergrrl/art-of-readme), hackergrrl, github.com/hackergrrl/art-of-readme, Internet Archive copy of 2023-12-31: "even if it's just a regular npm install, I'd like to see that mentioned, too."
- [Tutorials](https://diataxis.fr/tutorials/), Procida, Diátaxis, diataxis.fr, no date: "Every step the learner follows should produce a comprehensible result, however small."
- [Tutorials](https://diataxis.fr/tutorials/), Procida, Diátaxis, diataxis.fr, no date: "A learner who follows your directions and doesn’t get the expected results will quickly lose confidence, in the tutorial, the tutor and themselves."

### Q7: For each gain and the idea, can the reader see in the figure of how the product works how the product keeps it?

**Thinking**: How it works shows, at a glance, who does what to whom so that each gain and the idea hold, at a grain a reader new to the product follows; a non-goal, being what the product does not do, is said once in the opening.

**Steps**

1. Point to each gain and the idea, and find the lines of the figure that keep it; where none does, mend the figure or the promise.

**Grounds**

- [System context diagram](https://c4model.com/diagrams/system-context), C4 model, c4model.com, no date: "Draw a diagram showing your system as a box in the centre, surrounded by its users and the other systems that it interacts with."
- [System context diagram](https://c4model.com/diagrams/system-context), C4 model, c4model.com, no date: "Detail isn’t important here as this is your zoomed out view showing a big picture of the system landscape."
- [System context diagram](https://c4model.com/diagrams/system-context), C4 model, c4model.com, no date: "The focus should be on people (actors, roles, personas, etc) and software systems rather than technologies, protocols and other low-level details."
- [System context diagram](https://c4model.com/diagrams/system-context), C4 model, c4model.com, no date: "It’s the sort of diagram that you could show to non-technical people."

### Q8: When the reader needs more than the README gives, such as fuller use or a change to the product, can they tell from it where to read next?

**Thinking**: The README holds what the reader needs to decide and to start, and points to one place for each need that comes after.

**Steps**

1. Write each link so it reaches its document wherever the README is read, such as relative to the README, and open each one.

**Grounds**

- [Art of README](https://web.archive.org/web/20231231175007/https://github.com/hackergrrl/art-of-readme), hackergrrl, github.com/hackergrrl/art-of-readme, Internet Archive copy of 2023-12-31: "Detailed documentation is good -- make separate pages for it! -- but keep your README succinct."
- [About the repository README file](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes), GitHub, GitHub Docs, no date: "A README should only contain information necessary for developers to get started using and contributing to your project. Longer documentation is best suited for wikis."
- [READMEs](https://github.com/google/styleguide/blob/gh-pages/docguide/READMEs.md), Google, Google documentation guide, github.com/google/styleguide, no date: "At a minimum, your `README.md` file should contain a link to your user- and/or team-facing documentation."
- [Starting an Open Source Project](https://opensource.guide/starting-a-project/), GitHub, Open Source Guides, opensource.guide, no date: "Link to your CONTRIBUTING file from your README, so more people see it."
- [About the repository README file](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes), GitHub, GitHub Docs, no date: "Relative links are easier for users who clone your repository."
- [Standard Readme](https://github.com/RichardLitt/standard-readme/blob/main/spec.md), Litt, github.com/RichardLitt/standard-readme, spec.md, no date: "Must not contain broken links."

### Q9: Can the reader tell from the README the terms on which they and their team may use the product?

**Thinking**: A reader may rule the product out by its license alone, so the README names the license and links its full text.

**Steps**

1. Open the link, and check that the text it reaches is the license the name says.

**Grounds**

- [Art of README](https://web.archive.org/web/20231231175007/https://github.com/hackergrrl/art-of-readme), hackergrrl, github.com/hackergrrl/art-of-readme, Internet Archive copy of 2023-12-31: "you're likely to exclude a module VERY quickly if it has a license incompatible with your work."
- [Make a README](https://www.makeareadme.com/), Guo, makeareadme.com, no date: "For open source projects, say how it is licensed."

### Q10: Reading from the top, does the reader find each answer just when they come to need it, so they can stop as soon as they have what they came for?

**Thinking**: The README goes in the order the reader decides in, from what every reader needs to what only a reader who has chosen the product needs.

**Steps**

1. Read the README from the top as someone who meets the product for the first time, and after each part, write the question the reader now has.
2. Check that the next part answers that question; move a part that answers a later one.
3. Cut what no reader needs at the point where it stands, or move it to the document a link leads to.

**Grounds**

- [Art of README](https://web.archive.org/web/20231231175007/https://github.com/hackergrrl/art-of-readme), hackergrrl, github.com/hackergrrl/art-of-readme, Internet Archive copy of 2023-12-31: "can be imagined as a funnel held upright, where the widest end contains the broadest more pertinent details"
- [perlmodstyle](https://github.com/RichardLitt/standard-readme/blob/main/spec.md), Robert, quoted in Litt, "Standard Readme", github.com/RichardLitt/standard-readme, spec.md, no date: "Ideally, someone who's slightly familiar with your module should be able to refresh their memory without hitting "page down"."
- [Art of README](https://web.archive.org/web/20231231175007/https://github.com/hackergrrl/art-of-readme), hackergrrl, github.com/hackergrrl/art-of-readme, Internet Archive copy of 2023-12-31: "The ideal README is as short as it can be without being any shorter."
