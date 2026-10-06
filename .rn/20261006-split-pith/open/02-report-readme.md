# Check: pith/README.md

Target: pith/README.md
Receiver and purpose: a Claude Code user meeting pith for the first time, who reads it to decide whether to install pith and then starts using it on their own work (a document, a prompt, code, tests). Some have used /writ:pith before, some use writ.
Aim: The reader learns from the opening that pith lets them check what they made by what happened when it was actually used as its receiver would use it, by a first user that does not know the discussion or how the work was made, rather than by their own reading filled with what they meant; and that this works for any work, a document, a prompt, code or tests, because for a kind of work with no essentials file pith first writes one worked back from the purpose, tries it on a real work, and keeps it in .pith/essentials/<kind>.md for the next check. They take this as the reason to choose pith over reading the work over themselves or asking the AI that made it. They take in the flow: call /pith:up with the work, its receiver and purpose, and an aim written out; pith returns a Good or More for every question with place and evidence, a short result, and a result file in .pith/open/ that pith does not commit; a missing aim or a question the aim does not cover is returned before any first user runs. They know what to do after: commit the file if they want to keep it, fix Mores, recall pith to recheck a More about what the work is for (a new first user on that question alone), settle other Mores in the file themselves (fixed becomes Good, left gets Left because:), and once all are settled copy the file into a commit message and delete it; a few lines of a result file shown in the README let them see what a More, a More rewritten as Good, and Left because: look like, and which fixed More goes back to pith and which they settle themselves. A former /writ:pith user learns that the same check is now /pith:up and comes installed with writ; a writ or rn user learns both check through pith, so an improvement reaches both, and that writ and rn keep their own essentials files and hand them to pith. Decided by the user: /pith:up called directly uses the essentials files named in the call, or else the one for the work's kind in .pith/essentials/, written first when there is none; it never uses writ's or another plugin's essentials, whether writ is installed or not, and checking with writ's essentials is done through /writ:up. With the README alone the reader can install it: Claude Code, Python 3.9 or later (pith stops rather than skip a check without it), no Node.js, the marketplace lovaizu/ccpm and /plugin install pith@ccpm, and knows writ or rn users already have it. They learn no internal names they need neither to decide nor to start.

The first user read the README once from the top as a newcomer who had used /writ:pith before, checked with `ls` and `.claude-plugin/marketplace.json` the places the README sends the reader, and did not run the install commands. It found that `pith/` holds only `README.md` (no `pith/docs/`), that `LICENSE` exists at the root, and that `.claude-plugin/marketplace.json` lists only `rn` and `writ`.

On the recheck, a new first user answered four questions alone (doc.md: decide and do; doc.md: stop, go back or look ahead; readme.md: the opening; readme.md: installing from the README alone), told that pith is in the marketplace and pith/docs/design.md exists for a real reader. It ran only `python3 --version`.

On the second recheck, after README:3, 88 and 96 were fixed, a new first user answered two questions alone (doc.md: stop, go back or look ahead; readme.md: installing from the README alone), told the same. It ran `python3 --version` and listed `~/.claude/plugins/cache/ccpm/`, which holds `rn` and `writ` 0.1.0 and no `pith`.

On the third recheck, after README:108-112 (which essentials /pith:up uses when called directly) and README:84-106 (a few lines of a result file, and where the line falls between a More to recheck and one settled in the file) were fixed, a new first user answered two questions alone (doc.md: stop, go back or look ahead; readme.md: installing from the README alone), told the same. It ran `python3 --version` and listed `~/.claude/plugins/cache/ccpm/`, which holds `rn` and `writ` and no `pith`. A More found again at the same place with the same struggle as one left earlier keeps the earlier `Left because:`.

On the fourth recheck, after README:11 and README:112 (which command a former /writ:pith user calls, and what /writ:up does) and README:88 with the excerpt's Report line (the two extra findings) were fixed, a new first user answered two questions alone (doc.md: stop, go back or look ahead; readme.md: installing from the README alone), told the same. It ran `python3 --version` and checked that the README's links exist.

