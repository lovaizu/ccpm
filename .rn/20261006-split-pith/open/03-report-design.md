# Check: pith/docs/design.md

Target: pith/docs/design.md
Receiver and purpose: builders and maintainers of pith, writ and rn. They build pith from this design document (pith is being cut out of writ into a plugin of its own, with writ and rn checking through it), reading it through once, and later pick the section a proposed change touches to weigh that change by what it costs the user. They hold pith/README.md, which the design serves, and the repository (writ/, rn/), where today's parts live. A verification document pith/docs/verification.md is to be written later and does not exist yet.
Aim: The reader learns which feature brings each of the README's benefits (learning where the receiver falls short from what happened in use; each point naming its place and quoting what happened; checking any kind of work, writing the questions first for a kind with none; and, from "With writ and rn", an improvement to how work is checked made once in pith and reaching both writ and rn), and the acceptance criteria A1, A2, M1-M5 each feature gives, and can build pith from it: what moves into pith/ unchanged but for its names (the /pith:up skill replacing /writ:pith, result form and check script, the first user and its hook, the generator, the essentials files doc.md, readme.md, design.md, prompt.md, essentials.md, style.md, lint/, with tests and trials in dev/pith/), the small skill pith:where through which writ finds pith's files because a plugin cannot name a file in another plugin, writ keeping /writ:up and its foreground hook and starting pith:generator, rn keeping its own viewpoint files and dropping its own first user, report.md and the first-user hooks, and calling /pith:up for every check it makes with what it hands; writ and rn declaring pith as a dependency with ^0.1.0 and the marketplace copy used until release; /pith:up running with context: fork and background: false so the caller waits; where result files go (.writ/open/ for writ:up, .pith/open/ when called directly, a caller-named file for rn, essentials written for a new kind in .pith/essentials/). They take in, with the reason for each, the principles that hold throughout: only pith's conductor judges and only the caller decides fix or leave; the first user never learns how the work was made, held by its definition and a hook for what the definition cannot hold, and never given the aim; essentials content lives only in the essentials files; what a script can decide is checked by script and a check is never skipped when Python 3.9 is missing; only the work remains. From #37: a first user runs once for each work checked and once more per fixed attractive-quality More on that question alone, nothing else; the caller settles the result file itself (fixed More becomes Good, left one gets Left because:) and a hook of pith's runs the form check on every write to a result file, so pith no longer has a run that only settles the file. The result file's form is a contract with the outside, kept in the design with why each part exists: the form does not change and no field is added now; the marks → fixed:, → let go:, → to the user: belong to the commit that clears the file, not to the file's form. What callers rely on (inputs, short result, form, pith:where and the paths under it, pith:generator) is named, so a maintainer sees a change there is a change to writ and rn. For checking: per attractive criterion, the situation and what must happen to pass (A1 with pith alone on the README's pull-request review prompt with a hole that shows only when run, and on cli/src/export.js with no essentials file; A2 one /writ:up run and one rn plan check each starting pith:first-user and leaving a result file that passes the form check), machine checks for M4 and M5, and where a run starts and how it goes left to the verification document. Statements carry how certain they are (tried on which Claude Code version, official docs, decided), and what is not decided, such as how the form-check hook knows which essentials files a result file was checked against, is shown as not decided rather than covered over. With it, a maintainer who picks a likely change can decide from what the user would lose whether it fits the design and why.

A first user read the design once from the top as someone about to build pith, with pith/README.md beside it and today's parts in writ/ and rn/ (writ/skills/pith/, writ/agents/, dev/writ/trials/scenes.py, .claude/rules/plugin.md). It picked two likely changes, "when /pith:up is called directly, pith commits the result file itself" and "add a field naming the essentials files' directories to the result file", and tried to check A1 by use; pith is not built and verification.md does not exist, so nothing was run.

## doc.md: Once you finished reading, what did you take it you should decide and do?

Report: When I finished, this is what I took I should build:
- A `pith/` plugin holding every part listed at design.md:416-418: "the `/pith:up` skill with the result form and the check script, `pith:where`, the first user and its hook, the generator, the essentials files … `style.md`, and `lint/`". These are moved from writ "with their names changed" (422), and their tests go to `dev/pith/` (423).
- `/pith:up` as a skill with `context: fork` and `background: false` (164).
- A default result path `.pith/open/{NN}-report-{target}.md` (302).
- Essentials selection by kind, with a fallback to `.pith/essentials/` (183-185).
- A hook that limits the first user to `agent_type` `pith:first-user` (117-121).
- A `pith:where` skill that returns pith's directory (434-435).
- writ and rn declaring pith with `^0.1.0` (426).
- Removing `/writ:pith` (M3, 58).
- rn calling `/pith:up` for each of its checks (449-451).

Later, when weighing a change, I took it I should read the decisions under each feature heading and the "Principles every feature keeps".

There was one thing I took I could not build as specified: the hook that checks result files. design.md:342-345 says: "Not decided yet: how the hook knows which essentials files a result file was checked against … How the hook tells a result file from other files, and what it does when the check finds a problem, are not decided either." Yet design.md:311 ("The form is held by the check script and a hook") and 338-339 ("a hook of pith's runs it on every write to a result file") state the hook as if it were settled.

- Good: `pith/docs/design.md:416-451` The builder takes in what moves into pith/, pith:where, the dependency range, the fork-and-wait skill, the default result path and rn calling /pith:up for each check, as the aim intends.
  - Evidence (report): "A `pith/` plugin holding every part listed at design.md:416-418"
- More: `pith/docs/design.md:449-458` The builder's list of what to build has nothing on what rn drops besides its first user: rn's report.md and its first-user hooks, which today sit in rn/references/essentials/report.md and rn/hooks/checks/first_user_reads.py and first_user_writes.py, are not named, so the builder would leave them in rn.
  - Evidence (report): "rn calling `/pith:up` for each of its checks (449-451)."
  - Evidence (work): "rn keeps no first"
- More: `pith/docs/design.md:311` The builder takes the result-file hook as settled at 311 and 338-339 and only at 342 learns it cannot be built yet, so it reads the decided part and the undecided part as at odds.
  - Evidence (report): "state the hook as if it were settled"

## doc.md: Which parts did you use to decide or act, which did you skip without using, and where did you find yourself reading again what you had already read?

Report: **Used:**
- Acceptance criteria (38-63).
- The feature-to-criterion mapping (71-90).
- Every bullet under the four feature headings.
- The result-file form (347-391).
- The dependency and `pith:where` bullets (426-440).
- Validation (475-506).

**Skimmed:**
- The opening of "Four features bring the benefits" (67-69). It restates the README's three benefits, which I had just read at README.md:5-7.
- Lines 31-36, which define terms. The flowchart at 8-29 had already shown them, so I read them as a repeat. The one new point in them, "The aim is what the receiver should gain, written out in sentences by the caller" (34-35), I only caught on a second pass.

**Read again:**
- The `omitClaudeMd` paragraph (110-113), twice, to work out whether the design relies on the documentation or on the trial ("the official sub-agents documentation says `omitClaudeMd` is ignored for plugin agents, but on Claude Code 2.1.285 a plugin agent with it did not read the project's CLAUDE.md").
- The two hook statements (311 and 338-339), read again after reaching 342-345.
- Line 90, "M5 is held by the machine checks in the last section". I jumped ahead to 501-504 to see what those are.

- Good: `pith/docs/design.md:38-63` The acceptance criteria, the feature-to-criterion list, every feature section, the result form, the dependency and pith:where bullets and the validation were all used to build.
  - Evidence (report): "The feature-to-criterion mapping (71-90)."
- More: `pith/docs/design.md:67-69` The reader skims the restated README benefits, though the line is where each benefit is named for the feature list below it.
  - Evidence (report): "It restates the README's three benefits, which I had just read at README.md:5-7."
- More: `pith/docs/design.md:31-36` The term definitions read as a repeat of the figure, so the one new point, that the caller writes the aim out in sentences, was missed on the first pass.
  - Evidence (report): "I only caught on a second pass"
- More: `pith/docs/design.md:110-113` The reader reads the omitClaudeMd paragraph twice to tell whether the design rests on the documentation or on the trial.
  - Evidence (report): "to work out whether the design relies on the documentation or on the trial"
- More: `pith/docs/design.md:90` The reader jumps to the last section to learn which machine checks hold M5.
  - Evidence (report): "I jumped ahead to 501-504 to see what those are."

## doc.md: In trying to decide or act, what was not in the document, so that you could only guess or ask someone?

Report: - **The result-file hook.** How it knows the essentials files, how it recognizes a result file, and what it does on failure. The document says these are undecided (342-345).
- **The report language.** design.md:190 hands the first user "the language of its report", but the caller's inputs (figure line 19; sequence line 153) do not include a language. I could not tell where pith gets it from. I guessed it is "the user's language" (351).
- **rn's essentials file for "a question and a proposal".** Line 449-451 lists rn's checks as "the plan, the design, a task's result, the deliverable, a question and a proposal" and its files as "`plan.md`, `design.md`, `task-result.md`, `deliverable.md` and `conductor.md`". I guessed the last two checks use `conductor.md`. Today's rn/references/essentials/ also holds `report.md`, which the design does not mention, so I could not tell whether it moves, stays or goes.
- **What `pith:where` returns.** Line 434 says it "returns pith's own directory". The exact form (bare path or sentence) and how a calling skill reads it are not given.
- **The renames.** Line 422 says "moved with their names changed". Only the agent and skill names are given (`pith:first-user`, `pith:generator`, `pith:where`). Today the script lives at writ/skills/pith/scripts/check_result.py next to `parse.py` and `checks/`. The design names only `check_result.py` (335), not where it sits inside pith or what happens to `parse.py` and `checks/`.
- **How pith decides a document's kind** (prompt vs readme vs design) when the caller names no essentials file. Line 184 says "whichever … fits its kind" and nothing more.
- **Where the A1 validation fixtures live.** Lines 483-494 use "the pull-request review prompt of the README's example, which has one hole" and `cli/src/export.js`. Neither exists under pith/. I found the prompt scene only in today's writ trials (dev/writ/trials/scenes.py:53, `"pr-review-hole"`). How a run goes is deferred to verification.md (6, 481), which does not exist.
- **Issue references.** "#37" (246, 312) and "#44" (172, 466) are given without a repository or link, so I could not read them.

- Good: `pith/docs/design.md:342-345` The undecided parts of the result-file hook show as undecided, so the builder does not build a guess.
  - Evidence (report): "The document says these are undecided (342-345)."
- Good: `pith/docs/design.md:481` Where a run starts and how it goes is left to the verification document, as the aim intends.
  - Evidence (report): "How a run goes is deferred to verification.md (6, 481), which does not exist."
- More: `pith/docs/design.md:449-451` The builder cannot tell which of rn's essentials files checks a question and a proposal, or whether rn's report.md moves, stays or goes.
  - Evidence (report): "so I could not tell whether it moves, stays or goes"
- More: `pith/docs/design.md:190` The builder cannot tell where pith gets the language of the first user's report, since no caller input carries one, and guesses the user's language.
  - Evidence (report): "I could not tell where pith gets it from."
- More: `pith/docs/design.md:434` The builder of writ and rn does not know what form pith:where's answer takes or how a calling skill reads it.
  - Evidence (report): "The exact form (bare path or sentence) and how a calling skill reads it are not given."
- More: `pith/docs/design.md:422` The builder does not know the new names beyond the agents and skills, nor where the check script and its parts sit inside pith.
  - Evidence (report): "not where it sits inside pith or what happens to `parse.py` and `checks/`"
- More: `pith/docs/design.md:183-185` The builder does not know how pith tells a prompt from a README or a design document when no essentials file is named.
  - Evidence (report): "fits its kind" and nothing more."
- More: `pith/docs/design.md:172` The maintainer cannot read #37 and #44, which the design cites as grounds, because no repository or link is given.
  - Evidence (report): "are given without a repository or link, so I could not read them"

## doc.md: Reading through, where did you stop, go back or look ahead, and what did you not understand there?

Report: - **Line 19 (figure).** It uses "aim", "essentials files" and "result file" before the definitions at 31-36. I read on and found them afterwards.
- **Line 110-113.** I stopped on "Here pith relies on a trial against the documentation". I could not tell at first whether "against" meant "contradicting" or "checked against". I understood it once I read on to "the official sub-agents documentation says `omitClaudeMd` is ignored for plugin agents, but … did not read the project's CLAUDE.md".
- **Line 236.** "each fixed More of attractive quality". Until here, "attractive quality" had been a category of pith's own acceptance criteria (40). Here it classifies a More in someone else's work. Who decides whether a More is attractive or must-be quality is not said; I inferred it is the caller, from 241-243 ("the caller confirms its fix at its place").
- **Lines 311 / 338-339 vs 342-345.** I went back. The hook is first stated as working, then its key behaviour is said to be undecided.
- **Line 466.** "#44 stays rn's own for them". I did not understand what "stays rn's own" means. I guessed rn keeps its own foreground hook (today rn/hooks/checks/foreground_agents.py exists), like writ's at line 444 ("writ keeps … its hook that runs its agents in the foreground").
- **Line 293.** "writ:up's conductor commits and clears it, or rn's when rn called writ:up". I stopped to work out who commits a file in `.writ/open/` when rn is the outer caller.
- **Line 388-389.** It refers to `.claude/rules/plugin.md`, and I opened it. plugin.md:81 says of result files "commit it, and push it". The design's 314 says "pith never commits or pushes a result file". I matched these up through plugin.md:88-91 ("Only the conductor that talks with the user commits").

- Good: `pith/docs/design.md:8-29` The opening figure carries the reader past terms not yet defined without a stop.
  - Evidence (report): "I read on and found them afterwards."
- More: `pith/docs/design.md:110` The reader stops on "a trial against the documentation", unsure whether it means contradicting or checked against.
  - Evidence (report): "I could not tell at first whether"
- More: `pith/docs/design.md:236` "attractive quality" changes meaning from pith's own criteria to a kind of More in someone else's work, and who decides which kind a More is goes unsaid.
  - Evidence (report): "Who decides whether a More is attractive or must-be quality is not said"
- More: `pith/docs/design.md:466` The maintainer does not understand "#44 stays rn's own for them" and guesses rn keeps its own foreground hook.
  - Evidence (report): "I did not understand what"
- More: `pith/docs/design.md:293` The reader stops to work out who commits a file in .writ/open/ when rn called /writ:up.
  - Evidence (report): "I stopped to work out who commits a file in `.writ/open/` when rn is the outer caller."
- More: `pith/docs/design.md:311` The reader goes back from 342 to 311 and 338, where the hook was stated as working.
  - Evidence (report): "The hook is first stated as working, then its key behaviour is said to be undecided."

## doc.md: When you looked for a part to read again by its heading, under which heading did you find it, and under which did you not?

Report: - **Result file form:** found under "The result file's form, a contract with the outside" (347).
- **Recheck behaviour:** found under "A first user only where use can show something new" (233). That heading did not read to me as "recheck"; I found it by scrolling.
- **First-user isolation and the history hook:** not under a heading of their own. Found as the second bullet of "Principles every feature keeps" (103-121).
- **Result-file hook:** found under "The form check" (333).
- **Dependency, versions and install:** no heading named that. Found under "Be the one place where writ and rn check their work" (426).
- **Python requirement:** no heading. Found inside the principle "Whatever a script can decide is checked by a script" (130-138).
- **Validation:** found under "Check that the user gets each benefit (validation)" (475).
- **Where each feature is:** each feature has a heading worded the same as its bullet at 71-86, so I could jump from the list to the section.

- Good: `pith/docs/design.md:71-86` Each feature's heading matches its line in the feature list, so the maintainer jumps from a benefit to the section a change touches.
  - Evidence (report): "so I could jump from the list to the section"
- Good: `pith/docs/design.md:347` The result form, the form check and validation are found by their headings.
  - Evidence (report): "The result file's form, a contract with the outside"
- More: `pith/docs/design.md:233` The maintainer does not find the recheck by its heading and finds it by scrolling.
  - Evidence (report): "I found it by scrolling."
- More: `pith/docs/design.md:426` Dependency and versions, and the Python requirement, sit under no heading of their own, so a maintainer looking for them by heading does not find them.
  - Evidence (report): "no heading named that"

## doc.md: Where, while reading, did you have to piece together in your head who does what, what passes, and in what order?

Report: - **Nested calls rn → /writ:up → /pith:up.** I had to assemble this chain from 293, 304, 442-443 and 457 ("rn's documents are written by `/writ:up`, which checks them through pith in turn"). The point was to learn which `open/` the file goes into and who commits it. No figure shows this chain; the figure at 396-414 shows rn and writ calling pith side by side.
- **The full set of first-user inputs.** I combined three places: the figure line 20 ("work's location, receiver and purpose, essentials files; never the aim"), the sequence line 157, and the bullet at 190-192, which adds "the language of its report and, on a recheck, the questions to answer".
- **The essentials-writing path.** The order (generator writes → first user tries it on the work with `essentials.md` → conductor decides fixes → new generator per fix → then the actual check) I pieced together from the bullets at 256-283. That section has no figure.
- The figures at 8-29, 148-162 and 287-295 gave me who calls whom and in what order without my having to assemble it.

- Good: `pith/docs/design.md:148-162` The figures give who calls whom and in what order without assembling it.
  - Evidence (report): "gave me who calls whom and in what order without my having to assemble it"
- More: `pith/docs/design.md:396-414` The chain rn to /writ:up to /pith:up, and so which open/ a file lands in and who commits it, is pieced together from four places.
  - Evidence (report): "No figure shows this chain"
- More: `pith/docs/design.md:190-192` The full set of what the first user is handed is assembled from three places.
  - Evidence (report): "I combined three places"
- More: `pith/docs/design.md:256-283` The order of writing, trying and fixing an essentials file before the real check is pieced together from bullets.
  - Evidence (report): "That section has no figure."

## doc.md: How certain did you take each statement you relied on to decide or act?

Report: **Taken as tried, with the reach stated:**
- `omitClaudeMd` works on a plugin agent: "Only that version was tried, running the definition with and without the field twice each" (112-113).
- A forked skill can start the first user, "tried on Claude Code 2.1.285" (170-171).
- `background: false` makes the caller wait, "as tried on 2.1.291" (174).
- A dependency's skill returning its directory, "Tried on Claude Code 2.1.291" (439-440).

**Taken as documented, not tried:**
- Hooks carry `agent_type` on subagent tool calls, "By the official hooks documentation" (119-120).
- A range with no tag falls back to the marketplace's copy, "By the official documentation" (430-432).

**Taken as measured:**
- "13 calls of `/writ:up` ran pith 43 times, and three of rn's documents took 2 hours 43 minutes (#37)" (245-246).

**Taken as undecided:**
- 342-345.

**Stated flatly, with no source or check:**
- "python3 comes with git in the Mac developer tools, and on Linux and Windows it is no less common than jq" (134-135).
- "follows Anthropic's guidance that a role apart from the maker grades more strictly" (169), with no link.

I took these as assumptions.

**`background: false` as a skill frontmatter field.** Today's writ/skills/pith/SKILL.md:4 has only `context: fork` and no `background` line. I relied on line 174's trial for it.

- Good: `pith/docs/design.md:110-113` Tried statements carry the Claude Code version and how far they were tried, documented ones say so, and the undecided is marked, so the builder knows what to check again.
  - Evidence (report): "Taken as tried, with the reach stated:"
- Good: `pith/docs/design.md:430-432` Statements resting on the documentation say so.
  - Evidence (work): "By the official documentation"
- More: `pith/docs/design.md:134-135` The claim about where python3 is found carries no source or check, so the reader takes it as an assumption.
  - Evidence (report): "Stated flatly, with no source or check:"
- More: `pith/docs/design.md:169` The appeal to Anthropic's guidance has no link, so the reader cannot check it.
  - Evidence (report): "with no link"

## design.md: Having picked one likely change, how did you decide, from what the user would lose, whether it fits the design?

Report: **Change: "when called directly, pith commits the result file itself".** I went to "Keep the whole result in a result file that the caller settles" (285).
- 314-319 says: "pith never commits or pushes a result file; only the conductor that talks with the user does … a caller such as rn stops every other role from using git. Called directly, pith leaves the commit to the user, as the README says."
- From this I took what would be lost: under rn, pith's commit would fail, since rn blocks git for other roles. In every case, the commit would record settlement by a role that does not know what the user decided.
- I decided the change does not fit.
- The feature is tied at 83 to "A1, bringing the second benefit, and A2". I could not tie the commit rule itself to a README benefit, so I weighed the change through A2 (rn must be able to use pith) and 317 ("The record is kept by the one role that knows what the user decided").

**Second change: "add a `Checked against:` field holding the essentials files' directories, so the hook can find them".** I went to 342-345 and 350. Line 344 says "no field is to be added to the form", and line 350 says "The form below does not change, and no field is added now". From the design I decided this change does not fit. The design does not say what the user would lose by adding the field. The surrounding text names who reads the file: "the user, … callers such as writ and rn, and … later versions of pith" (349).

- Good: `pith/docs/design.md:314-319` The maintainer decides that pith committing does not fit, from what would break for rn and from who knows what the user decided.
  - Evidence (report): "I decided the change does not fit."
- More: `pith/docs/design.md:350` The maintainer rejects a new field only because the design says no field is added, without learning what the user would lose by it.
  - Evidence (report): "The design does not say what the user would lose by adding the field."
- More: `pith/docs/design.md:314` The commit rule ties to no README benefit, so the maintainer weighs it only through A2.
  - Evidence (report): "I could not tie the commit rule itself to a README benefit"

## design.md: When you were unsure whether a change fits the design, which principle did you recall and use?

Report: **For the commit change:**
- I recalled "Only pith's conductor judges a check, and only the caller decides what to do with it" (94). Its sentence "Whether to fix or leave a More is the caller's, since only the caller knows the purpose and the discussion" (99-100) led me to: the caller also commits.
- I recalled "In the end only the work remains, and a result file stays in `open/` until it is settled" (140). I took it that a result file must not leave `open/` through pith's own commit before it is settled.
- The deciding rule (314) is not among the principles; it sits beside the feature.

**For the field change:** I recalled no principle. I used the contract section (347-351).

- Good: `pith/docs/design.md:94` The maintainer recalls the judging principle and the only-the-work principle and uses them to weigh the change, while the rule that concerns one feature sits beside that feature.
  - Evidence (report): "The deciding rule (314) is not among the principles; it sits beside the feature."

## design.md: For each principle you used, what did you take it would break if it were not kept?

Report: - **Line 94 principle.** The text states it: "If this broke, a check would report what the maker meant, and the first benefit would be gone" (100-101).
- **Line 140 principle.** "Left behind, they would be for the user to clear away, and the user would not know which is the real one" (142-143). I took this as tied to the user's working tree, not to a README benefit by name.
- **The other principles, which I read but did not use for my change:**
  - 103 (first user never learns how the work was made): no "if it broke" sentence. I took it that the first benefit breaks, by analogy with 94.
  - 123 (essentials only in essentials files): "what the generator aims for and what the first user answers drift apart" (127). No README benefit is named.
  - 130 (scripts, never skipped): "no one would learn that the rule was not kept" (138).

- Good: `pith/docs/design.md:100-101` The judging principle names the benefit lost if it broke.
  - Evidence (work): "If this broke, a check would report what the maker meant, and the first benefit would be gone."
- More: `pith/docs/design.md:103` The first-user principle names nothing that breaks, so the maintainer infers it by analogy.
  - Evidence (report): "I took it that the first benefit breaks, by analogy with 94."
- More: `pith/docs/design.md:123-128` The essentials principle says what drifts but no benefit the user loses.
  - Evidence (report): "No README benefit is named."

## design.md: For each of the README's benefits, through which feature did you take it the user gets it?

Report: From 67-90:
- **README.md:5, learning from use →** "Check a work by its use, and give a Good or More for every question" (71-74: "brings the first two benefits").
- **README.md:6, place and quote →** the same feature, plus "Keep the whole result in a result file that the caller settles" (81-84: "bringing the second benefit").
- **README.md:7, any kind of work →** "Write an essentials file for a kind of work that has none, and try it on the work" (76-79: "brings the third benefit").
- **README.md:110, an improvement reaches writ and rn →** "Be the one place where writ and rn check their work" (86-88) and the result-file feature (83: "A2, since writ and rn read and settle the same file").
- **README.md:11, `/writ:pith` is now `/pith:up` →** M3, through "Be the one place…" (88).

Each feature line points to README section headings, such as "It works in the README's 'Call `/pith:up` with the work and your aim' …" (73-74).

- Good: `pith/docs/design.md:71-88` Every README benefit maps to a feature with the criteria it gives and the README section where it works.
  - Evidence (report): "Each feature line points to README section headings"

## design.md: After the change you picked, what did you take it must always hold?

Report: Line 297-299 introduces "The following always hold." After the commit change I took these to still have to hold:
- "pith never commits or pushes a result file" (314). My change breaks this.
- "`open/` holds only what is not settled … a file whose Mores are all settled is cleared by copying its whole text into a commit message and deleting it in that commit" (321-323).
- "There is one file per target, and a recheck or a settling rewrites that file" (329).

I read these as conditions, not steps. The clearing in 322-323 reads as a procedure step ("copying … and deleting it in that commit"), but it is placed under "always hold".

- Good: `pith/docs/design.md:297-329` What always holds about the result file reads as conditions, so the maintainer knows which one the change breaks.
  - Evidence (report): "I read these as conditions, not steps."
- More: `pith/docs/design.md:321-323` The clearing reads as a procedure step under "always hold".
  - Evidence (report): "The clearing in 322-323 reads as a procedure step"

## design.md: In trying to check one benefit, what did you take it must happen for the check to pass?

Report: **Benefit picked:** A1 by use (483-488).
**Pass bar:** "It passes when a More points at that hole with what happened in use as its evidence" (486). The reason given is that the hole "cannot be seen by reading the prompt and shows only when the prompt is run" (487-488).

**What I did:** I looked for the prompt with the hole. It is not in pith/. The README shows only fragments of it (README.md:50, 95-99: lines 3, 12 and 13). I found a scene for it in today's writ trials, dev/writ/trials/scenes.py:53-60 (`"pr-review-hole"`, `"look": "a More points at the missing check on response fields, with what happened in use as its evidence"`).

**Where I stopped:** That file also has a `"pr-review-sound"` scene (62-68): `"look": "the question the other scene's More answers comes back Good"`. design.md's A1 scene has no counterpart to it. I did not run the check: pith is not built, and how a run goes is deferred to verification.md, which does not exist (481).

**The other A1 scene (490-494)** passes when "pith first writes an essentials file for code in `.pith/essentials/`, and then checks `export.js` with it, every question answered from what happened when the code was run".

- Good: `pith/docs/design.md:486-488` The pass bar is what must happen in use, with why the situation proves the benefit.
  - Evidence (report): "It passes when a More points at that hole with what happened in use as its evidence"
- More: `pith/docs/design.md:483-488` The builder stops at the A1 scene because today's trials also have a sound-prompt scene that must come back Good, and the design has no counterpart, so it cannot tell whether a pass that flags everything counts.
  - Evidence (report): "design.md's A1 scene has no counterpart to it."

## design.md: In what situation did you take it that check is run?

Report: - "with pith installed alone, without writ" (483), on a prompt "which has one hole, with the README's aim" (484-485).
- The general rule is at 478-479: "in situations where the user would plainly struggle without the benefit; in other situations, whether it arrived cannot be seen".
- For A2 (496-499): "one `/writ:up` run and one rn check of a plan against `plan.md`", passing when "each starts `pith:first-user` and leaves a result file that passes pith's form check".

- Good: `pith/docs/design.md:483-499` Each attractive scene names the situation, pith alone on the prompt with a hole, and one /writ:up run and one rn plan check for A2.
  - Evidence (report): "with pith installed alone, without writ"

## design.md: Where did you take it the checking effort goes?

Report: - "Checking effort goes to A1 and A2 first" (477).
- Scripts every time for M4 and M5 (501-504), plus tests of the check script and the first user's hook on a case each stops and lets through (503-505).
- "M1 to M3 are not checked up front" (505-506).

- Good: `pith/docs/design.md:477-506` Effort goes to A1 and A2 first, scripts hold M4 and M5, and M1 to M3 wait for use.
  - Evidence (report): "Checking effort goes to A1 and A2 first"

## design.md: Where you were tempted to replace the current way with another option, why did you take it the current way was chosen?

Report: - **Copying essentials into rn, or hard-coding a path into pith, instead of `pith:where`.** 437-440: "A plugin cannot name a file inside another plugin: the official documentation gives no path variable for a dependency's directory", plus the 2.1.291 trial. Copying is ruled out at 420-421 and 126-128.
- **Guarding the first user with hooks only.** 108-109: "watching every way it is called with hooks grows tangled, while a definition holds however it is called".
- **Making `/pith:up` an agent.** 167: "because the user calls it by name and other plugins' skills call it too".
- **Returning the whole result in the conversation.** 221-222.
- **Rechecking must-be Mores and rechecking the whole work.** 239-246, with the #37 figures.
- **Node.js for the scripts.** 134-136.
- **pith committing (my change).** 317-319.

- Good: `pith/docs/design.md:437-440` For each option a maintainer would reach for, pith:where, hooks only, an agent, the whole result in the conversation, wider rechecks, Node.js and pith committing, the reason the current way was chosen is beside it.
  - Evidence (report): "A plugin cannot name a file inside another plugin"

## design.md: Supposing the change you picked were made, which sentences would have to be rewritten though the intent stays the same?

Report: For the commit change I would rewrite:
- 314-319;
- the figure node at 292 ("The user commits and clears it");
- line 86 of README.md.

Those sentences state the decision itself, so the intent would change too.

Going through for sentences that would go stale on a rebuild with the intent unchanged, I noted:
- `context: fork` / `background: false` (164);
- Claude Code version numbers (111, 171, 174, 439);
- `check_result.py` (335, 340);
- `dev/pith/` (423);
- `references/essentials/`, `references/style.md`, `references/lint/` (435);
- `pith--v<version>` and `^0.1.0` (426-427);
- the agent names `pith:first-user` and `pith:generator` (120, 263);
- the git subcommand list "log, show, diff, blame, reflog, stash" (118);
- `.claude/projects` (119).

Line 460-462 marks `pith:where`'s paths and `pith:generator` as relied on by callers.

- Good: `pith/docs/design.md:460-462` The names a rebuild could change are marked where callers rely on them, so a change there reads as a change to writ and rn.
  - Evidence (report): "Line 460-462 marks `pith:where`'s paths and `pith:generator` as relied on by callers."
- More: `pith/docs/design.md:118-119` The list of git subcommands and the path the hook stops go stale on a rebuild though the intent, keeping the first user from history, stays.
  - Evidence (report): "log, show, diff, blame, reflog, stash"
- More: `pith/docs/design.md:335` The script's file name goes stale on a rebuild, though callers rely on the form, not the script.
  - Evidence (report): "`check_result.py` (335, 340);"

## design.md: In trying to change the form of something left in the user's environment for later versions or people to read, which fields did you take it could be changed without breaking those who read it?

Report: **What I tried:** adding a `Checked against:` line (my second change).

**What the design says about the form:**
- At 350-351: "The form below does not change, and no field is added now. The text beside each label is written in the user's language."
- Fixed: the labels (353-356), the name `{NN}-report-{target}.md` (361-362), the top fields (366), one section per question headed `<essentials file name>: <question>` (370-371), and `path:line` with quoted evidence (376-377). Each has a stated reason, such as "The check script and every caller find each question's section … by these words" (358-359).

**What I took could change without breaking readers:**
- the text beside the labels;
- the commit-message marks `→ fixed:`, `→ let go:`, `→ to the user:`, which "belong to the commit message that clears the file … not to the file's form" (388-391);
- a caller's own marks in its commit (391).

**What I did not find stated:**
- the order of Goods and Mores within a section;
- whether a section may hold both kinds of Evidence line under one item.

**About today's implementation:** today's writ/skills/pith/result-form.md:1-30 holds a second copy of the same form. The design says nothing about whether pith/ keeps such a file; line 416 lists "the `/pith:up` skill with the result form".

- Good: `pith/docs/design.md:347-391` Each part of the form carries why it exists, and the commit marks are set apart from it, so the maintainer tells what can change without breaking readers.
  - Evidence (report): "Each has a stated reason"
- More: `pith/docs/design.md:416` The design keeps the form and also moves the skill's own result form into pith, so the maintainer cannot tell which of the two copies is the form when they differ.
  - Evidence (report): "The design says nothing about whether pith/ keeps such a file"
- More: `pith/docs/design.md:376-377` The order of Goods and Mores in a section, and whether one item may carry both kinds of evidence, are not stated, so the maintainer cannot tell whether a caller relies on them.
  - Evidence (report): "the order of Goods and Mores within a section;"
