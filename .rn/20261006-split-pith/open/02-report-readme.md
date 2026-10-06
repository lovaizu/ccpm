# Check: pith/README.md

Target: pith/README.md
Receiver and purpose: a Claude Code user meeting pith for the first time, who reads it to decide whether to install pith and then starts using it on their own work (a document, a prompt, code, tests). Some have used /writ:pith before.
Aim: The reader learns from the opening that pith lets them check what they made by what happened when it was actually used as its receiver would use it, by a first user that does not know the discussion or how the work was made, rather than by their own reading filled with what they meant; and that this works for any work, a document, a prompt, code or tests, because for a kind of work with no essentials file pith first writes one worked back from the purpose, tries it on a real work, and keeps it in .pith/essentials/<kind>.md for the next check. They take this as the reason to choose pith over reading the work over themselves or asking the AI that made it. They take in the flow: call /pith:up with the work, its receiver and purpose, and an aim written out; pith returns a Good or More for every question with place and evidence, a short result, and a result file in .pith/open/ that pith does not commit; a missing aim or a question the aim does not cover is returned before any first user runs. They know what to do after: commit the file if they want to keep it, fix Mores, recall pith to recheck a More about what the work is for (a new first user on that question alone), settle other Mores in the file themselves (fixed becomes Good, left gets Left because:), and once all are settled copy the file into a commit message and delete it. A former /writ:pith user learns that the same check is now /pith:up and comes installed with writ; a writ or rn user learns both check through pith, so an improvement reaches both, and that writ and rn keep their own essentials files and hand them to pith. With the README alone the reader can install it: Claude Code, Python 3.9 or later (pith stops rather than skip a check without it), no Node.js, the marketplace lovaizu/ccpm and /plugin install pith@ccpm, and knows writ or rn users already have it. They learn no internal names they need neither to decide nor to start. Undecided by design and not to be stated as decided: which essentials pith uses when called directly while writ is also installed.

The first user read the README once from the top as a newcomer who had used /writ:pith before, checked with `ls` and `.claude-plugin/marketplace.json` the places the README sends the reader, and did not run the install commands. It found that `pith/` holds only `README.md` (no `pith/docs/`), that `LICENSE` exists at the root, and that `.claude-plugin/marketplace.json` lists only `rn` and `writ`.

On the recheck, a new first user answered four questions alone (doc.md: decide and do; doc.md: stop, go back or look ahead; readme.md: the opening; readme.md: installing from the README alone), told that pith is in the marketplace and pith/docs/design.md exists for a real reader. It ran only `python3 --version`.

On the second recheck, after README:3, 88 and 96 were fixed, a new first user answered two questions alone (doc.md: stop, go back or look ahead; readme.md: installing from the README alone), told the same. It ran `python3 --version` and listed `~/.claude/plugins/cache/ccpm/`, which holds `rn` and `writ` 0.1.0 and no `pith`.

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
- Good: `pith/README.md:88` The reader now knows to recheck by naming the result file in a new call, and to settle the other Mores by rewriting them as Good or adding `Left because:`.
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
- Good: `pith/README.md:94` The reader meets the tie between writ, rn and pith once there, without the install being repeated in that section.
  - Evidence (work): "both check their work through pith, so an improvement to how work is checked is made once in pith and reaches both."
- More: `pith/README.md:91-95` The newcomer skimmed the writ and rn section as not changing what they would do.
  - Evidence (report): "It did not change what I would do"
  - Left because: the aim needs this section for writ and rn users.
- More: `pith/README.md:111-113` The design document section was skipped without use.
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

- Good: `pith/README.md:42-44` The examples show a call as plain prose after the command, and the reader formed a first call from them.
  - Evidence (work): "> /pith:up Check .github/prompts/pr-review.md."
- More: `pith/README.md:105` The install command names a plugin the marketplace in this checkout does not list, so the reader guesses whether pith is published.
  - Evidence (report): "the marketplace file in this checkout has no `pith` plugin, so I would have to guess whether it is published yet"
  - Left because: pith is added to `.claude-plugin/marketplace.json` and `pith/docs/design.md` is written later in this same change; registration and the design document are their own tasks.
- More: `pith/README.md:112` The linked design document does not exist.
  - Evidence (report): "README:112 links `docs/design.md`, which does not exist under `pith/`."
  - Left because: pith is added to `.claude-plugin/marketplace.json` and `pith/docs/design.md` is written later in this same change; registration and the design document are their own tasks.