The result was then settled without a recheck: README:11 and README:88 were fixed, and the other Mores of the fourth recheck were left with a reason.

## doc.md: Once you finished reading, what did you take it you should decide and do?

Report: When I finished, I took it that I had two things to decide and do.

1. **Whether I need to install anything.**
   - README:102 says "If you have writ or rn, pith is already installed."
   - README:11 says the check "is now `/pith:up`, and it comes installed with writ."
   - So as a writ user I would install nothing and just start typing `/pith:up` instead of `/writ:pith`.
   - Without writ or rn, I would run the two commands at README:105-106 and check that I have Python 3.9 or later (README:100).
2. **How to call it.** I would call `/pith:up` with three things:
   - the work's path
   - who uses it and what for ("who uses it and what for", README:22)
   - an aim written out in sentences (README:36, "Write your aim out in sentences when you call pith")
   I modelled the call on README:43-45, where a free-text sentence starts "The aim is ...".

After a result comes back, I took these steps:
- Read the Good and More lines.
- Fix the Mores.
- Recheck by naming the result file (README:88).
- Settle the remaining Mores by hand, either rewriting them as Good or adding `Left because:`.
- Finally copy the file into a commit message and delete it in that commit (README:90).

I also took it that pith will write `.pith/essentials/<kind>.md` into my repository when no essentials file exists for my kind of work (README:47, 71, 82). From README:86 I took it that pith never commits that result file for me. I took the deciding reason to install from README:9: the check is done by "a separate AI that does not know the discussion".

- Good: `pith/README.md:11` The reader decides whether to install from whether they have writ or rn, and a former /writ:pith user switches to /pith:up with nothing to install.
  - Evidence (report): "So as a writ user I would install nothing and just start typing `/pith:up` instead of `/writ:pith`."
- Good: `pith/README.md:104` The reader now knows to recheck by naming the result file in a new call, and to settle the other Mores by rewriting them as Good or adding `Left because:`.
  - Evidence (report): "Settle the remaining Mores by hand, either rewriting them as Good or adding `Left because:`."
- Good: `pith/README.md:86` The reader takes it that pith does not commit the result file, and that they clear it into a commit once settled.
  - Evidence (report): "From README:86 I took it that pith never commits that result file for me."

## doc.md: Which parts did you use to decide or act, which did you skip without using, and where did you find yourself reading again what you had already read?

Report: Parts I used to decide:
- the three benefits at README:5-7
- the paragraph at README:9 on why my own rereading does not find these places
- the PR-review example at README:37-58

Parts I used to act:
- README:35 (write the aim out)
- README:85-89 (result file lifecycle)
- README:99-108 (getting started)

Parts I skimmed or skipped:
- README:91-95 ("With writ and rn"). It did not change what I would do, except that README:101 repeats that writ or rn already brings pith.
- README:110-112 (design document)
- README:114-116 (license)

Places where I read the same thing again:
- README:31 ("never your aim. Knowing the aim, it would use the work looking for it, and fill in what is missing in its head") repeats README:9 ("Both know what you meant, and fill in what the work leaves out without noticing").
- README:81 ("pith works the questions back from the purpose you gave, and tries them on a real work of that kind") repeats README:7 and the opt block at README:21-23.
- "Comes installed with writ" appears at README:11, README:93 and README:101.
- README:60 ("Every question gets one line…") restates the parenthetical inside the example at README:53.

- Good: `pith/README.md:5-9` The opening benefits and the reason against reading it over oneself carry the decision; the reader used them, the PR-review example, and the aim, result-file and getting-started parts to act.
  - Evidence (report): "the paragraph at README:9 on why my own rereading does not find these places"
- Good: `pith/README.md:110` The reader meets the tie between writ, rn and pith once there, without the install being repeated in that section.
  - Evidence (work): "both check their work through pith, so an improvement to how work is checked is made once in pith and reaches both."
- More: `pith/README.md:108-112` The newcomer skimmed the writ and rn section as not changing what they would do.
  - Evidence (report): "It did not change what I would do"
  - Left because: the aim needs this section for writ and rn users.
