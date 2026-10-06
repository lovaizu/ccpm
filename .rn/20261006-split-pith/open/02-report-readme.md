# Check: pith/README.md

Target: pith/README.md
Receiver and purpose: a Claude Code user meeting pith for the first time, who reads it to decide whether to install pith and then starts using it on their own work (a document, a prompt, code, tests). Some have used /writ:pith before, some use writ or rn.
Aim: The reader learns from the opening that pith lets them check what they made by what happened when it was actually used as its receiver would use it, by a first user that does not know the discussion or how the work was made, rather than by their own reading filled with what they meant; and that this works for any work: a document or a prompt with the questions pith comes with, and a kind of work with no essentials file, such as code or tests, with one pith first writes from the purpose, tries on a real work, and keeps in .pith/essentials/<kind>.md for the next check. They take this as the reason to choose pith over reading the work over themselves or asking the AI that made it. They take in the flow: call /pith:up with the work, its receiver and purpose, and an aim written out; pith returns a Good or More for every question with place and evidence, a short result, and a result file in .pith/open/ that pith does not commit; a missing aim or a question the aim does not cover is returned before any first user runs. They know what to do after: commit the file if they want to keep it, fix Mores, recall pith to recheck a More about what the work is for (a new first user on that question alone), settle other Mores in the file themselves (fixed becomes Good, left gets Left because:), and once all are settled copy the file into a commit message and delete it; a few lines of a result file shown in the README let them see what a More, a More rewritten as Good, and Left because: look like, and which fixed More goes back to pith and which they settle themselves. A former /writ:pith user learns that the same check, with the same questions, is now /pith:up and comes installed with writ. A writ or rn user learns both check through pith, so an improvement reaches both; that /writ:up checks a document with the same questions as /pith:up and then fixes what it finds; and that rn keeps its own questions for its kinds of work and hands them to pith. Decided by the user: /pith:up called directly uses the essentials files named in the call; otherwise, for a document or a prompt, the questions pith comes with, and for any other kind the one for that kind in .pith/essentials/, written first when there is none; this is the same whether writ is installed or not. With the README alone the reader can install it: Claude Code, Python 3.9 or later (pith stops rather than skip a check without it), no Node.js, the marketplace lovaizu/ccpm and /plugin install pith@ccpm, and knows writ or rn users already have it. They learn no internal names they need neither to decide nor to start.

The whole README was checked again, since the agreed design changed. A new first user read it once from the top as a newcomer, keeping in mind a former /writ:pith user, a writ or rn user, and someone new to all of them, told that pith will be listed in the marketplace and pith/docs/design.md will exist for a real reader. It ran `ls` on the linked files (`../writ/README.md` and `../LICENSE` exist, `docs/design.md` not yet) and did not run the install commands. A More found again at the same place with the same struggle as one left earlier keeps the earlier `Left because:`.

The Mores were then settled by the caller, and after README:112 was fixed (which command to call for a document), a new first user answered two questions alone (doc.md: what was not in the document; readme.md: installing from the README alone), told the same. It ran `python3 --version` and listed its plugin cache, which holds `rn` and `writ` and no `pith`, since pith is not released yet.

## doc.md: Once you finished reading, what did you take it you should decide and do?

Report: What I took in:
- Decide: install pith if I want to learn where the person or AI that uses my work falls short of my aim, judged from an actual use of the work (README:5, "from what happened when the work was actually used, not from what you meant while making it").
- Install: have Python 3.9+ and run `/plugin marketplace add lovaizu/ccpm` then `/plugin install pith@ccpm` (README:116-123). If I already have writ or rn, I skip this: "If you have writ or rn, pith is already installed." (README:118; README:11 says the same.)
- Use: call `/pith:up` and give it the work, who uses it and what for, and my aim written out in sentences (README:22, README:36, README:43-45).
- After the result: fix each More. I settle an easy one (a wrong path, a broken link, a word used two ways) in the result file myself (README:104). For a More where "the receiver did not get what the work is for", I recheck with `/pith:up Recheck <file>; I fixed ...` (README:104). Once every More is fixed or "let go with a reason", I copy the file into a commit message and delete it in that commit (README:106).
- As a former /writ:pith user, I took it that I should type `/pith:up` from now on (README:11, "The check you called as `/writ:pith` is now `/pith:up`").
- For code or tests, I took it that pith writes `.pith/essentials/<kind>.md` the first time and reuses it after that (README:71, README:82).