- Good: `pith/README.md:82` The reader sees how to name their own essentials files in the call.
  - Evidence (work): "If you already have your own essentials files, name them in the call instead"
- Good: `pith/README.md:88` The reader sees how to call pith again with the result file.
  - Evidence (work): "call pith again with the result file and that question"
- Good: `pith/README.md:88` The reader is told what to write on a More they leave, with no form check to learn.
  - Evidence (work): "Give a More you leave `Left because:` and the reason."
- Good: `pith/README.md:86` The reader knows the result file is written at the root of the repository.
  - Evidence (work): "in `.pith/open/` at the root of your repository"
- More: `pith/README.md:11` A former /writ:pith user does not learn whether earlier results or essentials carry over to `.pith/`.
  - Evidence (report): "I could only guess that they do not."
  - Left because: pith is not released yet (the release waits for an instruction), and this is needed neither to decide nor to start.
- More: `pith/README.md:99` How pith finds Python is not said.
  - Evidence (report): "I guessed `python3`."
  - Left because: the README states what is needed and why, so readers get it their own way, and pith tells them if it is missing.

## doc.md: Reading through, where did you stop, go back or look ahead, and what did you not understand there?

Report: - **README:7.** "pith writes those questions from the work's purpose, tries them on your work, and keeps them for the next check of that kind." I stopped at "those questions". Up to here no questions had been mentioned, only the three bullet benefits. I read ahead to README:15 ("pith checks with questions kept in an essentials file, one for each kind of work") to learn what they were. "Tries them on your work" stayed unclear to me until the diagram at README:24.
- **README:11.** "If you used `/writ:pith`, the same check is now `/pith:up`, and it comes installed with writ." I stopped on "it". I could not tell whether it meant `/pith:up` or pith itself. I also could not tell whether "comes installed with writ" means my current writ, or a writ version I would have to update to. I looked ahead and found README:102: "If you have writ or rn, pith is already installed." That read as the same claim.
  - I then looked at my own machine. `ls ~/.claude/plugins/cache/ccpm/` shows `rn` and `writ` (writ is at 0.1.0) and no `pith` directory.
  - Going by README:11 and README:102, I would expect pith to be there already. I could not settle from the README whether I need to update writ, or run the install at README:106 anyway.
- **README:13 heading.** "...you get a Good or More for every question". "Good" and "More" appear in the heading before they are explained; README:15 defines them right after. I read on without going back.
- **README:15 and README:21.** "That separate AI, called the first user..." I paused on the name "first user", because it sounded like a person. The diagram label at README:21, "an AI that does not know the discussion", resolved it.
- **README:36.** "If a question cannot be compared with anything in your aim, pith names that question and asks you to add to the aim before any first user runs." I stopped here and did not understand how I would write an aim in advance so that every question can be compared with it. At this point I did not yet know what the questions would be, since pith may write them itself (README:7, README:24).
- **README:47 against README:96.**
  - README:47 says: "There was no essentials file for prompts, so I wrote .pith/essentials/prompt.md".
  - README:96 says: "writ keeps the essentials files for its kinds of work, ... READMEs, design documents and prompts, ... each hands them to pith."
  - When I reached README:96, I went back to README:47. As a writ user, I could not tell whether pith called directly via `/pith:up` would use writ's prompt essentials file, or write its own as the example shows. I also could not tell whether the example assumes a user without writ.
- **README:54 and README:61.** README:54 says "(every other question gets one line: Good or More, and where)". README:61 says "The short result opens with pith's view of where the work stands against your aim." I went back to README:48 to match "pith's view" to the line "Changed endpoints are caught as the aim intends, but one kind of change gets past."
  - In the second example, README:71-73 lists two questions. Only the second gets a More line (README:74-77). No Good/More line is shown for "Called as its users call it, what ended up in the output?"
  - I went back to README:54 and README:61 to check whether a line was expected there. I did not find out whether it was left out of the example on purpose.
- **README:88.** I stopped here and reread the paragraph twice.
  - It sets two kinds of fixed More side by side: "a More where the receiver did not get what the work is for", which is rechecked, and "A fixed More that is easy to see, such as a broken link or a word used two ways", which "you settle in the file yourself ... rewrite it as the Good it now is".
  - I did not understand where the line falls between the two kinds for my own Mores.
  - I also did not understand what "rewrite it as the Good it now is" looks like in the result file. The README never shows that file's contents, only its path (README:56, README:79).
  - For "Give a More you leave `Left because:` and the reason", I did not know where in the file that line goes.