- More: `pith/README.md:127-129` The design document section was skipped without use.
  - Evidence (report): "README:110-112 (design document)"
  - Left because: it serves a later use, a reader who wants to know why pith is built that way, not the first decision or start.

## doc.md: In trying to decide or act, what was not in the document, so that you could only guess or ask someone?

Report: - The install entry did not exist. README:105 says `/plugin install pith@ccpm`, but the marketplace file in this checkout has no `pith` plugin, so I would have to guess whether it is published yet.
- The design document was not there. README:112 links `docs/design.md`, which does not exist under `pith/`.
- I did not know how to give the work, the receiver and the aim to `/pith:up` other than as free text. The examples at README:42-44 and README:67-68 are prose after the command, and I guessed that free prose is the expected form.
- I did not know how to hand over my own essentials files (README:81). No syntax or example is given.
- I did not know how to "call `/pith:up` again with the result file" (README:87). I guessed something like `/pith:up .pith/open/01-report-pr-review.md`.
- The form pith "checks … each time it is written" (README:87) is not described. I could only guess what a valid `Left because:` entry looks like.
- The README says Python 3.9+ is needed (README:99) but does not say how pith finds Python (`python3` on PATH?). I guessed `python3`.
- I could not tell whether the result file is written in `.pith/open/` at the repository root or relative to the work. README:55 shows `.pith/open/01-…`, and I assumed the repository root.
- For a former /writ:pith user, the README does not say whether existing results or essentials from /writ:pith (if any lived elsewhere, for example under `.writ/`) carry over to `.pith/`. I could only guess that they do not.

- Good: `pith/README.md:43-45` The examples show a call as plain prose after the command, and the reader formed a first call from them.
  - Evidence (work): "> /pith:up Check .github/prompts/pr-review.md."
- More: `pith/README.md:122` The install command names a plugin the marketplace in this checkout does not list, so the reader guesses whether pith is published.
  - Evidence (report): "the marketplace file in this checkout has no `pith` plugin, so I would have to guess whether it is published yet"
  - Left because: pith is added to `.claude-plugin/marketplace.json` and `pith/docs/design.md` is written later in this same change; registration and the design document are their own tasks.
- More: `pith/README.md:129` The linked design document does not exist.
  - Evidence (report): "README:112 links `docs/design.md`, which does not exist under `pith/`."
  - Left because: pith is added to `.claude-plugin/marketplace.json` and `pith/docs/design.md` is written later in this same change; registration and the design document are their own tasks.
- Good: `pith/README.md:82` The reader sees how to name their own essentials files in the call.
  - Evidence (work): "If you already have your own essentials files, name them in the call instead"
- Good: `pith/README.md:104` The reader sees how to call pith again with the result file.
  - Evidence (work): "call pith again with the file and that question"
- Good: `pith/README.md:101` The reader sees what to write on a More they leave, with no form check to learn.
  - Evidence (work): "Left because: our pull requests stay under 500 lines."
- Good: `pith/README.md:86` The reader knows the result file is written at the root of the repository.
  - Evidence (work): "in `.pith/open/` at the root of your repository"
- More: `pith/README.md:11` A former /writ:pith user does not learn whether earlier results or essentials carry over to `.pith/`.
  - Evidence (report): "I could only guess that they do not."
  - Left because: pith is not released yet (the release waits for an instruction), and this is needed neither to decide nor to start.
- More: `pith/README.md:116` How pith finds Python is not said.
  - Evidence (report): "I guessed `python3`."
  - Left because: the README states what is needed and why, so readers get it their own way, and pith tells them if it is missing.

## doc.md: Reading through, where did you stop, go back or look ahead, and what did you not understand there?

Report: These are the places where I stopped, in reading order.