Things I took in only partly:
- I am not sure whether I am expected to commit the `.pith/essentials/code.md` that pith writes. README:86 says the result file is not committed. Nothing says what happens to the essentials file.
- The heading at README:13 reads "Call `/pith:up` with the work and your aim". The diagram (README:22) and the example (README:44) also pass "who uses it and what for". I took it that I should pass all three.

- Good: `pith/README.md:11` A former /writ:pith user takes it that they now type /pith:up.
  - Evidence (report): "As a former /writ:pith user, I took it that I should type `/pith:up` from now on"
- Good: `pith/README.md:118` A writ or rn user takes it that there is nothing to install.
  - Evidence (report): "If I already have writ or rn, I skip this"
- Good: `pith/README.md:104-106` The reader takes the steps after a result as the aim intends: settle an easy More in the file, recheck a More about what the work is for, then clear the file into a commit.
  - Evidence (report): "I settle an easy one (a wrong path, a broken link, a word used two ways) in the result file myself (README:104)."
- Good: `pith/README.md:82` The reader takes it that pith writes the essentials file for code or tests once and reuses it.
  - Evidence (report): "pith writes `.pith/essentials/<kind>.md` the first time and reuses it after that"
- More: `pith/README.md:82` The reader does not know whether to commit the essentials file pith writes into their repository.
  - Evidence (report): "Nothing says what happens to the essentials file."
  - Left because: it is the reader's own repository, and the reader can decide it; it is needed neither to decide on pith nor to start.
- More: `pith/README.md:13` The heading names only the work and the aim, so the reader infers from the diagram and the example that the receiver and purpose are passed too.
  - Evidence (report): "I took it that I should pass all three."
  - Left because: the reader passed the receiver and purpose too, from the diagram and the example.

## doc.md: Which parts did you use to decide or act, which did you skip without using, and where did you find yourself reading again what you had already read?

Report: - Used to decide: README:3-9 (the gains, and why reading it over myself does not find these places) and the first example, README:40-59.
- Used to act: README:36 (write the aim out), README:43-45 (the shape of a call), README:82 (naming my own essentials files), README:104-106 (what to do with Mores), README:116-125 (installing).
- Read but did not use: README:110-112 (writ and rn). As a writ user I got what I needed from README:11 and README:118. I skimmed README:129-133.
- Read again: I read README:88-104 twice. The section brings in a hypothetical: "Say that, besides the renamed field, the same question also found a wrong path, which you fixed and then rewrote in the file as a Good yourself, and a long diff read only in part, which you left." I had to go back to README:93 and README:97 to match the wrong path ("src/ui/apiClient.js, which does not exist") to the Good entry ("read `src/ui/api-client.js`"). I also read the example question twice: it is quoted at README:32 and again at README:51 and README:91. The second time I recognised it and skimmed it.

- Good: `pith/README.md:3-9` The gains and the reason against reading the work over oneself carry the decision, with the first example.
  - Evidence (report): "Used to decide: README:3-9"
- Good: `pith/README.md:116-125` The aim, the shape of a call, own essentials, what to do with Mores and installing are each used to act.
  - Evidence (report): "README:116-125 (installing)"
- More: `pith/README.md:108-112` The newcomer read the writ and rn section without using it.
  - Evidence (report): "Read but did not use: README:110-112 (writ and rn)."
  - Left because: the aim needs this section for writ and rn users.
- More: `pith/README.md:127-129` The design document section was skimmed without use.
  - Evidence (report): "I skimmed README:129-133."
  - Left because: it serves a later use, a reader who wants to know why pith is built that way, not the first decision or start.
- More: `pith/README.md:97` The reader read the excerpt twice to match the fixed wrong path to its Good entry.
  - Evidence (report): "I had to go back to README:93 and README:97 to match the wrong path"
  - Left because: the reader did link it and read on; README:88 names the wrong path and the Report line at README:93 says the prompt sent it to a file that does not exist.
- More: `pith/README.md:91` The example question, met at README:32 and README:51, is met a third time and skimmed.
  - Evidence (report): "The second time I recognised it and skimmed it."
  - Left because: the excerpt shows a real result file, whose section heading repeats the question.

## doc.md: In trying to decide or act, what was not in the document, so that you could only guess or ask someone?