- **README:94.** "rn, which carries a goal through to a finished change". I did not know what rn is beyond this phrase. I read on, since it did not seem needed to use pith.
- **README:100.** "Its checks are Python scripts". I stopped, because README:9 and README:15-29 described the check as a separate AI using the work. I did not understand what the Python scripts do in a check that an AI performs. I went back to README:9 and did not resolve it.
  - "on a Mac, it comes in the same developer tools as git": I took this to mean the Command Line Tools. The README gives no way to check the version.
- **README:109.** "Now you can use `/pith:up`." To form my first call, I went back to the examples at README:43-45 and README:68-69, and to README:36 for the rule that the aim must be written out in sentences.

- Good: `pith/README.md:3` The reader knows from the first line what kind of thing pith is, and no longer stops in the opening to look for it.
  - Evidence (work): "pith is a Claude Code plugin. When it checks something you made, a document, a prompt, code or tests, you get the following."
- Good: `pith/README.md:13-15` Good and More, met in the heading, are defined right after, so the reader reads on.
  - Evidence (report): "README:15 defines them right after. I read on without going back."
- Good: `pith/README.md:21` The diagram label tells the reader that the first user is an AI, not a person.
  - Evidence (report): "I paused on the name"
- More: `pith/README.md:7` "those questions" is met before any question is explained, and "tries them on your work" stays unclear until the diagram; the reader looks ahead to lines 15 and 24.
  - Evidence (report): "Up to here no questions had been mentioned, only the three bullet benefits."
  - Left because: the reader still carries through to a first call and its result; the examples are illustrations.
- More: `pith/README.md:11` The reader cannot tell what "it" refers to, nor whether their current writ already brings pith or must be updated; with writ installed and no pith found, they cannot settle whether to install anyway.
  - Evidence (report): "I could not settle from the README whether I need to update writ, or run the install at README:106 anyway."
  - Left because: the reader still carries through to a first call and its result; the examples are illustrations. As for which writ version brings pith, pith is not released yet (the release waits for an instruction), and this is needed neither to decide nor to start.
- More: `pith/README.md:36` The reader does not see how to write an aim in advance that every question can be compared with, when pith may write the questions itself.
  - Evidence (report): "did not understand how I would write an aim in advance so that every question can be compared with it."
  - Left because: pith names the uncovered question when it happens, and pith writes essentials itself; the reader's own files are optional.
- More: `pith/README.md:47` Reaching line 96, a writ user goes back to the first example and cannot tell whether /pith:up would use writ's prompt essentials file or write its own.
  - Evidence (report): "I could not tell whether pith called directly via `/pith:up` would use writ's prompt essentials file, or write its own as the example shows."
  - Left because: returned to the user. Which essentials /pith:up uses when called directly while writ is installed is undecided in the design.
- More: `pith/README.md:71-77` The second example shows a line for only one of its two questions, and the reader goes back to lines 54 and 61 to see whether that is on purpose.
  - Evidence (report): "Only the second gets a More line (README:74-77)."
  - Left because: the reader still carries through to a first call and its result; the examples are illustrations.
- More: `pith/README.md:88` The reader still cannot tell where the line falls between a More pith rechecks and one they settle themselves, and, never having seen the result file's contents, what a More rewritten as Good looks like or where `Left because:` goes.
  - Evidence (report): "I did not understand where the line falls between the two kinds for my own Mores."
  - Left because: returned to the user. The same More remained after two fixes, and the reader cannot see the result file's content in the README; the user decides whether to show a short excerpt of a result file or accept it as it is.
- More: `pith/README.md:94` rn is read past without being understood.
  - Evidence (report): "I did not know what rn is beyond this phrase."
  - Left because: the reader still carries through to a first call and its result; the examples are illustrations.
- More: `pith/README.md:100` "Its checks are Python scripts" conflicts in the reader's head with the check being done by a separate AI, and stays unresolved.
  - Evidence (report): "I did not understand what the Python scripts do in a check that an AI performs."
  - Left because: the reader still carries through to a first call and its result; the examples are illustrations.
- More: `pith/README.md:109` To make a first call, the reader goes back to the examples and to line 36.
  - Evidence (report): "To form my first call, I went back to the examples at README:43-45 and README:68-69"
  - Left because: the reader still carries through to a first call and its result; the examples are illustrations.

## doc.md: When you looked for a part to read again by its heading, under which heading did you find it, and under which did you not?