- **README:7, the word "questions".** It says "pith writes those questions from the work's purpose, tries them on your work, and keeps them". This is the first time the word "questions" appears, and line 7 doesn't say what they are or who answers them. I read on and only understood at README:15: "pith checks with questions kept in an essentials file, one for each kind of work."
- **README:9, "the discussion".** It says "a separate AI that does not know the discussion or how the work was made". I stopped to work out which discussion was meant. I took it to be my conversation with the AI that helped me make the work, from "asking the AI that helped you make it" earlier in the same paragraph.
- **README:11, a sentence I re-read twice.**
  - The sentence is "If you used `/writ:pith`, call `/pith:up` instead, which comes installed with writ; which questions it checks with is told under [With writ and rn]".
  - I wasn't sure whether "which comes installed with writ" refers to `/pith:up` or to pith.
  - The second clause, "which questions it checks with is told under", stopped me on grammar. I had to read it again to see it as "the questions it uses are explained under…".
  - As a reader who has never used writ, I couldn't tell whether this line applied to me. I looked ahead to README:108–112.
- **README:13, "Good or More" in the heading.** The heading is "…you get a Good or More for every question". I didn't know what "More" meant until README:15: "a More, where the receiver falls short of it."
- **README:36, comparing a question with my aim.** It says "If a question cannot be compared with anything in your aim, pith names that question and asks you to add to the aim". I stopped because I couldn't predict when this would happen, since I don't see the questions before I call. I didn't find an answer and went on.
- **README:47, the `.pith/` directory.** The example says "I wrote .pith/essentials/prompt.md". This is the first time `.pith/` appears, and I didn't yet know it was a directory in my own repository. README:82 ("pith keeps the questions in `.pith/essentials/` in your repository") and README:86 answered this later.
- **README:88, "which you fixed and marked Good".** I stopped on who does the marking, pith or me. I looked ahead to README:104, "you settle in the file yourself like this, without a recheck", and then went back to README:88.
- **README:93 and README:97, the fixed path.** The report at :93 says "The prompt sent it to src/ui/apiClient.js, which does not exist". The Good at :97 quotes the work as "read `src/ui/api-client.js`". I had to put together on my own that the Good is the wrong path after it was fixed. Nothing at :97 says it is that item.
- **README:101, "Left because".** I first understood this from README:106, "let go with a reason".
- **README:110, rn.** It says "rn, which carries a goal through to a finished change". I didn't know what rn is beyond this phrase. It wasn't needed to go on, so I went on.
- **README:112 against README:11, which questions I get.**
  - README:112 says `/pith:up` "called on its own never uses them [writ's essentials files], whether writ is installed or not".
  - I went back to README:11, which tells `/writ:pith` users to call `/pith:up` "instead".
  - Putting the two together, I understood that a former `/writ:pith` user who switches to `/pith:up` gets different questions: those in `.pith/essentials/`, or newly written ones. To get writ's questions they would call `/writ:up`.
  - I had to work this out by placing the two passages side by side. Neither passage says it outright.
- **README:116 and README:118 against README:11, whether pith is already installed.**
  - README:11 says "comes installed with writ", and README:118 says "If you have writ or rn, pith is already installed". These agree with each other.
  - README:116 says that on a Mac, Python "comes in the same developer tools as git". I stopped here because I didn't know how to confirm what I have. No command is given.
  - Nothing is said for Linux or Windows.

- Good: `pith/README.md:112` A former /writ:pith user now comes out knowing which command to call: /pith:up for pith's own questions, /writ:up for writ's; README:11 and README:112 are no longer read as contradicting each other.
  - Evidence (report): "To get writ's questions they would call `/writ:up`."
- Good: `pith/README.md:118` README:11 and README:118 are read as agreeing on pith coming with writ.
  - Evidence (report): "These agree with each other."
- Good: `pith/README.md:88` The setup of the excerpt no longer reads as findings the reader had not seen.
  - Evidence (work): "Say that, besides the renamed field, the same question also found a wrong path"
- Good: `pith/README.md:13-15` Good and More, met in the heading, are defined right after, so the reader reads on.
  - Evidence (report): "meant until README:15"