Report: When I finished reading, I took it that I should do three things: install pith (or rely on writ having brought it), check Python, and call `/pith:up` with a work, its receiver and purpose, and my aim. Below is each point where I had to guess.

1. Is pith already on my machine? README:11 says "pith comes installed with writ", and README:118 says "If you have writ or rn, pith is already installed." My plugin cache (`/Users/kiyo/.claude/plugins/cache/ccpm/`) holds only `rn` and `writ` (writ is at version `0.1.0`); there is no `pith`. The README gives no writ or rn version that brings pith. It also doesn't say whether I must update writ first, or how I would tell that pith is present. I guessed I would need to update writ, or run `/plugin install pith@ccpm` (README:122) anyway. (This may only be because pith isn't released yet. I'm reporting what I saw.)
2. Does `/writ:pith` still work? README:11 says the check "is now `/pith:up`". It doesn't say whether `/writ:pith` still exists, now fails, or forwards to the new command. I guessed it was removed.
3. Python on other systems. README:116 covers only Mac: "on a Mac, it comes in the same developer tools as git". It doesn't say which command pith calls (`python3` or `python`), or what Linux or Windows users should do. On my machine `python3 --version` printed `Python 3.9.6` (`/usr/bin/python3`), so I guessed I meet "Python 3.9 or later".
4. What counts as "the work" in a call. Both examples name a single file (README:43, README:68). Nothing says whether I can pass a directory, several files, or a test suite. For tests, I couldn't tell what to name: the test files, or the command that runs them.
5. How pith decides what kind of work it is. README:15 says it "uses the one for that kind in `.pith/essentials/`". README:71 shows `code.md` being written. Nothing says how the kind is decided, or what the file is called for tests. I also couldn't tell whether a README counts as "a document" and so gets the questions pith comes with (README:7, README:15). I guessed it does.
6. What the first user runs on my machine. README:9 says it "calls code, runs tests". In the code example (README:76) it ran `taskctl export`, which writes a file. Nothing says whether this happens in my working tree, whether I'm asked for permission, or where output files end up. I couldn't tell before deciding whether running pith on code is safe in my repository.
7. Whether to commit `.pith/essentials/`. README:84-106 covers only `.pith/open/`: "does not commit or push it", and to "delete the file" when done. README:82 says "The next check of code uses these same questions". Nothing says whether the essentials file should be committed or added to `.gitignore`. I guessed it should be committed so it is kept.
8. Cost and duration of a check. Nothing on how long a check takes or how much it uses. It mattered for deciding whether to run it on every change.
9. After installing. README:125 says "Now you can use `/pith:up`." It doesn't say whether Claude Code needs a restart. I assumed it doesn't.

- Good: `pith/README.md:112` The reader no longer has to guess which command to call for a document: the choice between /pith:up and /writ:up is not among the gaps, and README:112 is followed only by a reader who wants a document written for them.
  - Evidence (work): "To check a document and fix it yourself, call `/pith:up`; to have a document written or fixed for you, call `/writ:up`"
- Good: `pith/README.md:13-45` The reader takes in what to do: install or rely on writ, check Python, and call /pith:up with the work, its receiver and purpose, and the aim.
  - Evidence (report): "call `/pith:up` with a work, its receiver and purpose, and my aim"
- More: `pith/README.md:118` A writ or rn user whose plugins do not yet hold pith cannot tell which writ or rn version brings it, or how to see that pith is present, and guesses to update writ or install anyway.
  - Evidence (report): "The README gives no writ or rn version that brings pith."
  - Left because: pith is not released yet (the release waits for an instruction); the version that brings it is known only then.
- More: `pith/README.md:11` A former /writ:pith user does not know whether /writ:pith still works, and guesses it was removed.
  - Evidence (report): "I guessed it was removed."
  - Left because: the reader guessed rightly that it is gone ("is now /pith:up"), and calls /pith:up.
- More: `pith/README.md:116` How to check Python, and what to do outside a Mac, is not said.
  - Evidence (report): "what Linux or Windows users should do"
  - Left because: the README states what is needed and why, so readers get it their own way, and pith tells them if it is missing.
- More: `pith/README.md:43` The reader cannot tell whether the work can be a directory, several files or a test suite, nor what to name for tests.
  - Evidence (report): "For tests, I couldn't tell what to name: the test files, or the command that runs them."
  - Left because: the call is plain prose, so the reader names the work as they would to Claude, as both examples do; they made a first call.