Report: - How to install: found under "Getting started" (README:97).
- What to do with the result file and how to clean up: found under "What stays in your repository, and how to clear it" (README:83).
- How to re-check after a fix: I looked under "Getting started" and under the "/pith:up" heading (README:13) first. I found it under "What stays in your repository, and how to clear it" (README:87).
- What Good and More mean: I looked for a heading with those words and found the definition only by scanning the body of README:13's section (README:33).
- The /writ:pith migration note: I looked under "With writ and rn" (README:91). It was not there; it is at README:11, before any heading.
- What to give `/pith:up`: found under the heading at README:13.

- Good: `pith/README.md:97` Installing, clearing the result file, and what to give /pith:up are found at once under their headings (lines 97, 83, 13).
  - Evidence (report): "How to install: found under"
- More: `pith/README.md:84` Rechecking after a fix was looked for under other headings first.
  - Evidence (report): "heading (README:13) first. I found it under"
  - Left because: the reader found it in the section at README:84, whose heading names the result file, and carried through.
- Good: `pith/README.md:15` Good and More are explained at the start of the section, before its diagram.
  - Evidence (work): "pith then gives each question a Good, where the receiver gains what your aim intends, or a More, where the receiver falls short of it."
- More: `pith/README.md:11` The /writ:pith note was looked for under "With writ and rn" and is not there.
  - Evidence (report): "It was not there; it is at README:11, before any heading."
  - Left because: a former /writ:pith user meets it in the opening at README:11, before any heading.

## doc.md: Where, while reading, did you have to piece together in your head who does what, what passes, and in what order?

Report: - The sequence diagram (README:15-27) gave the order: me → pith → (optional question writing) → first user → pith → me.
- I had to work out myself where the comparison against the aim happens. The diagram shows pith returning "A Good or More" (README:26), but the step where pith compares the report with the aim is described only in text (README:33).
- The re-check loop after fixing (README:87) is not in the diagram. I had to work out the second round in my head: who reruns, on which questions, and what I edit by hand.
- Who owns which essentials files had to be put together from README:29, README:81 and README:95: pith-written ones go into `.pith/essentials/`, writ and rn keep their own, and the user can hand over their own.

- Good: `pith/README.md:15-27` The diagram gives the order of who passes what at a glance.
  - Evidence (report): "The sequence diagram (README:15-27) gave the order"
- Good: `pith/README.md:28` The diagram shows where pith lays what happened beside the aim.
  - Evidence (work): "Lays what happened beside your aim"
- Good: `pith/README.md:88` The recheck round is told: who reruns, on which question, and what the reader settles in the file.
  - Evidence (work): "A new first user then uses the work again on that question alone."
- More: `pith/README.md:82` Who owns which essentials files is put together from several places (now lines 82 and 96).
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

- Good: `pith/README.md:39` The examples are taken as illustrations, not as recorded runs.
  - Evidence (report): "(README:39, README:64), not as recorded runs"
- More: `pith/README.md:104-105` The install commands are taken as fact, while this checkout's marketplace does not list pith.
  - Evidence (report): "When I checked, the marketplace file in this checkout did not list pith."
  - Left because: pith is added to `.claude-plugin/marketplace.json` and `pith/docs/design.md` is written later in this same change; registration and the design document are their own tasks.
- More: `pith/README.md:101` "already installed" with writ or rn is taken as fact with no version it holds from.
  - Evidence (report): "Nothing in the README says from which version this holds."
  - Left because: pith is not released yet (the release waits for an instruction), and this is needed neither to decide nor to start.
- More: `pith/README.md:9` The claim that one's own reading does not find these places is read as flat, with no evidence or reach.
  - Evidence (report): "The README gives no evidence or scope for it beyond the example."
  - Left because: it is the reason to choose pith, and the example at README:59 shows it.
- Good: `pith/README.md:90` The reader is no longer asked to take a form check on trust; clearing the file is told as plain steps.
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
- Good: `pith/README.md:58` The example shows the hole found by use, not by reading, and both examples were read as close to the reader's own work.
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

- Good: `pith/README.md:31` Internal roles beyond the first user, such as the conductor, are not met.
  - Evidence (report): "does not appear"
- Good: `pith/README.md:88` The reader settles Mores in the file without learning a form check.
  - Evidence (work): "you settle in the file yourself without a recheck"

## readme.md: Relying on this README alone, how far did you get in installing it and starting to use it, and where did you look elsewhere?