- Good: `pith/README.md:11` A former /writ:pith user reads at once that pith, not only the command, comes installed with writ, in a sentence with no clause to trip on.
  - Evidence (work): "The check you called as `/writ:pith` is now `/pith:up`, and pith comes installed with writ."
- Good: `pith/README.md:11` A former /writ:pith user is told outright that /pith:up on its own checks with other questions than writ's, without putting README:11 and README:112 together.
  - Evidence (work): "Called on its own, `/pith:up` checks with pith's own questions, not writ's"
- Good: `pith/README.md:88` The reader knows they themselves rewrite the fixed More as a Good, not pith.
  - Evidence (work): "which you fixed and then rewrote in the file as a Good yourself"
- More: `pith/README.md:97` The reader links the Good to the fixed wrong path on their own, by comparing two near-identical file names.
  - Evidence (report): "I had to put together on my own that the Good is the wrong path after it was fixed."
  - Left because: the reader did link it and read on; README:88 names the wrong path and the Report line at README:93 says the prompt sent it to a file that does not exist.
- More: `pith/README.md:101` `Left because:` is understood only at README:106.
  - Evidence (report): "I first understood this from README:106"
  - Left because: the explanation follows the excerpt right after, at README:104-106, and the reader understood it there.
- More: `pith/README.md:9` The reader stops to work out which discussion "the discussion" means.
  - Evidence (report): "I stopped to work out which discussion was meant."
  - Left because: the reader inferred it rightly (the conversation in which the work was made), and it is needed neither to decide nor to start.
- More: `pith/README.md:47` `.pith/` is met in the example before the reader knows it is a directory in their repository; README:82 and README:86 answer it later.
  - Evidence (report): "I didn't yet know it was a directory in my own repository."
  - Left because: README:82 and README:86 tell it within the same reading, and the reader carried through.
- More: `pith/README.md:7` "those questions" is met before any question is explained; the reader looks ahead to line 15.
  - Evidence (report): "line 7 doesn't say what they are or who answers them"
  - Left because: the reader still carries through to a first call and its result; the examples are illustrations.
- More: `pith/README.md:36` The reader does not see when a question cannot be compared with the aim.
  - Evidence (report): "I couldn't predict when this would happen"
  - Left because: pith names the uncovered question when it happens, and pith writes essentials itself; the reader's own files are optional.
- More: `pith/README.md:110` rn is read past without being understood.
  - Evidence (report): "I didn't know what rn is beyond this phrase."
  - Left because: the reader still carries through to a first call and its result; the examples are illustrations.
- More: `pith/README.md:116` The reader does not know how to confirm their Python; nothing is said for Linux or Windows.
  - Evidence (report): "Nothing is said for Linux or Windows."
  - Left because: the README states what is needed and why, so readers get it their own way, and pith tells them if it is missing.

## doc.md: When you looked for a part to read again by its heading, under which heading did you find it, and under which did you not?

Report: - How to install: found under "Getting started" (README:97).
- What to do with the result file and how to clean up: found under "What stays in your repository, and how to clear it" (README:83).
- How to re-check after a fix: I looked under "Getting started" and under the "/pith:up" heading (README:13) first. I found it under "What stays in your repository, and how to clear it" (README:87).
- What Good and More mean: I looked for a heading with those words and found the definition only by scanning the body of README:13's section (README:33).
- The /writ:pith migration note: I looked under "With writ and rn" (README:91). It was not there; it is at README:11, before any heading.
- What to give `/pith:up`: found under the heading at README:13.

- Good: `pith/README.md:114` Installing, clearing the result file, and what to give /pith:up are found at once under their headings (lines 114, 84, 13).
  - Evidence (report): "How to install: found under"
- More: `pith/README.md:84` Rechecking after a fix was looked for under other headings first.
  - Evidence (report): "heading (README:13) first. I found it under"
  - Left because: the reader found it in the section at README:84, whose heading names the result file, and carried through.
- Good: `pith/README.md:15` Good and More are explained at the start of the section, before its diagram.
  - Evidence (work): "pith then gives each question a Good, where the receiver gains what your aim intends, or a More, where the receiver falls short of it."