- More: `pith/README.md:15` The reader does not know how pith tells the kind of a work, nor the file name for tests, and guesses that a README counts as a document.
  - Evidence (report): "Nothing says how the kind is decided, or what the file is called for tests."
  - Left because: pith decides it and names the file it wrote, as the code example shows; the reader made a first call.
- More: `pith/README.md:9` The reader cannot tell whether running pith on code is safe in their repository: where the first user runs it, whether it asks, where output files end up.
  - Evidence (report): "I couldn't tell before deciding whether running pith on code is safe in my repository."
  - Left because: not decided by the user; it is needed neither to decide on pith nor to start, and is raised to the user.
- More: `pith/README.md:82` The reader does not know whether to commit `.pith/essentials/`, and guesses to commit it.
  - Evidence (report): "Nothing says whether the essentials file should be committed or added to `.gitignore`."
  - Left because: it is the reader's own repository, and the reader can decide it; it is needed neither to decide on pith nor to start.
- More: `pith/README.md:13` Nothing tells how long a check takes or how much it uses, which the reader weighed for running it on every change.
  - Evidence (report): "Nothing on how long a check takes or how much it uses."
  - Left because: needed neither to decide nor to start in the aim; the reader carried through.
- More: `pith/README.md:125` The reader does not know whether Claude Code needs a restart after installing, and assumes not.
  - Evidence (report): "It doesn't say whether Claude Code needs a restart."
  - Left because: pith is not released yet (the release waits for an instruction), and this is needed neither to decide nor to start.

## doc.md: Reading through, where did you stop, go back or look ahead, and what did you not understand there?

Report: - README:7, "with questions pith writes from the work's purpose, tries on your work, and keeps". I stopped at "tries on your work" and did not know what trying meant. The diagram at README:24 repeats it ("Writes the questions from the purpose and tries them on the work"). I only got a picture of it at README:71-73, where pith lists the questions it wrote.
- README:15, "essentials file". This is the first time the term appears. It is explained in the same sentence ("questions kept in an essentials file, one for each kind of work"), so I went on.
- README:36, "If a question cannot be compared with anything in your aim, pith names that question and asks you to add to the aim before any first user runs." I stopped here. I did not yet know which questions there were, so I could not tell what kind of aim would fall short.
- README:91, the heading "## prompt.md: When you gave it ...". I stopped at "prompt.md". The work in the example is `pr-review.md`. I worked out that `prompt.md` is probably the essentials file for prompts, but the README never names that file.
- README:88-93 (see above): I went back to tie the wrong path to the Good entry.
- README:104, "The renamed field is different: the receiver did not get what the work is for". I read it again to work out the rule for when a recheck is needed. What I took: an easy-to-see fix can be settled by hand, and a More about the purpose needs a recheck.

- Good: `pith/README.md:15` "essentials file" is explained where it is first met, so the reader goes on.
  - Evidence (report): "It is explained in the same sentence"
- Good: `pith/README.md:104` After reading it again, the reader takes the line the aim draws between a More to recheck and one to settle in the file.
  - Evidence (report): "an easy-to-see fix can be settled by hand, and a More about the purpose needs a recheck."
- More: `pith/README.md:7` The reader does not know what "tries on your work" means until the code example.
  - Evidence (report): "did not know what trying meant"
  - Left because: the code example shows it, and the reader carried through.
- More: `pith/README.md:36` The reader cannot tell what kind of aim would fall short of a question.
  - Evidence (report): "so I could not tell what kind of aim would fall short."
  - Left because: pith names the uncovered question when it happens, and pith writes essentials itself; the reader's own files are optional.
- More: `pith/README.md:91` "prompt.md" in the excerpt's heading is never named, and the reader works out what it is.
  - Evidence (report): "but the README never names that file."
  - Left because: the reader worked out it names the file of the questions, and it is needed only after a check.
- More: `pith/README.md:97` The reader goes back to tie the wrong path to the Good entry.
  - Evidence (report): "I went back to tie the wrong path to the Good entry."
  - Left because: the reader did link it and read on; README:88 names the wrong path and the Report line at README:93 says the prompt sent it to a file that does not exist.
- More: `pith/README.md:104` The reader reads the sentence again to find the rule for when a recheck is needed.
  - Evidence (report): "I read it again to work out the rule for when a recheck is needed."
  - Left because: after the reading again the reader took the line the aim draws.