Report: 1. **Prerequisites (README:100).** "you need Claude Code ... it also needs Python 3.9 or later ... Node.js is not needed."
   - The README does not say how to check the Python version. I used my own knowledge and ran `python3 --version`, which printed `Python 3.9.6` (`/usr/bin/python3`). So the requirement is met on this machine.
   - "Without it, pith stops instead of skipping the check, and tells you to install it": I took this as a sign that I would be told if it were missing.
2. **Whether I need to install at all (README:102).** "If you have writ or rn, pith is already installed." I have writ and rn, so going by the README I would skip the install.
   - I looked outside the README, at `~/.claude/plugins/cache/ccpm/`. It contains `rn` and `writ` (0.1.0) and no `pith`.
   - The README does not say which writ version brings pith, or what to do if `/pith:up` is not available despite having writ. That is where I stopped trusting the README alone.
   - The next step I would take, from the README, is README:105-106: `/plugin marketplace add lovaizu/ccpm` then `/plugin install pith@ccpm`. As you instructed, I did not run them.
   - The README does not say whether Claude Code must be restarted or reloaded after installing. README:109 says only "Now you can use `/pith:up`."
3. **Starting to use it.** From README:43-45, README:68-69 and README:36, I could write a first call in the same form: the work's path, who receives it and what for, and the aim in sentences. With my own essentials file, the form is README:82: "`/pith:up Check cli/src/export.js with docs/essentials/code.md ...`".
   - From the README alone, I did not know these things:
     - which essentials file would be used for a document or prompt when writ is installed (README:47 against README:96);
     - what the result file in `.pith/open/` looks like inside, which I would need in order to "rewrite it as the Good it now is" or add "`Left because:`" (README:88);
     - how to write an aim so that no question is "unable to be compared" with it (README:36).
   - For each of these I would have had to run pith and see, or look elsewhere. README:113 points to docs/design.md for "why pith is built that way", not for these usage points.
4. **Places I looked outside the README:**
   - my own knowledge of how to check the Python version;
   - the plugin cache directory, to see whether writ had already brought pith.

   I did not open any other files.

- Good: `pith/README.md:43-45` The reader writes a first call from the examples alone, including one that names their own essentials file.
  - Evidence (report): "I could write a first call in the same form: the work's path, who receives it and what for, and the aim in sentences."
- Good: `pith/README.md:100` The reader knows the prerequisites, and that pith will tell them if Python is missing.
  - Evidence (report): "I took this as a sign that I would be told if it were missing."
- Good: `pith/README.md:96` The reader no longer looks elsewhere to learn whether pith alone has questions for documents.
  - Evidence (work): "Without writ, pith writes the questions for documents too, as it does for any kind of work with no essentials file."
- More: `pith/README.md:100` The reader checks the Python version from their own knowledge; the README gives no way to check it.
  - Evidence (report): "The README does not say how to check the Python version."
  - Left because: the README states what is needed and why, so readers get it their own way, and pith tells them if it is missing.
- More: `pith/README.md:102` A writ user who does not find pith cannot tell which writ version brings it or what to do, looks in the plugin cache, and stops trusting the README alone.
  - Evidence (report): "That is where I stopped trusting the README alone."
  - Left because: pith is not released yet (the release waits for an instruction), and this is needed neither to decide nor to start.
- More: `pith/README.md:109` Whether Claude Code must be restarted or reloaded after installing is not said.
  - Evidence (report): "The README does not say whether Claude Code must be restarted or reloaded after installing."
  - Left because: pith is not released yet (the release waits for an instruction), and this is needed neither to decide nor to start.
- More: `pith/README.md:47` Which essentials file is used for a document or prompt when writ is installed is left for the reader to find by running pith.
  - Evidence (report): "which essentials file would be used for a document or prompt when writ is installed (README:47 against README:96)"
  - Left because: returned to the user. Which essentials /pith:up uses when called directly while writ is installed is undecided in the design.
- More: `pith/README.md:88` To settle Mores in the result file, the reader would have to run pith to see what the file looks like inside.
  - Evidence (report): "what the result file in `.pith/open/` looks like inside"
  - Left because: returned to the user. The same More remained after two fixes, and the reader cannot see the result file's content in the README; the user decides whether to show a short excerpt of a result file or accept it as it is.
- More: `pith/README.md:36` How to write an aim that every question can be compared with is left for the reader to find by running pith.
  - Evidence (report): "how to write an aim so that no question is"
  - Left because: pith names the uncovered question when it happens, and pith writes essentials itself; the reader's own files are optional.