- Good: `pith/README.md:11` The /writ:pith note in the opening links the "With writ and rn" section, where the reader looked for it, so the two are found from each other.
  - Evidence (work): "as told under [With writ and rn](#with-writ-and-rn)"

## doc.md: Where, while reading, did you have to piece together in your head who does what, what passes, and in what order?

Report: - The sequence diagram (README:15-27) gave the order: me → pith → (optional question writing) → first user → pith → me.
- I had to work out myself where the comparison against the aim happens. The diagram shows pith returning "A Good or More" (README:26), but the step where pith compares the report with the aim is described only in text (README:33).
- The re-check loop after fixing (README:87) is not in the diagram. I had to work out the second round in my head: who reruns, on which questions, and what I edit by hand.
- Who owns which essentials files had to be put together from README:29, README:81 and README:95: pith-written ones go into `.pith/essentials/`, writ and rn keep their own, and the user can hand over their own.

- Good: `pith/README.md:17-30` The diagram gives the order of who passes what at a glance.
  - Evidence (report): "The sequence diagram (README:15-27) gave the order"
- Good: `pith/README.md:28` The diagram shows where pith lays what happened beside the aim.
  - Evidence (work): "Lays what happened beside your aim"
- Good: `pith/README.md:104` The recheck round is told: who reruns, on which question, and what the reader settles in the file.
  - Evidence (work): "A new first user then uses the work again on that question alone"
- More: `pith/README.md:82` Who owns which essentials files is put together from several places (now lines 82 and 112).
  - Evidence (report): "Who owns which essentials files had to be put together from README:29, README:81 and README:95"
  - Left because: not needed to decide or start; the reader still made a first call with or without own essentials.

## doc.md: How certain did you take each statement you relied on to decide or act?

Report: - I took the install commands (README:104-105) as fact. When I checked, the marketplace file in this checkout did not list pith.
- I took "If you have writ or rn, pith is already installed" (README:101) and "comes installed with writ" (README:11) as fact. Nothing in the README says from which version this holds.
- I took "on a Mac, it comes in the same developer tools as git" (README:99) as fact.
- I took "Without it, pith stops instead of skipping the check" (README:99) as fact.
- I took the example outputs (README:46-55, README:70-78) as illustrations prefixed with "Say…" (README:39, README:64), not as recorded runs.
- I took "Reading your work over yourself… does not find these places" (README:9) as a flat claim. The README gives no evidence or scope for it beyond the example.
- I took "pith checks the file's form each time it is written" (README:87) as fact, without knowing what the check covers.

- Good: `pith/README.md:40` The examples are taken as illustrations, not as recorded runs.
  - Evidence (report): "(README:39, README:64), not as recorded runs"
- More: `pith/README.md:121-122` The install commands are taken as fact, while this checkout's marketplace does not list pith.
  - Evidence (report): "When I checked, the marketplace file in this checkout did not list pith."
  - Left because: pith is added to `.claude-plugin/marketplace.json` and `pith/docs/design.md` is written later in this same change; registration and the design document are their own tasks.
- More: `pith/README.md:118` "already installed" with writ or rn is taken as fact with no version it holds from.
  - Evidence (report): "Nothing in the README says from which version this holds."
  - Left because: pith is not released yet (the release waits for an instruction), and this is needed neither to decide nor to start.
- More: `pith/README.md:9` The claim that one's own reading does not find these places is read as flat, with no evidence or reach.
  - Evidence (report): "The README gives no evidence or scope for it beyond the example."
  - Left because: it is the reason to choose pith, and the example at README:59 shows it.
- Good: `pith/README.md:106` The reader is no longer asked to take a form check on trust; clearing the file is told as plain steps.
  - Evidence (work): "Once every More is fixed or let go with a reason, copy the file into a commit message and delete the file in that commit."

## readme.md: Having read the opening, what did you take it you would get from this product?