## doc.md: When you looked for a part to read again by its heading, under which heading did you find it, and under which did you not?

Report: - How to install: found under "## Getting started" (README:114).
- What to do with the result file: found under "## What stays in your repository, and how to clear it" (README:84).
- How to call it: found under "## Call `/pith:up` with the work and your aim, and you get a Good or More for every question" (README:13). The call shape itself is only in the examples (README:43).
- How to recheck: I first looked under the README:13 heading and did not find it. It is inside "## What stays in your repository, and how to clear it" (README:104).
- What to do about my own essentials files: I looked under README:13 and did not find it. It is under "## Example: checking code with no essentials file yet" (README:82).
- What changed for /writ:pith users: there is no heading for this. It is in the untitled opening (README:11). I first looked under "## With writ and rn" (README:108).

- Good: `pith/README.md:114` Installing, the result file and how to call are found at once under their headings (lines 114, 84, 13).
  - Evidence (report): "How to install: found under"
- More: `pith/README.md:84` Rechecking after a fix was looked for under another heading first.
  - Evidence (report): "How to recheck: I first looked under the README:13 heading and did not find it."
  - Left because: the reader found it in the section at README:84, whose heading names the result file, and carried through.
- More: `pith/README.md:82` Naming one's own essentials files was looked for under the call's heading and found under the code example.
  - Evidence (report): "What to do about my own essentials files: I looked under README:13 and did not find it."
  - Left because: the reader found it and named their own files in a first call.
- More: `pith/README.md:11` What changed for /writ:pith users has no heading, and the reader looked for it under "With writ and rn" first.
  - Evidence (report): "there is no heading for this"
  - Left because: it sits in the opening, where a former user reads first, and the reader took it.

## doc.md: Where, while reading, did you have to piece together in your head who does what, what passes, and in what order?

Report: - The sequence diagram (README:17-30) laid out who passes what. I read it as mermaid source text. From it I learned that the first user receives "The work, who uses it and what for, and the questions" and not the aim. README:34 says the same in prose.
- I had to piece together the life of a result file across README:86, 104 and 106: pith writes it, I fix things, I either edit it myself or recheck, pith rewrites one section, and finally I copy it into a commit and delete it. No single place shows this order.
- The relation between pith, writ and rn (README:11, 110-112, 118): writ and rn call pith, and installing either one installs pith. I put this together from three places.

- Good: `pith/README.md:17-30` The diagram gives who passes what, and that the first user does not get the aim.
  - Evidence (report): "laid out who passes what"
- More: `pith/README.md:86-106` The reader pieces together the life of a result file from three places.
  - Evidence (report): "No single place shows this order."
  - Left because: the three are in one section, in the order they happen, and the reader carried through.
- More: `pith/README.md:110-112` The reader pieces together how pith, writ and rn relate from three places.
  - Evidence (report): "I put this together from three places."
  - Left because: not needed to decide or start; the reader took both points the aim needs.

## doc.md: How certain did you take each statement you relied on to decide or act?

Report: - README:9, "Reading your work over yourself, or asking the AI that helped you make it, does not find these places." I took this as a flat claim and the main reason to choose pith. Nothing says how it was established.
- I took the example outputs (README:47-56, 71-79) as illustrations, because each is introduced with "Say ..." (README:40, README:65). I did not take them as recorded runs.
- README:116, "Without it, pith stops instead of skipping the check, and tells you to install it." I took this as a stated fact about behaviour.
- README:116, "on a Mac, it comes in the same developer tools as git". I took it as fact, but I would check my own Python version, since the README does not say which version those tools ship.
- README:11, "It checks the same way with the same questions". I took this as a guarantee for former /writ:pith users.
- README:110, "an improvement to how work is checked is made once in pith and reaches both". I took this as a statement of design, not something I act on.

- Good: `pith/README.md:40` The examples are taken as illustrations, not as recorded runs.
  - Evidence (report): "I did not take them as recorded runs."
- Good: `pith/README.md:11` A former /writ:pith user relies on getting the same check with the same questions.
  - Evidence (report): "I took this as a guarantee for former /writ:pith users."
- Good: `pith/README.md:110` A writ or rn user takes it that an improvement made in pith reaches both.
  - Evidence (report): "I took this as a statement of design, not something I act on."
- More: `pith/README.md:9` The claim that one's own reading does not find these places is read as flat, with nothing to show how it was established.
  - Evidence (report): "Nothing says how it was established."
  - Left because: it is the reason to choose pith, and the example at README:59 shows it.
- More: `pith/README.md:116` The reader would check their own Python, since the version the Mac tools ship is not said.
  - Evidence (report): "since the README does not say which version those tools ship"
  - Left because: the README states what is needed and why, so readers get it their own way, and pith tells them if it is missing.

## readme.md: Having read the opening, what did you take it you would get from this product?

Report: From README:3-7 I took three gains:
1. Knowing "where the receiver of your work, the person or AI that uses it, falls short of what you aimed for, from what happened when the work was actually used" (README:5).
2. Each point names a place and quotes what happened, "so you see what to fix and what must not be lost while fixing" (README:6). The part "what must not be lost" stayed vague for me until the Good entry at README:97.
3. Any kind of work can be checked, including code or tests, with questions written and kept for that kind (README:7).

- Good: `pith/README.md:5` From the opening the reader gains that pith shows where the receiver falls short, from an actual use of the work.
  - Evidence (report): "from what happened when the work was actually used"
- Good: `pith/README.md:7` The reader takes it that any kind of work can be checked, with questions written and kept for a new kind.
  - Evidence (report): "Any kind of work can be checked, including code or tests, with questions written and kept for that kind (README:7)."
- More: `pith/README.md:6` "What must not be lost" stays vague until the Good entry in the excerpt.
  - Evidence (report): "stayed vague for me until the Good entry at README:97."
  - Left because: the excerpt shows it in the same reading.

## readme.md: What did you take in as the reason to choose this product over what you would use instead?

Report: - The alternatives named are reading the work over myself and asking the AI that helped me make it (README:9). The reason given is that both "know what you meant, and fill in what the work leaves out without noticing". pith instead uses "a separate AI that does not know the discussion", which actually uses the work: it reads a document, runs a prompt, calls code, runs tests (README:9).
- The first example backs this up: "The first user did not read the prompt and say whether it looked right. It gave the prompt to an AI with a diff no step covers" (README:59).
- The examples are a CI PR-review prompt and a CLI export function. Both were close to the kind of work I would check. There is no example for a document, though the opening lists "a document" first (README:3).

- Good: `pith/README.md:9` The reader takes the reason the aim intends: their own reading and the AI that made the work fill in what they meant, and pith has a separate AI use the work.
  - Evidence (work): "Both know what you meant, and fill in what the work leaves out without noticing."
- Good: `pith/README.md:59` The example backs the reason, and both examples are close to the reader's own work.
  - Evidence (report): "Both were close to the kind of work I would check."
- More: `pith/README.md:3` There is no example for a document, though a document is listed first.
  - Evidence (report): "There is no example for a document"
  - Left because: the two examples show the flow for any work, and a writ user meets document checks through /writ:up.

## readme.md: How did you take in the way from starting to use it to getting the result, as a flow of what you do and what you get?

Report: The flow I took in: install (README:120-123), then call `/pith:up` with the work, the receiver and purpose, and the aim (README:22, 43-45). If no essentials file exists, pith writes one (README:23-25, 71-73). The first user uses the work, pith compares against my aim, and I get a short result of Good or More per question plus a file in `.pith/open/` (README:29, 56, 86). Then I fix things, settle easy ones by hand or recheck (README:104), and finally commit the file's text and delete it (README:106).

For each reason in the opening I found a step it leads to: a separate AI using the work (diagram line README:26-27), named places and quotes (README:50, 74, 95-100), and any kind of work (README:63-82). The only thing I did not find was how to see the built-in document and prompt questions.

- Good: `pith/README.md:13` The reader takes in the whole flow the aim intends, from install and the call through the result file to recheck and clearing, and ties each opening reason to a step.
  - Evidence (report): "For each reason in the opening I found a step it leads to"
- More: `pith/README.md:15` The reader finds no way to see the questions pith comes with for a document or a prompt.
  - Evidence (report): "The only thing I did not find was how to see the built-in document and prompt questions."
  - Left because: the examples show the kind of question asked, and the reader decided from them.

## readme.md: What names or mechanisms did you have to learn before you could go on, though you needed them neither to decide whether to use it nor to start?