Report: From README:3-9 I took three gains:
- I learn where the person or AI using my work "falls short of what you aimed for", and this comes "from what happened when the work was actually used, not from what you meant while making it" (README:5).
- Each point names a place in the work and quotes what happened there, "so you see what to fix and what must not be lost while fixing" (README:6).
- I can check kinds of work that have no questions yet, such as code or tests, because pith writes the questions and keeps them (README:7).

From README:9 I took the reason this differs from re-reading the work myself or asking the AI I worked with: "Both know what you meant, and fill in what the work leaves out". pith uses "a separate AI that does not know the discussion".

What I did not take from the opening: that pith is a Claude Code plugin, or what I type to use it. The first command shown is `/pith:up`, at README:11, and that line is addressed to former `/writ:pith` users.

- Good: `pith/README.md:5-9` From the opening the reader gains that pith checks the work by what happened in real use, by an AI that does not know the discussion, rather than by their own reading or the AI that made it.
  - Evidence (report): "a separate AI that does not know the discussion"
- Good: `pith/README.md:7` The reader now takes from the opening that pith writes the questions for a new kind of work and keeps them for the next check.
  - Evidence (report): "because pith writes the questions and keeps them (README:7)"
- Good: `pith/README.md:3` The opening tells the reader that pith is a Claude Code plugin.
  - Evidence (work): "pith is a Claude Code plugin."

## readme.md: What did you take in as the reason to choose this product over what you would use instead?

Report: The alternatives named are "Reading your work over yourself, or asking the AI that helped you make it" (README:9). The reason I took in is that "Both know what you meant, and fill in what the work leaves out without noticing", while pith's first user does not.

The PR-review example (README:37-58) reinforced this. README:58 says "The first user did not read the prompt and say whether it looked right. It gave the prompt to an AI with a diff no step covers". I read both examples (a CI review prompt, and a CLI export in a team tool) as close to the kind of work a Claude Code user does.

For a former /writ:pith user, the reason to use `/pith:up` was simply that it is the same check under a new name (README:11).

No other tools, such as linters, test suites or human review, are compared.

- Good: `pith/README.md:9` The reader takes the reason the aim intends: their own reading and the AI that made the work fill in what they meant, and pith's first user does not.
  - Evidence (work): "Both know what you meant, and fill in what the work leaves out without noticing."
- Good: `pith/README.md:59` The example shows the hole found by use, not by reading, and both examples were read as close to the reader's own work.
  - Evidence (report): "I read both examples (a CI review prompt, and a CLI export in a team tool) as close to the kind of work a Claude Code user does."

## readme.md: How did you take in the way from starting to use it to getting the result, as a flow of what you do and what you get?

Report: I took it in as:
1. Install (README:104-105), or have writ/rn.
2. Call `/pith:up` with the work, who uses it and what for, and an aim in sentences (README:20, README:35, README:42-44).
3. If no essentials file exists for that kind of work, pith writes one into `.pith/essentials/` (README:46, README:70, README:81).
4. Get a short result: pith's view, one line per question, and each More in full, plus a file in `.pith/open/` (README:53-55, README:60).
5. Fix, then call again with the result file. Settle other Mores by rewriting them as Good or adding `Left because:` (README:87).
6. Copy the file into a commit message and delete it (README:89).

The heading at README:13 states the core flow in one line: "Call `/pith:up` with the work and your aim, and you get a Good or More for every question". Each benefit in README:5-7 maps onto a step:
- receiver shortfall: step 4
- quoted place: README:49-51
- questions written from the purpose: step 3

- Good: `pith/README.md:13` The reader takes in the whole flow the aim intends, from install and the call through the short result and result file to recheck and clearing, and ties each opening benefit to a step.
  - Evidence (report): "Each benefit in README:5-7 maps onto a step"

## readme.md: What names or mechanisms did you have to learn before you could go on, though you needed them neither to decide whether to use it nor to start?

Report: - "essentials file" (README:29, README:81, README:95)
- "first user" (README:19, README:31)
- "the conductor" does not appear
- the rule that the first user is "never" given the aim (README:31)
- pith's form check on the result file (README:87)
- the rn/writ relationship and "an improvement to how work is checked is made once in pith and reaches both" (README:93)
- writ's own essentials files for "documents of every kind, READMEs, design documents and prompts" (README:95)
- the Python scripts as the implementation of checks (README:99)