Report: - "essentials file" (README:15) and the path `.pith/essentials/` (README:15). I needed these only when I reached code.
- "first user" (README:15, 21, 34). Its definition was not needed to call pith.
- The result-file format: `## prompt.md: ...`, `Evidence (report)`, `Evidence (work)`, `Left because:` (README:91-101). I needed this only after a check, and `prompt.md` was never explained.
- The rule that an aim must cover every question, or pith asks before any first user runs (README:36).
- That rn "keeps its own questions for its kinds of work, such as a plan, a design or a finished change, and hands them to pith" (README:112). I did not need this to decide or start.

- Good: `pith/README.md:34` The names met are those the aim needs the reader to know (the first user, the essentials file, the aim covering every question, a few lines of a result file, rn's own questions), and no further internal role.
  - Evidence (work): "The first user is given the work, who uses it and what for, and the questions, but never your aim."
- More: `pith/README.md:91` `prompt.md` in the result-file lines is learned without being explained.
  - Evidence (report): "`prompt.md` was never explained"
  - Left because: the reader worked out it names the file of the questions, and it is needed only after a check.

## readme.md: Relying on this README alone, how far did you get in installing it and starting to use it, and where did you look elsewhere?

Report: Prerequisites (README:116).
- I learned I need Claude Code, plus Python 3.9 or later because "Its checks are Python scripts".
- "Node.js is not needed."
- If Python is missing, "pith stops instead of skipping the check, and tells you to install it."
- I checked Python myself with `python3 --version`, which gave `Python 3.9.6`. The README doesn't give that command, so I used my own.

Install (README:118-123).
- I had the two commands: `/plugin marketplace add lovaizu/ccpm` and `/plugin install pith@ccpm`.
- Before running them, I looked at my plugin cache to check README:118 ("If you have writ or rn, pith is already installed"). That was the one place I looked outside the README.
- It showed `rn` and `writ` but no `pith`. The README gave me no step to resolve this (update writ, or install anyway), so I would have run the install command as a guess.
- I did not run the commands, as instructed.

First use.
- From README:13-36 and the two examples (README:43-45, README:68-69), I could write a call: the file path, who receives it and for what, then "The aim is ..." written out in sentences.
- README:36 told me pith asks for the aim if it is missing.
- README:86 and README:104-106 told me where the result goes (`.pith/open/`), how to recheck (`/pith:up Recheck .pith/open/01-report-pr-review.md; I fixed ...`), and how to clear it (copy the file into a commit message and delete it).
- I stopped short of a real call because pith is not installed here. The open points from the first answer (items 4-7) are what I would have had to guess on that first call.

Links I would follow.
- README:112 sends readers who want a document written for them to `../writ/README.md`.
- README:129 sends design questions to `docs/design.md`.
- I needed neither to install pith or start using it.

- Good: `pith/README.md:116-123` The reader has the prerequisites and both install commands from the README alone.
  - Evidence (report): "I had the two commands: `/plugin marketplace add lovaizu/ccpm` and `/plugin install pith@ccpm`."
- Good: `pith/README.md:43-45` The reader writes a first call from the examples, with the work, its receiver and purpose, and the aim.
  - Evidence (report): "I could write a call: the file path, who receives it and for what"
- Good: `pith/README.md:104-106` The reader knows where the result goes, how to recheck and how to clear it.
  - Evidence (report): "how to recheck (`/pith:up Recheck .pith/open/01-report-pr-review.md; I fixed ...`)"
- Good: `pith/README.md:112` The reader is no longer sent to writ's README to start; the link serves only a reader who wants a document written for them.
  - Evidence (report): "I needed neither to install pith or start using it."
- More: `pith/README.md:118` The reader looked outside the README to check that writ brought pith, found no pith, and had no step to resolve it but to install as a guess.
  - Evidence (report): "The README gave me no step to resolve this (update writ, or install anyway), so I would have run the install command as a guess."
  - Left because: pith is not released yet (the release waits for an instruction); the version that brings it is known only then.
- More: `pith/README.md:116` The reader checked Python with a command of their own, since the README gives none.
  - Evidence (report): "The README doesn't give that command, so I used my own."
  - Left because: the README states what is needed and why, so readers get it their own way, and pith tells them if it is missing.
- More: `pith/README.md:43` On a first call the reader would guess what counts as the work, the kind, whether running it on code is safe, and whether to commit the essentials file.
  - Evidence (report): "The open points from the first answer (items 4-7) are what I would have had to guess on that first call."
  - Left because: the call is plain prose, so the reader names the work as they would to Claude, as both examples do; they made a first call.