- Good: `pith/README.md:34` Internal roles beyond the first user, such as the conductor, are not met.
  - Evidence (report): "does not appear"
- Good: `pith/README.md:104` The reader settles Mores in the file without learning a form check.
  - Evidence (work): "you settle in the file yourself like this, without a recheck"

## readme.md: Relying on this README alone, how far did you get in installing it and starting to use it, and where did you look elsewhere?

Report: **Prerequisites (README:116).**
- I ran `python3 --version`, which printed `Python 3.9.6`. That meets "Python 3.9 or later".
- I had to know on my own to type `python3 --version`. The README names no check.
- The README names no install route outside a Mac, saying only "on a Mac, it comes in the same developer tools as git".

**Install (README:118–123).**
- The two commands `/plugin marketplace add lovaizu/ccpm` and `/plugin install pith@ccpm` are given in full.
- I inferred that "ccpm" in `pith@ccpm` is the marketplace `lovaizu/ccpm` from README:118. The repository's marketplace.json has `"name": "ccpm"`, which matches.
- README:125 says "Now you can use `/pith:up`". Nothing says whether Claude Code needs a restart or reload after the install.
- As instructed, I did not run the install. So I did not see what happens after these two commands.

**First call.**
- No section gives the form of a call on its own. I built mine from the examples at README:43–45 and README:68–69. The form I took from them is: what to check, then "The receiver is …", then "The aim is …".
- From README:36 I took that the aim must be written out in sentences.
- From README:82 I took that I can name my own essentials files: `/pith:up Check … with docs/essentials/code.md ...`.
- I didn't see whether "receiver" must be stated, or in what words. README:68 says "Engineers run `taskctl export`…" without the word "receiver", so I took the wording to be free.

**Places I looked outside the README.**
- I ran `python3 --version` (see above).
- I checked the links:
  - `../writ/README.md` (README:112) exists in the repository.
  - `../LICENSE` (README:133) exists.
  - `docs/design.md` (README:129) does not exist yet, as stated above.
- I read nothing more from these to install or start. For deciding whether writ's questions apply to me, README:112 sends the reader to "writ's README", and I did not follow it.

- Good: `pith/README.md:118-123` The reader has the two install commands in full and ties `pith@ccpm` to the marketplace from README:118.
  - Evidence (report): "is the marketplace `lovaizu/ccpm` from README:118."
- Good: `pith/README.md:116` The reader knows the prerequisites and finds them met.
  - Evidence (report): "which printed `Python 3.9.6`"
- Good: `pith/README.md:43-45` The reader writes a first call for their own work from the examples, the rule to write the aim in sentences, and the way to name their own essentials files.
  - Evidence (report): "The form I took from them is: what to check, then"
- Good: `pith/README.md:112` A writ user no longer has to look elsewhere to choose between /pith:up and /writ:up for starting; nothing on the way from install to first call sent the reader outside the README.
  - Evidence (report): "I read nothing more from these to install or start."
- More: `pith/README.md:68` The reader does not see whether the receiver must be stated in the call, or in what words, and takes the wording to be free.
  - Evidence (report): "must be stated, or in what words."
  - Left because: the first example at README:44 states the receiver as "The receiver is ..." and the diagram at README:22 says the call carries who uses the work and what for; the reader made a first call.
- More: `pith/README.md:116` The reader checks the Python version from their own knowledge; nothing is said for systems other than a Mac.
  - Evidence (report): "I had to know on my own to type `python3 --version`. The README names no check."
  - Left because: the README states what is needed and why, so readers get it their own way, and pith tells them if it is missing.
- More: `pith/README.md:125` Whether Claude Code must be restarted or reloaded after installing is not said.
  - Evidence (report): "Nothing says whether Claude Code needs a restart or reload after the install."
  - Left because: pith is not released yet (the release waits for an instruction), and this is needed neither to decide nor to start.
